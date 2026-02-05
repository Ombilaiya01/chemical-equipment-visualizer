# Deployment Guide

This guide covers deploying the Chemical Equipment Visualizer to production.

## Option 1: Deploy Web Version to Vercel (Recommended)

### Backend Deployment (Railway/Render/Heroku)

#### Using Railway

1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI:
```bash
npm i -g @railway/cli
```

3. Login and deploy:
```bash
cd backend
railway login
railway init
railway up
```

4. Add environment variables in Railway dashboard:
```
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=your-app.railway.app
```

5. Run migrations:
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

#### Using Render

1. Create account at [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn config.wsgi:application`
   - Add environment variables (same as above)

### Frontend Deployment (Vercel)

1. Create account at [vercel.com](https://vercel.com)

2. Update API URL in `frontend-web/src/App.js`:
```javascript
const API_URL = 'https://your-backend.railway.app/api';
```

3. Deploy via Vercel CLI:
```bash
cd frontend-web
npm install -g vercel
vercel
```

Or via Vercel Dashboard:
- Connect GitHub repository
- Select `frontend-web` as root directory
- Deploy

## Option 2: Deploy to AWS

### Backend (EC2)

1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip nginx
```

4. Clone repository:
```bash
git clone <your-repo>
cd backend
pip3 install -r requirements.txt
pip3 install gunicorn
```

5. Run migrations:
```bash
python3 manage.py migrate
python3 manage.py collectstatic
```

6. Create systemd service (`/etc/systemd/system/django.service`):
```ini
[Unit]
Description=Django Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/backend
ExecStart=/usr/local/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

7. Configure Nginx (`/etc/nginx/sites-available/django`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/ubuntu/backend/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/backend/media/;
    }
}
```

8. Enable and start services:
```bash
sudo systemctl enable django
sudo systemctl start django
sudo ln -s /etc/nginx/sites-available/django /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

### Frontend (S3 + CloudFront)

1. Build React app:
```bash
cd frontend-web
npm run build
```

2. Create S3 bucket and enable static hosting

3. Upload build folder to S3:
```bash
aws s3 sync build/ s3://your-bucket-name
```

4. Create CloudFront distribution pointing to S3 bucket

## Option 3: Docker Deployment

### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Frontend Dockerfile

Create `frontend-web/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml` in root:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend/media:/app/media
      - ./backend/staticfiles:/app/staticfiles
  
  frontend:
    build: ./frontend-web
    ports:
      - "80:80"
    depends_on:
      - backend
```

Deploy:
```bash
docker-compose up -d
```

## Environment Variables

### Backend (.env file)
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Frontend (.env file)
```
REACT_APP_API_URL=https://api.your-domain.com
```

## Post-Deployment Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS (Let's Encrypt)
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Test all features in production
- [ ] Set up CI/CD pipeline

## Security Considerations

1. **Django Security**:
   - Use environment variables for secrets
   - Enable CSRF protection
   - Use HTTPS only
   - Set secure cookie flags
   - Configure CORS properly

2. **Database**:
   - Use PostgreSQL in production (not SQLite)
   - Regular backups
   - Secure connection strings

3. **API**:
   - Rate limiting
   - API authentication
   - Input validation
   - File upload limits

## Monitoring

### Log Aggregation
- Set up CloudWatch (AWS)
- Use Papertrail or Loggly
- Configure Django logging

### Performance Monitoring
- Use New Relic or DataDog
- Enable Django Debug Toolbar (dev only)
- Monitor database queries

### Error Tracking
- Sentry for error tracking
- Set up alerts for critical errors

## Scaling

### Backend Scaling
- Use load balancer
- Multiple Gunicorn workers
- Redis for caching
- CDN for static files

### Database Scaling
- Read replicas
- Connection pooling
- Query optimization

## Backup Strategy

1. **Database Backups**:
```bash
# PostgreSQL backup
pg_dump database_name > backup.sql

# Automated daily backups
0 2 * * * pg_dump database_name > /backups/$(date +\%Y\%m\%d).sql
```

2. **Media Files**:
- Regular S3 snapshots
- Cross-region replication

## Cost Optimization

- Use free tiers when possible:
  - Vercel: Free for personal projects
  - Railway: $5 credit monthly
  - Render: Free tier available
  
- Optimize images and static files
- Use CDN for static content
- Monitor and optimize database queries

## Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connectivity
4. Check firewall/security groups
5. Review CORS settings

---

**Remember**: Always test in staging before deploying to production!
