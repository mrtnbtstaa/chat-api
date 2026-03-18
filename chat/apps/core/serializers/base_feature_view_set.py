from apps.core.utils.response_message import response_message
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.serializers.serializer_action_mixin import SerializerActionMixin
from apps.core.serializers.message_response import MessageResponse
from django.db.models import Q

class BaseFeatureViewSet(
    SerializerActionMixin,
    MessageResponse,
    viewsets.ModelViewSet
):
    
    """
        Base class feature with:
        - CRUD
        - Search
    """

    model = None

    many = False

    with_pagination = True

    permission_classes = [IsAuthenticated]

    lookup_field = 'id' # Model object lookup

    lookup_url_kwarg = 'id' # The URL keyword argument that will be used to extract the lookup value from the URL

    prefetch_related_model = None # (reverse/M2M relations)
    select_related_model = None # (FK/O1O relations)

    item_to_search = [] # 

    # Action specific serializers
    serializer_action_classes = {
        "create": None,
        "list": None,
        "retrieve": None,
        "update": None,
        "partial_update": None
    }

    def base_get_queryset(self):
        """
            Base queryset hook. Subclasses can override this
            if needed to prefilter the queryset
        """
        return self.model.objects.all()
    
    def get_queryset(self):
        
        qs = self.base_get_queryset()

        # Apply the select_related_model if has been set
        if self.select_related_model:
            qs = qs.select_related(*self.select_related_model)

        # Apply the prefetch_related_model if has been set
        if self.prefetch_related_model:
            qs = qs.prefetch_related(*self.prefetch_related_model)

        search = self.request.query_params.get('search')

        if search:
            
            query = Q()

            for field in self.item_to_search:
                query |= Q(**{f"{field}__icontains": search})
            return qs.filter(query).order_by('created_at')
        
        return qs.order_by('created_at')
    
    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data, many=self.many)

        serializer.is_valid(raise_exception=True)
        
        instance = self.perform_create(serializer)

        return response_message(
            success=True,
            message=self.success_create_message,
            status_code=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        
        instance = self.get_object()

        serializer = self.get_serializer(instance)

        return response_message(
            success=True,
            data=serializer.data,
            message=self.success_retrieve_message
        )
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())

        # Handle pagination
        page = self.paginate_queryset(queryset)

        # Check if pagination is enabled and if the DEF paginator is configured
        if self.with_pagination and self.paginator is not None:
            page = self.paginate_queryset(queryset)
            
            if page:

                serializer = self.get_serializer(page, many=True)

                paginated_data = self.get_paginated_response(serializer.data)

                return response_message(
                    status_code=True,
                    message=self.success_list_message,
                    data=paginated_data.data
                )

        # Fallback for no pagination
        serializer = self.get_serializer(queryset, many=True)

        return response_message(
            success=True,
            message=self.success_list_message,
            data=serializer.data
        )
        

    def handle_update(self, request, partial):

        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return response_message(
            success=True,
            message=self.success_update_message,
            data=serializer.data
        )
    
    def update(self, request, *args, **kwargs):
        return self.handle_update(request, False)
    
    def partial_update(self, request, *args, **kwargs):
        return self.handle_update(request, True)
    

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        self.perform_destroy(instance)

        return response_message(
            success=True,
            message=self.success_delete_message,

        )






