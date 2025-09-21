"""
주의: 아래 파일들은 '수정 금지(Do Not Modify)'입니다:
  - ai_models/criminal_qa_model.py  (형사법 LLM 핵심)
  - chatgpt_api.py                  (ChatGPT 보강 로직)

허용 변경 범위:
  - 라우팅 추가/변경, 보안 설정, 로깅, CORS, 템플릿/정적 파일 서빙 등 웹 서버 부분
  - 단, AI 호출 인터페이스(메서드 시그니처) 변경 금지
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import signup
# [수정 금지] 라우팅은 블루프린트로 관리. AI 호출 로직은 블루프린트 내부 참조
from routing.base import bp_base
from routing.chat import bp_chat
from routing.chatroom import bp_chatroom
from db_connection import get_db
from signup import bp_signup
from login import bp_login
from routing.documents import bp_documents
from logout import bp_logout
from delete_account import bp_delete
load_dotenv()  # .env 파일 자동 로드

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.register_blueprint(bp_base)
app.register_blueprint(bp_chat)
app.register_blueprint(bp_chatroom)
app.register_blueprint(bp_signup)
app.register_blueprint(bp_login)
app.register_blueprint(bp_documents)
app.register_blueprint(bp_logout)
app.register_blueprint(bp_delete)




"""
라우팅 구성
- /                    : index.html 서빙 (routing/base)
- /health              : 헬스체크 (routing/base)
- /api/chat            : 채팅 처리 (routing/chat)
- /api/chatrooms       : 채팅방 관리 (routing/chatroom)
- /signup              : 회원가입 (signup)
"""



if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    
     # 서버 시작 전 DB 연결 테스트
    try:
        db = get_db()
        print("DB 연결 성공")
        db.close()
    except Exception as e:
        print("DB 연결 실패:", e)

    # 모델 로딩 시도 (실패해도 서버는 시작)
    try:
        from runtime import preload_model_if_configured
        preload_model_if_configured()
    except Exception as e:
        print(f"모델 로딩 실패 (서버는 정상 시작): {e}")
    
    print(f"Flask 서버 시작: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)