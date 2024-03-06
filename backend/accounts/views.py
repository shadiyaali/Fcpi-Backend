from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from .helpers import *


class RegisterView(APIView):
    
    def post(self, request):
        try:
            serializer = UserSerializer(data = request.data)
            
            if not serializer.is_valid():
               return Response({
                   'status' : 403,
                   'errors' : serializer.errors
               })
            serializer.save()
            return Response({'status' : 200 ,'message':'an OTP sent on your number and email http://127.0.0.1:8000/{uuid.uuid4()}/'})
        except Exception as e:
            print(e)
            
            return Response({'status' : 404,'error' : 'something went wrong'})

class VerifyOtp(APIView):
    
    def post(self , request):
        try:
            data = request.data
            user_obj = User.objects.get(phone = data['phone'])
            otp = data.get('otp')
            
            if user_obj.otp == otp:
                user_obj.is_phone_verified = True
                user_obj.save()
                return Response({'status':200 , 'message':'your OTP is verified'})
        
            return Response({'status':403 , 'message':'your OTP is wrong'})        
            
        except Exception as e:
            print(e)
        return Response({'status' : 404,'error' :'something went wrong'})        
    
    def patch(self, request):
        try:
            data = request.data
            
            if not User.objects.filter(phone= data.get('phone')).exists():
                return Response({'status' : 404,'error' :'no user found'}) 
            
            if send_otp_to_mobile(data.get('phone')):
                return Response({'status' : 200,'message' :'new otp sent'})   
            
            return Response({'status' : 404,'error' :'try after few seconds'}) 
        
        except Exception as e:
            print(e)    