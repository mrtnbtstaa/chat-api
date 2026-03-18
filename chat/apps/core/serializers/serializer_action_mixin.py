class SerializerActionMixin:

    """
        Allows mapping serializer per action (create, retrieve, list, update)
    """
    serializer_action_classes = {}

    def get_serializer_class(self):
        
        # Matching action
        if self.action in self.serializer_action_classes:
            # Check for specific action
            serializer = self.serializer_action_classes.get(self.action)

            if not serializer and self.action == 'partial_update':
                serializer = self.serializer_action_classes.get('update')
        
        return serializer or super().get_serializer_class()