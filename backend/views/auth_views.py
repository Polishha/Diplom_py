"""
Представления для аутентификации пользователей.
Содержит функции для регистрации, подтверждения email, входа и управления профилем.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from backend.models import User, ConfirmEmailToken
from backend.serializers import UserSerializer


class RegisterAccount(APIView):
    """
    Регистрация нового пользователя.
    
    Создает нового пользователя с указанными данными.
    После создания отправляет email с токеном для подтверждения.
    
    POST /api/v1/user/register
    
    Request body:
        - email (str): Email пользователя (обязательно)
        - password (str): Пароль (обязательно, минимум 8 символов)
        - first_name (str): Имя (обязательно)
        - last_name (str): Фамилия (обязательно)
        - patronymic (str): Отчество (опционально)
        - company (str): Компания (опционально)
        - position (str): Должность (опционально)
        - type (str): Тип пользователя: 'buyer' или 'shop' (по умолчанию 'buyer')
    
    Returns:
        201 Created: {
            "Status": True,
            "Message": "Пользователь создан. Проверьте email для подтверждения."
        }
        400 Bad Request: {
            "Status": False,
            "Error": "Описание ошибки"
        }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Проверяем обязательные поля
        required_fields = ['email', 'password', 'first_name', 'last_name']
        if not all(field in request.data for field in required_fields):
            return Response(
                {'Status': False, 'Error': 'Не указаны все необходимые аргументы'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка пароля
        try:
            validate_password(request.data['password'])
        except ValidationError as e:
            return Response(
                {'Status': False, 'Errors': {'password': list(e.messages)}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка существования пользователя
        if User.objects.filter(email=request.data['email']).exists():
            return Response(
                {'Status': False, 'Error': 'Пользователь с таким email уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Создание пользователя
            user = User.objects.create_user(
                email=request.data['email'],
                password=request.data['password'],
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', ''),
                patronymic=request.data.get('patronymic', ''),
                company=request.data.get('company', ''),
                position=request.data.get('position', ''),
                type=request.data.get('type', 'buyer')
            )

            # Создаем токен для подтверждения email
            token = ConfirmEmailToken.objects.create(user=user)
            
            # Отправляем письмо с подтверждением
            send_mail(
                'Подтверждение регистрации',
                f'Для подтверждения регистрации перейдите по ссылке:\n'
                f'http://localhost:8000/api/v1/user/confirm/?token={token.key}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response(
                {
                    'Status': True, 
                    'Message': 'Пользователь создан. Проверьте email для подтверждения.'
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'Status': False, 'Error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfirmAccount(APIView):
    """
    Подтверждение email пользователя.
    
    Активирует пользователя после проверки токена, отправленного на email.
    
    POST /api/v1/user/confirm
    
    Request body:
        - token (str): Токен подтверждения из письма
    
    Returns:
        200 OK: {
            "Status": True,
            "Message": "Email успешно подтвержден"
        }
        400 Bad Request: {
            "Status": False,
            "Error": "Не указан токен"
        }
        404 Not Found: {
            "Status": False,
            "Error": "Неверный токен"
        }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'Status': False, 'Error': 'Не указан токен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            confirm_token = ConfirmEmailToken.objects.get(key=token)
            user = confirm_token.user
            user.is_active = True
            user.save()
            confirm_token.delete()
            
            return Response(
                {'Status': True, 'Message': 'Email успешно подтвержден'}
            )
        except ConfirmEmailToken.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Неверный токен'},
                status=status.HTTP_404_NOT_FOUND
            )


class LoginAccount(APIView):
    """
    Авторизация пользователя.
    
    Проверяет email и пароль, возвращает токен для последующих запросов.
    
    POST /api/v1/user/login
    
    Request body:
        - email (str): Email пользователя
        - password (str): Пароль
    
    Returns:
        200 OK: {
            "Status": True,
            "Token": "токен_для_авторизации",
            "User": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "type": "buyer"
            }
        }
        400 Bad Request: {
            "Status": False,
            "Error": "Не указаны email или пароль"
        }
        404 Not Found: {
            "Status": False,
            "Error": "Пользователь не найден"
        }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if 'email' not in request.data or 'password' not in request.data:
            return Response(
                {'Status': False, 'Error': 'Не указаны email или пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.check_password(request.data['password']):
            return Response(
                {'Status': False, 'Error': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            return Response(
                {'Status': False, 'Error': 'Email не подтвержден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'Status': True,
            'Token': token.key,
            'User': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'type': user.type
            }
        })


class AccountDetails(APIView):
    """
    Получение и обновление данных пользователя.
    
    GET - возвращает информацию о текущем пользователе
    POST - обновляет данные текущего пользователя
    
    GET /api/v1/user/details
    POST /api/v1/user/details
    
    Request body (POST):
        - first_name (str): Имя
        - last_name (str): Фамилия
        - patronymic (str): Отчество
        - company (str): Компания
        - position (str): Должность
    
    Returns:
        200 OK: Данные пользователя в формате UserSerializer
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получение данных текущего пользователя.
        
        Returns:
            Response: Данные пользователя в формате JSON
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Обновление данных текущего пользователя.
        
        Args:
            request: HTTP запрос с полями для обновления
            
        Returns:
            Response: Обновленные данные пользователя
        """
        user = request.user
        allowed_fields = ['first_name', 'last_name', 'patronymic', 'company', 'position']
        
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)