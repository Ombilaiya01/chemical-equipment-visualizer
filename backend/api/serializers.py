from rest_framework import serializers
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    type_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'filename', 'uploaded_at', 'total_count',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution', 'equipment'
        ]
    
    def get_type_distribution(self, obj):
        return obj.get_type_distribution()


class DatasetSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for history list"""
    type_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'filename', 'uploaded_at', 'total_count',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution'
        ]
    
    def get_type_distribution(self, obj):
        return obj.get_type_distribution()
