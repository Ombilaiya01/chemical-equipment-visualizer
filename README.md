# Chemical Equipment Parameter Visualizer

A hybrid web + desktop application for visualizing and analyzing chemical equipment parameters. Built with Django REST Framework backend, React web frontend, and PyQt5 desktop frontend.

## 🎯 Features

- ✅ CSV file upload for equipment data
- ✅ Real-time data analysis and statistics
- ✅ Interactive charts and visualizations
- ✅ Equipment data table view
- ✅ Upload history management (last 5 datasets)
- ✅ PDF report generation
- ✅ User authentication (login/register)
- ✅ Web and Desktop interfaces

## 🛠️ Tech Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API
- **Pandas** - Data processing
- **ReportLab** - PDF generation
- **SQLite** - Database

### Frontend Web
- **React 18** - UI framework
- **Chart.js** - Data visualization
- **Axios** - HTTP client

### Frontend Desktop
- **PyQt5** - Desktop GUI
- **Matplotlib** - Charts
- **Requests** - HTTP client

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### 2. Web Frontend Setup

```bash
cd frontend-web

# Install dependencies
npm install

# Start development server
npm start
```

The web app will open at `http://localhost:3000`

### 3. Desktop Frontend Setup

```bash
cd frontend-desktop

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 📊 Sample Data

A sample CSV file (`sample_equipment_data.csv`) is provided in the backend directory for testing.

### CSV Format Required

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-A1,Reactor,150.5,25.3,180.2
Pump-B2,Pump,200.0,40.5,85.0
...
```

## 🎮 Usage

### Web Application

1. Open `http://localhost:3000` in your browser
2. (Optional) Click "Login / Register" to create an account
3. Click "Choose File" and select a CSV file
4. Click "Upload & Analyze" to process the data
5. View summary statistics, charts, and data table
6. Download PDF report using the button
7. Access upload history in the bottom section

### Desktop Application

1. Launch the application using `python main.py`
2. (Optional) Click "Login / Register" for authentication
3. Click "Browse" to select a CSV file
4. Click "Upload & Analyze"
5. Navigate through tabs:
   - **Summary**: View statistics and download PDF
   - **Charts**: Interactive visualizations
   - **Data Table**: Detailed equipment data
   - **History**: Previously uploaded datasets

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/upload/` | Upload CSV file |
| GET | `/api/datasets/history/` | Get last 5 datasets |
| GET | `/api/datasets/{id}/` | Get specific dataset |
| GET | `/api/datasets/{id}/generate_pdf/` | Download PDF report |
| POST | `/api/register/` | Register new user |
| POST | `/api/login/` | User login |

## 📁 Project Structure

```
chemical-equipment-visualizer/
├── backend/
│   ├── config/              # Django settings
│   ├── api/                 # API app
│   │   ├── models.py        # Database models
│   │   ├── views.py         # API views
│   │   ├── serializers.py   # DRF serializers
│   │   └── urls.py          # API routes
│   ├── manage.py
│   ├── requirements.txt
│   └── sample_equipment_data.csv
├── frontend-web/
│   ├── public/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── App.css          # Styles
│   │   └── index.js
│   └── package.json
├── frontend-desktop/
│   ├── main.py              # PyQt5 application
│   └── requirements.txt
└── README.md
```

## 🎨 Features Detail

### Data Analysis
- Total equipment count
- Average flowrate, pressure, temperature
- Equipment type distribution

### Visualizations
- **Web**: Chart.js pie and bar charts
- **Desktop**: Matplotlib charts (pie, bar)

### PDF Report
- Summary statistics
- Equipment type distribution table
- Detailed equipment data
- Professional formatting with ReportLab

### Authentication
- User registration
- Login system
- Optional authentication (can be disabled for demo)

## 🔧 Configuration

### Backend Settings
Edit `backend/config/settings.py`:
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Add your domain
- `DATABASES`: Configure production database
- `SECRET_KEY`: Change in production

### Frontend Configuration
- Web: Update `API_URL` in `App.js` for production
- Desktop: Update `API_URL` in `main.py` for production

## 🚀 Deployment

### Backend (Django)
```bash
# Collect static files
python manage.py collectstatic

# Use gunicorn for production
pip install gunicorn
gunicorn config.wsgi:application
```

### Web Frontend (React)
```bash
# Build for production
npm run build

# Serve build folder with any static server
# Or deploy to Vercel, Netlify, etc.
```

## 🐛 Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure `django-cors-headers` is properly configured in `settings.py`.

### Port Conflicts
- Backend: Change port with `python manage.py runserver 8080`
- Frontend: Change port with `PORT=3001 npm start`

### Connection Refused
- Ensure backend is running before starting frontends
- Check firewall settings
- Verify `API_URL` in frontend code

## 📝 Testing

### Backend
```bash
python manage.py test
```

### Web Frontend
```bash
npm test
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is created for educational purposes.

## 👥 Authors

Your Name - Intern Screening Task

## 🙏 Acknowledgments

- Django REST Framework documentation
- React documentation
- PyQt5 documentation
- Chart.js and Matplotlib communities

## 📞 Support

For issues and questions, please create an issue in the GitHub repository.

---

Made with ❤️ for Chemical Equipment Analysis
