# GO Train Delay Refund Tracker

**Automated delay detection and refund email generation for GO Transit passengers**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

GO Train Delay Refund Tracker is a web application that automatically monitors GO Transit train delays and generates pre-filled refund email drafts when delays exceed the 15-minute service guarantee threshold. The system eliminates the manual process of checking delays and filling out refund forms by continuously polling live transit data and matching delays to user subscriptions.

**Current Status:** MVP Development Phase

## 🎯 Problem Statement

GO Transit offers a service guarantee where passengers can request compensation for trains delayed 15 minutes or more. However, the current process is entirely manual:

- ❌ Passengers must manually check if their train was delayed
- ❌ Passengers must fill out refund request forms
- ❌ Passengers must remember to submit refund claims
- ❌ Many eligible passengers never claim their refunds

**This project automates:**
- ✅ Real-time delay detection from live GTFS feeds
- ✅ Refund eligibility verification (≥15 minute delays)
- ✅ Generation of pre-filled refund email drafts

## ✨ Features

### MVP Features (Current Scope)
- **Real-time Delay Monitoring**: Polls GO Transit GTFS TripUpdates feed every 1-2 minutes
- **Automated Delay Detection**: Identifies trains delayed ≥15 minutes (900 seconds)
- **Email Draft Generation**: Creates ready-to-send refund request emails with trip details
- **Live Dashboard**: Simple Next.js interface displaying currently delayed trains
- **Single Line Focus**: MVP focuses on one GO train line for simplified development

### Planned Features (Post-MVP)
- Multiple train line support
- User authentication and accounts
- Automatic email submission
- SMS/push notifications for delay alerts
- Historical delay analytics and reporting
- Subscription billing via Stripe
- Mobile app (iOS/Android)

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│  GO Transit API │ (GTFS Realtime TripUpdates)
└────────┬────────┘
         │ Poll every 1-2 min
         ▼
┌─────────────────┐
│  FastAPI Backend│
│  - Parse GTFS   │
│  - Detect delays│
│  - Match subs   │
│  - Gen emails   │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐      ┌──────────────┐
│   PostgreSQL    │◄─────┤  Next.js UI  │
│   Database      │      │  Dashboard   │
└─────────────────┘      └──────────────┘
```

### Tech Stack

**Backend**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Scheduling**: APScheduler or FastAPI BackgroundTasks
- **API Client**: Requests library for GO Transit API
- **Data Format**: GTFS Realtime (JSON/Protocol Buffers)

**Frontend**
- **Framework**: Next.js 14+ (React)
- **Styling**: Tailwind CSS
- **Data Fetching**: Polling-based dashboard (30-60s intervals)
- **Deployment**: Vercel

**Infrastructure**
- **Backend Hosting**: Render / Railway / Heroku
- **Database**: Managed PostgreSQL (Supabase / Render / Railway)
- **Frontend**: Vercel
- **Monitoring**: (TBD)

## 📊 Database Schema

### MVP Schema

**subscriptions**
```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    route_id VARCHAR(50) NOT NULL,
    stop_id VARCHAR(50) NOT NULL,
    scheduled_time TIME NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**delay_events**
```sql
CREATE TABLE delay_events (
    id SERIAL PRIMARY KEY,
    trip_id VARCHAR(100) NOT NULL,
    route_id VARCHAR(50) NOT NULL,
    stop_id VARCHAR(50) NOT NULL,
    delay_seconds INTEGER NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- GO Transit Open API key ([Request here](https://api.openmetrolinx.com/))

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/go-refund-tracker.git
cd go-refund-tracker/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary requests apscheduler
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials:
# DATABASE_URL=postgresql://user:pass@localhost/go_refund_tracker
# GO_API_KEY=your_metrolinx_api_key
```

5. **Initialize database**
```bash
python -m app.database.init_db
```

6. **Run development server**
```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.local.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run development server**
```bash
npm run dev
```

Dashboard will be available at `http://localhost:3000`

## 📡 API Endpoints

### Backend REST API

**GET /delayed_trains**
- Returns list of currently delayed trips
- Response: JSON array of delayed trains with trip details

```json
{
  "delayed_trains": [
    {
      "trip_id": "123456_LSW_WB",
      "route_id": "LSW",
      "stop_id": "OAK",
      "delay_seconds": 1200,
      "detected_at": "2024-03-15T17:30:00Z"
    }
  ]
}
```

**POST /generate_email**
- Accepts subscription ID
- Returns formatted refund email draft

```json
{
  "subscription_id": 42
}
```

Response:
```json
{
  "email_draft": {
    "subject": "Refund Request – Delayed GO Train",
    "body": "Train: Lakeshore West\nDate: March 15, 2024\n..."
  }
}
```

**POST /subscriptions**
- Create new delay subscription
- Request body: route_id, stop_id, scheduled_time, email

**GET /subscriptions**
- List all active subscriptions

## 🔄 Development Workflow

### Phase 1: Core Backend ✅ (Current)
- [x] FastAPI project structure
- [x] PostgreSQL database setup
- [x] SQLAlchemy models
- [ ] GO Transit API integration
- [ ] GTFS TripUpdates parser
- [ ] Delay detection logic
- [ ] Background polling task
- [ ] REST API endpoints

### Phase 2: Frontend Dashboard
- [ ] Next.js project setup
- [ ] Delayed trains display component
- [ ] Email generation UI
- [ ] Subscription management (simple form)

### Phase 3: Deployment
- [ ] Backend deployment (Render/Railway)
- [ ] Database migration to managed Postgres
- [ ] Frontend deployment (Vercel)
- [ ] Environment variable configuration
- [ ] API key management

### Phase 4: Testing & Refinement
- [ ] Unit tests for delay detection
- [ ] Integration tests for API endpoints
- [ ] End-to-end testing
- [ ] Performance optimization

## 📖 How It Works

### Delay Detection Algorithm

1. **Polling Loop** (every 1-2 minutes)
   - Fetch latest TripUpdates from GO Transit API
   - Parse GTFS Realtime feed (JSON or Protocol Buffers)

2. **Subscription Matching**
   - For each active subscription:
     - Match by route_id and stop_id
     - Check if train is within time window
     - Extract arrival_delay from stop_time_update

3. **Eligibility Check**
   - If `arrival_delay >= 900 seconds` (15 minutes):
     - Create delay_event record
     - Mark as eligible for refund

4. **Email Generation**
   - On user request via API:
     - Fetch delay_event details
     - Format email with trip information
     - Return draft to frontend

### Example Email Output

```
Subject: Refund Request – Delayed GO Train

Dear GO Transit Customer Service,

I am writing to request compensation under the GO Transit Service Guarantee policy.

Train Details:
- Route: Lakeshore West
- Date: March 15, 2024
- Train Number: 1937
- Boarding Station: Oakville
- Scheduled Arrival: 5:15 PM
- Actual Arrival: 5:38 PM
- Delay: 23 minutes

As per your service guarantee, I am eligible for compensation for this delay exceeding 15 minutes.

Thank you for your attention to this matter.

[Passenger Name]
[Contact Email]
```

## 🌐 Data Sources

This project uses the **Metrolinx Open API** to access GO Transit real-time data:

- **API Base URL**: `https://api.openmetrolinx.com/OpenDataAPI/`
- **Primary Feed**: GTFS Realtime TripUpdates
- **Data Format**: JSON or Protocol Buffers
- **Rate Limit**: 300 calls/second
- **Update Frequency**: Real-time (polling every 1-2 minutes)

**Key Data Fields Used:**
- `trip_id`: Unique trip identifier
- `route_id`: Train line identifier
- `stop_id`: Station code
- `arrival.time`: Scheduled arrival (epoch format)
- `arrival.delay`: Delay in seconds (negative = early)

## 🛣️ Roadmap

### v1.0 (MVP) - Q2 2024
- Single GO train line support
- Basic delay detection
- Email draft generation
- Simple dashboard

### v1.1 - Q3 2024
- All GO train lines
- User authentication
- Personal subscription management
- Email history

### v2.0 - Q4 2024
- Automatic email submission
- SMS/push notifications
- Historical analytics dashboard
- API rate limiting and caching

### v3.0 - 2025
- Mobile app (iOS/Android)
- Premium features (Stripe billing)
- Advanced analytics and reporting
- Multi-tenant support

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/TypeScript
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Metrolinx** for providing the Open API
- GO Transit passengers who inspired this project
- Open source community for the amazing tools and libraries

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/oliverbisbee/go-train-refund-system/issues)
- **Email**: oli.bisbee+gorefund@gmail.com
- **Linkedin** linkedin.com/in/oliver-bisbee

## ⚠️ Disclaimer

This is an unofficial third-party application and is not affiliated with, endorsed by, or associated with Metrolinx or GO Transit. Users are responsible for ensuring their refund claims comply with GO Transit's official policies.

---

**Built with ❤️ by a passionate GO Transit commuter**
