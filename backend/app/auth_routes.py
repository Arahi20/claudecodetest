from flask import Blueprint, request, jsonify, current_app, redirect
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from authlib.integrations.requests_client import OAuth2Session
from app import db
from app.models import User
from datetime import datetime
import requests

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user with email/password"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        email = data['email'].lower().strip()
        password = data['password']
        name = data.get('name', '').strip()

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User with this email already exists'}), 409

        # Create new user
        user = User(
            email=email,
            name=name or email.split('@')[0],
            email_verified=False  # Could send verification email here
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create tokens (identity must be string)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(include_email=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'An error occurred during signup'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email/password"""
    try:
        data = request.get_json()

        email = data.get('email', '').lower().strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create tokens (identity must be string)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(include_email=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)

        return jsonify({
            'access_token': access_token
        }), 200

    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'An error occurred refreshing token'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': user.to_dict(include_email=True)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout (client should delete tokens)"""
    # In a more robust system, you'd add the token to a blacklist here
    return jsonify({'message': 'Logged out successfully'}), 200


# OAuth Routes

@auth_bp.route('/oauth/google', methods=['GET'])
def google_login():
    """Initiate Google OAuth login"""
    try:
        if not current_app.config['GOOGLE_CLIENT_ID']:
            return jsonify({'error': 'Google OAuth not configured'}), 501

        client = OAuth2Session(
            current_app.config['GOOGLE_CLIENT_ID'],
            redirect_uri=f"{current_app.config['FRONTEND_URL']}/auth/callback/google",
            scope=['openid', 'email', 'profile']
        )

        authorization_url, state = client.create_authorization_url(
            'https://accounts.google.com/o/oauth2/v2/auth'
        )

        return jsonify({
            'authorization_url': authorization_url,
            'state': state
        }), 200

    except Exception as e:
        current_app.logger.error(f"Google OAuth init error: {str(e)}")
        return jsonify({'error': 'OAuth initialization failed'}), 500


@auth_bp.route('/oauth/google/callback', methods=['POST'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        data = request.get_json()
        code = data.get('code')

        if not code:
            return jsonify({'error': 'Authorization code required'}), 400

        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': f"{current_app.config['FRONTEND_URL']}/auth/callback/google",
            'grant_type': 'authorization_code'
        }

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()

        # Get user info
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f"Bearer {tokens['access_token']}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        # Find or create user
        user = User.query.filter_by(
            oauth_provider='google',
            oauth_id=user_info['id']
        ).first()

        if not user:
            # Check if email already exists
            user = User.query.filter_by(email=user_info['email']).first()
            if user:
                # Link OAuth to existing account
                user.oauth_provider = 'google'
                user.oauth_id = user_info['id']
            else:
                # Create new user
                user = User(
                    email=user_info['email'],
                    name=user_info.get('name', ''),
                    oauth_provider='google',
                    oauth_id=user_info['id'],
                    avatar_url=user_info.get('picture'),
                    email_verified=user_info.get('verified_email', False)
                )
                db.session.add(user)

        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create JWT tokens (identity must be string)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(include_email=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except requests.RequestException as e:
        current_app.logger.error(f"Google OAuth callback error: {str(e)}")
        return jsonify({'error': 'OAuth authentication failed'}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Google OAuth callback error: {str(e)}")
        return jsonify({'error': 'An error occurred during authentication'}), 500


@auth_bp.route('/oauth/okta', methods=['GET'])
def okta_login():
    """Initiate Okta OAuth login"""
    try:
        if not current_app.config['OKTA_DOMAIN'] or not current_app.config['OKTA_CLIENT_ID']:
            return jsonify({'error': 'Okta OAuth not configured'}), 501

        okta_domain = current_app.config['OKTA_DOMAIN']
        client = OAuth2Session(
            current_app.config['OKTA_CLIENT_ID'],
            redirect_uri=f"{current_app.config['FRONTEND_URL']}/auth/callback/okta",
            scope=['openid', 'email', 'profile']
        )

        authorization_url, state = client.create_authorization_url(
            f'https://{okta_domain}/oauth2/default/v1/authorize'
        )

        return jsonify({
            'authorization_url': authorization_url,
            'state': state
        }), 200

    except Exception as e:
        current_app.logger.error(f"Okta OAuth init error: {str(e)}")
        return jsonify({'error': 'OAuth initialization failed'}), 500


@auth_bp.route('/oauth/okta/callback', methods=['POST'])
def okta_callback():
    """Handle Okta OAuth callback"""
    try:
        data = request.get_json()
        code = data.get('code')

        if not code:
            return jsonify({'error': 'Authorization code required'}), 400

        okta_domain = current_app.config['OKTA_DOMAIN']

        # Exchange code for token
        token_url = f'https://{okta_domain}/oauth2/default/v1/token'
        token_data = {
            'code': code,
            'client_id': current_app.config['OKTA_CLIENT_ID'],
            'client_secret': current_app.config['OKTA_CLIENT_SECRET'],
            'redirect_uri': f"{current_app.config['FRONTEND_URL']}/auth/callback/okta",
            'grant_type': 'authorization_code'
        }

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()

        # Get user info
        user_info_response = requests.get(
            f'https://{okta_domain}/oauth2/default/v1/userinfo',
            headers={'Authorization': f"Bearer {tokens['access_token']}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        # Find or create user
        user = User.query.filter_by(
            oauth_provider='okta',
            oauth_id=user_info['sub']
        ).first()

        if not user:
            user = User.query.filter_by(email=user_info['email']).first()
            if user:
                user.oauth_provider = 'okta'
                user.oauth_id = user_info['sub']
            else:
                user = User(
                    email=user_info['email'],
                    name=user_info.get('name', ''),
                    oauth_provider='okta',
                    oauth_id=user_info['sub'],
                    email_verified=user_info.get('email_verified', False)
                )
                db.session.add(user)

        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create JWT tokens (identity must be string)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(include_email=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except requests.RequestException as e:
        current_app.logger.error(f"Okta OAuth callback error: {str(e)}")
        return jsonify({'error': 'OAuth authentication failed'}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Okta OAuth callback error: {str(e)}")
        return jsonify({'error': 'An error occurred during authentication'}), 500
