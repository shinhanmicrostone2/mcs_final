from flask import Blueprint, request, jsonify
from db_connection import get_db
#AI가 생성한 법률 문서(고소장, 진술서)를 DB에 저장하는 기능 수정중
bp_documents = Blueprint("documents", __name__, url_prefix="/documents")

@bp_documents.route("/", methods=["POST"])
def create_document():
    data = request.get_json()
    user_id = data.get("user_id")
    document_type = data.get("document_type")
    input_facts = data.get("input_facts")
    document_text = data.get("document_text")

    if not user_id or not document_type or not input_facts or not document_text:
        return jsonify({"error": "필수 입력값 누락"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        sql = """
        INSERT INTO GeneratedDocument (user_id, document_type, input_facts, document_text)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, document_type, input_facts, document_text))
        conn.commit()
        return jsonify({"message": "문서 생성 성공", "document_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
