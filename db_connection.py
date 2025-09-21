import pymysql  
from datetime import datetime

def get_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        database='micro',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

# ChatRoom 관련 CRUD 함수들
def create_chat_room(user_id, title):
    """새로운 채팅방을 생성합니다."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO ChatRoom (user_id, title) VALUES (%s, %s)",
            (user_id, title)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_chat_rooms_by_user(user_id):
    """사용자의 모든 채팅방을 가져옵니다."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM ChatRoom WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_chat_room_by_id(room_id):
    """특정 채팅방 정보를 가져옵니다."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM ChatRoom WHERE id = %s",
            (room_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def update_chat_room_title(room_id, new_title):
    """채팅방 제목을 업데이트합니다."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE ChatRoom SET title = %s WHERE id = %s",
            (new_title, room_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def delete_chat_room(room_id):
    """채팅방을 삭제합니다 (CASCADE로 관련 메시지도 함께 삭제됨)."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM ChatRoom WHERE id = %s",
            (room_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    """사용자 정보를 가져옵니다."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, email, name FROM User WHERE id = %s",
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()