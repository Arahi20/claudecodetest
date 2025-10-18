# UK Flood Reporting App

A full-stack web application for reporting and visualizing flood incidents in the UK.

## Features

- Submit flood reports with location, severity, and optional photos
- Interactive map view with color-coded markers
- Filter reports by severity, date range, and status
- Real-time statistics dashboard
- Mobile-responsive design

## Tech Stack

### Backend
- Python 3.9+
- Flask - Web framework
- PostgreSQL - Database
- SQLAlchemy - ORM
- Flask-Migrate - Database migrations
- Flask-CORS - Cross-origin support

### Frontend
- React 18
- React Router - Navigation
- Leaflet - Interactive maps
- Axios - API client

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ (with PostGIS)

## Installation

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database is already created and migrated
# If you need to recreate:
# createdb flood_reporting
# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade
```

### 2. Frontend Setup

```bash
cd frontend

# Dependencies are already installed
# If you need to reinstall:
# npm install
```

## Running the Application

### Start the Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
python run.py
```

The API will be available at `http://localhost:5000`

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm start
```

The application will open at `http://localhost:3000`

## API Endpoints

### Public Endpoints

- `GET /api/floods` - Get all flood reports (with optional filters)
  - Query params: `severity`, `start_date`, `end_date`, `status`
- `GET /api/floods/:id` - Get single flood report
- `POST /api/floods` - Create new flood report
- `POST /api/upload` - Upload photo
- `GET /api/stats` - Get statistics

### Admin Endpoints (Future)

- `PUT /api/floods/:id` - Update report
- `DELETE /api/floods/:id` - Delete report

## Database Schema

### flood_reports

| Column      | Type      | Description                  |
|-------------|-----------|------------------------------|
| id          | Integer   | Primary key                  |
| latitude    | Float     | Location latitude            |
| longitude   | Float     | Location longitude           |
| address     | String    | Human-readable address       |
| severity    | String    | Low, Medium, High, Critical  |
| description | Text      | User description             |
| photo_url   | String    | Path to uploaded photo       |
| status      | String    | Active, Resolved, Deleted    |
| created_at  | DateTime  | Auto-generated timestamp     |
| updated_at  | DateTime  | Auto-updated timestamp       |

## Environment Variables

### Backend (.env)

```
DATABASE_URL=postgresql://username@localhost/flood_reporting
SECRET_KEY=your-secret-key
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

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py       # Application factory
│   │   ├── config.py         # Configuration
│   │   ├── models.py         # Database models
│   │   ├── routes.py         # API endpoints
│   │   └── utils.py          # Helper functions
│   ├── migrations/           # Database migrations
│   ├── uploads/              # Uploaded photos
│   ├── .env                  # Environment variables
│   ├── requirements.txt      # Python dependencies
│   └── run.py                # Entry point
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Home.jsx
│   │   │   ├── ReportForm.jsx
│   │   │   └── MapView.jsx
│   │   ├── services/
│   │   │   └── api.js        # API client
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── .env
│   └── package.json
│
├── CLAUDE.md                 # Claude Code guidance
└── README.md                 # This file
```

## Usage

### Reporting a Flood

1. Click "Report Flood" in the navigation
2. Click on the map to select the flood location
3. Select severity level (Low, Medium, High, Critical)
4. Add a description
5. Optionally upload a photo
6. Submit the report

### Viewing Reports

1. Click "View Map" in the navigation
2. Use the filter sidebar to filter by:
   - Severity level
   - Status (Active/Resolved)
   - Date range
3. Click markers on the map to view report details

## Features Implemented

✅ Full CRUD API for flood reports
✅ Photo upload with validation
✅ Interactive map with Leaflet
✅ Filtering by severity, date, and status
✅ Statistics dashboard
✅ Mobile-responsive design
✅ Loading states and error handling
✅ Form validation

## Future Enhancements

- Admin authentication and dashboard
- Address geocoding (convert addresses to coordinates)
- Push notifications for nearby floods
- Integration with official flood warning APIs
- Real-time updates with WebSockets
- User accounts and report tracking

## Troubleshooting

### PostgreSQL Connection Error

Make sure PostgreSQL is running:
```bash
brew services start postgresql@14
```

### Port Already in Use

Backend (5000):
```bash
lsof -ti:5000 | xargs kill -9
```

Frontend (3000):
```bash
lsof -ti:3000 | xargs kill -9
```

### Module Not Found Errors

Backend:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

## License

MIT

## Contributors

Built with Claude Code
