from rest_framework import serializers

def raise_validation(message: str):
    raise serializers.ValidationError({"message": message})