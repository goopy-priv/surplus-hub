# 프로젝트 개요

## 📱 Surplus Hub Flutter란?

Surplus Hub는 **건설 현장의 잉여 자재를 효율적으로 거래할 수 있는 모바일 플랫폼**입니다. 
건설 업계에서 발생하는 자재 낭비를 줄이고, 필요한 사람들에게 적정 가격으로 자재를 공급하는 것을 목표로 합니다.

### 🎯 프로젝트 목적
- **자재 낭비 최소화**: 건설 현장에서 남은 자재의 재활용 촉진
- **비용 절감**: 새 자재 대비 저렴한 가격으로 필요한 자재 구매 가능
- **환경 보호**: 자재 재사용을 통한 환경 영향 감소
- **커뮤니티 형성**: 건설 업계 종사자들 간의 네트워킹 및 정보 공유

### 🚀 주요 기능
1. **자재 거래 마켓플레이스**
   - 자재 등록 및 검색
   - 카테고리별 분류 시스템
   - 가격 비교 및 필터링

2. **사용자 프로필 시스템**
   - 신뢰도 기반 평가 시스템
   - 거래 이력 관리
   - 매너 온도 등급

3. **실시간 채팅**
   - 판매자-구매자 간 직접 소통
   - 거래 조건 협상
   - 안전한 거래 지원

4. **커뮤니티**
   - 업계 정보 공유
   - 질문 및 답변
   - 경험 공유

## 🏗️ 프로젝트 아키텍처

### Clean Architecture 패턴
본 프로젝트는 **Clean Architecture** 패턴을 기반으로 구성되어 있습니다.

```
┌─────────────────────────────────────┐
│           Presentation Layer        │ ← UI, BLoC, Pages, Widgets
├─────────────────────────────────────┤
│            Domain Layer             │ ← Entities, Use Cases, Repositories (Interface)
├─────────────────────────────────────┤
│             Data Layer              │ ← Models, Data Sources, Repository Implementations
└─────────────────────────────────────┘
```

#### 📋 계층별 역할

**1. Presentation Layer (프레젠테이션 계층)**
- **책임**: UI 표시 및 사용자 상호작용 처리
- **구성 요소**:
  - `Pages`: 화면 구성
  - `Widgets`: 재사용 가능한 UI 컴포넌트
  - `BLoC`: 상태 관리 및 비즈니스 로직 호출

**2. Domain Layer (도메인 계층)**
- **책임**: 핵심 비즈니스 로직 및 규칙 정의
- **구성 요소**:
  - `Entities`: 핵심 데이터 구조
  - `Use Cases`: 비즈니스 로직 구현
  - `Repositories`: 데이터 접근 인터페이스 정의

**3. Data Layer (데이터 계층)**
- **책임**: 외부 데이터 소스와의 통신 및 데이터 변환
- **구성 요소**:
  - `Models`: 데이터 전송 객체 (DTO)
  - `Data Sources`: API, 로컬 DB 등 실제 데이터 소스
  - `Repository Implementations`: Repository 인터페이스 구현

### 🔄 데이터 흐름
1. **UI** → BLoC (Event 발생)
2. **BLoC** → Use Case 호출
3. **Use Case** → Repository Interface를 통한 데이터 요청
4. **Repository** → Data Source에서 데이터 취득
5. **Data Source** → API/Local DB에서 데이터 반환
6. **Repository** → Entity로 변환하여 반환
7. **Use Case** → 비즈니스 로직 처리 후 결과 반환
8. **BLoC** → State 업데이트
9. **UI** → State 변화에 따른 화면 갱신

## 🎨 디자인 시스템

### Material Design 3
- **디자인 언어**: Google의 Material Design 3 사용
- **색상 시스템**: 일관된 브랜드 색상 팔레트
- **컴포넌트**: 재사용 가능한 UI 컴포넌트 시스템

### 주요 컬러 팔레트
- **Primary**: `#2563EB` (브랜드 메인 컬러)
- **Background**: `#FFFFFF`, `#F9FAFB`
- **Text**: `#111827`, `#6B7280`

## 📱 앱 구조

### 네비게이션 구조
```
Bottom Navigation (5개 탭)
├── 홈 (/)
├── 커뮤니티 (/community)
├── 등록 (FAB) (/register)
├── 채팅 (/chat)
└── 내 정보 (/profile)

Modal/Full Screen Pages
├── 자재 상세 (/material/:id)
├── 검색 (/search)
└── 알림 (/notifications)
```

### 주요 피처 모듈
1. **Home**: 자재 목록, 검색, 필터링
2. **Community**: 게시글 작성/조회, 댓글
3. **Chat**: 실시간 채팅, 채팅방 관리
4. **Profile**: 사용자 정보, 거래 이력
5. **Register**: 새 자재 등록

## 🎓 학습 포인트

### Flutter 초보자가 주목할 점
1. **Widget 기반 UI**: 모든 UI 요소가 Widget으로 구성
2. **상태 관리**: BLoC 패턴을 통한 체계적인 상태 관리
3. **네비게이션**: Go Router를 사용한 선언적 라우팅
4. **의존성 주입**: Get_it을 사용한 의존성 관리

### 권장 학습 순서
1. **Flutter 기본 개념** (Widget, State, Build 메서드)
2. **프로젝트 구조 이해** (Clean Architecture)
3. **BLoC 패턴 학습** (Event, State, BLoC)
4. **Go Router 네비게이션**
5. **의존성 주입 개념**

## 🔧 개발 환경 요구사항

### 필수 도구
- **Flutter SDK**: 3.5.0 이상
- **Dart**: 3.5.0 이상
- **IDE**: Android Studio, VS Code, IntelliJ IDEA
- **Git**: 버전 관리

### 권장 플러그인
- Flutter (공식)
- Dart (공식)
- Flutter BLoC (상태 관리 도구)
- GitLens (Git 시각화)

## 📊 프로젝트 현황

### 개발 단계
- ✅ **기본 프로젝트 구조 설정 완료**
- ✅ **디자인 시스템 구축 완료**
- ✅ **네비게이션 시스템 구축 완료**
- 🔄 **각 피처별 기본 UI 구현 중**
- ⏳ **API 연동 준비 중**
- ⏳ **테스트 코드 작성 예정**

### 다음 개발 계획
1. **API 서버 연동**
2. **실제 데이터 연동**
3. **사용자 인증 시스템**
4. **이미지 업로드 기능**
5. **푸시 알림 기능**

---

다음: [기술 스택](02-tech-stack.md) →