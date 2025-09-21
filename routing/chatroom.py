"""
채팅방 관리 라우팅 블루프린트
- 채팅방 생성, 조회, 수정, 삭제
"""

from flask import Blueprint, request, jsonify
from db_connection import (
    create_chat_room, 
    get_chat_rooms_by_user, 
    get_chat_room_by_id,
    update_chat_room_title,
    delete_chat_room,
    get_user_by_id
)

bp_chatroom = Blueprint("chatroom", __name__)

@bp_chatroom.post("/api/chatrooms")
def create_new_chatroom():
    """새로운 채팅방을 생성합니다."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    title = data.get("title", "새 대화")
    
    if not user_id:
        return jsonify({"error": "user_id는 필수입니다."}), 400
    
    # 사용자 존재 확인
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "존재하지 않는 사용자입니다."}), 404
    
    try:
        room_id = create_chat_room(user_id, title)
        return jsonify({
            "message": "채팅방이 생성되었습니다.",
            "room_id": room_id,
            "title": title
        }), 201
    except Exception as e:
        return jsonify({"error": f"채팅방 생성 실패: {str(e)}"}), 500

@bp_chatroom.get("/api/chatrooms/user/<int:user_id>")
def get_user_chatrooms(user_id):
    """사용자의 모든 채팅방을 가져옵니다."""
    try:
        chatrooms = get_chat_rooms_by_user(user_id)
        return jsonify({
            "chatrooms": chatrooms,
            "count": len(chatrooms)
        }), 200
    except Exception as e:
        return jsonify({"error": f"채팅방 조회 실패: {str(e)}"}), 500

@bp_chatroom.get("/api/chatrooms/<int:room_id>")
def get_chatroom(room_id):
    """특정 채팅방 정보를 가져옵니다."""
    try:
        chatroom = get_chat_room_by_id(room_id)
        if not chatroom:
            return jsonify({"error": "채팅방을 찾을 수 없습니다."}), 404
        
        return jsonify(chatroom), 200
    except Exception as e:
        return jsonify({"error": f"채팅방 조회 실패: {str(e)}"}), 500

@bp_chatroom.put("/api/chatrooms/<int:room_id>")
def update_chatroom(room_id):
    """채팅방 제목을 업데이트합니다."""
    data = request.get_json(silent=True) or {}
    new_title = data.get("title")
    
    if not new_title:
        return jsonify({"error": "title은 필수입니다."}), 400
    
    try:
        success = update_chat_room_title(room_id, new_title)
        if not success:
            return jsonify({"error": "채팅방을 찾을 수 없습니다."}), 404
        
        return jsonify({
            "message": "채팅방 제목이 업데이트되었습니다.",
            "room_id": room_id,
            "title": new_title
        }), 200
    except Exception as e:
        return jsonify({"error": f"채팅방 업데이트 실패: {str(e)}"}), 500

@bp_chatroom.delete("/api/chatrooms/<int:room_id>")
def delete_chatroom(room_id):
    """채팅방을 삭제합니다."""
    try:
        success = delete_chat_room(room_id)
        if not success:
            return jsonify({"error": "채팅방을 찾을 수 없습니다."}), 404
        
        return jsonify({
            "message": "채팅방이 삭제되었습니다.",
            "room_id": room_id
        }), 200
    except Exception as e:
        return jsonify({"error": f"채팅방 삭제 실패: {str(e)}"}), 500
