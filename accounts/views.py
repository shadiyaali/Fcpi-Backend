from rest_framework import generics, status
 
 
from .serializers import RegisterSerializer, VerifyAccountSerializer 
from rest_framework.response import Response
from .models import User, OTPVerification 
from .emails import send_otp_via_mail
from django.utils import timezone
 
from django.shortcuts import get_object_or_404


# Create your views here.


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_otp_via_mail(serializer.data['email'])

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        return Response({
            'status': 200,
            'message': 'registration successfull check email',
            'data': serializer.data,
        })


class OTPVerificationView(generics.CreateAPIView):

    def post(self, request):
        data = request.data
        serializer = VerifyAccountSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp_code = serializer.data['otp']
            user = User.objects.get(email=email)
        try:
            otp_verification = OTPVerification.objects.get(user=user)
        except OTPVerification.DoesNotExist:
            return Response({'message': 'OTP verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_verification.otp == otp_code and otp_verification.expiration_time > timezone.now():
            # OTP is valid
            user.is_verified = True
            user.save()
            otp_verification.delete()  # Delete the OTP verification entry after successful verification
            return Response({'message': 'OTP verification successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'OTP verification failed'}, status=status.HTTP_400_BAD_REQUEST)
