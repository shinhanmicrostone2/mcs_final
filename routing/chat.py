"""
채팅 관련 라우팅 블루프린트

파이프라인:
  1) 형사법 LLM 1차 응답 (CriminalQAModel.generate_answer)
  2) 품질 판정 (is_weak)
  3) 필요 시 ChatGPT 보강 (refine_with_chatgpt)

[수정 금지] 위 3단계의 호출 순서/인터페이스를 변경하지 마세요.
"""

from flask import Blueprint, request, jsonify
from runtime import get_model, is_model_available  # [수정 금지]
from db_connection import get_db

bp_chat = Blueprint("chat", __name__)


@bp_chat.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()
    if not question:
        return jsonify({"error": "message 필드는 필수입니다."}), 400

    # AI 모델 사용 가능 여부 확인
    if not is_model_available():
        return jsonify({
            "answer": "죄송합니다. 현재 AI 모델이 로드되지 않았습니다. ai_models 디렉토리가 있는지 확인해주세요.",
            "refined": False,
            "model_available": False
        })

    # 1) 형사법 LLM 1차 응답 — [수정 금지]
    model = get_model()
    if model is None:
        return jsonify({
            "answer": "AI 모델을 초기화할 수 없습니다.",
            "refined": False,
            "model_available": False
        })
    
    law_answer = model.generate_answer(question)

    # 2) 품질 점검 + 필요 시 보강 — [수정 금지]
    final_answer = law_answer
    refined = False
    try:
        from ai_models.chatgpt_api import is_weak, refine_with_chatgpt
        if is_weak(law_answer):
            final_answer = refine_with_chatgpt(question, law_answer)
            refined = True
    except ImportError:
        # ChatGPT API가 없으면 원본 답변 사용
        final_answer = law_answer
    except Exception:
        final_answer = law_answer

    return jsonify({
        "answer": final_answer,
        "refined": refined,
        "model_available": True
    })


@bp_chat.post("/chat/message")
def save_chat_message():
    """채팅 메시지를 데이터베이스에 저장"""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    chat_room_id = data.get("chat_room_id")
    question = data.get("question")
    response = data.get("response")

    if not all([user_id, chat_room_id, question, response]):
        return jsonify({"error": "필수 필드가 누락되었습니다"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "INSERT INTO ChatMessage (user_id, chat_room_id, question, response) VALUES (%s, %s, %s, %s)",
            (user_id, chat_room_id, question, response)
        )
        db.commit()
        
        return jsonify({
            "message": "채팅 메시지 저장 성공",
            "message_id": cursor.lastrowid
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


@bp_chat.get("/chat/messages/<int:chat_room_id>")
def get_chat_messages(chat_room_id):
    """특정 채팅방의 메시지들을 조회"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "SELECT question, response, created_at FROM ChatMessage WHERE chat_room_id = %s ORDER BY created_at ASC",
            (chat_room_id,)
        )
        messages = cursor.fetchall()
        
        return jsonify(messages), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


