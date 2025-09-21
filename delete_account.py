from flask import Blueprint, request, jsonify
import jwt
from db_connection import get_db
from datetime import datetime
from functools import wraps

# 블랙리스트 (로그아웃된 토큰들을 저장)
blacklist = set()


import os
SECRET_KEY = os.getenv("SECRET_KEY", "shinhanmicrostone")
bp_delete = Blueprint("delete", __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"message": "토큰이 필요합니다"}), 401
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"message": "유효하지 않은 토큰 형식입니다"}), 401

        if token in blacklist:
            return jsonify({"message": "유효하지 않은 토큰입니다"}), 401
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "토큰이 만료되었습니다"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "유효하지 않은 토큰입니다"}), 401
        return f(decoded, *args, **kwargs)
    return decorated



@bp_delete.route("/delete", methods=["DELETE"])
@token_required
def withdraw(decoded_token):
    email = decoded_token["email"]

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM user WHERE email=%s", (email,))
        db.commit()

        # 탈퇴 후 토큰 블랙리스트에 실제 토큰만 추가
        token_header = request.headers.get("Authorization")
        token = None
        if token_header:
            try:
                token = token_header.split(" ")[1]
            except IndexError:
                pass
        if token:
            blacklist.add(token)

        return jsonify({"message": "회원 탈퇴가 완료되었습니다"}), 200
    finally:
        cursor.close()
        db.close()
