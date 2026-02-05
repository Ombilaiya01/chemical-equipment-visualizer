from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import FileResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Dataset, Equipment
from .serializers import DatasetSerializer, DatasetSummarySerializer, EquipmentSerializer
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [AllowAny]  # Change to IsAuthenticated for production
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Handle CSV file upload and data processing"""
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # Validate file extension
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read CSV file
            df = pd.read_csv(file)
            
            # Validate required columns
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_columns):
                return Response(
                    {'error': f'CSV must contain columns: {", ".join(required_columns)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate summary statistics
            total_count = len(df)
            avg_flowrate = df['Flowrate'].mean()
            avg_pressure = df['Pressure'].mean()
            avg_temperature = df['Temperature'].mean()
            type_distribution = df['Type'].value_counts().to_dict()
            
            # Create dataset record
            dataset = Dataset.objects.create(
                user=request.user if request.user.is_authenticated else None,
                filename=file.name,
                total_count=total_count,
                avg_flowrate=avg_flowrate,
                avg_pressure=avg_pressure,
                avg_temperature=avg_temperature,
            )
            dataset.set_type_distribution(type_distribution)
            dataset.save()
            
            # Create equipment records
            for _, row in df.iterrows():
                Equipment.objects.create(
                    dataset=dataset,
                    equipment_name=row['Equipment Name'],
                    equipment_type=row['Type'],
                    flowrate=row['Flowrate'],
                    pressure=row['Pressure'],
                    temperature=row['Temperature']
                )
            
            # Keep only last 5 datasets
            datasets = Dataset.objects.all()
            if datasets.count() > 5:
                datasets_to_delete = datasets[5:]
                for ds in datasets_to_delete:
                    ds.delete()
            
            serializer = self.get_serializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get last 5 uploaded datasets"""
        datasets = Dataset.objects.all()[:5]
        serializer = DatasetSummarySerializer(datasets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF report for a dataset"""
        dataset = self.get_object()
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=1  # Center
        )
        elements.append(Paragraph("Chemical Equipment Analysis Report", title_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Dataset info
        info_data = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Dataset:', dataset.filename],
            ['Upload Date:', dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')],
        ]
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c5282')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.4 * inch))
        
        # Summary Statistics
        elements.append(Paragraph("Summary Statistics", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Equipment Count', str(dataset.total_count)],
            ['Average Flowrate', f'{dataset.avg_flowrate:.2f}'],
            ['Average Pressure', f'{dataset.avg_pressure:.2f}'],
            ['Average Temperature', f'{dataset.avg_temperature:.2f}'],
        ]
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4 * inch))
        
        # Equipment Type Distribution
        elements.append(Paragraph("Equipment Type Distribution", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        type_dist = dataset.get_type_distribution()
        type_data = [['Equipment Type', 'Count']]
        for eq_type, count in type_dist.items():
            type_data.append([eq_type, str(count)])
        
        type_table = Table(type_data, colWidths=[3 * inch, 2 * inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(type_table)
        elements.append(Spacer(1, 0.4 * inch))
        
        # Equipment Details
        elements.append(Paragraph("Equipment Details", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        equipment = dataset.equipment.all()[:20]  # Limit to first 20 for PDF
        equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
        for eq in equipment:
            equipment_data.append([
                eq.equipment_name[:20],  # Truncate long names
                eq.equipment_type,
                f'{eq.flowrate:.1f}',
                f'{eq.pressure:.1f}',
                f'{eq.temperature:.1f}'
            ])
        
        equipment_table = Table(equipment_data, colWidths=[1.8*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(equipment_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f'equipment_report_{dataset.id}.pdf',
            content_type='application/pdf'
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({'message': 'User created successfully', 'username': username}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        return Response({'message': 'Login successful', 'username': username}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
