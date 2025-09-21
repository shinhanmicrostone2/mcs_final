"""
기본 라우팅 (index, health)
"""

from flask import Blueprint, jsonify, current_app, send_from_directory, render_template

bp_base = Blueprint("base", __name__)


@bp_base.get("/")
def serve_index():
    # 로그인 페이지로 리다이렉트
    from flask import redirect, url_for
    return redirect(url_for('login.login_page'))


@bp_base.get("/main")
def serve_main():
    # 메인 페이지 (로그인 후 접근)
    return render_template('index.html')

@bp_base.get("/health")
def health():
    return jsonify({"status": "ok"})


