from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.database import UserAccount, Household
from app.models.schemas import UserCreate, UserResponse, Token, HouseholdCreate, HouseholdResponse
from app.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from uuid import UUID

async def create_household(db: AsyncSession, household_in: HouseholdCreate) -> HouseholdResponse:
    db_household = Household(
        name=household_in.name,
        location=household_in.location,
        inverter_type=household_in.inverter_type,
        capacity_kw=household_in.capacity_kw,
        grid_zone=household_in.grid_zone
    )
    db.add(db_household)
    await db.commit()
    await db.refresh(db_household)
    return HouseholdResponse.model_validate(db_household)

async def create_user(db: AsyncSession, user_in: UserCreate, household_id: UUID) -> UserResponse:
    result = await db.execute(select(UserAccount).where(UserAccount.email == user_in.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = UserAccount(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        household_id=household_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse.model_validate(new_user)

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Token:
    result = await db.execute(select(UserAccount).where(UserAccount.email == email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(db_user.user_id), "household_id": str(db_user.household_id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.user_id)})
    
    db_user.jwt_refresh_token = refresh_token
    await db.commit()
    
    from app.config import settings
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
