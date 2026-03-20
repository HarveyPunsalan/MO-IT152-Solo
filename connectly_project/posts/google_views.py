# google_views.py
# Handles Google OAuth login for the Connectly API.
# Accepts a Google id_token, verifies it with Google, then returns our app token.

import requests  
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from allauth.socialaccount.models import SocialAccount
from singletons.logger_singleton import LoggerSingleton

# Using our existing Singleton Logger from MS1 for consistent logging
logger = LoggerSingleton().get_logger()

class GoogleLoginView(APIView):
    # No auth required here this is the login endpoint itself
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        # Step 1: Get the Google token from the request body
        id_token = request.data.get('id_token') 

        # Reject immediately if no token was sent
        if not id_token:
            logger.warning('Google login attempted without id_token')
            return Response(
                {'error': 'id_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Step 2: Send the token to Google to verify it's real and not expired
        try:
            google_response = requests.get( 
                'https://oauth2.googleapis.com/tokeninfo',
                params={'id_token': id_token}
            )
            google_data = google_response.json()

            # If Google says the token is invalid, reject the request
            if google_response.status_code != 200 or 'error' in google_data:
                logger.warning(f'Invalid Google token received: {google_data}')
                return Response(
                    {'error': 'Invalid or expired Google Token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        # Handle the case where we can't reach Google's servers at all
        except requests.RequestException as e:  
            logger.error(f'Could not reach Google servers: {str(e)}')
            return Response(
                {'error': 'Could not verify token with Google. Try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Step 3: Extract user info from Google's response
        # 'sub' is Google's permanent unique ID for this user
        google_user_id = google_data.get('sub')
        email          = google_data.get('email')
        name           = google_data.get('name', '')

        # To make sure i got the essential user info back from Google
        if not google_user_id or not email:
            logger.error('Google token missing sub or email')
            return Response(
                {'error': 'Could not retrieve user info from Google'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 4: Find or create the user in our database
        try:
            # Check if this Google account is already linked to a local user
            social_account = SocialAccount.objects.get(
                provider='google',
                uid=google_user_id
            )
            user = social_account.user
            logger.info(f'Existing Google user logged in: {email}')

        except SocialAccount.DoesNotExist:
            # First time this Google account is used — find or create a local user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )

            if created:
                # New user — set unusable password since they log in via Google
                user.set_unusable_password()
                user.save()
                logger.info(f'New user created via Google OAuth: {email}')
            else:
                logger.info(f'Existing user linked to Google: {email}')

            # To link this Google account to the local user for future logins
            SocialAccount.objects.create(
                user=user,
                provider='google',
                uid=google_user_id,
                extra_data=google_data
            )
        
        # Step 5: Generate the app token and return it to the client
        # From here the user uses this token — not the Google token
        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f'Google OAuth login successful for: {email}')

        return Response({
            'message': 'Google login successful',
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'username': user.username,
        }, status=status.HTTP_200_OK)
     