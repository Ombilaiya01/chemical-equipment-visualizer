import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QHBoxLayout, QMessageBox, 
                             QGroupBox, QGridLayout, QLineEdit, QDialog,
                             QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import io


API_URL = 'http://localhost:8000/api'


class UploadThread(QThread):
    """Thread for uploading files to avoid blocking UI"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
    
    def run(self):
        try:
            with open(self.filepath, 'rb') as f:
                files = {'file': f}
                response = requests.post(f'{API_URL}/datasets/upload/', files=files)
                if response.status_code == 201:
                    self.finished.emit(response.json())
                else:
                    self.error.emit(f"Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            self.error.emit(str(e))


class LoginDialog(QDialog):
    """Login/Register dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login / Register')
        self.setModal(True)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.login)
        register_btn = QPushButton('Register')
        register_btn.clicked.connect(self.register)
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        try:
            response = requests.post(f'{API_URL}/login/', 
                                   json={'username': username, 'password': password})
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Login successful!')
                self.accept()
            else:
                QMessageBox.warning(self, 'Error', 'Invalid credentials')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Login failed: {str(e)}')
    
    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        try:
            response = requests.post(f'{API_URL}/register/', 
                                   json={'username': username, 'password': password})
            if response.status_code == 201:
                QMessageBox.information(self, 'Success', 
                                      'Registration successful! Please login.')
            else:
                error_msg = response.json().get('error', 'Registration failed')
                QMessageBox.warning(self, 'Error', error_msg)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Registration failed: {str(e)}')


class ChartWidget(QWidget):
    """Widget for displaying matplotlib charts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_bar_chart(self, data, title):
        """Plot bar chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.bar(data.keys(), data.values(), color='skyblue')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Type')
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie_chart(self, data, title):
        """Plot pie chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
        ax.set_title(title, fontsize=14, fontweight='bold')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_parameters(self, flowrate, pressure, temperature):
        """Plot average parameters"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        parameters = ['Flowrate', 'Pressure', 'Temperature']
        values = [flowrate, pressure, temperature]
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        ax.bar(parameters, values, color=colors)
        ax.set_title('Average Parameters', fontsize=14, fontweight='bold')
        ax.set_ylabel('Value')
        self.figure.tight_layout()
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel('🧪 Chemical Equipment Parameter Visualizer')
        header.setFont(QFont('Arial', 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('background-color: #667eea; color: white; padding: 15px;')
        main_layout.addWidget(header)
        
        # Auth button
        auth_btn = QPushButton('Login / Register')
        auth_btn.clicked.connect(self.show_auth_dialog)
        auth_btn.setMaximumWidth(150)
        main_layout.addWidget(auth_btn, alignment=Qt.AlignRight)
        
        # Upload section
        upload_group = QGroupBox('Upload CSV File')
        upload_layout = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self.browse_file)
        upload_btn = QPushButton('Upload & Analyze')
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setStyleSheet('background-color: #48bb78; color: white; font-weight: bold; padding: 10px;')
        upload_layout.addWidget(self.file_label)
        upload_layout.addWidget(browse_btn)
        upload_layout.addWidget(upload_btn)
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Summary tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        self.summary_group = self.create_summary_section()
        summary_layout.addWidget(self.summary_group)
        self.tabs.addTab(summary_tab, 'Summary')
        
        # Charts tab
        charts_tab = QWidget()
        charts_layout = QVBoxLayout(charts_tab)
        
        chart_container = QWidget()
        chart_grid = QGridLayout(chart_container)
        self.type_chart = ChartWidget()
        self.param_chart = ChartWidget()
        chart_grid.addWidget(self.type_chart, 0, 0)
        chart_grid.addWidget(self.param_chart, 0, 1)
        
        scroll = QScrollArea()
        scroll.setWidget(chart_container)
        scroll.setWidgetResizable(True)
        charts_layout.addWidget(scroll)
        
        self.tabs.addTab(charts_tab, 'Charts')
        
        # Data table tab
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        self.data_table = QTableWidget()
        table_layout.addWidget(self.data_table)
        self.tabs.addTab(table_tab, 'Data Table')
        
        # History tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        self.history_table = QTableWidget()
        refresh_history_btn = QPushButton('Refresh History')
        refresh_history_btn.clicked.connect(self.load_history)
        history_layout.addWidget(refresh_history_btn)
        history_layout.addWidget(self.history_table)
        self.tabs.addTab(history_tab, 'History')
        
        main_layout.addWidget(self.tabs)
        
        # Load initial history
        self.load_history()
    
    def create_summary_section(self):
        """Create summary statistics section"""
        group = QGroupBox('Summary Statistics')
        layout = QGridLayout()
        
        self.total_label = QLabel('Total Equipment: -')
        self.flowrate_label = QLabel('Avg Flowrate: -')
        self.pressure_label = QLabel('Avg Pressure: -')
        self.temperature_label = QLabel('Avg Temperature: -')
        
        for label in [self.total_label, self.flowrate_label, 
                     self.pressure_label, self.temperature_label]:
            label.setFont(QFont('Arial', 12))
            label.setStyleSheet('padding: 10px; background-color: #f0f0f0; border-radius: 5px;')
        
        layout.addWidget(self.total_label, 0, 0)
        layout.addWidget(self.flowrate_label, 0, 1)
        layout.addWidget(self.pressure_label, 1, 0)
        layout.addWidget(self.temperature_label, 1, 1)
        
        # PDF button
        pdf_btn = QPushButton('📄 Download PDF Report')
        pdf_btn.clicked.connect(self.download_pdf)
        pdf_btn.setStyleSheet('background-color: #ed8936; color: white; font-weight: bold; padding: 15px; margin-top: 20px;')
        layout.addWidget(pdf_btn, 2, 0, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def show_auth_dialog(self):
        """Show login/register dialog"""
        dialog = LoginDialog(self)
        dialog.exec_()
    
    def browse_file(self):
        """Open file browser"""
        filename, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if filename:
            self.file_label.setText(filename)
    
    def upload_file(self):
        """Upload selected file"""
        filepath = self.file_label.text()
        if filepath == 'No file selected':
            QMessageBox.warning(self, 'Error', 'Please select a file first')
            return
        
        self.upload_thread = UploadThread(filepath)
        self.upload_thread.finished.connect(self.on_upload_success)
        self.upload_thread.error.connect(self.on_upload_error)
        self.upload_thread.start()
        
        self.file_label.setText('Uploading...')
    
    def on_upload_success(self, data):
        """Handle successful upload"""
        self.current_data = data
        self.file_label.setText('Upload successful!')
        self.update_display()
        self.load_history()
        QMessageBox.information(self, 'Success', 'File uploaded and analyzed successfully!')
    
    def on_upload_error(self, error_msg):
        """Handle upload error"""
        self.file_label.setText('Upload failed')
        QMessageBox.critical(self, 'Error', f'Upload failed: {error_msg}')
    
    def update_display(self):
        """Update all displays with current data"""
        if not self.current_data:
            return
        
        # Update summary
        self.total_label.setText(f"Total Equipment: {self.current_data['total_count']}")
        self.flowrate_label.setText(f"Avg Flowrate: {self.current_data['avg_flowrate']:.2f}")
        self.pressure_label.setText(f"Avg Pressure: {self.current_data['avg_pressure']:.2f}")
        self.temperature_label.setText(f"Avg Temperature: {self.current_data['avg_temperature']:.2f}")
        
        # Update charts
        type_dist = self.current_data['type_distribution']
        self.type_chart.plot_pie_chart(type_dist, 'Equipment Type Distribution')
        self.param_chart.plot_parameters(
            self.current_data['avg_flowrate'],
            self.current_data['avg_pressure'],
            self.current_data['avg_temperature']
        )
        
        # Update data table
        equipment = self.current_data['equipment']
        self.data_table.setRowCount(len(equipment))
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'
        ])
        
        for i, eq in enumerate(equipment):
            self.data_table.setItem(i, 0, QTableWidgetItem(eq['equipment_name']))
            self.data_table.setItem(i, 1, QTableWidgetItem(eq['equipment_type']))
            self.data_table.setItem(i, 2, QTableWidgetItem(f"{eq['flowrate']:.2f}"))
            self.data_table.setItem(i, 3, QTableWidgetItem(f"{eq['pressure']:.2f}"))
            self.data_table.setItem(i, 4, QTableWidgetItem(f"{eq['temperature']:.2f}"))
        
        self.data_table.resizeColumnsToContents()
    
    def load_history(self):
        """Load upload history"""
        try:
            response = requests.get(f'{API_URL}/datasets/history/')
            if response.status_code == 200:
                history = response.json()
                self.history_table.setRowCount(len(history))
                self.history_table.setColumnCount(6)
                self.history_table.setHorizontalHeaderLabels([
                    'ID', 'Filename', 'Date', 'Count', 'Avg Flowrate', 'Actions'
                ])
                
                for i, dataset in enumerate(history):
                    self.history_table.setItem(i, 0, QTableWidgetItem(str(dataset['id'])))
                    self.history_table.setItem(i, 1, QTableWidgetItem(dataset['filename']))
                    self.history_table.setItem(i, 2, QTableWidgetItem(dataset['uploaded_at'][:19]))
                    self.history_table.setItem(i, 3, QTableWidgetItem(str(dataset['total_count'])))
                    self.history_table.setItem(i, 4, QTableWidgetItem(f"{dataset['avg_flowrate']:.2f}"))
                    
                    load_btn = QPushButton('Load')
                    load_btn.clicked.connect(lambda checked, ds_id=dataset['id']: self.load_dataset(ds_id))
                    self.history_table.setCellWidget(i, 5, load_btn)
                
                self.history_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load history: {str(e)}')
    
    def load_dataset(self, dataset_id):
        """Load a specific dataset"""
        try:
            response = requests.get(f'{API_URL}/datasets/{dataset_id}/')
            if response.status_code == 200:
                self.current_data = response.json()
                self.update_display()
                self.tabs.setCurrentIndex(0)
                QMessageBox.information(self, 'Success', 'Dataset loaded successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load dataset: {str(e)}')
    
    def download_pdf(self):
        """Download PDF report"""
        if not self.current_data:
            QMessageBox.warning(self, 'Error', 'No data to generate report')
            return
        
        try:
            dataset_id = self.current_data['id']
            response = requests.get(f'{API_URL}/datasets/{dataset_id}/generate_pdf/', stream=True)
            
            if response.status_code == 200:
                filename, _ = QFileDialog.getSaveFileName(
                    self, 'Save PDF', f'equipment_report_{dataset_id}.pdf', 'PDF Files (*.pdf)'
                )
                if filename:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', f'PDF saved to {filename}')
            else:
                QMessageBox.critical(self, 'Error', 'Failed to generate PDF')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to download PDF: {str(e)}')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
