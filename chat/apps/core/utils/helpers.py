from rest_framework import serializers

def raise_validation(message: str, key: str = "message"):
    raise serializers.ValidationError({key: message})