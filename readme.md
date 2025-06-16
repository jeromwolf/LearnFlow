# 🌊 LearnFlow

> **모두가 사랑하는 일을 하며 살 수 있도록 - 자연스러운 학습의 흐름**

LearnFlow는 사용자 친화적인 온라인 학습 플랫폼입니다. 복잡하지 않은 간단명료한 인터페이스로 누구나 쉽게 배우고 가르칠 수 있는 학습 생태계를 구축합니다.

![LearnFlow Banner](https://via.placeholder.com/800x200/4F46E5/FFFFFF?text=LearnFlow+-+Learn+Naturally)

## 📋 **프로젝트 개요**

### **🎯 비전**
"누구나 쉽게 배우고 가르칠 수 있는 온라인 학습 생태계 구축"

### **✨ 핵심 가치**
- **Simple**: 직관적이고 간단한 사용자 경험
- **Practical**: 실무에 바로 적용 가능한 실용적 교육
- **Accessible**: 언제 어디서나 학습 가능한 플랫폼
- **Community**: 학습자와 강사가 함께 성장하는 커뮤니티

### **🚀 차별화 포인트**
- Class101 대비 더 간소화된 UI/UX
- 실무형 교육에 특화된 커리큘럼
- 합리적인 가격 정책
- 빠른 로딩과 안정적인 비디오 스트리밍

## 🛠 **기술 스택**

### **Frontend**
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query + Zustand
- **UI Components**: Shadcn/ui
- **Video Player**: Video.js

### **Backend**
- **Framework**: FastAPI (Python)
- **Database & Auth**: Supabase (PostgreSQL + Auth)
- **ORM**: SQLAlchemy 2.0 + Alembic (데이터베이스 마이그레이션)
- **Storage**: Supabase Storage
- **API**: Supabase Realtime API
- **Authentication**: Supabase Auth (Email, Social Login)
- **API Documentation**: Swagger UI

### **Infrastructure**
- **Frontend Deployment**: Vercel
- **Backend Deployment**: Railway
- **Database Hosting**: Supabase
- **CDN**: Supabase Edge Network
- **Monitoring**: Supabase Dashboard
- **Server Costs**: Initial Free Plan (Upgrade to Paid Plan as Growth)

## 🚀 **개발 환경 설정**

### **필수 도구**
- Python 3.9+
- Node.js 18+
- Git
- PostgreSQL (로컬 개발용, 또는 Supabase 사용)

### **백엔드 설정**

1. 저장소 클론:
   ```bash
   git clone https://github.com/yourusername/learnflow.git
   cd learnflow
   ```

2. Python 가상 환경 생성 및 활성화:
   ```bash
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수 설정 (`.env` 파일 생성):
   ```env
   # Supabase 설정
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   
   # 데이터베이스 연결 (Supabase 또는 로컬)
   DATABASE_URL=postgresql://postgres:your_password@your_supabase_url:5432/postgres
   
   # 기타 설정
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

5. 데이터베이스 마이그레이션 적용:
   ```bash
   cd src/backend
   alembic upgrade head
   ```

6. 개발 서버 실행:
   ```bash
   uvicorn main:app --reload
   ```

### **프론트엔드 설정**

1. 의존성 설치:
   ```bash
   cd frontend
   npm install
   ```

2. 환경 변수 설정 (`.env.local` 파일 생성):
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

3. 개발 서버 실행:
   ```bash
   npm run dev
   ```

## 📊 **데이터베이스 마이그레이션**

Alembic을 사용하여 데이터베이스 스키마를 관리합니다.

### **새 마이그레이션 생성**
```bash
alembic revision --autogenerate -m "설명을_여기에_작성"
```

### **마이그레이션 적용**
```bash
alembic upgrade head
```

### **마이그레이션 되돌리기**
```bash
alembic downgrade -1
```

### **마이그레이션 히스토리 확인**
```bash
alembic history
```

### **현재 마이그레이션 상태 확인**
```bash
alembic current
```

## 📁 **프로젝트 구조**

```
learnflow/
├── src/
│   ├── frontend/         # Next.js Frontend
│   │   ├── app/          # App Router Pages
│   │   ├── components/   # React Components
│   │   ├── lib/         # Utilities & API Client
│   │   ├── hooks/       # Custom Hooks
│   │   └── types/       # TypeScript Types
│   ├── backend/         # FastAPI Backend
│   │   ├── models/     # SQLAlchemy Models
│   │   ├── schemas/    # Pydantic Schemas
│   │   ├── api/       # API Routes
│   │   ├── core/      # Core Utilities
│   │   └── utils/     # Helper Functions
├── infra/                # Infrastructure as Code
│   └── main.tf          # Terraform Configuration
├── docs/                # Documentation
│   ├── PRD.md          # Product Requirements Document
│   ├── API.md          # API Documentation
│   └── DEPLOYMENT.md   # Deployment Guide
└── README.md           # This file
```

## 🚀 **빠른 시작**

### **사전 요구사항**
- Node.js 18.x 이상
- Python 3.11 이상
- Supabase 계정
- PostgreSQL 14 (Supabase)

### **1. 저장소 클론**
```bash
git clone https://github.com/your-username/learnflow.git
cd learnflow
```

### **2. Backend 설정**
```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어 데이터베이스 및 AWS 설정 입력

# 데이터베이스 마이그레이션
python -m alembic upgrade head

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend 설정**
```bash
cd frontend

# Supabase 설정
# Supabase 대시보드에서 프로젝트 생성 후 .env 파일에 설정 추가
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# 환경변수 설정
cp .env.local.example .env.local
# .env.local 파일을 열어 API URL 설정

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### **4. 접속 확인**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 📱 **주요 기능**

### **🎓 학습자 기능**
- [x] 회원가입 / 로그인
- [x] 강의 탐색 및 검색
- [x] 강의 상세 정보 조회
- [x] 수강 신청 및 결제
- [x] 나의 강의실
- [x] 학습 진도 추적
- [x] 비디오 학습 (이어보기, 배속 조절)
- [x] 댓글 및 Q&A

### **👨‍🏫 강사 기능**
- [x] 강사 등록
- [x] 강의 생성 및 관리
- [x] 영상 업로드
- [x] 커리큘럼 구성
- [x] 학생 관리
- [x] 수익 현황 조회

### **🛡 관리자 기능**
- [x] 사용자 관리
- [x] 강의 승인/거부
- [x] 플랫폼 통계 조회
- [x] 신고 처리

## 🎨 **UI/UX 미리보기**

| 화면 | 설명 |
|------|------|
| ![메인 페이지](https://via.placeholder.com/300x200/E5E7EB/374151?text=Main+Page) | 깔끔한 메인 페이지 |
| ![강의 목록](https://via.placeholder.com/300x200/EEF2FF/4F46E5?text=Course+List) | 직관적인 강의 목록 |
| ![학습 화면](https://via.placeholder.com/300x200/F0FDF4/16A34A?text=Learning+Page) | 몰입도 높은 학습 화면 |
| ![대시보드](https://via.placeholder.com/300x200/FEF3C7/D97706?text=Dashboard) | 한눈에 보는 대시보드 |

## 📊 **개발 현황**

### **MVP 개발 일정 (8주)**
- [x] **Week 1-2**: 기본 인증 및 강의 CRUD ✅
- [x] **Week 3-4**: Frontend 기본 기능 ✅  
- [ ] **Week 5-6**: 비디오 플레이어 및 학습 기능 🚧
- [ ] **Week 7**: 결제 및 관리자 기능 📋
- [ ] **Week 8**: 배포 및 테스트 📋

### **현재 진행률**
```
전체 진행률: ████████████░░░░░░░░░░░░ 50%

Backend API:    ████████████████░░░░ 80%
Frontend UI:    ████████████░░░░░░░░ 60%
Integration:    ████████░░░░░░░░░░░░ 40%
Testing:        ████░░░░░░░░░░░░░░░░ 20%
```

## 🧪 **테스트**

### **Backend 테스트**
```bash
cd backend
pytest tests/ -v
```

### **Frontend 테스트**
```bash
cd frontend
npm run test
```

### **E2E 테스트**
```bash
cd frontend
npm run e2e
```

## 📚 **API 문서**

### **주요 엔드포인트**

#### **인증**
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/me` - 내 정보 조회

#### **강의**
- `GET /api/courses` - 강의 목록 조회
- `GET /api/courses/{id}` - 강의 상세 조회
- `POST /api/courses` - 강의 생성 (강사용)
- `PUT /api/courses/{id}` - 강의 수정 (강사용)

#### **수강**
- `POST /api/enrollments` - 수강 신청
- `GET /api/enrollments/my-courses` - 나의 강의 목록
- `GET /api/enrollments/{course_id}/progress` - 학습 진도 조회

자세한 API 문서는 [여기](http://localhost:8000/docs)에서 확인할 수 있습니다.

## 🚀 **배포**

### **Production 배포**
```bash
# Frontend (Vercel)
npm run build
vercel --prod

# Backend (AWS EC2)
docker build -t learnflow-api .
docker run -p 8000:8000 learnflow-api
```

### **환경별 설정**
- **Development**: 로컬 개발 환경
- **Staging**: 테스트 서버 (테스트용)
- **Production**: 운영 서버 (실제 서비스)

## 🤝 **기여하기**

### **기여 방법**
1. 이 저장소를 Fork 합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push 합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

### **코딩 컨벤션**
- **Python**: PEP 8 (Black 포맷터 사용)
- **TypeScript**: ESLint + Prettier 설정 준수
- **Commit**: Conventional Commits 형식 사용

### **브랜치 전략**
- `main`: 운영 환경 배포용
- `develop`: 개발 환경 통합
- `feature/*`: 새로운 기능 개발
- `hotfix/*`: 긴급 버그 수정

## 📄 **라이선스**

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 📞 **연락처**

- **이메일**: team@learnflow.com
- **GitHub**: https://github.com/your-username/learnflow
- **홈페이지**: https://learnflow.com (예정)

## 🙏 **감사의 말**

- [Class101](https://class101.net) - 영감을 주신 훌륭한 서비스
- [Next.js](https://nextjs.org) - 강력한 React 프레임워크
- [FastAPI](https://fastapi.tiangolo.com) - 현대적인 Python API 프레임워크
- [Tailwind CSS](https://tailwindcss.com) - 유틸리티 우선 CSS 프레임워크

---

**LearnFlow** - 자연스러운 학습의 흐름 🌊

Made with ❤️ by LearnFlow Team