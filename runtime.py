"""
AI 런타임 유틸
- 전역 모델 핸들(get_model)
- 사전 로딩(preload_model_if_configured)

[수정 금지] CriminalQAModel의 인터페이스나 호출 순서를 변경하지 마세요.
"""

import os

_model = None
_model_available = False

def get_model():
    """지연 로딩 방식으로 전역 모델 핸들을 반환합니다."""
    global _model, _model_available
    
    if _model is None:
        try:
            from ai_models.criminal_qa_model import CriminalQAModel
            _model = CriminalQAModel()
            _model_available = True
        except ImportError:
            print("AI 모델을 찾을 수 없습니다. ai_models 디렉토리가 없거나 모델 파일이 누락되었습니다.")
            _model_available = False
            return None
        except Exception as e:
            print(f"AI 모델 로딩 중 오류 발생: {e}")
            _model_available = False
            return None
    
    return _model

def is_model_available():
    """AI 모델이 사용 가능한지 확인합니다."""
    global _model_available
    if _model is None:
        get_model()
    return _model_available

def preload_model_if_configured(logger=None) -> None:
    """서버 시작 시 모델을 미리 로딩(옵션)합니다.

    - PRELOAD_MODEL 환경변수 = '1' (기본) → 사전 로딩
    - 디버그 모드(reloader)에서는 자식 프로세스에서만 로딩
    """
    try:
        should_preload = os.getenv("PRELOAD_MODEL", "1") == "1"
        if not should_preload:
            return

        debug = os.getenv("FLASK_DEBUG", "1") == "1"
        is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

        if (not debug) or is_reloader_child:
            model = get_model()
            if model and logger:
                logger.info("AI 모델 사전 로딩 완료")
            elif not model and logger:
                logger.info("AI 모델 없이 서버 시작")
    except Exception as e:
        if logger:
            logger.warning(f"AI 모델 사전 로딩 실패: {e}")
        print(f"AI 모델 사전 로딩 실패: {e}")

