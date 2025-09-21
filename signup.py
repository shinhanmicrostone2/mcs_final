from flask import Flask, request, jsonify, Blueprint, render_template
from werkzeug.security import generate_password_hash
from db_connection import get_db  # db기존 연결함수 활용 

app = Flask(__name__)

bp_signup = Blueprint("signup", __name__)

@bp_signup.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@bp_signup.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"message": "모든 필드를 입력해주세요"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        # 1. 중복 이메일 체크
        cursor.execute("SELECT id FROM user WHERE email=%s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "이미 존재하는 이메일입니다"}), 409

        # 2. 비밀번호 암호화
        hashed_password = generate_password_hash(password)

        # 3. INSERT
        cursor.execute(
            "INSERT INTO user (email, password, name) VALUES (%s, %s, %s)",
            (email, hashed_password, name)
        )
        db.commit()

        return jsonify({"message": "회원가입 완료"}), 201

    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    app.run(debug=True)
