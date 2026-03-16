from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.models.schemas import UserCreate, UserResponse, Token, HouseholdCreate
from app.services.auth_service import create_user, authenticate_user, create_household
from jose import jwt, JWTError
from app.config import settings
import uuid
from sqlalchemy import select
from app.models.database import UserAccount

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    result = await db.execute(select(UserAccount).where(UserAccount.user_id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Create a dummy household for the user since the PRD mentions a multi-step onboarding flow
    default_household = HouseholdCreate(
        name=f"{user_in.name}'s Home",
        location="Gwalior",
        inverter_type="mock",
        capacity_kw=3.0,
        grid_zone="MP"
    )
    household = await create_household(db, default_household)
    return await create_user(db, user_in, household.household_id)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, form_data.username, form_data.password)

@router.get("/verify")
async def verify(current_user: UserAccount = Depends(get_current_user)):
    """
    Simple token validation endpoint.
    Returns a boolean flag and the authenticated user's ID.
    """
    return {"valid": True, "user_id": str(current_user.user_id)}
