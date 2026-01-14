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
    
    # Generate and store state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    
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
    
    # Verify state to prevent CSRF attacks
    stored_state = request.session.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter. Possible CSRF attack.",
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
    
    # Set refresh token cookie
    response.set_cookie(
        "refresh_token_lf",
        user_tokens["refresh_token"],
        httponly=settings.REFRESH_HTTPONLY,
        samesite=settings.REFRESH_SAME_SITE,
        secure=settings.REFRESH_SECURE,
        expires=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        domain=settings.COOKIE_DOMAIN,
    )
    
    # Redirect to frontend with access token
    frontend_url = f"http://127.0.0.1:7860/?access_token={user_tokens['access_token']}"
    return RedirectResponse(url=frontend_url)


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
    
    # Set refresh token cookie
    response.set_cookie(
        "refresh_token_lf",
        user_tokens["refresh_token"],
        httponly=settings.REFRESH_HTTPONLY,
        samesite=settings.REFRESH_SAME_SITE,
        secure=settings.REFRESH_SECURE,
        expires=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        domain=settings.COOKIE_DOMAIN,
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
