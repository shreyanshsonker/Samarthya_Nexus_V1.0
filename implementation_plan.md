# Samarthya Nexus — Comprehensive Software & ML Implementation Plan

> **Project**: Samarthya Nexus — AI-Driven Carbon Footprint Analyzer for Homes Using Renewable Energy
> **Version**: 1.0 | **Team**: Samarth Shrivastava, Shreyansh Sonker, Shreya Kumari
> **Source Documents**: PRD v1.0, SAD v1.0, AI Rules v1.0, UI Design Rules v1.0

---

## 1. Project Understanding

### 1.1 Product Vision
*[Source: PRD §1]*

Samarthya Nexus is a **mobile application** (React Native + Expo) that transforms the invisible environmental impact of rooftop solar energy into a tangible, real-time narrative for Indian homeowners. It targets homeowners in **Gwalior, Madhya Pradesh** with Growatt or SMA inverters.

### 1.2 Core Problem
*[Source: PRD §2]*

| Root Cause | Impact |
|---|---|
| Manual data entry | High friction → user abandonment |
| Generic national averages | MP grid is 0.82 kg/kWh, not the 0.71 national average — 15% inaccuracy |
| No actionability | Data without path to reduce footprint |
| No solar offset visualization | Can't see ROI of panels |
| No real-time feedback | Missed daily opportunity windows |

### 1.3 Product Goals
*[Source: PRD §3.1]*

1. **Automate** carbon footprint tracking — zero manual data entry (Growatt/SMA inverter integration)
2. **Localize** — real-time MP grid carbon intensity (0.82 kg CO₂/kWh) vs. national averages
3. **Visualize** solar ROI — Shadow-Grid comparison (actual vs. grid-only household)
4. **Drive behavior** — Green Window alerts shift appliance usage to peak solar hours
5. **Build engagement** — gamification + social sharing create habits

### 1.4 Success Metrics (OKRs)
*[Source: PRD §3.2]*

| Objective | Key Result | Target |
|---|---|---|
| Automate tracking | Sessions with zero manual input | 95% |
| Accuracy | Error vs actual bill data | < 8% |
| Engagement | DAU/MAU ratio | ≥ 40% |
| Behavior change | Users following ≥ 1 Green Window rec/week | ≥ 55% |
| ML accuracy | ARIMA-LSTM forecast MAE | < 0.4 kW |
| Reliability | API uptime | ≥ 99% |

---

## 2. Extracted Requirements

### 2.1 Functional Requirements Summary
*[Source: PRD §6]*

| Module | Key Requirements |
|---|---|
| **Authentication** | Email/password, JWT (24h access + 30-day refresh), OTP email verification, account lockout after 5 failures |
| **Onboarding** | 4-step flow: Inverter Setup → Location → System Capacity → Feature Tour |
| **Home Dashboard** | Real-time energy display (30s WebSocket updates), Green Window banner, pull-to-refresh |
| **Shadow-Grid Engine** | Side-by-side green vs shadow comparison at 15-min/daily/weekly/monthly granularity, share cards |
| **Green Window & ML** | 4-hour ARIMA-LSTM forecast (16 × 15-min steps), sliding 2-hour optimal window, push notifications |
| **Insights** | 7-day bar chart, area chart, hourly carbon heatmap, 30-day trend, household benchmark |
| **Recommendations** | Up to 5 daily AI recommendations with SHAP explanations, follow/dismiss actions |
| **Gamification** | Daily score (0–100), achievement badges (6 types), annual carbon certificate (PDF) |
| **Settings** | Profile management, inverter config, notification prefs, data export (CSV), privacy controls |

### 2.2 Non-Functional Requirements
*[Source: PRD §7]*

| Category | Requirement | Target |
|---|---|---|
| Performance | API response time (p95) | < 400ms |
| Performance | WebSocket push latency | < 800ms |
| Performance | App cold start | < 2.5s |
| Performance | ML forecast generation | < 3s |
| Reliability | API uptime | 99% monthly |
| Security | Password storage | bcrypt, cost factor 12 |
| Security | JWT | Access: 24h, Refresh: 30 days |
| Security | Inverter credentials | AES-256 encrypted in DB |
| Security | Transport | TLS 1.3 enforced (HTTPS/WSS) |
| Scalability | Concurrent users | Up to 100 households |
| Maintainability | Test coverage | ≥ 70% backend, ≥ 50% frontend |

### 2.3 Technology Stack
*[Source: PRD §13, SAD §15]*

| Layer | Technology | Version |
|---|---|---|
| Frontend | React Native + Expo | SDK 51 |
| State Management | Zustand | 4.x |
| Charts | Victory Native | 36.x |
| Backend | Python FastAPI | 0.111 |
| ML — ARIMA | statsmodels | 0.14 |
| ML — LSTM | TensorFlow / Keras | 2.16 |
| ML — XAI | SHAP | 0.45 |
| Time-Series DB | InfluxDB | 2.7 OSS |
| Relational DB | PostgreSQL | 15-alpine |
| Cache | Redis | 7-alpine |
| IoT Broker | EMQX (MQTT) | 5.6 |
| Auth | python-jose + passlib | Latest |
| Deployment | Docker + Docker Compose | Latest |
| CI/CD | GitHub Actions | — |
| Push Notifications | Firebase Cloud Messaging (FCM) | — |
| Reverse Proxy | Nginx | Alpine |

### 2.4 AI & ML Constraints
*[Source: AI Rules §4, PRD §6.4, SAD §5]*

| Constraint | Specification |
|---|---|
| Model architecture | Hybrid ARIMA-LSTM (residual correction), not pure LSTM or pure ARIMA |
| ARIMA order | (2,1,2) fitted on solar_kw time series |
| LSTM architecture | 2-layer: LSTM(64) → Dropout(0.2) → LSTM(32) → Dropout(0.2) → Dense(16) |
| Input shape | (batch, 96, 1) — 24 hours of 15-min residuals |
| Output shape | (batch, 16) — 4 hours of residual corrections |
| Loss function | Huber loss |
| Training frequency | Every 4 hours via APScheduler |
| Training data window | Last 30 days of energy_readings from InfluxDB |
| Forecast horizon | 4 hours (16 × 15-min intervals) |
| MAE threshold | < 0.4 kW (target), warn if > 0.6 kW |
| Explainability | SHAP DeepExplainer at inference time, top 3 features stored |
| Inference latency | < 3 seconds (cold), < 10ms (cached in Redis) |
| Carbon formulas | **Fixed** — never modify without explicit instruction |

**Fixed Carbon Constants** *[Source: AI Rules §11]*:
- `GRID_INTENSITY_MP_FALLBACK = 0.82` (kg CO₂/kWh)
- `TREE_DAILY_ABSORPTION = 0.0596` (kg CO₂/day/tree)
- `CAR_HOURLY_EMISSION = 0.417` (kg CO₂/hr)
- `INVERTER_API_TIMEOUT_SEC = 2`
- `DARK_BACKGROUND = #141420`

---

## 3. System Architecture

### 3.1 Overall Architecture
*[Source: SAD §1, §3]*

**Five-Layer, Event-Driven Architecture** within a monorepo structure:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 5 — PRESENTATION (React Native + Expo)               │
│  25 screens, 5 navigation flows, Zustand state, WebSocket   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4 — API & REAL-TIME (FastAPI + WebSocket)             │
│  9 REST + 1 WS + Recommendation Engine + Push Service        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3 — AI/ML INTELLIGENCE                                │
│  ARIMA + LSTM + Shadow-Grid + SHAP/XAI                       │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2 — INGESTION & PROCESSING                            │
│  MQTT Broker + FastAPI ingestion + Cleaning Pipeline          │
│  → InfluxDB 2.0 + PostgreSQL                                │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1 — EXTERNAL DATA SOURCES                             │
│  Growatt | SMA | Electricity Maps | Open-Meteo | Mock Engine │
└─────────────────────────────────────────────────────────────┘
```

**Key Patterns** *[Source: SAD §1]*:
- Primary: Layered Architecture (5 tiers)
- Real-time: Event-Driven (WebSocket push, MQTT pub/sub)
- Client: Mobile Client-Server (REST + WebSocket)
- ML: Pipeline Architecture (sequential training + inference)
- Data: CQRS-lite (InfluxDB reads/writes, separate ML write path)
- Security: Defense in Depth (5 security layers)

### 3.2 Design Principles
*[Source: SAD §2.1]*

| Principle | Application |
|---|---|
| Graceful Degradation | Mock Engine fallback, CEA static fallback, cached ML predictions |
| Separation of Concerns | Independent services: GrowattService, CarbonService, MLService, AuthService |
| Real-Time First | WebSocket primary, HTTP polling fallback |
| Explainability by Design | SHAP integrated at inference time, not post-hoc |
| Localization Over Generics | Gwalior-specific grid intensity (0.82 kg/kWh) |
| Privacy by Default | JWT guards, AES-256 encrypted tokens, GDPR-ready delete |
| Testability | Mock Engine, dependency injection, factory pattern |

### 3.3 Architectural Constraints
*[Source: SAD §2.2]*

- **No physical inverter** during development → Mock Engine is mandatory
- **Zero cloud cost** — BCA academic project, everything runs locally or on free-tier VPS
- **3 developers** — module boundaries must be strict for parallel work
- **10-week timeline** — monorepo with modular internal boundaries (no microservice deployments)
- **Gwalior-specific** data — fallback to MP state-level data when no Gwalior API exists

### 3.4 Backend Internal Architecture
*[Source: SAD §4]*

**Three-sublayer structure**: Routes → Services → Data Access

> [!IMPORTANT]
> **RULE-002 (HARD STOP)**: Routes must NEVER directly call databases or external APIs. All data access goes through the service layer. *[Source: AI Rules §4.1]*

| Router | Prefix | Responsibility |
|---|---|---|
| auth_router | `/auth` | Registration, login, token refresh, profile, password reset |
| energy_router | `/api/energy` | Live readings, historical queries |
| carbon_router | `/api/carbon` | Shadow-Grid calculations, daily/weekly summaries |
| forecast_router | `/api/forecast` | ARIMA-LSTM forecast, Green Window detection |
| recommend_router | `/api/recommendations` | Daily recommendation list, mark-as-followed |
| ws_router | `/ws` | WebSocket connection management |
| inverter_router | `/api/inverter` | Credential management, connection test, sync |
| data_router | `/data` | CSV export, data deletion, privacy controls |

**Service Layer** (dependency injection pattern):
```python
def get_inverter_service() -> BaseInverterService:
    if settings.USE_MOCK:
        return MockService()
    elif settings.INVERTER_BRAND == 'growatt':
        return GrowattService()
    elif settings.INVERTER_BRAND == 'sma':
        return SMAService()
```

**Data Access Layer** (3 singleton clients):
| Client | Library | Connected To |
|---|---|---|
| InfluxDBClient | influxdb-client-python | InfluxDB 2.0 (port 8086) |
| AsyncSession | SQLAlchemy + asyncpg | PostgreSQL (port 5432) |
| Redis | aioredis | Redis (port 6379) |

### 3.5 Security Architecture
*[Source: SAD §9]*

5 layers of defense in depth:

1. **Network**: TLS 1.3, Nginx rate limiting (100 req/min/IP), CORS whitelisting
2. **Authentication**: bcrypt (cost 12), JWT stateless, OTP verification, account lockout
3. **Authorization**: verify_token FastAPI dependency, household_id scoped queries
4. **Data**: AES-256 encrypted inverter tokens, InfluxDB bucket-level tokens, .env secrets
5. **Privacy**: GDPR-ready export/delete APIs, data retention policies

### 3.6 Deployment Architecture
*[Source: SAD §10]*

Docker Compose services: `fastapi`, `influxdb`, `postgres`, `redis`, `emqx`, `nginx`

**Production spec**: 2 vCPU, 4 GB RAM, 40 GB SSD, Ubuntu 22.04 LTS

---

## 4. UI Implementation Plan (Stitch)

### 4.1 Design Philosophy
*[Source: UI Design Rules §1]*

| Principle | Manifestation |
|---|---|
| Immersive depth | Foreground/midground/background layers, hero cards float |
| Organic energy | Rounded corners everywhere, green hero color, warm dark mode (navy, not black) |
| Data as story | Large display numbers, animated counters, CO₂ always shown with trees equivalent |
| Earned complexity | Simple home screen, detail one tap away, progressive disclosure |
| Not AI-generated | No generic card grids, no purple gradients, no floating orbs |

### 4.2 Complete Screen Inventory (25 Screens)
*[Source: PRD §9, UI Design Rules §7]*

| # | Screen Name | Flow | Stitch Prompt Section |
|---|---|---|---|
| 1 | Splash / Launch | Auth | — (system screen) |
| 2 | Login | Auth | UI Rules §7.1 Screen 1 |
| 3 | Register | Auth | UI Rules §7.1 Screen 2 |
| 4 | OTP Verification | Auth | UI Rules §7.1 Screen 3 |
| 5 | Inverter Setup | Onboarding | UI Rules §7.2 Screen 4 |
| 6 | Location Setup | Onboarding | UI Rules §7.2 Screen 5 |
| 7 | System Capacity | Onboarding | UI Rules §7.2 Screen 6 |
| 8 | Feature Tour | Onboarding | UI Rules §7.2 Screen 7 |
| 9 | Home Dashboard | Core Tab | UI Rules §7.3 Screen 8 |
| 10 | Shadow-Grid View | Core Tab | UI Rules §7.3 Screen 9 |
| 11 | Green Window | Core Tab | UI Rules §7.3 Screen 10 |
| 12 | Insights | Core Tab | UI Rules §7.3 Screen 11 |
| 13 | Recommendations | Core Tab | UI Rules §7.3 Screen 12 |
| 14 | Score & Badges | Core Tab | UI Rules §7.3 Screen 13 |
| 15 | Live Reading Detail | Detail | — |
| 16 | Day Detail | Detail | UI Rules §7.4 Screen 14 |
| 17 | Forecast Detail | Detail | UI Rules §7.4 Screen 15 |
| 18 | Recommendation Detail | Detail | UI Rules §7.4 Screen 16 |
| 19 | Notification Center | Detail | — |
| 20 | Carbon Certificate | Detail | UI Rules §7.4 Screen 17 |
| 21 | Inverter Status | Detail | UI Rules §7.4 Screen 18 |
| 22 | Profile & Account | Settings | UI Rules §7.5 Screen 21 |
| 23 | Inverter Settings | Settings | UI Rules §7.5 Screen 22 |
| 24 | Notification Prefs | Settings | UI Rules §7.5 Screen 23 |
| 25 | Data & Privacy | Settings | UI Rules §7.5 Screen 24 |
| — | About & Help | Settings | UI Rules §7.5 Screen 25 |

### 4.3 Design Tokens
*[Source: UI Design Rules §2, §3, §4]*

**Color Tokens**:
| Token | Light | Dark |
|---|---|---|
| background.primary | #F7F8FA | #141420 |
| background.surface | #FFFFFF | #1E1E2E |
| brand.primary | #00C896 | #00E5A8 |
| text.primary | #0A0A0A | #FFFFFF |
| status.error | #FF6B6B | #FF7070 |

**Typography Scale**: display (32sp/700), h1 (24sp/600), h2 (18sp/600), h3 (15sp/500), body.lg (14sp/400), body.sm (13sp/400), label (11sp/400), micro (10sp/500)

**Corner Radius**: r4, r8, r12, r16, r20, r28, r50 only

**Spacing**: Multiples of 4dp only (4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48)

### 4.4 Key Components
*[Source: UI Design Rules §5, §6]*

- **CapsuleTabBar**: Floating full-pill navigation bar (r28, 56dp height, spring-animated active indicator) — replaces standard React Navigation tab bar
- **Metric Cards**: 3 types — Standard (r12), Hero (r20, brand-green bg), Stat (compact, r14)
- **Buttons**: Primary (brand.primary, r22 pill), Secondary, Outline, Ghost, Destructive
- **Input Fields**: 52dp height, floating labels, r12 border, focus/error states
- **Theme Hook**: `useTheme()` — all colors via tokens, never hardcoded hex

### 4.5 Stitch Workflow
*[Source: AI Rules §7]*

> [!IMPORTANT]
> **RULE-030 (MUST)**: Every screen MUST be generated from the corresponding Stitch prompt first. Manual UI code without a prior Stitch generation attempt is NOT permitted.

**Workflow per screen**:
1. Copy Universal Context Block from UI Design Rules §7
2. Copy exact Stitch prompt for the target screen
3. Submit combined prompt to Stitch MCP
4. Run 8-point Token Audit (colors, radius, fonts, spacing, capsule nav, dark mode, no AI clichés, touch targets)
5. Apply corrections for any failed audit points
6. Add `// [STITCH-GENERATED]` header comment
7. Replace hardcoded colors with `useTheme()` tokens
8. Replace local state with Zustand stores
9. Add spring animations (react-native-reanimated)
10. Integrate into project file structure

### 4.6 Navigation Structure
*[Source: SAD §6.2]*

```
App.tsx
  └── AuthStack (if not logged in)
  │     ├── SplashScreen → LoginScreen → RegisterScreen
  │     └── OnboardingStack (InverterSetup → Location → Capacity → Tour)
  └── MainTabs (if logged in)
  │     ├── HomeTab → HomeDashboard → LiveReadingDetail
  │     ├── ShadowTab → ShadowGridView → DayDetail
  │     ├── GreenTab → GreenWindowScreen → ForecastDetail
  │     ├── InsightsTab → InsightsScreen
  │     └── RecommendTab → RecommendationsScreen → RecommendDetail
  └── SettingsStack (modal)
        ├── ProfileScreen → InverterSettings → NotificationPrefs
        ├── DataPrivacyScreen
        └── AboutScreen
```

### 4.7 State Management (Zustand)
*[Source: SAD §6.1]*

| Store | State | Updated By |
|---|---|---|
| useEnergyStore | solar_kw, consumption_kw, net_grid_kw, source | WebSocket push (30s) |
| useCarbonStore | green_co2, shadow_co2, offset, trees | REST `/api/carbon/*` |
| useForecastStore | forecast array, green_window start/end | REST `/api/forecast/*` |
| useRecommendStore | recommendations list, followed, streak | REST `/api/recommendations/*` |
| useAuthStore | access_token, user_id, household_id | Auth flow + refresh |
| useSettingsStore | quiet_hours, alert_threshold, mode | Settings screen |

---

## 5. Backend Architecture

### 5.1 API Specification
*[Source: PRD §11, SAD §8]*

**Base URL**: `https://api.samarthya.app/v1` (prod) / `http://localhost:8000` (dev)

| Method | Endpoint | Auth | Request | Response |
|---|---|---|---|---|
| POST | `/auth/register` | None | `{ name, email, password }` | `{ user_id, message: 'OTP sent' }` |
| POST | `/auth/login` | None | `{ email, password }` | `{ access_token, refresh_token, expires_in }` |
| GET | `/auth/verify` | Bearer | — | `{ valid: true, user_id }` |
| GET | `/api/energy/current` | Bearer | — | `{ solar_kw, consumption_kw, net_grid_kw, source, timestamp }` |
| GET | `/api/energy/history` | Bearer | `?days=7` | `[{ timestamp, solar_kw, consumption_kw }]` |
| GET | `/api/carbon/live` | Bearer | — | `{ energy:{...}, carbon:{ green_kg, shadow_kg, saved_kg, trees } }` |
| GET | `/api/carbon/daily-summary` | Bearer | — | `{ date, solar_kwh, grid_kwh, saved_kg, trees, shadow_kg }` |
| GET | `/api/carbon/weekly-summary` | Bearer | — | `[{ date, saved_kg, footprint_kg } × 7]` |
| GET | `/api/forecast/solar` | Bearer | — | `{ forecast:[{ timestamp, predicted_kw, lower, upper }] }` |
| GET | `/api/forecast/green-window` | Bearer | — | `{ window:{ start, end, avg_kw, saving_kg }, recommendation }` |
| GET | `/api/recommendations/today` | Bearer | — | `[{ id, title, desc, saving_kg, shap_features }]` |
| PATCH | `/api/recommendations/:id` | Bearer | `{ followed: true }` | `{ success: true }` |
| GET | `/api/inverter/status` | Bearer | — | `{ connected, last_sync, errors_24h, power_kw }` |
| POST | `/api/inverter/sync` | Bearer | — | `{ synced: true, reading: {...} }` |
| WS | `/ws/live` | Bearer (query) | — | Pushes `energy_update` payload every 30s |

**Response Envelope** *[Source: SAD §8.2]*:
```json
{
  "data": { /* actual payload */ },
  "meta": { "timestamp": "ISO-8601-UTC", "source": "growatt_live" }
}
```

**Error Envelope**:
```json
{
  "error": {
    "code": "INVERTER_TIMEOUT",
    "message": "...",
    "fallback_activated": true,
    "fallback_source": "mock_engine",
    "timestamp": "ISO-8601-UTC"
  }
}
```

### 5.2 Service Layer Responsibilities
*[Source: SAD §4.2]*

| Service | Responsibility |
|---|---|
| **AuthService** | JWT management (python-jose), bcrypt hashing, OTP generation, account lockout |
| **GrowattService** | ShinePhone Cloud API wrapper (unofficial REST), 2s timeout, credential encryption |
| **SMAService** | Sunny Portal API wrapper (OAuth2), 2s timeout, credential encryption |
| **MockService** | Synthetic bell-curve solar data, behavioral consumption, fixed seed for reproducibility |
| **CarbonService** | Shadow-Grid calculations, Electricity Maps API integration, CEA fallback |
| **MLService** | ARIMA-LSTM training pipeline, inference pipeline, SHAP computation |
| **RecommendationEngine** | Rule-based + ML-assisted scoring, Green Window detection, recommendation generation |
| **NotificationService** | FCM/APNs push, quiet hours enforcement, scheduling |
| **DataExportService** | CSV generation, data deletion, privacy controls |

### 5.3 Error Handling
*[Source: SAD §13]*

| Failed Component | Fallback | User Experience |
|---|---|---|
| Growatt/SMA API | Mock Engine | Badge shows 'MOCK', data flows |
| Electricity Maps | CEA static 0.82 | Calculations continue |
| Open-Meteo | Skip weather overlay | Forecast runs, cloud chart hidden |
| InfluxDB | Queue retry (max 3) | 'Last updated X min ago' |
| Redis | Bypass cache | Slower response, no impact |
| ML Service | Serve cached forecast | Stale Green Window, warning logged |
| WebSocket | HTTP polling (60s) | Brief delay, badge shows 'cached' |

---

## 6. Database Design

### 6.1 InfluxDB Schema (Time-Series)
*[Source: SAD §7.1, PRD §12.1]*

**Measurement: `energy_readings`**
- Tags: `source`, `location`, `inverter_id`
- Fields: `solar_kw`, `consumption_kw`, `net_grid_kw`, `carbon_intensity`, `green_co2_kg`, `shadow_co2_kg`, `offset_co2_kg`, `trees_equiv`
- Retention: Raw 90 days → Hourly avg 2 years → Daily aggregate forever

**Measurement: `ml_predictions`**
- Tags: `model_version`, `horizon_hours`
- Fields: `predicted_solar_kw`, `confidence_lower`, `confidence_upper`, `arima_component`, `lstm_correction`, `mae_last_run`
- Retention: 48 hours

**Measurement: `recommendations`**
- Tags: `category`, `household_id`
- Fields: `message`, `potential_saving_kg`, `peak_start`, `peak_end`, `confidence`, `followed`
- Retention: 30 days

### 6.2 PostgreSQL Schema (Relational)
*[Source: PRD §12.2, SAD §7.2]*

```
HOUSEHOLD (household_id UUID PK)
├── name, location, inverter_type, capacity_kw, grid_zone, created_at
│
USER_ACCOUNT (user_id UUID PK, household_id UUID FK → HOUSEHOLD)
├── email, password_hash (bcrypt), inverter_token (AES-256), jwt_refresh_token, created_at
│
ENERGY_READING (reading_id UUID PK, household_id UUID FK)
├── timestamp, solar_kw, consumption_kw, net_grid_kw, source
│ ↓ 1:1
CARBON_RECORD (record_id UUID PK, reading_id UUID FK → ENERGY_READING)
├── green_co2_kg, shadow_co2_kg, offset_co2_kg, grid_intensity, trees_equiv
│
ML_PREDICTION (pred_id UUID PK, household_id UUID FK)
├── horizon_hours, predicted_solar_kw, arima_component, lstm_correction, mae
│
RECOMMENDATION (rec_id UUID PK, household_id UUID FK)
├── category, message, saving_kg, confidence, followed, created_at
```

### 6.3 Redis Cache Keys
*[Source: SAD §7.3]*

| Key Pattern | Value | TTL |
|---|---|---|
| `forecast:current:{household_id}` | 16-step ARIMA+LSTM forecast JSON | 4 hours |
| `green_window:{household_id}` | Green Window start/end/saving JSON | 4 hours |
| `carbon_summary:daily:{household_id}:{date}` | Daily aggregation | 24 hours |
| `session:{user_id}` | JWT refresh token metadata | 30 days |

### 6.4 Retention & Downsampling Strategy
*[Source: SAD §7.1]*

| Resolution | Duration | Downsampling | Query Use |
|---|---|---|---|
| 15-min raw | 90 days | None | Live dashboard, day detail |
| 1-hour avg | 2 years | InfluxDB Task: `mean() window(1h)` | Weekly insights |
| 1-day aggregate | Forever | InfluxDB Task: `sum() window(1d)` | Annual certificate |

---

## 7. Machine Learning / AI System Design

### 7.1 ML Problem Definition
*[Source: SAD §5, PRD §6.4]*

**Task Type**: Time-series forecast (regression)
- **Input**: Last 24 hours (96 × 15-min) of `solar_kw` from `energy_readings`
- **Output**: Next 4 hours (16 × 15-min) of predicted solar generation
- **Downstream**: Green Window detection (sliding 2-hour window optimization)

### 7.2 Data Pipeline
*[Source: SAD §5.1]*

**Data Sources**:
- Growatt ShinePhone Cloud API (`solar_kw`, `eToday_kWh`, `device_status`)
- SMA Sunny Portal API (`currentPower_W`, `energyToday_Wh`)
- Open-Meteo Weather API (`solarIrradiance`, `cloudCover`, `temp`)
- Mock Engine (synthetic bell-curve for development)

**Preprocessing**:
1. Convert Wh to kWh
2. Forward-fill missing intervals (sparse night hours)
3. Flag outliers (3σ from rolling mean)
4. Synchronize timestamps to IST
5. ADF stationarity test — if p-value > 0.05, apply d=1 differencing
6. MinMaxScaler normalization of residuals to [0,1] for LSTM

### 7.3 Model Architecture
*[Source: SAD §5.1, ADR-001]*

**Hybrid ARIMA-LSTM (Residual Correction)**:

```
                  ┌──────────────────────────┐
  30-day          │  ARIMA(2,1,2)            │    Linear forecast
  solar_kw ──────►│  statsmodels             │──────────────────┐
  series          │                          │                  │
                  └──────────┬───────────────┘                  │
                             │ residuals = actual - fitted      │
                             ▼                                  │  COMBINE
                  ┌──────────────────────────┐                  │
  24-hour         │  LSTM (2-layer)          │     Residual     │
  residuals ─────►│  64 → Dropout(0.2) →     │──  correction ──►│── Final = ARIMA + LSTM
  (96 steps)      │  32 → Dropout(0.2) →     │   (16 steps)    │   clip(≥ 0)
                  │  Dense(16)               │                  │
                  └──────────────────────────┘                  │
                                                                ▼
                                                         16 × 15-min
                                                         solar forecast
```

**Hyperparameters**:
- ARIMA order: (2, 1, 2)
- LSTM input shape: (batch, 96, 1)
- LSTM output shape: (batch, 16)
- Loss: Huber loss (robust to cloud-induced outliers)
- Optimizer: Adam, lr=0.001
- Early stopping: patience=10, monitor=val_loss, restore_best_weights=True
- Train/val split: 80/20 on sliding window sequences

### 7.4 Training Pipeline
*[Source: SAD §5.1]*

**Schedule**: Every 4 hours via APScheduler

| Step | Operation | Details |
|---|---|---|
| 1 — Data Prep | Query InfluxDB last 30 days, forward-fill, ADF test, normalize | ~200ms |
| 2 — ARIMA Train | `ARIMA(2,1,2).fit()` on full solar_kw series, extract residuals | ~5s |
| 3 — LSTM Train | Train on residuals, early stopping, 80/20 val split | ~30-60s |
| 4 — Validation | Compute MAE on val set, warn if > 0.6 kW, save models | ~2s |

**Model Registry**:
- LSTM: `/models/lstm_{timestamp}.h5`
- ARIMA: `/models/arima_{timestamp}.pkl`
- `current_model` symlink to latest weights
- Training run metrics logged to InfluxDB

### 7.5 Inference Pipeline
*[Source: SAD §5.2]*

```python
async def get_solar_forecast():
    cached = await redis.get(f'forecast:current:{household_id}')
    if cached and age(cached) < 4h:
        return cached                          # <10ms
    recent_24h = await influxdb.query_last_24h()  # ~200ms
    arima_forecast = arima_model.forecast(steps=16)  # ~50ms
    lstm_correction = lstm_model.predict(residuals)  # ~800ms
    final = clip(arima + inverse_scale(lstm), min=0)
    await redis.set(cache_key, final, ttl=4h)
    return final                               # total: ~1.1s
```

### 7.6 Green Window Detection
*[Source: PRD §6.4 FR-GW-02]*

**Algorithm**: Sliding 2-hour window over 16 forecast steps
- Score = Σ(predicted_solar - estimated_consumption) for each step
- Window with highest score = Green Window
- Output: start time, end time, avg predicted solar kW, potential CO₂ saving

### 7.7 SHAP Explainability
*[Source: SAD §5.3]*

- SHAP DeepExplainer applied to LSTM at inference time
- Top 3 feature importances stored with each `ml_prediction` record
- Human-readable feature name mapping:

| Raw Feature | Human Label | Typical Importance |
|---|---|---|
| `solar_kw_t-1` | Solar generation 15 min ago | High (0.45-0.65) |
| `solar_kw_t-4` | Solar generation 1 hour ago | Medium (0.20-0.35) |
| `cloud_cover_pct` | Cloud cover forecast | Medium (0.15-0.30) |

### 7.8 AI Safety & Guardrails
*[Source: AI Rules §4, §6]*

- **No feature hallucination**: Only features listed in PRD §5.1 are permitted
- **Fixed carbon math**: Formulas cannot be modified — `offset = solar_kWh × grid_intensity`
- **External API timeouts**: 2 seconds, then fallback activates
- **Model monitoring**: MAE logged per training run, warning threshold at 0.6 kW
- **Stale forecast protection**: If training fails, serve last cached forecast with warning
- **Cross-household isolation**: All cache keys and queries scoped by `household_id`

### 7.9 Model Deployment
*[Source: SAD §5, §10]*

- **Serving**: In-process within FastAPI (no separate ML serving infrastructure for v1.0)
- **Versioning**: Timestamped model files + `current_model` symlink
- **Rollback**: Point `current_model` symlink to previous version
- **Monitoring**: InfluxDB stores training run metrics (MAE, val_loss, data_points, timestamp)

---

## 8. Development Roadmap

*[Source: PRD §14]*

### Phase 1 — Project Setup (Week 1)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Monorepo structure (backend/ + mobile/) | None | Low |
| Docker Compose with all 6 services | Docker installed | Medium |
| Environment configuration (.env template) | None | Low |
| GitHub repo + Actions CI/CD pipeline | GitHub account | Low |
| Expo project initialization (SDK 51) | Node.js | Low |
| FastAPI skeleton with router structure | Python 3.11+ | Low |

### Phase 2 — Core Backend Foundation (Week 1-2)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Auth service (register, login, JWT, OTP) | PostgreSQL | Medium |
| Mock Engine service | None | Medium |
| Pydantic request/response models | FastAPI | Low |
| Dependency injection pattern setup | FastAPI | Low |
| InfluxDB schema creation (3 measurements) | InfluxDB | Low |
| PostgreSQL schema (6 tables via SQLAlchemy) | PostgreSQL | Medium |

### Phase 3 — Data Pipeline (Week 2-3)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Growatt API integration service | Phase 2 | High |
| SMA API integration service | Phase 2 | High |
| Data cleaning pipeline (Wh→kWh, null handling, outlier flagging) | InfluxDB | Medium |
| APScheduler polling (every 5 min) | FastAPI | Low |
| WebSocket server (/ws/live endpoint) | Phase 2 | Medium |
| InfluxDB retention policies + downsampling Tasks | InfluxDB | Medium |

### Phase 4 — ML Pipeline (Week 3-5)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| ARIMA training module (statsmodels) | 30 days of data (mock) | Medium |
| LSTM training module (TensorFlow/Keras) | ARIMA residuals | High |
| Hybrid combiner (ARIMA + LSTM correction) | Both models | Medium |
| SHAP DeepExplainer integration | LSTM model | Medium |
| Inference pipeline with Redis caching | Redis | Medium |
| Model registry + symlink versioning | File system | Low |
| APScheduler training trigger (4h cycle) | APScheduler | Low |

### Phase 5 — Stitch UI Development (Week 5-7)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Theme system (useTheme hook, light/dark tokens) | Expo | Low |
| CapsuleTabBar component | react-native-reanimated | High |
| Auth screens (3) via Stitch + token audit | Stitch MCP | Medium |
| Onboarding screens (4) via Stitch + token audit | Stitch MCP | Medium |
| Core tab screens (6) via Stitch + token audit | Stitch MCP | High |
| Detail screens (7) via Stitch + token audit | Stitch MCP | Medium |
| Settings screens (5) via Stitch + token audit | Stitch MCP | Medium |
| Zustand stores integration | Phase 2 API | Medium |

### Phase 6 — API Integration (Week 6-7)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Shadow-Grid Engine (carbon calculations) | Phase 3 | Medium |
| Green Window detection endpoint | Phase 4 ML | Medium |
| Recommendations Engine | Phase 4 ML + SHAP | High |
| Carbon summary endpoints (daily, weekly) | InfluxDB queries | Medium |
| Mobile ↔ Backend full integration | Phases 3-5 | High |

### Phase 7 — AI Integration (Week 7-8)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Push notification service (FCM) | Green Window detection | Medium |
| Recommendation follow/dismiss flow | Phase 6 | Medium |
| Gamification scoring (3-component formula) | Phase 6 | Medium |
| Annual carbon certificate generation (PDF) | InfluxDB aggregations | Medium |

### Phase 8 — Testing & QA (Week 8-9)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Backend unit tests (pytest, 70% coverage target) | All backend modules | Medium |
| Frontend unit tests (Jest, 50% coverage target) | All screens | Medium |
| Integration tests (API contract validation) | Full system | Medium |
| ML model validation (MAE on mock dataset) | Phase 4 | Medium |
| Security audit (JWT, encryption, CORS) | Phase 2-3 | Medium |

### Phase 9 — Deployment & Monitoring (Week 9-10)
| Deliverable | Dependencies | Complexity |
|---|---|---|
| Production Docker Compose configuration | All phases | Medium |
| Nginx reverse proxy + TLS (Let's Encrypt) | VPS | Medium |
| UptimeRobot monitoring | Domain | Low |
| Demo dataset preparation (30-day mock) | Mock Engine | Low |
| Viva-ready build (Expo Go or standalone APK) | All phases | Medium |

---

## 9. Detailed Task Breakdown

### Epic 1: Project Foundation
| Task | Subtasks | Owner |
|---|---|---|
| E1.1 Repository Setup | Create monorepo, .gitignore, README, .env.example | Samarth |
| E1.2 Docker Infrastructure | docker-compose.yml with 6 services, volume mounts, port mapping | Samarth |
| E1.3 FastAPI Skeleton | App factory, lifespan events, 8 router modules, CORS config | Samarth |
| E1.4 Expo Project | `npx create-expo-app`, install dependencies (zustand, victory, reanimated) | Shreya |
| E1.5 CI/CD Pipeline | GitHub Actions: lint (ruff), test (pytest), type check (mypy) | Samarth |

### Epic 2: Authentication System
| Task | Subtasks | Owner |
|---|---|---|
| E2.1 User Models | SQLAlchemy models: HOUSEHOLD, USER_ACCOUNT | Samarth |
| E2.2 Auth Service | Register, login, JWT issue/refresh, OTP generation, lockout logic | Samarth |
| E2.3 Auth Router | POST /auth/register, /auth/login, GET /auth/verify, password reset flow | Samarth |
| E2.4 Auth Screens | Login, Register, OTP screens via Stitch → token audit → Zustand integration | Shreya |

### Epic 3: Inverter Integration
| Task | Subtasks | Owner |
|---|---|---|
| E3.1 Base Inverter Interface | `BaseInverterService` abstract class with `get_current_reading()` | Samarth |
| E3.2 Mock Engine | Synthetic bell-curve solar (Gwalior lat 26.2°N), behavioral consumption | Samarth |
| E3.3 Growatt Service | ShinePhone API wrapper, 2s timeout, credential encryption | Samarth |
| E3.4 SMA Service | Sunny Portal OAuth2 wrapper, 2s timeout | Samarth |
| E3.5 Onboarding Screens | Inverter Setup, Location, Capacity, Feature Tour via Stitch | Shreya |

### Epic 4: Data Pipeline
| Task | Subtasks | Owner |
|---|---|---|
| E4.1 InfluxDB Setup | Create bucket, 3 measurements, retention policies | Samarth |
| E4.2 PostgreSQL Schema | SQLAlchemy models for all 6 entities, migrations | Samarth |
| E4.3 Cleaning Pipeline | Wh→kWh conversion, null forward-fill, outlier flagging, IST sync | Samarth |
| E4.4 Scheduled Polling | APScheduler: poll inverter API every 5 min, write to InfluxDB | Samarth |
| E4.5 WebSocket Server | /ws/live endpoint, 30s push loop, heartbeat, connection management | Samarth |

### Epic 5: Carbon Engine
| Task | Subtasks | Owner |
|---|---|---|
| E5.1 Carbon Service | Shadow-Grid calculation: net_grid, green_co2, shadow_co2, offset, trees | Samarth |
| E5.2 Electricity Maps Integration | API wrapper, 2s timeout, CEA 0.82 fallback | Samarth |
| E5.3 Carbon API Endpoints | `/api/carbon/live`, `/daily-summary`, `/weekly-summary` | Samarth |
| E5.4 Shadow-Grid Screen | Stitch generation + token audit + data binding | Shreya |

### Epic 6: ML Pipeline
| Task | Subtasks | Owner |
|---|---|---|
| E6.1 Data Preparation | InfluxDB query, forward-fill, ADF test, MinMaxScaler | Shreyansh |
| E6.2 ARIMA Module | `statsmodels ARIMA(2,1,2)`, fit, extract residuals, log MAE | Shreyansh |
| E6.3 LSTM Module | Keras 2-layer LSTM, Huber loss, early stopping | Shreyansh |
| E6.4 Hybrid Combiner | ARIMA + LSTM correction, clip ≥ 0, validation | Shreyansh |
| E6.5 SHAP Integration | DeepExplainer, top 3 features, human-readable mapping | Shreyansh |
| E6.6 Inference Pipeline | Redis caching, 4h TTL, cold/warm inference paths | Shreyansh |
| E6.7 Training Scheduler | APScheduler 4h trigger, model registry, symlink versioning | Shreyansh |
| E6.8 Green Window Detection | Sliding 2h window algorithm, scoring, optimal window | Shreyansh |

### Epic 7: Recommendations & Gamification
| Task | Subtasks | Owner |
|---|---|---|
| E7.1 Recommendation Engine | Rule-based + ML scoring, 5 daily recommendations, categories | Samarth |
| E7.2 Recommendation API | GET /today, PATCH /:id (follow/dismiss) | Samarth |
| E7.3 Gamification Scoring | 3-component formula (offset 40%, recs 40%, engagement 20%) | Samarth |
| E7.4 Badge System | 6 achievement badges, unlock conditions, streak tracking | Samarth |
| E7.5 Carbon Certificate | PDF generation, shareable certificate with branding | Samarth |
| E7.6 Recommendations Screen | Stitch + SHAP bar chart integration | Shreya |
| E7.7 Score & Badges Screen | Stitch + animated score ring + badge grid | Shreya |

### Epic 8: Core UI Screens
| Task | Subtasks | Owner |
|---|---|---|
| E8.1 Theme System | useTheme hook, LIGHT/DARK tokens, useColorScheme | Shreya |
| E8.2 CapsuleTabBar | Floating pill nav, spring animation, 5 tabs | Shreya |
| E8.3 Home Dashboard | Hero card, stats row, shadow-grid mini, green window banner | Shreya |
| E8.4 Green Window Screen | Forecast chart, countdown, appliance suggestions | Shreya |
| E8.5 Insights Screen | Bar chart, area chart, heatmap, benchmark | Shreya |
| E8.6 Detail Screens | Day Detail, Forecast Detail, Recommendation Detail, Certificate | Shreya |
| E8.7 Settings Screens | Profile, Inverter, Notifications, Data & Privacy, About | Shreya |

### Epic 9: Notifications
| Task | Subtasks | Owner |
|---|---|---|
| E9.1 FCM Setup | Firebase project, Android config | Samarth |
| E9.2 Push Service | Green Window alerts, quiet hours check, 30-min pre-notification | Samarth |
| E9.3 Notification Center | UI screen for past alerts | Shreya |

### Epic 10: Testing & Deployment
| Task | Subtasks | Owner |
|---|---|---|
| E10.1 Backend Tests | pytest for all services, 70% coverage | Samarth |
| E10.2 Frontend Tests | Jest for components and stores, 50% coverage | Shreya |
| E10.3 ML Validation | MAE benchmark on mock dataset, cross-validation | Shreyansh |
| E10.4 Integration Tests | API contract validation, WebSocket test | Samarth |
| E10.5 Docker Production | Production compose, Nginx, TLS | Samarth |
| E10.6 Demo Preparation | 30-day mock dataset, demo scenario scripting | All |

---

## 10. Risks and Clarifications

### 10.1 Technical Risks
*[Source: PRD §15]*

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Growatt API changes/breaks (unofficial) | Medium | High | Mock Engine fallback, monitor library updates |
| LSTM training too slow on CPU | Medium | Medium | Pre-train on mock data, serve cached forecast |
| InfluxDB disk full | Low | High | Retention policies, 80% disk usage alert |
| WebSocket drops on mobile | High | Low | HTTP polling fallback in 5s |
| ML model overfits to mock data | Medium | Medium | 80/20 cross-validation, MAE monitoring |

### 10.2 ML-Specific Risks

| Risk | Mitigation |
|---|---|
| ARIMA non-stationarity | ADF test before fitting, apply differencing if p > 0.05 |
| LSTM vanishing gradients | 2-layer architecture with dropout, Huber loss |
| SHAP computational cost | Apply only at inference for top 3 features, cache with predictions |
| Weather data unavailable | Forecast proceeds without weather overlay, use historical irradiance |
| Insufficient training data (new installation) | Mock Engine provides baseline, 30-day minimum before accurate forecasts |

### 10.3 Items Requiring Clarification

> [!WARNING]
> The following items are explicitly flagged as **REQUIRES CLARIFICATION** based on gaps or ambiguities found in the source documents.

| # | Item | Source | Status |
|---|---|---|---|
| 1 | Which specific Growatt inverter models are most common in Gwalior? | PRD §16 OQ-01 | REQUIRES CLARIFICATION |
| 2 | Is free-tier Electricity Maps API sufficient for 100 households (100 calls/day)? | PRD §16 OQ-02 | REQUIRES CLARIFICATION |
| 3 | Should the app support Hindi language in v1.0? | PRD §16 OQ-03 | REQUIRES CLARIFICATION |
| 4 | What is the correct tree CO₂ absorption factor for Indian tree species? (currently using 0.0596 from FSI) | PRD §16 OQ-04 | REQUIRES CLARIFICATION — needs verification against latest FSI data |
| 5 | Should recommendations be server-side or on-device computed? | PRD §16 OQ-05 | REQUIRES CLARIFICATION — performance benchmark needed |
| 6 | Is Expo Go sufficient for demo or do we need a standalone APK? | PRD §16 OQ-06 | REQUIRES CLARIFICATION |
| 7 | Screen 15 (Live Reading Detail) and Screen 19 (Notification Center) have no Stitch prompts in UI Design Rules | UI Design Rules §7 | REQUIRES CLARIFICATION — prompts need to be created or these screens need manual UI design |
| 8 | PRD lists 25 screens but Screen 13 (Score & Badges) has no dedicated tab in the 5-tab CapsuleTabBar | PRD §9 vs UI Design Rules §5.2 | REQUIRES CLARIFICATION — where does Score & Badges live in navigation? |
| 9 | MQTT/EMQX broker is specified in SAD but no concrete IoT hardware is planned for v1.0 | SAD §3.2 vs PRD §5.1 | REQUIRES CLARIFICATION — is EMQX needed for v1.0 or is it future-proofing? |
| 10 | Stat card corner radius r14 in UI Design Rules §6.1 is NOT on the r-scale (permitted: 4/8/12/16/20/28/50) | UI Design Rules §6.1 vs §4.2 | REQUIRES CLARIFICATION — should this be r12 or r16? This contradicts RULE-032. |
| 11 | Alert/Banner card corner radius r14 is also off the r-scale | UI Design Rules §6.1 | REQUIRES CLARIFICATION — same contradiction as above |
| 12 | PRD data model (§12.2) lists ENERGY_READING and CARBON_RECORD as PostgreSQL tables, but SAD (§7.1) stores energy readings exclusively in InfluxDB. Dual storage is ambiguous. | PRD §12.2 vs SAD §7.1 | REQUIRES CLARIFICATION — InfluxDB should be the canonical store per SAD, but PRD suggests PostgreSQL entities. Are these redundant or do both exist? |
| 13 | PRD §12.2 lists relational entities but SAD §7.2 says "accessed exclusively through SQLAlchemy async ORM" without showing the complete PostgreSQL schema. Which entity set is canonical? | PRD §12.2 vs SAD §7.2 | REQUIRES CLARIFICATION — recommend using PRD entities as source of truth + InfluxDB for time-series optimization |

### 10.4 Scalability Concerns

- **v1.0 target**: 100 concurrent households on single 4GB VPS — well within limits
- **Scaling trigger**: At 500+ households, will need horizontal scaling (multiple FastAPI workers behind Nginx)
- **InfluxDB write throughput**: 6,000 points/min max — 100 households at 1 point/15 min is far under
- **ML training concurrency**: Single training run at a time — could bottleneck at scale

### 10.5 Security Concerns

- **Growatt API is unofficial** — credentials are sent to a third-party cloud not under project control
- **JWT access tokens cannot be revoked** before 24h expiry — stolen token has a 24h exposure window
- **AES-256 encryption key** storage in Docker secret — needs careful key management
- **OTP via email** — susceptible to email compromise; could consider TOTP in v2

---

> **Document generated from analysis of**: PRD v1.0 (1123 lines), SAD v1.0 (1000 lines), AI Rules v1.0 (815 lines), UI Design Rules v1.0 (1240 lines)
>
> Every specification, technology choice, formula, and constraint in this plan references the source document it came from. Items not covered by any source document are explicitly marked as **REQUIRES CLARIFICATION**.
