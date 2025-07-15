from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Author
        fields = '__all__'

