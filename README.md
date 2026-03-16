# Samarthya Nexus ☀️🌱

**Samarthya Nexus** is an AI-driven carbon footprint analyzer and energy management system designed for residential renewable energy setups. It empowers homeowners to monitor their environmental impact in real-time, predict future solar generation with high accuracy, and receive actionable, AI-generated insights to optimize their energy consumption.

---

## 🚀 Quick Start: Run the System (Start to Finish)

Follow these steps to get the complete system running on your local machine.

### 1. Prerequisites
Ensure you have the following installed:
- **Docker & Docker Compose** (Required for the backend infrastructure)
- **Node.js (v18+)** (Required for the mobile development environment)
- **Expo Go** (Install on your iOS/Android phone to view the app)

### 2. Infrastructure Setup (Backend)
The backend uses a containerized infrastructure for PostgreSQL, InfluxDB, Redis, and the FastAPI server.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/samarthya-nexus.git
    cd samarthya-nexus
    ```

2.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and paste the following:
    ```env
    POSTGRES_USER=nexus_user
    POSTGRES_PASSWORD=nexus_pass
    POSTGRES_DB=nexus_db
    DB_HOST=postgres
    REDIS_URL=redis://redis:6379/0
    INFLUXDB_URL=http://influxdb:8086
    INFLUXDB_TOKEN=my-super-secret-auth-token
    INFLUXDB_ORG=nexus
    INFLUXDB_BUCKET=energy_readings
    INFLUXDB_ADMIN_USER=admin
    INFLUXDB_ADMIN_PASSWORD=password123
    SECRET_KEY=your_super_secret_jwt_key
    ```

3.  **Start the Services**:
    Run the following command to build and start all containers:
    ```bash
    docker-compose up --build -d
    ```

4.  **Verify Backend**:
    - **API Swagger**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)
    - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
    - **InfluxDB UI**: [http://localhost:8086](http://localhost:8086)

### 3. Mobile App Setup (Frontend)
The mobile app is built with Expo and connects to the backend API.

1.  **Install Dependencies**:
    ```bash
    cd mobile
    npm install
    ```

2.  **Point to Backend**:
    *Note: If running on a physical device, ensure your phone and computer are on the same Wi-Fi network.*
    Update the `API_BASE_URL` in `mobile/hooks/use-api.ts` to your machine's local IP (e.g., `http://192.168.1.5:8000`). Use `localhost` only for emulators.

3.  **Launch the App**:
    ```bash
    npx expo start
    ```

4.  **Open on Device**:
    Scan the QR code printed in your terminal using the **Expo Go** app (Android) or the **Camera** app (iOS).

---

## 🛠️ Technology Stack

### Backend & AI
- **FastAPI**: Core logic and REST API.
- **Hybrid ML**: ARIMA (Trends) + LSTM (Residuals) for 4-hour solar forecasting.
- **Explainable AI (SHAP)**: Human-readable model feature importance.
- **Databases**: PostgreSQL (Relational), InfluxDB (Time-series), Redis (Cashing).

### Mobile
- **React Native & Expo Router**: Modern mobile architecture.
- **Zustand**: Global state synchronization (Energy, Forecast, Auth).
- **Victory Native**: High-end area graphs and energy gauges.

---

## 📁 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── routers/       # Auth, Energy, Forecast, Recs, Inverter
│   │   ├── services/      # ML Pipeline, Recommendation Engine
│   │   └── models/        # Database Schemas
│   └── tests/             # Logic Verification
├── mobile/
│   ├── app/               # Tab & Auth Screens
│   ├── components/        # EnergyGauge, ForecastGraph, CarbonCard
│   └── hooks/             # useStores, useApi
└── docker-compose.yml     # Infrastructure Orchestration
```

---

## ⚙️ Development & Testing
To run a syntax and sanity check on backend Python modules:
```bash
python3 -m py_compile backend/app/**/*.py
```

---
**Samarthya Nexus** - *Advanced AI for Sustainable Living.*
