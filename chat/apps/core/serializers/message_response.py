class MessageResponse:

    @property
    def success_create_message(self):
        return f"{str(self.model.__name__).lower()} created successfully."
    
    @property
    def success_list_message(self):
        return f"{str(self.model.__name__).lower()} list successfully"
    
    @property
    def success_retrieve_message(self):
        return f"{str(self.model.__name__).lower()} details retrieved successfully"
    
    @property
    def success_update_message(self):
        return f"{str(self.model.__name__).lower()} updated successfully."
    
    @property
    def success_delete_message(self):
        return f"{str(self.model.__name__).lower()} deleted successfully"