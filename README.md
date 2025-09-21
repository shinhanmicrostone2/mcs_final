# 🏛️ AI Law Assistant - 형사법 AI 챗봇

> **형사법 전문 AI 어시스턴트** - 형사법 LLM + ChatGPT 보강을 통한 지능형 법률 상담 서비스

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 프로젝트 개요

AI Law Assistant는 형사법 전문 LLM과 ChatGPT를 결합한 지능형 법률 상담 서비스입니다. 사용자의 형사법 관련 질문에 대해 전문적이고 정확한 답변을 제공하며, 채팅 기록을 데이터베이스에 저장하여 지속적인 대화를 지원합니다.

### 🎯 주요 기능

- **🔐 사용자 인증**: JWT 기반 로그인/로그아웃 시스템
- **💬 실시간 채팅**: 형사법 전문 AI와의 대화형 상담
- **🧠 이중 AI 시스템**: 형사법 LLM + ChatGPT 보강 파이프라인
- **💾 데이터 영속성**: 채팅방 및 메시지 데이터베이스 저장
- **📱 반응형 UI**: 모바일/데스크톱 최적화된 인터페이스
- **🔍 법률 링크**: 질문 기반 관련 법률 조문 추천

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Models     │
│   (HTML/CSS/JS) │◄──►│   (Flask)       │◄──►│   (LLM+ChatGPT) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (MySQL)       │
                       └─────────────────┘
```

### 🔄 AI 파이프라인

1. **형사법 LLM 1차 응답** - 전문 형사법 모델이 초기 답변 생성
2. **품질 판정** - 답변의 완성도 및 정확성 평가
3. **ChatGPT 보강** - 필요시 ChatGPT로 답변 개선 및 보완
4. **최종 응답** - 사용자에게 최적화된 답변 제공

## 🚀 설치 및 실행

### 📋 사전 요구사항

- Python 3.8+
- MySQL 8.0+
- CUDA 지원 GPU (선택사항, CPU도 지원)

### 🔧 설치 과정

1. **저장소 클론**
```bash
git clone https://github.com/your-username/ai-law-assistant.git
cd ai-law-assistant
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경변수 설정**
```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일에 다음 내용 추가:
```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# JWT 설정
SECRET_KEY=your_secret_key_here

# Flask 설정
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
FLASK_DEBUG=1
```

5. **데이터베이스 설정**
```sql
-- MySQL에서 데이터베이스 생성
CREATE DATABASE micro;
USE micro;

-- 사용자 테이블
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 채팅방 테이블
CREATE TABLE chatroom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- 채팅 메시지 테이블
CREATE TABLE chatmessage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    chat_room_id INT NOT NULL,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (chat_room_id) REFERENCES chatroom(id) ON DELETE CASCADE
);
```

6. **애플리케이션 실행**
```bash
python app.py
```

7. **브라우저에서 접속**
```
http://127.0.0.1:5000
```

## 📁 프로젝트 구조

```
ai-law-assistant/
├── 📁 ai_models/                 # AI 모델 관련
│   ├── criminal_qa_model.py     # 형사법 LLM 핵심 로직
│   ├── chatgpt_api.py           # ChatGPT API 연동
│   └── criminal-qa-best/        # LoRA 어댑터 모델
├── 📁 routing/                   # Flask 라우팅
│   ├── base.py                  # 기본 라우트
│   ├── chat.py                  # 채팅 API
│   ├── chatroom.py              # 채팅방 관리
│   └── documents.py             # 문서 관리
├── 📁 static/                    # 정적 파일
│   ├── app.js                   # 메인 프론트엔드 로직
│   ├── login.js                 # 로그인 로직
│   ├── signup.js                # 회원가입 로직
│   └── styles.css               # 스타일시트
├── 📁 templates/                 # HTML 템플릿
│   ├── index.html               # 메인 페이지
│   ├── login.html               # 로그인 페이지
│   └── signup.html              # 회원가입 페이지
├── app.py                       # Flask 메인 애플리케이션
├── db_connection.py             # 데이터베이스 연결
├── login.py                     # 로그인 로직
├── logout.py                    # 로그아웃 로직
├── signup.py                    # 회원가입 로직
├── runtime.py                   # 런타임 설정
└── requirements.txt             # Python 의존성
```

## 🔧 주요 기술 스택

### Backend
- **Flask 3.1+** - 웹 프레임워크
- **PyMySQL** - MySQL 데이터베이스 연결
- **PyJWT** - JWT 토큰 인증
- **python-dotenv** - 환경변수 관리

### Frontend
- **Vanilla JavaScript** - 클라이언트 사이드 로직
- **CSS3** - 반응형 스타일링
- **HTML5** - 시맨틱 마크업

### AI/ML
- **Transformers** - Hugging Face 모델 로딩
- **PyTorch** - 딥러닝 프레임워크
- **OpenAI API** - ChatGPT 연동
- **LoRA** - 효율적인 모델 파인튜닝

### Database
- **MySQL 8.0+** - 관계형 데이터베이스

## 🎮 사용법

### 1. 회원가입
- 이메일, 이름, 비밀번호 입력
- 이메일 중복 검사 및 비밀번호 유효성 검사

### 2. 로그인
- 등록된 이메일과 비밀번호로 로그인
- JWT 토큰 기반 세션 관리

### 3. 채팅 상담
- "새 대화" 버튼으로 새로운 채팅방 생성
- 형사법 관련 질문 입력
- AI가 전문적인 답변 제공

### 4. 채팅 기록 관리
- 이전 채팅방 목록 확인
- 채팅 내용 데이터베이스 저장
- 새로고침 후에도 대화 기록 유지

## 🔒 보안 기능

- **JWT 토큰 인증** - 안전한 사용자 세션 관리
- **비밀번호 해싱** - Werkzeug 보안 해싱
- **SQL 인젝션 방지** - 파라미터화된 쿼리 사용
- **CORS 설정** - 크로스 오리진 요청 제어

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

- **Hugging Face** - Transformers 라이브러리
- **OpenAI** - ChatGPT API
- **Flask Community** - 웹 프레임워크
- **MySQL** - 데이터베이스 시스템

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요! ⭐**

Made with ❤️ by [Your Team Name]

</div>
