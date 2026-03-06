import requests  
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from allauth.socialaccount.models import SocialAccount
from singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()

class GoogleLoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        id_token = request.data.get('id_token') 

        if not id_token:
            logger.warning('Google login attempted without id_token')
            return Response(
                {'error': 'id_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            google_response = requests.get( 
                'https://oauth2.googleapis.com/tokeninfo',
                params={'id_token': id_token}
            )
            google_data = google_response.json()

            if google_response.status_code != 200 or 'error' in google_data:
                logger.warning(f'Invalid Google token received: {google_data}')
                return Response(
                    {'error': 'Invalid or expired Google Token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except requests.RequestException as e:  
            logger.error(f'Could not reach Google servers: {str(e)}')
            return Response(
                {'error': 'Could not verify token with Google. Try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        google_user_id = google_data.get('sub')
        email          = google_data.get('email')
        name           = google_data.get('name', '')

        if not google_user_id or not email:
            logger.error('Google token missing sub or email')
            return Response(
                {'error': 'Could not retrieve user info from Google'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            social_account = SocialAccount.objects.get(
                provider='google',
                uid=google_user_id
            )
            user = social_account.user
            logger.info(f'Existing Google user logged in: {email}')

        except SocialAccount.DoesNotExist:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )

            if created:
                user.set_unusable_password()
                user.save()
                logger.info(f'New user created via Google OAuth: {email}')
            else:
                logger.info(f'Existing user linked to Google: {email}')

            SocialAccount.objects.create(
                user=user,
                provider='google',
                uid=google_user_id,
                extra_data=google_data
            )

        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f'Google OAuth login successful for: {email}')

        return Response({
            'message': 'Google login successful',
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'username': user.username,
        }, status=status.HTTP_200_OK)
     