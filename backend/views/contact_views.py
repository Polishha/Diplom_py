"""
Представления для управления контактами пользователя (адресами доставки).
Содержит функции для создания, просмотра, обновления и удаления контактов.
"""

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from backend.models import Contact
from backend.serializers import ContactSerializer


class ContactView(generics.ListCreateAPIView):
    """
    Получение списка контактов и создание нового контакта.
    
    GET /api/v1/contacts - список всех контактов текущего пользователя
    POST /api/v1/contacts - создание нового контакта
    
    GET returns:
        200 OK: Список контактов пользователя в формате JSON
    
    POST request body:
        {
            "city": "Москва",
            "street": "Тверская",
            "house": "10",
            "apartment": "25",
            "phone": "+79991234567"
        }
    
    POST returns:
        201 Created: Созданный контакт в формате JSON
        400 Bad Request: Ошибки валидации
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Получение queryset только для текущего пользователя.
        
        Returns:
            QuerySet: Контакты текущего пользователя
        """
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Сохранение контакта с привязкой к текущему пользователю.
        
        Args:
            serializer: Сериализатор с данными контакта
        """
        serializer.save(user=self.request.user)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление конкретного контакта.
    
    GET /api/v1/contacts/{id} - просмотр контакта
    PUT /api/v1/contacts/{id} - полное обновление контакта
    PATCH /api/v1/contacts/{id} - частичное обновление контакта
    DELETE /api/v1/contacts/{id} - удаление контакта
    
    Args:
        id: ID контакта
    
    Returns:
        GET: 200 OK - Данные контакта
        PUT/PATCH: 200 OK - Обновленные данные контакта
        DELETE: 204 No Content
        403 Forbidden: Попытка доступа к чужому контакту
        404 Not Found: Контакт не найден
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Получение queryset только для текущего пользователя.
        
        Returns:
            QuerySet: Контакты текущего пользователя
        """
        return Contact.objects.filter(user=self.request.user)