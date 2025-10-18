# Docker Quick Start Guide

## ✅ Your App is Running!

All three containers are now running:
- **Frontend**: http://localhost:3000 (React with hot reload)
- **Backend**: http://localhost:5001/api (Flask API)
- **Database**: PostgreSQL on port 5432

## How to Use

### View Your App
Open your browser and go to:
```
http://localhost:3000
```

### Stop the App
```bash
docker-compose down
```

### Start the App Again
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

### Check Status
```bash
docker-compose ps
```

## Hot Reload is Working! 🔥

You can edit files and see changes instantly:

**Backend (Python):**
- Edit any `.py` file in `backend/`
- Gunicorn will auto-restart
- Changes appear in ~2 seconds

**Frontend (React):**
- Edit any file in `frontend/src/`
- Browser auto-refreshes with hot module replacement
- Changes appear instantly

**No need to rebuild containers!**

## Troubleshooting

### Frontend can't reach backend?

The frontend environment variable is set correctly. Open the browser console (F12) and check for any errors.

### Backend not starting?

Check logs:
```bash
docker-compose logs backend
```

### Port already in use?

If you have the app running outside Docker, stop it first:
- Stop your local Flask server (Ctrl+C)
- Stop your local React server (Ctrl+C)
- Stop your local PostgreSQL if it's using port 5432

### Reset everything?

```bash
# Stop and remove all containers, volumes
docker-compose down -v

# Start fresh
docker-compose up -d --build
```

## Next Steps

1. **Develop locally**: Edit code and see changes with hot reload
2. **Test the app**: Create flood reports, view them on the map
3. **Deploy**: When ready, use Railway or Vercel (see DOCKER_DEPLOYMENT.md)

## Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after changing Dockerfile or package.json
docker-compose up -d --build

# Access backend shell
docker-compose exec backend bash

# Access PostgreSQL
docker-compose exec db psql -U floodapp -d flood_reporting

# Add Python package
docker-compose exec backend pip install <package-name>
# Then add to requirements.txt and rebuild

# Add npm package
docker-compose exec frontend npm install <package-name>
# Frontend will auto-rebuild
```

---

**Everything is working!** 🎉

Go to http://localhost:3000 and start using your flood reporting app!
