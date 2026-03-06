"""
Представления для восстановления пароля.
Содержит функции для запроса сброса пароля и установки нового пароля.
"""

from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.serializers import (
    EmailSerializer,
    PasswordTokenSerializer
)
from backend.models import User


class RequestPasswordReset(APIView):
    """
    Запрос на сброс пароля.
    
    Отправляет на email пользователя письмо с токеном для сброса пароля.
    
    POST /api/v1/password/reset
    
    Request body:
        - email (str): Email пользователя
    
    Returns:
        200 OK: {
            "Status": True,
            "Message": "Инструкции по восстановлению пароля отправлены на email"
        }
        404 Not Found: {
            "Status": False,
            "Error": "Пользователь с таким email не найден"
        }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Обработка запроса на сброс пароля.
        
        Args:
            request: HTTP запрос с email пользователя
            
        Returns:
            Response: Результат операции
        """
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Проверяем, существует ли пользователь с таким email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Пользователь с таким email не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Создаем токен для сброса пароля
        token = ResetPasswordToken.objects.create(user=user)

        # Отправляем email с токеном
        send_mail(
            'Восстановление пароля',
            f'Для восстановления пароля перейдите по ссылке:\n'
            f'http://localhost:8000/reset-password?token={token.key}\n\n'
            f'Или используйте токен: {token.key}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({
            'Status': True,
            'Message': 'Инструкции по восстановлению пароля отправлены на email'
        })


class ConfirmPasswordReset(APIView):
    """
    Подтверждение сброса пароля и установка нового.
    
    Проверяет токен и устанавливает новый пароль для пользователя.
    
    POST /api/v1/password/reset/confirm
    
    Request body:
        - token (str): Токен из письма
        - password (str): Новый пароль
    
    Returns:
        200 OK: {
            "Status": True,
            "Message": "Пароль успешно изменен"
        }
        404 Not Found: {
            "Status": False,
            "Error": "Неверный или просроченный токен"
        }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Обработка подтверждения сброса пароля.
        
        Args:
            request: HTTP запрос с токеном и новым паролем
            
        Returns:
            Response: Результат операции
        """
        serializer = PasswordTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        # Получаем токен из базы
        try:
            reset_token = ResetPasswordToken.objects.get(key=token)
        except ResetPasswordToken.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Неверный или просроченный токен'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Устанавливаем новый пароль
        user = reset_token.user
        user.set_password(password)
        user.save()

        # Удаляем использованный токен
        reset_token.delete()

        return Response({
            'Status': True,
            'Message': 'Пароль успешно изменен'
        })