# Samarthya

Samarthya is a full-stack carbon footprint and energy monitoring app with:

- a React + Vite frontend
- a FastAPI backend
- a MySQL database
- optional ML training scripts for solar and usage models

This README is a Mac-friendly step-by-step guide to start the ML, database, backend, and frontend locally.

## Project Structure

- `Samarthya_frontend` - React web app
- `Samarthya_backend` - FastAPI API and database integration
- `Samarthya_ml` - model training scripts and datasets

## Prerequisites For macOS

Install these first:

1. Homebrew
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Node.js 18+
   ```bash
   brew install node
   ```
3. Python 3.11+
   ```bash
   brew install python
   ```
4. Docker Desktop for Mac
   Download and install from [Docker Desktop](https://www.docker.com/products/docker-desktop/), then open it once and wait until Docker says it is running.

Recommended version checks:

```bash
node -v
npm -v
python3 --version
docker --version
docker compose version
```

## Before You Start

Open Terminal and move into the project root:

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP"
```

You will usually run the app in 3 terminals:

1. database + backend
2. frontend
3. optional ML training

## Step 1: Start The Database And Backend

The backend uses Docker Compose and starts:

- MySQL on `3306`
- FastAPI on `8000`

### 1.1 Create the backend `.env`

In a new terminal:

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP/Samarthya_backend"
```

Create a `.env` file:

```bash
touch .env
```

Open it in any editor and add:

```env
APP_NAME=Samarthya
DEBUG=true
APP_VERSION=1.0.0

DATABASE_URL=mysql+aiomysql://user:password@db:3306/Samarthya_db
DATABASE_URL_SYNC=mysql+pymysql://user:password@db:3306/Samarthya_db

SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

ML_MODELS_DIR=app/ml_models
SOLAR_MODEL_FILE=solar_regressor_v1.pkl
KMEANS_MODEL_FILE=usage_kmeans_v1.pkl
SCALER_FILE=scaler_solar_v1.pkl

WEATHER_API_KEY=
WEATHER_API_URL=https://api.openweathermap.org/data/2.5

ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:8081"]
```

Notes:

- `ALLOWED_ORIGINS` includes the Vite frontend port `5173`.
- `WEATHER_API_KEY` can be left blank. The backend will return mock weather data if no API key is set.

### 1.2 Start Docker services

From `Samarthya_backend` run:

```bash
docker compose up --build
```

If you want it in the background:

```bash
docker compose up -d --build
```

### 1.3 Wait for startup

The backend automatically creates tables on startup using SQLAlchemy `create_all`, so you do not need to run a manual migration command for basic local setup.

When startup is complete:

- API: [http://localhost:8000](http://localhost:8000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 1.4 Verify backend health

In another terminal:

```bash
curl http://localhost:8000/health
```

You should get a JSON response showing backend status, database status, and ML model status.

## Step 2: Start The Frontend

Open a second terminal:

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP/Samarthya_frontend"
```

### 2.1 Install dependencies

```bash
npm install
```

### 2.2 Create frontend `.env`

Create the file:

```bash
touch .env
```

Add:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 2.3 Start the frontend

```bash
npm run dev
```

Vite will print a local URL, usually:

- [http://localhost:5173](http://localhost:5173)

Open that URL in your browser.

## Step 3: Start The ML Environment

This step is optional for normal app usage because trained model files are already present in the backend.

Use this if you want to retrain the ML models.

Open a third terminal:

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP/Samarthya_ml"
```

### 3.1 Create a virtual environment

```bash
python3 -m venv venv
```

### 3.2 Activate it

```bash
source venv/bin/activate
```

### 3.3 Install ML dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 Train the models

```bash
python train.py
```

After training finishes, the generated `.pkl` files should be available for backend use.

## Recommended Startup Order

Use this order on Mac:

1. Start Docker Desktop
2. Start backend + database with `docker compose up --build`
3. Confirm `http://localhost:8000/health` works
4. Start frontend with `npm run dev`
5. Optionally run ML training in a third terminal

## Quick Start Summary

If everything is already installed:

### Terminal 1

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP/Samarthya_backend"
docker compose up --build
```

### Terminal 2

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP/Samarthya_frontend"
npm install
npm run dev
```

### Terminal 3, optional

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP/Samarthya_ml"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train.py
```

## Useful URLs

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

## How To Stop Everything

### Stop frontend

In the frontend terminal, press `Ctrl + C`.

### Stop backend and database

If running in the foreground:

Press `Ctrl + C` in the backend terminal.

If running in detached mode:

```bash
cd "/Users/shrey/Desktop/Shrey/Minor Project/MVP/Samarthya_backend"
docker compose down
```

## Troubleshooting

### Docker is not running

If `docker compose` fails, open Docker Desktop and wait until it is fully started.

### Frontend cannot talk to backend

Check:

1. backend is running on `http://localhost:8000`
2. frontend `.env` contains `VITE_API_BASE_URL=http://localhost:8000`
3. backend `.env` includes `http://localhost:5173` in `ALLOWED_ORIGINS`

After changing `.env`, restart the affected service.

### Port already in use

If `3306`, `5173`, or `8000` is already occupied, stop the process using that port or change the port mapping/config.

### Weather endpoint fails

If you did not set `WEATHER_API_KEY`, the app should still work using mock weather data.

### ML models not loading

Make sure these files exist in `Samarthya_backend/app/ml_models`:

- `solar_regressor_v1.pkl`
- `usage_kmeans_v1.pkl`
- `scaler_solar_v1.pkl`

## Current Stack Notes

This repo currently uses:

- MySQL, not PostgreSQL
- React + Vite web frontend, not Expo
- backend startup table creation via `init_db()`

