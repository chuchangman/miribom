# 미리봄 AWS 프리티어 배포 가이드

이 문서는 AWS 프리티어 기준으로 EC2 한 대에 프론트엔드, 백엔드, AI 서버를 모두 올리고, DB만 RDS로 분리하는 배포 방법입니다.

## 배포 구조

```text
EC2 t3.micro 1대
- Nginx
- Vue 프론트엔드 dist 정적 파일
- Django 백엔드, gunicorn, 127.0.0.1:8000
- FastAPI AI 서버, uvicorn, 127.0.0.1:8001

RDS
- PostgreSQL

Cloudflare R2
- 영상, 썸네일 파일 저장
```

접속 경로는 한 도메인에서 나눕니다.

```text
https://your-domain.com/
-> 프론트엔드

https://your-domain.com/api/
-> Django 백엔드

https://your-domain.com/ai/
-> FastAPI AI 서버
```

## 1. AWS에서 먼저 만들 것

EC2:
Ubuntu, `t3.micro`로 생성합니다.

RDS:
PostgreSQL, Single-AZ, `db.t3.micro` 또는 `db.t4g.micro`, 스토리지 20GB 이하로 생성합니다.

보안 그룹:
EC2는 `80`, `443`, `22` 포트를 엽니다. 가능하면 SSH `22`는 본인 IP만 허용하세요.

RDS는 `5432` 포트를 열되, EC2 보안 그룹에서만 접근 가능하게 설정하세요.

과금 방지:
AWS Budgets에서 1달러, 5달러 알림을 꼭 설정하세요.

## 2. EC2 접속 후 기본 패키지 설치

```bash
sudo apt update
sudo apt install -y git nginx python3-venv python3-pip nodejs npm
sudo mkdir -p /opt/miribom
sudo chown -R ubuntu:www-data /opt/miribom
```

## 3. 프로젝트 배치

EC2의 `/opt/miribom` 위치에 프로젝트를 둡니다.

```bash
cd /opt/miribom
git clone <깃허브-레포-url> .
```

이미 파일을 직접 옮겼다면 `/opt/miribom` 아래에 `frontend`, `backend`, `AI`, `deploy` 폴더가 있어야 합니다.

## 4. 환경변수 파일 만들기

예시 파일을 복사합니다.

```bash
cp deploy/env/backend.env.example backend/.env
cp deploy/env/ai.env.example AI/.env
cp deploy/env/frontend.env.production.example frontend/.env.production
```

이제 값을 실제 배포 값으로 수정합니다.

```bash
nano backend/.env
nano AI/.env
nano frontend/.env.production
```

`backend/.env`에서 반드시 바꿔야 하는 값:

```env
DEBUG=False
DJANGO_SECRET_KEY=긴_랜덤_문자열
ALLOWED_HOSTS=your-domain.com,EC2_PUBLIC_IP
FRONTEND_URL=https://your-domain.com
BACKEND_PUBLIC_URL=https://your-domain.com
COOKIE_SECURE=True
CORS_ALLOWED_ORIGINS=https://your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

DB_NAME=RDS_DB_NAME
DB_USER=RDS_USER
DB_PASSWORD=RDS_PASSWORD
DB_HOST=RDS_ENDPOINT
DB_PORT=5432
```

도메인이 아직 없고 EC2 IP로만 테스트한다면 임시로 이렇게 둘 수 있습니다.

```env
FRONTEND_URL=http://EC2_PUBLIC_IP
BACKEND_PUBLIC_URL=http://EC2_PUBLIC_IP
COOKIE_SECURE=False
CORS_ALLOWED_ORIGINS=http://EC2_PUBLIC_IP
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

다만 소셜 로그인과 쿠키 인증은 HTTPS 도메인을 붙인 뒤 테스트하는 것이 안전합니다.

`frontend/.env.production` 예시:

```env
VITE_API_BASE_URL=https://your-domain.com/api
VITE_AI_API_URL=https://your-domain.com/ai
```

## 5. 백엔드 설치 및 DB 마이그레이션

```bash
cd /opt/miribom/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

여기서 RDS 연결 오류가 나면 아래를 확인하세요.

```text
backend/.env의 DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
RDS 보안 그룹이 EC2 보안 그룹을 허용하는지
RDS가 public/private 어디에 있는지
```

## 6. AI 서버 설치

```bash
cd /opt/miribom/AI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install torch torchvision
```

AI 모델 파일도 서버에 있어야 합니다.

```text
AI/checkpoints/phase3_18class_service_best.pth
```

파일이 없으면 AI 서버가 시작되지 않습니다.

## 7. 프론트엔드 빌드

```bash
cd /opt/miribom/frontend
npm ci
npm run build
```

성공하면 `frontend/dist` 폴더가 생성됩니다.

## 8. systemd 서비스 등록

Django 백엔드와 AI 서버를 자동 실행 서비스로 등록합니다.

```bash
sudo cp /opt/miribom/deploy/systemd/miribom-backend.service /etc/systemd/system/
sudo cp /opt/miribom/deploy/systemd/miribom-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now miribom-backend
sudo systemctl enable --now miribom-ai
```

상태 확인:

```bash
sudo systemctl status miribom-backend
sudo systemctl status miribom-ai
```

로그 확인:

```bash
sudo journalctl -u miribom-backend -f
sudo journalctl -u miribom-ai -f
```

## 9. Nginx 설정

```bash
sudo cp /opt/miribom/deploy/nginx/miribom.conf /etc/nginx/sites-available/miribom
sudo ln -sf /etc/nginx/sites-available/miribom /etc/nginx/sites-enabled/miribom
sudo nginx -t
sudo systemctl reload nginx
```

브라우저에서 확인합니다.

```text
http://EC2_PUBLIC_IP/
http://EC2_PUBLIC_IP/api/
http://EC2_PUBLIC_IP/ai/health
```

## 10. 도메인과 HTTPS 설정

도메인의 A 레코드를 EC2 public IP로 연결합니다.

이후 EC2에서 인증서를 발급합니다.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

인증서 발급 후에는 `backend/.env`, `frontend/.env.production`을 HTTPS 도메인 기준으로 수정하고 다시 빌드/재시작합니다.

```bash
cd /opt/miribom/frontend
npm run build

sudo systemctl restart miribom-backend
sudo systemctl restart miribom-ai
sudo systemctl reload nginx
```

## 11. 소셜 로그인 설정 변경

각 소셜 로그인 개발자 콘솔에서 callback URL을 배포 주소로 바꿔야 합니다.

```text
https://your-domain.com/api/auth/naver/callback
https://your-domain.com/api/auth/kakao/callback
https://your-domain.com/api/auth/google/callback
```

프론트 주소도 허용 도메인에 추가하세요.

```text
https://your-domain.com
```

## 12. R2 CORS 설정

Cloudflare R2 CORS에 배포 도메인을 허용해야 영상/썸네일 업로드가 됩니다.

허용 origin:

```text
https://your-domain.com
```

허용 method:

```text
GET
PUT
POST
HEAD
```

## 13. 배포 후 체크리스트

아래를 순서대로 확인하세요.

```text
프론트 첫 화면 접속 가능
회원가입 가능
로그인 가능
소셜 로그인 가능
생활환경 입력 가능
제품 검색 가능
후기 영상 업로드 가능
AI 이미지 예측 가능
추천 질문 플로우 가능
추천 결과 표시 가능
영상 재생 가능
```

## 14. 자주 쓰는 명령어

백엔드 재시작:

```bash
sudo systemctl restart miribom-backend
```

AI 재시작:

```bash
sudo systemctl restart miribom-ai
```

Nginx 재시작:

```bash
sudo systemctl reload nginx
```

백엔드 로그:

```bash
sudo journalctl -u miribom-backend -f
```

AI 로그:

```bash
sudo journalctl -u miribom-ai -f
```

프론트 다시 빌드:

```bash
cd /opt/miribom/frontend
npm run build
```

DB 마이그레이션:

```bash
cd /opt/miribom/backend
source venv/bin/activate
python manage.py migrate
```

## 주의사항

`t3.micro`는 메모리가 작습니다. AI 모델이 무거우면 AI 서비스가 죽을 수 있습니다. 그 경우에는 시연할 때만 AI를 켜거나, AI만 더 큰 인스턴스로 잠깐 올리는 방식을 고려하세요.

운영 배포에서는 `DEBUG=False`를 유지하세요.

RDS는 EC2에서만 접근 가능하게 설정하세요.

AWS Budgets 알림은 반드시 설정하세요.
