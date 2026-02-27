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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        required_fields = ['email', 'password', 'first_name', 'last_name']
        if not all(field in request.data for field in required_fields):
            return Response(
                {'Status': False, 'Error': 'Не указаны все необходимые аргументы'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(request.data['password'])
        except ValidationError as e:
            return Response(
                {'Status': False, 'Errors': {'password': list(e.messages)}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=request.data['email']).exists():
            return Response(
                {'Status': False, 'Error': 'Пользователь с таким email уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
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

            token = ConfirmEmailToken.objects.create(user=user)
            
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
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        allowed_fields = ['first_name', 'last_name', 'patronymic', 'company', 'position']
        
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)