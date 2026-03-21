from rest_framework.pagination import CursorPagination, PageNumberPagination

class CustomCursorPagination(CursorPagination):

    page_size = 25

    ordering = '-created_at'

    cursor_query_param = 'cursor'


class CustomPageNumberPagination(PageNumberPagination):

    page_size = 10

    page_size_query_param = 'page_size'

    max_page_size = 30
