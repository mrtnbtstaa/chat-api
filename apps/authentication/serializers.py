from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework import serializers
from django.db import transaction
from apps.core.utils.validators import is_field_empty

class CustomLoginObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        
        request = self.context.get('request')


        username = attrs.get('username')
        password = attrs.get('password')

        if is_field_empty(username):
            pass


    

