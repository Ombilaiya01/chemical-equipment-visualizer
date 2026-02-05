import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import './App.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const API_URL = 'http://localhost:8000/api';

function App() {
  const [file, setFile] = useState(null);
  const [currentData, setCurrentData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showAuth, setShowAuth] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/datasets/history/`);
      setHistory(response.data);
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/datasets/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCurrentData(response.data);
      fetchHistory();
      setFile(null);
      document.getElementById('file-input').value = '';
    } catch (err) {
      setError(err.response?.data?.error || 'Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/login/`, { username, password });
      setIsLoggedIn(true);
      setShowAuth(false);
      setError(null);
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/register/`, { username, password });
      setError('Registration successful! Please login.');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    }
  };

  const loadDataset = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/datasets/${id}/`);
      setCurrentData(response.data);
    } catch (err) {
      setError('Error loading dataset');
    }
  };

  const downloadPDF = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/datasets/${id}/generate_pdf/`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Error generating PDF');
    }
  };

  const getChartData = () => {
    if (!currentData) return null;

    const typeDistribution = currentData.type_distribution;
    const types = Object.keys(typeDistribution);
    const counts = Object.values(typeDistribution);

    return {
      labels: types,
      datasets: [{
        label: 'Equipment Count by Type',
        data: counts,
        backgroundColor: [
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 99, 132, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
        ],
      }]
    };
  };

  const getParameterChartData = () => {
    if (!currentData) return null;

    return {
      labels: ['Flowrate', 'Pressure', 'Temperature'],
      datasets: [{
        label: 'Average Parameters',
        data: [
          currentData.avg_flowrate,
          currentData.avg_pressure,
          currentData.avg_temperature
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 99, 132, 0.8)',
          'rgba(75, 192, 192, 0.8)',
        ],
      }]
    };
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧪 Chemical Equipment Parameter Visualizer</h1>
        <button 
          className="auth-btn"
          onClick={() => setShowAuth(!showAuth)}
        >
          {isLoggedIn ? '✓ Logged In' : 'Login / Register'}
        </button>
      </header>

      {showAuth && !isLoggedIn && (
        <div className="auth-section">
          <form onSubmit={handleLogin} className="auth-form">
            <h2>Login / Register</h2>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <div className="auth-buttons">
              <button type="submit">Login</button>
              <button type="button" onClick={handleRegister}>Register</button>
            </div>
          </form>
        </div>
      )}

      <div className="container">
        <div className="upload-section">
          <h2>Upload CSV File</h2>
          <div className="file-input-wrapper">
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
            />
            <button 
              onClick={handleUpload}
              disabled={loading || !file}
              className="upload-btn"
            >
              {loading ? 'Uploading...' : 'Upload & Analyze'}
            </button>
          </div>
          {error && <div className="error">{error}</div>}
        </div>

        {currentData && (
          <div className="results-section">
            <div className="summary-card">
              <h2>📊 Summary Statistics</h2>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Total Equipment:</span>
                  <span className="stat-value">{currentData.total_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Flowrate:</span>
                  <span className="stat-value">{currentData.avg_flowrate.toFixed(2)}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Pressure:</span>
                  <span className="stat-value">{currentData.avg_pressure.toFixed(2)}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Temperature:</span>
                  <span className="stat-value">{currentData.avg_temperature.toFixed(2)}</span>
                </div>
              </div>
              <button 
                className="pdf-btn"
                onClick={() => downloadPDF(currentData.id)}
              >
                📄 Download PDF Report
              </button>
            </div>

            <div className="charts-container">
              <div className="chart-card">
                <h3>Equipment Type Distribution</h3>
                <Pie data={getChartData()} />
              </div>
              <div className="chart-card">
                <h3>Average Parameters</h3>
                <Bar 
                  data={getParameterChartData()}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: { display: false }
                    }
                  }}
                />
              </div>
            </div>

            <div className="table-card">
              <h3>Equipment Details</h3>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Equipment Name</th>
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temperature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentData.equipment.map((eq) => (
                      <tr key={eq.id}>
                        <td>{eq.equipment_name}</td>
                        <td>{eq.equipment_type}</td>
                        <td>{eq.flowrate.toFixed(2)}</td>
                        <td>{eq.pressure.toFixed(2)}</td>
                        <td>{eq.temperature.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {history.length > 0 && (
          <div className="history-section">
            <h2>📜 Upload History (Last 5)</h2>
            <div className="history-grid">
              {history.map((dataset) => (
                <div key={dataset.id} className="history-card">
                  <h4>{dataset.filename}</h4>
                  <p className="history-date">
                    {new Date(dataset.uploaded_at).toLocaleString()}
                  </p>
                  <div className="history-stats">
                    <span>Count: {dataset.total_count}</span>
                    <span>Avg Flow: {dataset.avg_flowrate.toFixed(1)}</span>
                  </div>
                  <button 
                    onClick={() => loadDataset(dataset.id)}
                    className="load-btn"
                  >
                    Load Data
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
