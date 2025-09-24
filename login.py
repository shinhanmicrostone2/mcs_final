from flask import Flask, request, jsonify, render_template
from werkzeug.security import check_password_hash
import jwt
import datetime
import os
from flask import Blueprint
from db_connection import get_db  # 기존 DB 연결 함수 사용

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "shinhanmicrostone")  # JWT 서명용 비밀키

bp_login = Blueprint("login", __name__)

@bp_login.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@bp_login.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    print(f"로그인 시도: email={email}, password={password}")

    if not email:
        return jsonify({"message": "이메일을 입력해주세요"}), 400
    
    if not password:
        return jsonify({"message": "비밀번호를 입력해주세요"}), 400


    db = get_db()
    cursor = db.cursor()

    try:
        # DB에서 이메일 검색
        cursor.execute("SELECT id, password FROM user WHERE email=%s", (email,))
        row = cursor.fetchone()
        print(f"DB 조회 결과: {row}")
        
        if not row:
            print("사용자를 찾을 수 없음")
            return jsonify({"message": "이메일 또는 비밀번호가 잘못되었습니다"}), 401

        stored_password = row["password"]
        print(f"저장된 비밀번호 해시: {stored_password[:50]}...")

        # 비밀번호 체크
        password_check = check_password_hash(stored_password, password)
        print(f"비밀번호 체크 결과: {password_check}")
        
        if not password_check:
            print("비밀번호 불일치")
            return jsonify({"message": "이메일 또는 비밀번호가 잘못되었습니다"}), 401

        # JWT 생성
        token = jwt.encode(
            {
                "user_id": row["id"],
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1시간 유효
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        response = jsonify({"token": token})
        response.set_cookie('token', token, httponly=True, secure=False, samesite='Lax')
        return response, 200

    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    app.run(debug=True)
