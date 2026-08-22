# NIVARA Backend - Safety, Caregiver & Geofencing Platform

FastAPI-powered backend engine for NIVARA, providing child safety tracking, real-time GPS streaming, geofenced safe zones, SOS emergency dispatch, and caregiver community features.

---

## 🏗️ Architecture Overview

```
backend/
├── app/
│   ├── main.py                     # FastAPI application entrypoint & startup seeders
│   ├── config/                     # Configuration and environment layer
│   │   ├── settings.py             # Pydantic Settings & environment defaults
│   │   ├── database.py             # SQLAlchemy engine, SessionLocal & get_db
│   │   └── security.py             # JWT token handling & bcrypt password hashing
│   │
│   ├── models/                     # SQLAlchemy ORM Database Models
│   │   ├── user.py                 # User & Caregiver models
│   │   ├── child.py                # Child profile & telemetry relations
│   │   ├── location.py             # GPS coordinates & breadcrumb logs
│   │   ├── device.py               # Hardware devices & smart band tracking
│   │   ├── safe_zone.py            # Circular & Polygon Geofenced Safe Zones
│   │   ├── emergency.py            # SOS alert lifecycle & resolutions
│   │   ├── emergency_contact.py    # Priority emergency contact registry
│   │   └── safety_event.py         # Audit event logs & acknowledgements
│   │
│   ├── schemas/                    # Pydantic v2 validation & response schemas
│   │   ├── location.py             # Location ingestion & current status schemas
│   │   ├── device.py               # Device pairing & heartbeat telemetry
│   │   ├── safe_zone.py            # Geofence boundary schemas & containment check
│   │   ├── emergency.py            # SOS triggering & resolution schemas
│   │   ├── emergency_contact.py    # Contact schemas & priority ordering
│   │   └── safety_event.py         # Event logs & Overview summary schemas
│   │
│   ├── routers/                    # FastAPI APIRouters
│   │   ├── safety.py               # Master Safety router & /overview aggregator
│   │   ├── location.py             # GPS logging, current position, history query
│   │   ├── devices.py              # Wearable device CRUD & heartbeat
│   │   ├── safe_zones.py           # Geofence CRUD & location containment check
│   │   ├── emergencies.py          # SOS trigger, active queries, resolution
│   │   ├── emergency_contacts.py   # Contact CRUD & priority ordering
│   │   └── safety_events.py        # Event logs & alert acknowledgements
│   │
│   ├── services/                   # Business Logic & Algorithms
│   │   ├── location_service.py     # GPS recording & history retrieval
│   │   ├── device_service.py       # Heartbeat handling & battery monitoring
│   │   ├── geofence_service.py     # Containment checking & breach alert triggers
│   │   ├── separation_service.py   # Caregiver-to-child proximity monitoring
│   │   ├── emergency_service.py    # SOS dispatch & lifecycle management
│   │   └── notification_service.py # Multi-channel dispatch (SMS, Push, Calls)
│   │
│   ├── websocket/                  # Real-Time WebSocket Streaming
│   │   ├── manager.py              # Channel & room connection manager
│   │   └── location_socket.py      # /ws/location/{child_id} live stream
│   │
│   ├── utils/                      # Geo & Math Helpers
│   │   ├── distance.py             # Haversine distance & Point-in-Polygon
│   │   ├── location_utils.py       # Azimuth bearing, bounding boxes, formatting
│   │   └── validators.py           # Coordinates, phone numbers & radius validators
│   │
│   └── dependencies/
│       └── auth.py                 # Authentication dependencies
│
├── tests/                          # Pytest Automated Test Suite
│   ├── test_location.py            # GPS tracking & history tests
│   ├── test_devices.py             # Wearables & heartbeat tests
│   ├── test_safe_zones.py          # Safe zones, containment & breach tests
│   ├── test_emergency.py           # SOS triggers & emergency contacts tests
│   └── test_safety_events.py       # Separation alerts & overview tests
│
├── .env.example
├── requirements.txt
├── README.md
└── run.py
```

---

## 🚀 Getting Started

### 1. Installation & Environment
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Development Server
```powershell
python run.py
```
Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** to view the interactive Swagger / OpenAPI API documentation.

### 3. Run Tests
```powershell
python -m pytest -s tests/test_location.py tests/test_devices.py tests/test_safe_zones.py tests/test_emergency.py tests/test_safety_events.py
```
