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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Пользователь с таким email не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        token = ResetPasswordToken.objects.create(user=user)

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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        try:
            reset_token = ResetPasswordToken.objects.get(key=token)
        except ResetPasswordToken.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Неверный или просроченный токен'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = reset_token.user
        user.set_password(password)
        user.save()

        reset_token.delete()

        return Response({
            'Status': True,
            'Message': 'Пароль успешно изменен'
        })