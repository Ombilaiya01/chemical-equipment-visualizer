# Quick Setup Guide

## Step-by-Step Installation

### Prerequisites Check
Before starting, ensure you have:
- [ ] Python 3.8 or higher installed
- [ ] Node.js 14 or higher installed
- [ ] pip installed
- [ ] npm installed

### 1. Clone/Download the Project
```bash
# If from GitHub
git clone <repository-url>
cd chemical-equipment-visualizer

# Or extract the ZIP file and navigate to the folder
```

### 2. Backend Setup (Django)

```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create database tables
python manage.py makemigrations
python manage.py migrate

# (Optional) Create admin user
python manage.py createsuperuser
# Follow prompts to create username and password

# Start the backend server
python manage.py runserver
```

**✅ Backend is now running at http://localhost:8000**

Keep this terminal open!

### 3. Web Frontend Setup (React)

Open a NEW terminal window:

```bash
# Navigate to web frontend folder
cd frontend-web

# Install Node.js dependencies (this may take a few minutes)
npm install

# Start the React development server
npm start
```

**✅ Web app will automatically open at http://localhost:3000**

Keep this terminal open!

### 4. Desktop Frontend Setup (PyQt5)

Open a NEW terminal window:

```bash
# Navigate to desktop frontend folder
cd frontend-desktop

# Install Python dependencies
pip install -r requirements.txt

# Run the desktop application
python main.py
```

**✅ Desktop app window will appear**

## Testing the Application

### Test with Sample Data

1. Use the provided `sample_equipment_data.csv` file in the `backend/` folder
2. Upload it through either the web or desktop interface
3. View the analysis results, charts, and statistics

### Create Your Own CSV

Create a CSV file with these exact column names:
```
Equipment Name,Type,Flowrate,Pressure,Temperature
```

Example:
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-1,Reactor,150.5,25.3,180.2
Pump-1,Pump,200.0,40.5,85.0
Tank-1,Tank,100.0,10.5,25.0
```

## Common Issues & Solutions

### Issue: "Module not found" errors
**Solution**: Make sure you installed all dependencies:
- Backend: `pip install -r requirements.txt`
- Web: `npm install`
- Desktop: `pip install -r requirements.txt`

### Issue: Port already in use
**Solution**: 
- Backend: Use different port: `python manage.py runserver 8080`
- Web: Set PORT environment variable: `PORT=3001 npm start`

### Issue: CORS errors in web app
**Solution**: 
- Ensure backend is running at http://localhost:8000
- Check that `django-cors-headers` is installed
- Verify CORS settings in `backend/config/settings.py`

### Issue: "Connection refused" in desktop app
**Solution**:
- Ensure backend server is running first
- Check that API_URL in `main.py` matches your backend URL

### Issue: CSV upload fails
**Solution**:
- Verify CSV has exact column names: Equipment Name, Type, Flowrate, Pressure, Temperature
- Check that all values are numeric (except Equipment Name and Type)
- Ensure file is saved as CSV format

## Stopping the Applications

To stop any server:
1. Go to its terminal window
2. Press `Ctrl + C`

## Features to Try

1. **Upload Data**: Try uploading the sample CSV
2. **View Charts**: Check both pie and bar charts
3. **Download PDF**: Generate a professional report
4. **History**: View previous uploads (last 5 are kept)
5. **Authentication**: Register and login (optional)
6. **Switch Between Apps**: Upload data in web, view in desktop or vice versa

## Demo Video Script

Record a 2-3 minute video showing:

1. **Introduction (15s)**
   - "This is the Chemical Equipment Visualizer"
   - Show both web and desktop apps running

2. **Web App Demo (1 min)**
   - Upload CSV file
   - Show summary statistics
   - Display charts (pie and bar)
   - Scroll through data table
   - Download PDF report

3. **Desktop App Demo (45s)**
   - Open desktop application
   - Upload same/different CSV
   - Navigate through tabs (Summary, Charts, Data, History)
   - Show login feature

4. **History Feature (30s)**
   - Show upload history
   - Load previous dataset
   - Demonstrate that data persists

## Next Steps

- Customize the styling in `App.css` (web) or themes in `main.py` (desktop)
- Add more chart types
- Implement data export features
- Add data filtering capabilities
- Deploy web version to Vercel/Netlify

## Getting Help

If you encounter issues:
1. Check this guide first
2. Review the main README.md
3. Check terminal/console for error messages
4. Verify all prerequisites are installed
5. Ensure all three servers are running simultaneously

---

**You're all set! 🎉**

Start by uploading the sample CSV file and exploring the features!
