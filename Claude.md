# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask/React web application for reporting and visualizing flood incidents in the UK. Users can submit flood reports with location, severity, and photos, which are displayed on an interactive map using Leaflet.

## Architecture

### Backend (Flask + PostgreSQL)
- **Entry point**: `backend/run.py`
- **Application factory**: `backend/app/__init__.py`
- **Models**: `backend/app/models.py` - SQLAlchemy models with PostGIS support
- **API Routes**: `backend/app/routes.py` - RESTful endpoints for flood reports
- **Database**: PostgreSQL with PostGIS extension for geospatial queries

### Frontend (React)
- **Entry point**: `frontend/src/index.js`
- **Main app**: `frontend/src/App.jsx` - React Router configuration
- **Components**: `frontend/src/components/` - Page-level components (Home, ReportForm, MapView, etc.)
- **API client**: `frontend/src/services/api.js` - Axios wrapper for backend API calls
- **Map library**: Leaflet for interactive mapping

### Key Data Flow
1. User submits flood report via `ReportForm.jsx`
2. Form data sent to `POST /api/floods` endpoint
3. Flask validates and stores in PostgreSQL via SQLAlchemy ORM
4. `MapView.jsx` fetches reports from `GET /api/floods`
5. Leaflet renders markers color-coded by severity (Low/Medium/High/Critical)

## Development Commands

### Backend
```bash
cd backend
source venv/bin/activate  # Or venv\Scripts\activate on Windows
python run.py              # Start development server
flask db migrate           # Create new migration
flask db upgrade           # Apply migrations
pytest                     # Run tests
```

### Frontend
```bash
cd frontend
npm start                  # Start development server
npm test                   # Run Jest tests
npm run build              # Production build
```

### Database Setup
```bash
createdb flood_reporting   # Create PostgreSQL database
psql flood_reporting -c "CREATE EXTENSION postgis;"  # Enable PostGIS
flask db init              # Initialize migrations
flask db migrate           # Generate initial migration
flask db upgrade           # Apply migrations
```

## Database Schema

### flood_reports Table
- Location stored as `latitude`/`longitude` floats (consider using PostGIS Point geometry for spatial queries)
- `severity` enum: Low, Medium, High, Critical
- `status` field: Active, Resolved, Deleted
- `photo_url` stores path to uploaded image in `backend/uploads/`
- Timestamps: `created_at`, `updated_at`

## API Endpoints

### Public
- `GET /api/floods` - List all reports (supports query params for filtering by date/severity)
- `GET /api/floods/:id` - Single report details
- `POST /api/floods` - Create new report (expects JSON with lat/lng/severity/description)
- `POST /api/upload` - Photo upload (multipart/form-data)

### Admin (Optional)
- `POST /api/admin/login` - Authentication
- `DELETE /api/floods/:id` - Remove report
- `PUT /api/floods/:id` - Update report
- `GET /api/admin/stats` - Analytics

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/flood_reporting
SECRET_KEY=<random-secret-key>
FLASK_ENV=development
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=5242880
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_MAP_CENTER_LAT=54.5
REACT_APP_MAP_CENTER_LNG=-2.5
```

## Important Implementation Notes

### Security
- All uploads must be validated (file type, size) in `backend/app/utils.py`
- Use SQLAlchemy ORM to prevent SQL injection (never use raw queries)
- Rate limiting should be implemented on report submission endpoint
- Admin routes require authentication middleware

### Map Rendering
- Severity color coding: Green (Low), Yellow (Medium), Orange (High), Red (Critical)
- Markers should cluster when zoomed out to improve performance with many reports
- Default map center: UK (lat: 54.5, lng: -2.5)

### File Uploads
- Photos stored in `backend/uploads/` directory
- Filenames should be sanitized and made unique (e.g., UUID prefix)
- Consider max file size limit (default 5MB as per env vars)

### Database Migrations
- Always use `flask db migrate` to generate migrations after model changes
- Review generated migration files before applying with `flask db upgrade`
- PostGIS extension must be enabled before first migration

## Current Development Status

According to Claude.md specification:
- Phase 1 (Core Features): Marked as complete
- Phase 2 (Enhanced Features): Photo upload, filtering, geocoding pending
- Phase 3 (Optional Features): Admin functionality, analytics not started
