from rest_framework import serializers
from rest_framework import status
from apps.core.utils.helpers import raise_validation
from channels.layers import channel_layers
from asgiref.sync import async_to_sync


