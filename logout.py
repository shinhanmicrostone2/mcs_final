from flask import Flask, request, jsonify
import jwt
import os
from flask import Blueprint
from datetime import datetime
from db_connection import get_db

# 블랙리스트 (로그아웃된 토큰들을 저장)
blacklist = set()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "shinhanmicrostone")

bp_logout = Blueprint("logout", __name__)



@bp_logout.route("/logout", methods=["POST"])
def logout():
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"message": "토큰이 필요합니다"}), 400

    if token in blacklist:
        return jsonify({"message": "이미 로그아웃된 토큰입니다"}), 400

    try:
        jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "이미 만료된 토큰입니다"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다"}), 400

    # 블랙리스트에 추가
    blacklist.add(token)
    
    # 쿠키 삭제
    response = jsonify({"message": "로그아웃 완료"})
    response.set_cookie('token', '', expires=0)
    return response, 200



# 인증 필요할 때 블랙리스트 확인 예시
def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "토큰이 필요합니다"}), 401
        if token in blacklist:
            return jsonify({"message": "로그아웃된 토큰입니다"}), 401
        try:
            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except:
            return jsonify({"message": "유효하지 않은 토큰"}), 401
        return f(*args, **kwargs)
    return decorated
