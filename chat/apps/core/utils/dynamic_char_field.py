from rest_framework import serializers

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
    