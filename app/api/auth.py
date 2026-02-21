from flask import Blueprint, redirect, request, jsonify, url_for, session, current_app
from app.db.db import supabase
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    """Initiates Google OAuth login"""
    try:
        # Use APP_BASE_URL env var so this works on Vercel (behind a proxy).
        # Falls back to url_for for local development.
        base_url = os.environ.get('APP_BASE_URL', '').rstrip('/')
        if base_url:
            redirect_url = f"{base_url}/auth/callback"
        else:
            redirect_url = url_for('auth.callback', _external=True)
        # supabase.auth.sign_in_with_oauth returns an object containing the provider URL
        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        if res.url:
            return redirect(res.url)
        return jsonify({"error": "Failed to generate login URL"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/callback')
def callback():
    """Handles OAuth callback"""
    # The code is passed in query parameters for PKCE flow
    code = request.args.get('code')
    if code:
        try:
            res = supabase.auth.exchange_code_for_session({
                "auth_code": code
            })
            # res.session contains metadata
            session['access_token'] = res.session.access_token
            session['refresh_token'] = res.session.refresh_token
            session['user_email'] = res.user.email
            
            # Redirect to home page
            return redirect('/')
        except Exception as e:
            return jsonify({"error": f"Auth failed: {str(e)}"}), 400
    
    # Fallback/Error if no code
    return jsonify({"error": "No code provided. Ensure PKCE flow is enabled in Supabase."}), 400

@auth_bp.route('/me')
def me():
    """Returns current user info"""
    if 'access_token' not in session:
        return jsonify({"authenticated": False}), 200
        
    try:
        # Verify token
        user_response = supabase.auth.get_user(session['access_token'])
        return jsonify({
            "authenticated": True,
            "user": {
                "email": user_response.user.email,
                "id": user_response.user.id
            }
        }), 200
    except Exception as e:
        # Token might be expired
        session.clear()
        return jsonify({"authenticated": False, "error": str(e)}), 401

@auth_bp.route('/logout')
def logout():
    """Clears session"""
    if 'access_token' in session:
        try:
            supabase.auth.sign_out({"scope": "global", "token": session['access_token']})
        except:
            pass
    session.clear()
    return redirect(url_for('index'))
