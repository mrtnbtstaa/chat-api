from rest_framework import serializers
import uuid
from django.core.files.base import ContentFile
from io import BytesIO
import base64
import binascii
from PIL import Image, ImageFile
import six

class DynamicUUIDField(serializers.UUIDField):

    def fail(self, key, **kwargs):
        
        # Get the field name and format it from profile_image => Profile image
        field_name = self.field_name.replace('_', " ").capitalize()
        
        # Define custom error templates using the {fieldname} placeholder
        custom_messages = {
            "required": f"{field_name} is required.",
            "null": f"{field_name} cannot be null.",
            "blank": f"{field_name} cannot be blank.",
            "invalid": f"{field_name} is invalid."
        }

        if key in custom_messages:
            self.error_messages[key] = custom_messages[key]

        return super().fail(key, **kwargs)

class DynamicCharField(serializers.CharField):

    def fail(self, key, **kwargs):
        
        # Get the field name and format it from profile_image => Profile image
        field_name = self.field_name.replace('_', " ").capitalize()
        
        # Pull the actual value min length defined on the field
        min_limit = kwargs.get('min_length') or getattr(self, 'min_length', None)

        # Define custom error templates using the {fieldname} placeholder
        custom_messages = {
            "required": f"{field_name} is required.",
            "null": f"{field_name} cannot be null.",
            "blank": f"{field_name} cannot be blank.",
            "min_length": f"{field_name} must be atleast {min_limit} characters.",
            "invalid": f"{field_name} is invalid."
        }

        if key in custom_messages:
            self.error_messages[key] = custom_messages[key]

        return super().fail(key, **kwargs)
    

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):

        # Handle none, null or empty string
        if data in (None, ""):
            return None

        if isinstance(data, six.string_types):
            # Debug: Print first 100 chars of input
            print(f"Input data (first 100 chars): {data[:100]}...")

            # Handle data URI
            if ';base64,' in data:
                header, data = data.split(';base64,')
                print(f"Extracted header: {header} and the data: {data}")

            try:
                # Decoded base64
                decoded_file = base64.b64decode(data)
                print("Base64 decoded successfully")
                
                # Use a more forgiving image parser
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                buffer = BytesIO(decoded_file)
                
                # Try to open the image
                try:
                    image = Image.open(buffer)
                    print(f"Image format detected: {image.format}")
                    
                    # Verify without closing
                    image.load()
                    print("Image loaded and verified")
                    
                    # Get extension
                    extension = image.format.lower()
                    extension = 'jpg' if extension == 'jpeg' else extension
                    print(f"Using extension: {extension}")
                    
                    # Reset buffer
                    buffer.seek(0)
                    file_name = f"{uuid.uuid4().hex[:12]}.{extension}"
                    return ContentFile(buffer.read(), name=file_name)
                    
                except Exception as e:
                    print(f"Image opening failed: {str(e)}")
                    self.fail('invalid_image')
                    
            except (ValueError, TypeError, binascii.Error) as e:
                print(f"Base64 decoding failed: {str(e)}")
                self.fail('invalid_image')

        return super().to_internal_value(data)
    