"""
기본 라우팅 (index, health)
"""

from flask import Blueprint, jsonify, current_app, send_from_directory, render_template, request, redirect, url_for
from db_connection import verify_jwt_token

bp_base = Blueprint("base", __name__)


@bp_base.get("/")
def serve_index():
    # 로그인 페이지로 리다이렉트
    return redirect(url_for('login.login_page'))


@bp_base.get("/main")
def serve_main():
    # JWT 토큰 검증
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login.login_page'))
    
    user = verify_jwt_token(token)
    if not user:
        return redirect(url_for('login.login_page'))
    
    # 메인 페이지 (로그인 후 접근) - 사용자 정보 전달
    return render_template('index.html', user=user)

@bp_base.get("/health")
def health():
    return jsonify({"status": "ok"})


