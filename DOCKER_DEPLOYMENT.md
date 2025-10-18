# Docker Deployment Guide

## Overview

The UK Flood Reporting App is **fully Dockerized** - both frontend and backend! This guide covers local development with hot reload and production deployment.

## 🚀 Quick Start with Docker Compose

### Prerequisites
- Docker Desktop installed ([download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)

### Run the Full Stack Application

```bash
# Start all services (database + backend + frontend)
docker-compose up -d

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f frontend
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v
```

**Access the application:**
- Frontend: `http://localhost:3000` (React with hot reload)
- Backend API: `http://localhost:5001/api`
- Database: `localhost:5432`

### First Time Setup

The `docker-compose.yml` automatically:
- ✅ Creates PostgreSQL database
- ✅ Runs database migrations
- ✅ Starts Flask backend with gunicorn
- ✅ Starts React frontend with hot reload
- ✅ Configures networking between services

**Just run `docker-compose up -d` and you're ready to develop!**

## 💻 Development with Docker

### Live Code Reloading (Hot Reload) ⚡

Both frontend and backend support hot reload:

**Backend:**
- Volume mounted: `./backend:/app`
- Gunicorn with `--reload` flag
- Changes to Python files auto-restart the server

**Frontend:**
- Volume mounted: `./frontend:/app` (excluding node_modules)
- React dev server with hot module replacement (HMR)
- Changes to JS/CSS/JSX files auto-refresh the browser
- Polling enabled for Docker compatibility: `CHOKIDAR_USEPOLLING=true`

**Just edit your code and see changes instantly!** No need to rebuild containers.

### Running Commands Inside Containers

```bash
# Backend commands
docker-compose exec backend flask shell
docker-compose exec backend flask db migrate -m "migration message"
docker-compose exec backend flask db upgrade
docker-compose exec backend bash

# Frontend commands
docker-compose exec frontend npm install <package-name>
docker-compose exec frontend npm run build
docker-compose exec frontend sh

# Database commands
docker-compose exec db psql -U floodapp -d flood_reporting
docker-compose exec db psql -U floodapp -d flood_reporting -c "SELECT * FROM flood_reports;"
```

### Rebuilding Containers

If you change Dockerfile or package.json:

```bash
# Rebuild specific service
docker-compose build frontend
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build

# Force rebuild without cache
docker-compose build --no-cache frontend
```

## 🚢 Production Deployment

### Production Docker Compose

Use `docker-compose.prod.yml` for production deployment:

```bash
# Copy environment example
cp .env.example .env

# Edit .env with production values
nano .env

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

**Key differences in production:**
- Frontend: Multi-stage build with Nginx (optimized static files)
- Backend: More workers (4 instead of 2)
- Database: Restart policies enabled
- Networks: Isolated bridge network
- No volume mounting (uses built code)

### Option 1: Full Stack to Cloud Platform

#### Build Production Images

```bash
# Backend
cd backend
docker build -t flood-reporter-backend:latest .

# Frontend
cd ../frontend
docker build --target production -t flood-reporter-frontend:latest .
```

#### Test Production Stack Locally

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up
```

Access at `http://localhost:80`

#### Deploy to Railway (Recommended)

**Backend:**
```bash
cd backend
railway login
railway init
railway add --database postgresql
railway up
```

**Frontend:**
```bash
cd frontend
railway init
railway up
```

Set environment variable on frontend: `REACT_APP_API_URL=https://your-backend-url.railway.app/api`

**Cost:** Free tier available

#### Deploy to Render

**Backend:**
1. Push code to GitHub
2. New Web Service → Connect repo → Select `backend` folder
3. Render auto-detects Dockerfile
4. Add PostgreSQL database
5. Set environment variables
6. Deploy!

**Frontend:**
1. New Static Site → Connect repo → Select `frontend` folder
2. Build command: `npm run build`
3. Publish directory: `build`
4. Add environment variable: `REACT_APP_API_URL`
5. Deploy!

**Cost:** Free tier available

#### Deploy to Vercel (Frontend) + Railway (Backend)

This is the **easiest and recommended approach**:

**Backend on Railway:**
```bash
cd backend
railway login
railway init
railway add --database postgresql
railway up
```

**Frontend on Vercel:**
```bash
cd frontend
npm install -g vercel
vercel login
vercel
```

Set environment variable: `REACT_APP_API_URL=https://your-backend-url.railway.app/api`

**Cost:** Both have generous free tiers!

### Option 2: Full Stack on VPS (DigitalOcean, AWS EC2, etc.)

#### Push to Docker Hub

```bash
# Build and tag backend
cd backend
docker build -t yourusername/flood-reporter-backend:latest .
docker push yourusername/flood-reporter-backend:latest

# Build and tag frontend
cd ../frontend
docker build --target production -t yourusername/flood-reporter-frontend:latest .
docker push yourusername/flood-reporter-frontend:latest

```

#### Deploy on VPS with Docker Compose

```bash
# SSH into your VPS
ssh user@your-server-ip

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose

# Clone your repo or copy files
git clone https://github.com/yourusername/flood-reporter.git
cd flood-reporter

# Copy and edit environment file
cp .env.example .env
nano .env  # Edit with production values

# Start full stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

Access at `http://your-server-ip`

For HTTPS, add nginx reverse proxy with Let's Encrypt SSL.

---

## Environment Variables

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |
| `SECRET_KEY` | Flask secret key (generate with `openssl rand -hex 32`) | `a1b2c3d4...` |
| `FLASK_ENV` | Environment mode | `production` |

### Frontend

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:5001/api` or `https://api.yourdomain.com/api` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `UPLOAD_FOLDER` | Path for uploaded files | `/app/uploads` |
| `MAX_UPLOAD_SIZE` | Max file size in bytes | `5242880` (5MB) |

---

## 🎯 Deployment Comparison

| Platform | Backend | Frontend | Database | Cost | Docker | Difficulty |
|----------|---------|----------|----------|------|--------|------------|
| **Vercel + Railway** | Railway | Vercel | Railway PostgreSQL | Free tier | ✅ | ⭐ Easy |
| **Render** | Render | Render Static | Render PostgreSQL | Free tier | ✅ | ⭐ Easy |
| **Railway (Full)** | Railway | Railway | Railway PostgreSQL | Free tier | ✅ | ⭐⭐ Medium |
| **VPS (DigitalOcean)** | Docker | Docker | Docker | $6/month | ✅ | ⭐⭐⭐ Advanced |
| **AWS/GCP** | ECS/Cloud Run | S3/Cloud Storage | RDS | Variable | ✅ | ⭐⭐⭐⭐ Expert |

**Recommendation:** Start with **Vercel (frontend) + Railway (backend)** for easiest deployment with free tier.

## Troubleshooting

### Container Won't Start

```bash
# Check logs for all services
docker-compose logs

# Check specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Frontend Hot Reload Not Working

If file changes aren't reflected:

```bash
# Ensure polling is enabled (already set in docker-compose.yml)
# Check environment variables:
docker-compose exec frontend env | grep CHOKIDAR

# Rebuild frontend if needed
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Database Connection Issues

```bash
# Test connection from backend container
docker-compose exec backend python -c "from app import db; db.create_all(); print('Connected!')"
```

### Port Already in Use

```bash
# Change ports in docker-compose.yml
# Frontend:
ports:
  - "3001:3000"  # Use 3001 instead of 3000

# Backend:
ports:
  - "5002:5001"  # Use 5002 instead of 5001
```

### Permission Issues with Uploads

```bash
# Fix permissions
docker-compose exec backend chmod 755 /app/uploads
```

### Frontend Build Fails

```bash
# Clear node_modules and rebuild
docker-compose down
docker volume rm claudecodetest_frontend_node_modules
docker-compose build --no-cache frontend
docker-compose up -d
```

### Reset Everything

```bash
# Nuclear option - removes all containers, volumes, images
docker-compose down -v --rmi all
docker-compose up --build -d
```

## Health Checks

The Dockerfile includes a health check that pings the `/api/stats` endpoint every 30 seconds.

Check health:
```bash
docker ps  # Look at STATUS column
docker inspect flood_backend | grep -A 10 Health
```

## Performance Tuning

### Gunicorn Workers

Edit `Dockerfile` CMD:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "run:app"]
```

Workers formula: `(2 x CPU cores) + 1`

### Database Connection Pool

Add to `backend/app/config.py`:
```python
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
```

## Security Best Practices

1. **Never commit secrets**: Use environment variables
2. **Use strong SECRET_KEY**: Generate with `openssl rand -hex 32`
3. **Change default database password** in production
4. **Enable HTTPS**: Use reverse proxy (nginx) or platform SSL
5. **Limit file upload size**: Already configured to 5MB
6. **Use non-root user** in Dockerfile (already configured)

## Monitoring

### Docker Stats
```bash
docker stats flood_backend flood_db
```

### Application Logs
```bash
docker-compose logs -f backend --tail=100
```

### Database Logs
```bash
docker-compose logs -f db --tail=100
```

## Backup & Restore

### Backup Database
```bash
docker-compose exec db pg_dump -U floodapp flood_reporting > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker-compose exec -T db psql -U floodapp flood_reporting
```

### Backup Uploads
```bash
docker cp flood_backend:/app/uploads ./uploads_backup
```

## Next Steps

1. Set up CI/CD pipeline (GitHub Actions)
2. Add monitoring (Sentry, DataDog)
3. Configure CDN for uploaded images
4. Set up automated backups
5. Add load balancing for multiple containers

---

**Need help?** Check the main README.md or open an issue on GitHub.
