"""OAuth authentication endpoints for Google and Phantom wallet."""

from __future__ import annotations

import os
import secrets
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from langflow.api.utils import DbSession
from langflow.api.v1.schemas import Token
from langflow.initial_setup.setup import get_or_create_default_folder
from langflow.services.auth.utils import create_user_tokens, get_password_hash
from langflow.services.database.models.user.crud import get_user_by_username
from langflow.services.database.models.user.model import User
from langflow.services.deps import get_settings_service

router = APIRouter(tags=["OAuth"], prefix="/oauth")


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class PhantomVerifyRequest(BaseModel):
    """Request model for Phantom wallet verification."""
    publicKey: str
    signature: list[int]  # Phantom sends signature as byte array
    message: str


# ============================================================================
# GOOGLE OAUTH
# ============================================================================


@router.get("/google/authorize")
async def google_oauth_authorize(request: Request):
    """Redirect to Google OAuth consent screen."""
    settings = get_settings_service().auth_settings
    
    # Check if Google OAuth is configured
    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None) or os.environ.get('LANGFLOW_GOOGLE_CLIENT_ID')
    google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', None) or os.environ.get('LANGFLOW_GOOGLE_CLIENT_SECRET')
    
    if not google_client_id or not google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Google OAuth is not configured. Please set LANGFLOW_GOOGLE_CLIENT_ID and LANGFLOW_GOOGLE_CLIENT_SECRET environment variables.",
                "configured": False
            }
        )
    
    # Generate signed state for CSRF protection (no session storage needed)
    import time
    import hmac
    import hashlib
    
    # Get secret key as string (handle SecretStr type)
    secret_key_value = settings.SECRET_KEY.get_secret_value() if hasattr(settings.SECRET_KEY, 'get_secret_value') else str(settings.SECRET_KEY or "langflow-oauth-secret")
    timestamp = str(int(time.time()))
    random_value = secrets.token_urlsafe(16)
    
    # Create signed state: timestamp:random:signature
    message = f"{timestamp}:{random_value}"
    signature = hmac.new(secret_key_value.encode(), message.encode(), hashlib.sha256).hexdigest()
    state = f"{timestamp}:{random_value}:{signature}"
    
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    redirect_uri = str(request.base_url).rstrip("/") + "/api/v1/oauth/google/callback"
    
    params = {
        "client_id": google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    auth_url = f"{google_auth_url}?{urlencode(params)}"
    return {"authorization_url": auth_url}


@router.get("/google/callback")
async def google_oauth_callback(
    request: Request,
    response: Response,
    db: DbSession,
    code: str = Query(...),
    state: str = Query(...),
):
    """Handle Google OAuth callback and create/login user."""
    settings = get_settings_service().auth_settings
    
    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None) or os.environ.get('LANGFLOW_GOOGLE_CLIENT_ID')
    google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', None) or os.environ.get('LANGFLOW_GOOGLE_CLIENT_SECRET')
    
    if not google_client_id or not google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth is not configured properly.",
        )
    
    # Verify signed state to prevent CSRF attacks
    import time
    import hmac
    import hashlib
    
    try:
        # Parse state: timestamp:random:signature
        parts = state.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid state format")
        
        timestamp_str, random_value, received_signature = parts
        timestamp = int(timestamp_str)
        
        # Check if state is not too old (e.g., 10 minutes)
        current_time = int(time.time())
        if current_time - timestamp > 600:  # 10 minutes
            raise ValueError("State token expired")
        
        # Verify signature
        secret_key_value = settings.SECRET_KEY.get_secret_value() if hasattr(settings.SECRET_KEY, 'get_secret_value') else str(settings.SECRET_KEY or "langflow-oauth-secret")
        message = f"{timestamp_str}:{random_value}"
        expected_signature = hmac.new(secret_key_value.encode(), message.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected_signature, received_signature):
            raise ValueError("Invalid state signature")
            
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state parameter. Possible CSRF attack. Error: {str(e)}",
        )
    
    # Exchange authorization code for access token
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = str(request.base_url).rstrip("/") + "/api/v1/oauth/google/callback"
    
    token_data = {
        "code": code,
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for token: {str(e)}",
            ) from e
        
        # Get user info from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        try:
            userinfo_response = await client.get(userinfo_url, headers=headers)
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info: {str(e)}",
            ) from e
    
    # Create or get existing user
    google_id = user_info["id"]
    email = user_info["email"]
    username = email.split("@")[0]  # Use email prefix as username
    
    # Try to find existing user by username or create new one
    user = await get_user_by_username(db, username)
    
    if not user:
        # Create new user with OAuth provider info
        new_user = User(
            username=username,
            password=get_password_hash(secrets.token_urlsafe(32)),  # Random password
            is_active=True,
            oauth_provider="google",
            oauth_id=google_id,
            email=email,
        )
        try:
            db.add(new_user)
            await db.flush()
            await db.refresh(new_user)
            
            # Create default folder
            await get_or_create_default_folder(db, new_user.id)
            await db.commit()
            user = new_user
        except IntegrityError:
            await db.rollback()
            # Username conflict, try with google ID suffix
            username = f"{username}_{google_id[:8]}"
            user = await get_user_by_username(db, username)
            if not user:
                new_user.username = username
                db.add(new_user)
                await db.flush()
                await db.refresh(new_user)
                await get_or_create_default_folder(db, new_user.id)
                await db.commit()
                user = new_user
    
    # Generate JWT tokens
    user_tokens = await create_user_tokens(user_id=user.id, db=db, update_last_login=True)
    
    # Create HTML response that stores tokens and redirects
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login Success</title>
        <script>
            // Store both tokens in localStorage
            localStorage.setItem('access_token_lf', '{user_tokens["access_token"]}');
            localStorage.setItem('refresh_token_lf', '{user_tokens["refresh_token"]}');
            
            // Also set cookies via JavaScript as backup
            document.cookie = 'access_token_lf={user_tokens["access_token"]}; path=/; max-age={settings.ACCESS_TOKEN_EXPIRE_SECONDS}; samesite=lax';
            document.cookie = 'refresh_token_lf={user_tokens["refresh_token"]}; path=/; max-age={settings.REFRESH_TOKEN_EXPIRE_SECONDS}; samesite=lax';
            
            // Redirect to home page after a short delay to ensure cookies are set
            setTimeout(function() {{
                window.location.href = 'http://127.0.0.1:7860/';
            }}, 500);
        </script>
    </head>
    <body>
        <p>Login successful. Redirecting...</p>
    </body>
    </html>
    """
    
    # Create response with cookies set via Set-Cookie headers
    html_response = Response(content=html_content, media_type="text/html")
    
    # Set refresh token cookie (HTTP-only for security)
    html_response.set_cookie(
        "refresh_token_lf",
        user_tokens["refresh_token"],
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        path="/",
    )
    
    # Set access token cookie (httponly=False so JavaScript can read it)
    html_response.set_cookie(
        "access_token_lf",
        user_tokens["access_token"],
        httponly=False,
        samesite="lax",
        secure=False,
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        path="/",
    )
    
    return html_response


# ============================================================================
# PHANTOM WALLET OAUTH (Web3 Authentication)
# ============================================================================


@router.post("/phantom/verify")
async def phantom_wallet_verify(
    verify_request: PhantomVerifyRequest,
    response: Response,
    db: DbSession,
):
    """Verify Phantom wallet signature and create/login user."""
    settings = get_settings_service().auth_settings
    
    wallet_address = verify_request.publicKey
    signature = verify_request.signature
    message = verify_request.message
    
    # Create username from wallet address
    username = f"phantom_{wallet_address[:8]}_{wallet_address[-4:]}"
    
    # Try to find existing user
    user = await get_user_by_username(db, username)
    
    if not user:
        # Create new user with Phantom wallet
        new_user = User(
            username=username,
            password=get_password_hash(secrets.token_urlsafe(32)),
            is_active=True,
            oauth_provider="phantom",
            oauth_id=wallet_address,
            wallet_address=wallet_address,
        )
        try:
            db.add(new_user)
            await db.flush()
            await db.refresh(new_user)
            
            # Create default folder
            await get_or_create_default_folder(db, new_user.id)
            await db.commit()
            user = new_user
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user",
            ) from e
    else:
        # Update wallet address if changed
        if user.wallet_address != wallet_address:
            user.wallet_address = wallet_address
            await db.commit()
    
    # Generate JWT tokens
    user_tokens = await create_user_tokens(user_id=user.id, db=db, update_last_login=True)
    
    # Set refresh token cookie with proper settings for localhost
    response.set_cookie(
        "refresh_token_lf",
        user_tokens["refresh_token"],
        httponly=True,  # Prevent JavaScript access for security
        samesite="lax",  # Allow cookie to be sent with requests
        secure=False,  # False for http://127.0.0.1 (use True for HTTPS)
        max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        path="/",  # Make cookie available for all paths
    )
    
    # Set access token cookie (httponly=False so JavaScript can read it)
    response.set_cookie(
        "access_token_lf",
        user_tokens["access_token"],
        httponly=False,  # Allow JavaScript to read for Authorization headers
        samesite="lax",
        secure=False,
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        path="/",
    )
    
    # Return tokens
    return Token(
        access_token=user_tokens["access_token"],
        refresh_token=user_tokens["refresh_token"],
        token_type="bearer",
    )


@router.get("/phantom/message")
async def phantom_get_message():
    """Generate a message for Phantom wallet to sign."""
    nonce = secrets.token_urlsafe(16)
    message = f"Sign this message to authenticate with Langflow.\n\nNonce: {nonce}"
    
    return {
        "message": message,
        "nonce": nonce,
    }
