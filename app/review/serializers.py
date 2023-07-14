"""
Serializers for review model.
"""
from rest_framework import serializers

from core.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for model"""
    name = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['p_id','review','user','name','rating']
        read_only_fields = ["user"]
    
    def get_name(self, obj) -> str:
        return obj.user.first_name