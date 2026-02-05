# Quick Start Guide ⚡

Get the application running in under 5 minutes!

## Prerequisites
- Python 3.8+
- Node.js 14+
- pip and npm installed

## 🚀 Express Setup

### Terminal 1: Backend
```bash
cd backend
pip install Django djangorestframework django-cors-headers pandas reportlab --break-system-packages
python manage.py migrate
python manage.py runserver
```
✅ Backend running at http://localhost:8000

### Terminal 2: Web Frontend
```bash
cd frontend-web
npm install
npm start
```
✅ Web app at http://localhost:3000

### Terminal 3: Desktop Frontend
```bash
cd frontend-desktop
pip install PyQt5 requests matplotlib pandas --break-system-packages
python main.py
```
✅ Desktop app window opens

## 📁 Test with Sample Data

Use `backend/sample_equipment_data.csv` to test the application!

## 🎯 What to Do

1. **Upload CSV**: Click browse/upload in either app
2. **View Results**: See charts, stats, and tables
3. **Generate PDF**: Download professional report
4. **Check History**: View previous uploads
5. **Try Authentication**: Register and login (optional)

## ⚠️ Common Issues

**Port already in use?**
```bash
# Backend
python manage.py runserver 8080

# Web
PORT=3001 npm start
```

**Module not found?**
```bash
# Install dependencies again
pip install -r requirements.txt
npm install
```

**CORS errors?**
- Ensure backend is running first
- Check django-cors-headers is installed

## 📊 Project Structure

```
chemical-equipment-visualizer/
├── backend/          # Django API
├── frontend-web/     # React app
└── frontend-desktop/ # PyQt5 app
```

## 🔗 Important Links

- **Backend**: http://localhost:8000/api/
- **Web App**: http://localhost:3000
- **Admin Panel**: http://localhost:8000/admin

## 📚 Full Documentation

- Setup Guide: `SETUP_GUIDE.md`
- Main README: `README.md`
- Deployment: `DEPLOYMENT.md`
- Demo Script: `DEMO_SCRIPT.md`
- Submission Checklist: `SUBMISSION_CHECKLIST.md`

## 🎥 Recording Demo

Follow `DEMO_SCRIPT.md` for a complete 2-3 minute demo guide.

## 🐛 Troubleshooting

1. Check all three terminals are running
2. Verify Python and Node versions
3. Ensure all dependencies installed
4. Check ports 8000 and 3000 are free
5. Review error messages in terminals

## ✅ Ready to Submit?

1. ✅ All features working
2. ✅ Code on GitHub
3. ✅ Demo video recorded
4. ✅ Submit at: https://forms.gle/bSiKezbM4Ji9xnw66

---

**Need help?** Check the comprehensive `SETUP_GUIDE.md` or `README.md`

**Happy coding! 🎉**
