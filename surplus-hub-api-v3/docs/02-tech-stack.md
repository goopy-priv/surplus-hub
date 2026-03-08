# 기술 스택

## 🛠️ 핵심 기술 스택

### Flutter & Dart
- **Flutter**: 3.5.0+
- **Dart**: 3.5.0+
- **Material 3**: 최신 Material Design 사용

### 📱 플랫폼 지원
- **Android**: API 21+ (Android 5.0)
- **iOS**: iOS 12+
- **Web**: 추후 지원 예정
- **Desktop**: 추후 지원 예정

## 🏛️ 아키텍처 관련 패키지

### 상태 관리
```yaml
flutter_bloc: ^8.1.6      # BLoC 패턴 구현
bloc: ^8.1.4               # BLoC 코어 라이브러리
```

**사용 목적**:
- 복잡한 상태 관리
- 비즈니스 로직과 UI 분리
- 테스트 가능한 코드 작성

**핵심 개념**:
- **Event**: 사용자 액션이나 시스템 이벤트
- **State**: 현재 상태
- **BLoC**: Event를 State로 변환하는 로직

### 의존성 주입
```yaml
get_it: ^8.0.2             # 의존성 주입 컨테이너
injectable: ^2.4.4         # 의존성 주입 애노테이션
injectable_generator: ^2.6.2  # 코드 생성 (dev_dependency)
```

**사용 목적**:
- 느슨한 결합도 유지
- 테스트 용이성
- 의존성 라이프사이클 관리

## 🌐 네비게이션

### 라우팅
```yaml
go_router: ^14.7.1         # 선언적 라우팅
```

**주요 기능**:
- 네스트된 라우팅 지원
- Deep linking 지원
- 타입 안전한 라우팅
- Web URL과 호환

**사용 예시**:
```dart
// 라우트 정의
static final GoRouter router = GoRouter(
  routes: [
    GoRoute(
      path: '/material/:id',
      builder: (context, state) => MaterialDetailPage(
        materialId: state.pathParameters['id']!
      ),
    ),
  ],
);

// 네비게이션
context.push('/material/123');
context.go('/home');
```

## 🌍 네트워킹 & 데이터

### HTTP 클라이언트
```yaml
dio: ^5.7.0                # HTTP 클라이언트
```

**주요 기능**:
- Request/Response 인터셉터
- 에러 처리
- 타임아웃 설정
- JSON 시리얼라이제이션

### 로컬 저장소
```yaml
shared_preferences: ^2.3.5  # 키-값 저장소
```

**사용 용도**:
- 사용자 설정 저장
- 로그인 토큰 저장
- 앱 상태 저장

## 🖼️ 이미지 처리

### 이미지 관련 패키지
```yaml
cached_network_image: ^3.4.1  # 네트워크 이미지 캐싱
image_picker: ^1.1.2          # 갤러리/카메라 이미지 선택
```

**Cached Network Image 기능**:
- 자동 이미지 캐싱
- 플레이스홀더 지원
- 에러 처리
- 메모리 관리

**Image Picker 기능**:
- 갤러리에서 이미지 선택
- 카메라로 사진 촬영
- 다중 이미지 선택

## 🎨 UI 라이브러리

### UI 컴포넌트
```yaml
flutter_svg: ^2.0.12       # SVG 이미지 렌더링
shimmer: ^3.0.0           # 로딩 스켈레톤 효과
```

**Flutter SVG**:
- 벡터 그래픽 지원
- 색상 커스터마이징
- 크기 조절 가능

**Shimmer**:
- 로딩 상태 시각화
- 부드러운 애니메이션
- 커스터마이징 가능

## 🧰 유틸리티 라이브러리

### 데이터 처리
```yaml
equatable: ^2.0.7         # 객체 비교를 위한 유틸리티
dartz: ^0.10.1            # 함수형 프로그래밍 유틸리티
```

**Equatable**:
- 자동 equals/hashCode 생성
- 객체 비교 간소화
- BLoC State 비교에 필수

**Dartz**:
- Either 타입으로 에러 처리
- Option 타입으로 null 안전성
- 함수형 프로그래밍 패턴

## 🧪 테스트 관련

### 테스트 패키지
```yaml
# dev_dependencies
flutter_test: sdk           # 기본 테스트 프레임워크
bloc_test: ^9.1.7          # BLoC 테스트 유틸리티
mocktail: ^1.0.4           # Mock 객체 생성
```

**BLoC Test**:
- BLoC 단위 테스트
- 상태 변화 테스트
- 이벤트 시퀀스 테스트

**Mocktail**:
- Mock 객체 생성
- API 호출 모킹
- 의존성 모킹

## 🔧 개발 도구

### 코드 생성
```yaml
build_runner: ^2.4.13     # 코드 생성 실행기
injectable_generator: ^2.6.2  # 의존성 주입 코드 생성
```

### 코드 품질
```yaml
flutter_lints: ^5.0.0     # Flutter 린팅 규칙
```

## 📁 패키지 구조 분석

### 의존성 분류

**프로덕션 의존성** (`dependencies`):
- 앱 실행에 필수적인 패키지
- 앱 번들에 포함됨
- 런타임에 사용됨

**개발 의존성** (`dev_dependencies`):
- 개발/빌드 과정에서만 사용
- 앱 번들에 포함되지 않음
- 테스트, 코드 생성 등에 사용

## 🎯 패키지 선택 기준

### 1. 성능
- 앱 크기에 미치는 영향 최소화
- 메모리 사용량 고려
- 네트워크 효율성

### 2. 유지보수성
- 활발한 커뮤니티 지원
- 정기적인 업데이트
- 좋은 문서화

### 3. 호환성
- Flutter 최신 버전 지원
- 플랫폼 간 호환성
- 다른 패키지와의 호환성

## 🔄 버전 관리 전략

### 메이저 버전 업데이트
- 프로젝트 전체 영향 검토
- 테스트 코드 업데이트
- 문서 업데이트

### 마이너 버전 업데이트
- 새 기능 검토
- 호환성 확인
- 필요시 적용

### 패치 버전 업데이트
- 보안 수정 우선 적용
- 버그 수정 검토
- 자동 업데이트 고려

## 📊 패키지 사용률

### 핵심 패키지 (필수)
- `flutter_bloc`: 상태 관리
- `go_router`: 네비게이션  
- `dio`: 네트워킹
- `get_it`: 의존성 주입

### 편의 패키지
- `cached_network_image`: 성능 향상
- `shimmer`: UX 개선
- `equatable`: 코드 간소화

### 개발 도구
- `flutter_lints`: 코드 품질
- `bloc_test`: 테스트
- `mocktail`: 테스트

---

← [프로젝트 개요](01-project-overview.md) | [개발 환경 설정](03-development-setup.md) →