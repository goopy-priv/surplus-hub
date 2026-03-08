#!/bin/bash

# Surplus Hub API v3 실행 스크립트

echo "=== Surplus Hub API v3 시작 ==="
echo "1. Docker 컨테이너로 실행 (권장)"
echo "2. 로컬 파이썬 가상환경으로 실행"
read -p "실행 방식을 선택하세요 (1/2): " choice

if [ "$choice" = "1" ]; then
    echo "[Docker 실행모드] 컨테이너 빌드 및 백엔드 서비스를 시작합니다..."
    docker-compose up --build
elif [ "$choice" = "2" ]; then
    echo "[로컬 실행모드] Uvicorn 서버를 시작합니다..."
    
    if [ ! -d ".venv" ]; then
        echo "가상환경(.venv)이 존재하지 않습니다. 생성을 시도합니다..."
        python3 -m venv .venv
    fi
    
    # Database 컨테이너만 백그라운드로 실행
    echo "PostgreSQL 데이터베이스(db) 컨테이너를 시작합니다..."
    docker-compose up -d db
    
    # DB가 준비될 때까지 잠시 대기
    echo "DB 구동 대기 중..."
    sleep 3
    
    # 가상환경 활성화
    source .venv/bin/activate
    
    # 의존성 설치
    pip install -r requirements.txt
    
    # 로컬용 DATABASE_URL 환경변수 설정 (포트 5433 사용)
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/surplushub"
    
    # 마이그레이션 적용
    echo "DB 마이그레이션을 확인하고 적용합니다..."
    alembic upgrade head
    
    # 서버 실행
    echo "FastAPI 서버를 http://0.0.0.0:8000 에서 시작합니다..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "잘못된 입력입니다. (1 또는 2를 입력해주세요)"
    exit 1
fi
