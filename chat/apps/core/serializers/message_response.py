class MessageResponse:

    @property
    def success_create_message(self):
        return f"{self.model.__name__} created successfully."
    
    @property
    def success_list_message(self):
        return f"{self.model.__name__} list successfully"
    
    @property
    def success_retrieve_message(self):
        return f"{self.model.__name__} details retrieved successfully"
    
    @property
    def success_update_message(self):
        return f"{self.model.__name__} updated successfully."
    
    @property
    def success_delete_message(self):
        return f"{self.model.__name__} deleted successfully"