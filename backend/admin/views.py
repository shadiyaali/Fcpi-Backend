from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.views import APIView

class AdminLoginView(APIView):
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        admin = authenticate(request, email=email, password=password)
        if admin is not None and admin.is_admin:
            login(request, admin)
            return JsonResponse({'message': 'Admin login successful'})
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=400)

    def get(self, request):
        return JsonResponse({'error': 'Method not allowed'}, status=405)

