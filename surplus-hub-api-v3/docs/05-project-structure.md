# 프로젝트 구조

## 🎯 학습 목표
- Clean Architecture 패턴의 폴더 구조를 이해한다
- 각 폴더와 파일의 역할을 파악한다
- 새로운 기능을 추가할 때 올바른 위치를 찾을 수 있다
- 프로젝트의 의존성 흐름을 이해한다

**예상 소요 시간**: 1-2시간

## 📁 전체 프로젝트 구조

```
surplus-hub-flutter/
├── android/                 # Android 플랫폼 코드
├── ios/                    # iOS 플랫폼 코드
├── web/                    # Web 플랫폼 코드
├── windows/                # Windows 플랫폼 코드
├── linux/                 # Linux 플랫폼 코드
├── macos/                  # macOS 플랫폼 코드
├── assets/                 # 정적 리소스 (이미지, 폰트 등)
│   └── images/            # 이미지 파일들
├── lib/                   # 📱 메인 소스 코드
├── test/                  # 테스트 코드
├── docs/                  # 📚 프로젝트 문서
├── pubspec.yaml           # 의존성 및 설정
├── analysis_options.yaml  # 코드 분석 설정
└── README.md              # 프로젝트 소개
```

## 📱 lib 폴더 구조 (핵심)

### Clean Architecture 기반 구조
```
lib/
├── main.dart                    # 🚀 앱 진입점
├── core/                       # 🏗️ 공통 핵심 기능
│   ├── constants/
│   │   └── app_constants.dart   # 앱 상수 정의
│   ├── error/                  # 에러 처리 (향후 확장)
│   ├── navigation/
│   │   └── app_router.dart     # 라우팅 설정
│   ├── network/                # 네트워크 설정 (향후 확장)
│   ├── theme/                  # 🎨 테마 시스템
│   │   ├── app_colors.dart     # 색상 정의
│   │   ├── app_spacing.dart    # 간격 정의
│   │   ├── app_text_styles.dart # 텍스트 스타일
│   │   └── app_theme.dart      # 전체 테마 설정
│   ├── usecases/              # 공통 유즈케이스 (향후 확장)
│   └── utils/                 # 유틸리티 함수들 (향후 확장)
├── features/                   # 🎯 기능별 모듈
│   ├── home/                  # 홈 기능
│   ├── community/             # 커뮤니티 기능
│   ├── chat/                  # 채팅 기능
│   ├── profile/               # 프로필 기능
│   ├── register/              # 자재 등록 기능
│   ├── material/              # 자재 관련 기능
│   └── material_detail/       # 자재 상세 기능
├── injection/                  # 💉 의존성 주입
│   └── injection.dart         # 의존성 설정
└── shared/                    # 🔄 공유 위젯
    └── widgets/               # 재사용 가능한 위젯들
        ├── app_button.dart
        ├── category_selection_modal.dart
        ├── filter_bar.dart
        ├── main_navigation_shell.dart
        └── material_card.dart
```

## 🎯 Feature 모듈 구조

각 기능(feature)은 Clean Architecture의 3계층으로 구성됩니다:

```
features/home/                 # 예시: 홈 기능
├── data/                     # 📊 Data Layer
│   ├── datasources/          # 데이터 소스
│   │   ├── local/           # 로컬 데이터 소스
│   │   └── remote/          # 원격 데이터 소스
│   ├── models/              # 데이터 모델 (DTO)
│   └── repositories/        # Repository 구현체
├── domain/                   # 🧠 Domain Layer
│   ├── entities/            # 엔티티 (비즈니스 객체)
│   │   ├── material_item.dart
│   │   ├── category_node.dart
│   │   └── selected_category.dart
│   ├── repositories/        # Repository 인터페이스
│   └── usecases/           # 비즈니스 로직
└── presentation/            # 🖼️ Presentation Layer
    ├── bloc/               # 상태 관리 (BLoC)
    ├── pages/              # 화면 (페이지)
    │   ├── home_page.dart
    │   └── material_detail_page.dart
    └── widgets/            # UI 컴포넌트
```

## 📋 계층별 상세 설명

### 1. Core 폴더 (`lib/core/`)

#### 📌 역할
프로젝트 전체에서 공통으로 사용되는 핵심 기능들을 모아놓은 곳

#### 📂 하위 구조

**constants/**
```dart
// app_constants.dart 예시
class AppConstants {
  static const String appName = 'Surplus Hub';
  static const String sampleMaterialsJson = '''
  [
    {
      "id": "1",
      "title": "시멘트 50포",
      "price": "150,000원",
      "location": "서울시 강남구",
      "seller": "김건설",
      // ... 더 많은 샘플 데이터
    }
  ]
  ''';
}
```

**theme/**
- 모든 UI 요소의 스타일링 정의
- Material Design 3 기반 테마 시스템
- 일관된 색상, 간격, 텍스트 스타일 제공

**navigation/**
```dart
// app_router.dart 주요 구조
class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/',
    routes: [
      // Bottom Navigation Routes
      ShellRoute(...),
      // Full Screen Routes
      GoRoute(...),
    ],
  );
}
```

### 2. Features 폴더 (`lib/features/`)

#### 📌 역할
비즈니스 기능별로 독립적인 모듈을 구성

#### 🏠 Home Feature 예시

**Domain Layer (`domain/`)**
```dart
// entities/material_item.dart
class MaterialItem extends Equatable {
  final String id;
  final String title;
  final String price;
  // ... 비즈니스 로직과 규칙 포함
  
  int get priceAsNumber => 
    int.tryParse(price.replaceAll(RegExp(r'[^0-9]'), '')) ?? 0;
  
  int get popularityScore => likes + chats;
}
```

**Presentation Layer (`presentation/`)**
```dart
// pages/home_page.dart
class HomePage extends StatefulWidget {
  // UI 표시 및 사용자 상호작용
  // BLoC과 통신하여 상태 관리
}

// widgets/ (해당 기능 전용 위젯)
class MaterialCard extends StatelessWidget {
  // 재사용 가능하지만 Home 기능에 특화된 위젯
}
```

**Data Layer (`data/`) - 향후 확장**
```dart
// models/ - API 응답 데이터 구조
class MaterialItemModel extends MaterialItem {
  factory MaterialItemModel.fromJson(Map<String, dynamic> json) {
    // API 데이터를 Entity로 변환
  }
}

// repositories/ - 실제 데이터 처리
class MaterialRepositoryImpl implements MaterialRepository {
  // API 호출, 로컬 저장소 접근 등
}
```

### 3. Shared 폴더 (`lib/shared/`)

#### 📌 역할
여러 기능에서 공통으로 사용되는 UI 컴포넌트

```dart
// widgets/app_button.dart
class AppButton extends StatelessWidget {
  // 프로젝트 전체에서 사용하는 표준 버튼
}

// widgets/main_navigation_shell.dart
class MainNavigationShell extends StatelessWidget {
  // Bottom Navigation과 FAB을 관리하는 Shell
}
```

### 4. Injection 폴더 (`lib/injection/`)

#### 📌 역할
의존성 주입 설정 및 관리

```dart
// injection.dart
final getIt = GetIt.instance;

void configureDependencies() {
  // 향후 Repository, UseCase, BLoC 등 등록
  // getIt.registerLazySingleton<MaterialRepository>(
  //   () => MaterialRepositoryImpl()
  // );
}
```

## 🔄 의존성 방향

Clean Architecture의 핵심 원칙: **내부 계층은 외부 계층에 의존하지 않는다**

```
Presentation ─────► Domain ◄───── Data
    (UI)          (Business)      (External)
     │                │              │
 BLoC, Pages     Entities,        Models,
  Widgets       UseCases,       DataSources,
              Repositories(I)  Repositories(Impl)
```

### 의존성 규칙
1. **Domain Layer**: 다른 계층에 의존하지 않음 (순수 Dart 코드)
2. **Data Layer**: Domain의 인터페이스에만 의존
3. **Presentation Layer**: Domain에만 의존 (Data Layer 직접 접근 금지)

## 📁 파일 명명 규칙

### 일반 규칙
- **Snake Case**: `material_item.dart`, `user_profile.dart`
- **명사형**: 클래스명과 파일명 일치
- **설명적**: 파일 내용을 명확히 표현

### 계층별 명명 규칙

**Entities** (Domain)
```dart
// ✅ 좋은 예시
material_item.dart          → MaterialItem
user_profile.dart           → UserProfile
category_node.dart          → CategoryNode

// ❌ 나쁜 예시
material.dart               → 너무 일반적
item_entity.dart           → 불필요한 접미사
```

**Pages** (Presentation)
```dart
// ✅ 좋은 예시
home_page.dart              → HomePage
material_detail_page.dart   → MaterialDetailPage

// ❌ 나쁜 예시
home.dart                   → 명확하지 않음
home_screen.dart           → screen vs page 혼용 금지
```

**Widgets** (Presentation)
```dart
// ✅ 좋은 예시
material_card.dart          → MaterialCard
filter_bar.dart            → FilterBar

// ❌ 나쁜 예시
card.dart                   → 너무 일반적
material_item_widget.dart  → 불필요한 접미사
```

**BLoCs** (향후 확장)
```dart
// ✅ 좋은 예시
material_bloc.dart          → MaterialBloc
material_event.dart         → MaterialEvent
material_state.dart         → MaterialState
```

## 🏗️ 새 기능 추가 가이드

### 1단계: Feature 폴더 생성
```bash
mkdir -p lib/features/new_feature/{data/{datasources,models,repositories},domain/{entities,repositories,usecases},presentation/{bloc,pages,widgets}}
```

### 2단계: 계층별 파일 생성
```dart
// 1. Domain - Entity 생성
lib/features/new_feature/domain/entities/new_entity.dart

// 2. Presentation - Page 생성
lib/features/new_feature/presentation/pages/new_page.dart

// 3. Navigation 등록
lib/core/navigation/app_router.dart에 라우트 추가
```

### 3단계: 의존성 연결
```dart
// main.dart에서 새 페이지 import
// app_router.dart에서 라우트 등록
// 필요시 shared widgets으로 승격
```

## ✅ 프로젝트 구조 이해 체크리스트

다음을 이해했다면 프로젝트 구조 학습이 완료된 것입니다:

- [ ] Clean Architecture 3계층의 역할을 설명할 수 있다
- [ ] 새로운 엔티티를 추가할 위치를 안다
- [ ] 새로운 페이지를 추가하는 방법을 안다
- [ ] 공통 위젯을 만들 위치를 안다
- [ ] 의존성 방향을 이해한다
- [ ] 파일 명명 규칙을 적용할 수 있다

## 🔍 구조 탐색 연습

### 실습 1: 기존 기능 분석
1. `lib/features/home/` 폴더를 열어보세요
2. `domain/entities/material_item.dart` 파일을 읽어보세요
3. `presentation/pages/home_page.dart` 파일을 읽어보세요
4. 데이터 흐름을 따라가 보세요

### 실습 2: 파일 찾기
다음 기능들이 어느 파일에 구현되어 있는지 찾아보세요:
- [ ] 앱의 메인 테마 설정
- [ ] Bottom Navigation 구현
- [ ] 자재 아이템의 데이터 구조
- [ ] 홈 페이지의 UI
- [ ] 라우팅 설정

## 🎓 다음 단계

프로젝트 구조를 이해했다면:
1. [코딩 컨벤션](06-coding-conventions.md) 학습하기
2. 간단한 UI 수정 실습해보기
3. 새로운 위젯 만들어보기

---

← [프로젝트 설정](04-project-setup.md) | [코딩 컨벤션](06-coding-conventions.md) →