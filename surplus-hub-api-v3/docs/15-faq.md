# FAQ (자주 묻는 질문)

## 🎯 이 문서의 목적
- 신규 개발자들이 자주 묻는 질문에 대한 답변 제공
- 일반적인 궁금증 해결
- 개발 과정에서 발생하는 의문점 해소

## 📱 Flutter 기초

### Q1: Flutter와 React Native의 차이점은 무엇인가요?
**A:** 주요 차이점은 다음과 같습니다:
- **언어**: Flutter는 Dart, React Native는 JavaScript
- **렌더링**: Flutter는 자체 렌더링 엔진, React Native는 네이티브 컴포넌트
- **성능**: Flutter가 일반적으로 더 높은 성능
- **개발 경험**: Hot Reload는 둘 다 지원

### Q2: Widget과 Component의 차이는 무엇인가요?
**A:** Flutter에서는 모든 UI 요소가 Widget입니다:
- **StatelessWidget**: 상태가 없는 위젯 (React의 함수형 컴포넌트와 유사)
- **StatefulWidget**: 상태가 있는 위젯 (React의 클래스 컴포넌트와 유사)
- 모든 것이 Widget 트리로 구성됨

### Q3: Hot Reload가 동작하지 않아요
**A:** 다음을 확인해보세요:
1. 파일이 저장되었는지 확인 (`Ctrl/Cmd + S`)
2. 앱이 Debug 모드에서 실행 중인지 확인
3. `flutter run` 실행 후 `r` 키로 Hot Reload 수동 실행
4. 문제가 지속되면 `R` 키로 Hot Restart 시도

## 🏗️ 프로젝트 구조

### Q4: Clean Architecture가 복잡해 보이는데 꼭 필요한가요?
**A:** 네, 다음 이유로 필요합니다:
- **테스트 용이성**: 각 계층을 독립적으로 테스트 가능
- **유지보수성**: 코드 변경 시 영향 범위 최소화
- **확장성**: 새로운 기능 추가 시 체계적인 구조
- **팀 협업**: 일관된 코드 구조로 협업 효율성 증대

### Q5: 새로운 기능은 어디에 추가해야 하나요?
**A:** 다음 순서로 판단하세요:
1. **기존 기능 확장**: 해당 feature 폴더에 추가
2. **공통 기능**: shared/widgets 폴더에 추가
3. **새로운 독립 기능**: 새로운 feature 폴더 생성
4. **핵심 기능**: core 폴더에 추가 (신중히 결정)

### Q6: Entity와 Model의 차이는 무엇인가요?
**A:** 
- **Entity**: 비즈니스 로직을 담은 도메인 객체 (domain 계층)
- **Model**: API 응답 데이터 구조 (data 계층)
- Entity는 앱의 핵심 비즈니스 규칙을 포함하고, Model은 외부 데이터 변환용

## 🎨 UI 개발

### Q7: const를 언제 사용해야 하나요?
**A:** 가능한 모든 곳에서 사용하세요:
```dart
// ✅ 좋은 예시
const Text('Hello World')
const EdgeInsets.all(16)
const Color(0xFF2563EB)

// ❌ 나쁜 예시 (불필요한 rebuild 발생)
Text('Hello World')
EdgeInsets.all(16)
```

### Q8: StatefulWidget과 StatelessWidget을 언제 사용하나요?
**A:**
- **StatelessWidget**: 데이터가 변하지 않는 정적 UI
- **StatefulWidget**: 사용자 상호작용이나 데이터 변화가 있는 동적 UI
- 의심스러우면 StatelessWidget부터 시작하고 필요시 변경

### Q9: ListView vs ListView.builder 차이점은?
**A:**
- **ListView**: 모든 아이템을 한 번에 생성 (작은 목록용)
- **ListView.builder**: 화면에 보이는 아이템만 생성 (큰 목록용, 성능 우수)
- **권장**: 동적 데이터나 많은 아이템의 경우 ListView.builder 사용

## 🔄 상태 관리

### Q10: BLoC 패턴이 어려워요. 더 간단한 방법은 없나요?
**A:** BLoC가 복잡해 보이지만 장기적으로 이점이 큽니다:
- **학습 곡선**: 처음에는 어려우나 익숙해지면 매우 체계적
- **대안**: Provider, Riverpod, GetX 등이 있지만 프로젝트는 BLoC 사용
- **권장**: 작은 기능부터 BLoC로 시작해서 점진적으로 익히기

### Q11: Event와 State 이름 짓기가 어려워요
**A:** 다음 패턴을 따르세요:
```dart
// Event: 동사형 (사용자 액션)
LoadMaterials, UpdateMaterial, DeleteMaterial

// State: 형용사형 (현재 상태)  
MaterialInitial, MaterialLoading, MaterialLoaded, MaterialError
```

### Q12: BLoC에서 직접 API를 호출해도 되나요?
**A:** 아니요, Repository 패턴을 사용하세요:
- **BLoC**: 비즈니스 로직만 처리
- **Repository**: 데이터 처리 (API 호출, 로컬 저장소 등)
- **UseCase**: 복잡한 비즈니스 로직 (향후 확장 시)

## 🌐 네비게이션

### Q13: context.push vs context.go 차이는?
**A:**
- **context.push()**: 스택에 새 화면 추가 (뒒로가기 가능)
- **context.go()**: 현재 화면을 새 화면으로 교체
- **일반적**: push 사용, 로그인 후 홈으로 이동 시에는 go 사용

### Q14: 네비게이션에서 데이터는 어떻게 전달하나요?
**A:** 여러 방법이 있습니다:
```dart
// 1. Path Parameter
context.push('/material/123')

// 2. Query Parameter  
context.push('/search?query=cement')

// 3. Extra Data
context.push('/detail', extra: materialObject)
```

## 📦 패키지 및 의존성

### Q15: 새로운 패키지를 추가하고 싶어요
**A:** 다음 절차를 따르세요:
1. 팀원과 패키지 필요성 논의
2. 패키지 안정성 및 유지보수 상태 확인
3. `pubspec.yaml`에 추가
4. `flutter pub get` 실행
5. 사용법 문서 작성

### Q16: pubspec.yaml에서 dependencies와 dev_dependencies 차이는?
**A:**
- **dependencies**: 앱 실행에 필요한 패키지 (앱 번들에 포함)
- **dev_dependencies**: 개발/빌드에만 필요한 패키지 (앱 번들에 미포함)

## 🧪 테스트

### Q17: 테스트는 꼭 작성해야 하나요?
**A:** 네, 다음 이유로 권장합니다:
- **버그 예방**: 코드 변경 시 기존 기능 보호
- **리팩토링**: 안전한 코드 개선
- **문서 역할**: 코드의 의도된 동작 설명
- **팀 협업**: 다른 개발자의 실수 방지

### Q18: 어떤 테스트부터 시작해야 하나요?
**A:** 다음 순서로 시작하세요:
1. **Unit Test**: Entity, 유틸 함수 등 순수 로직
2. **BLoC Test**: 상태 관리 로직
3. **Widget Test**: UI 컴포넌트 (필요시)
4. **Integration Test**: 전체 플로우 (고급)

## 🚀 성능

### Q19: 앱이 느려지는 것 같아요
**A:** 다음을 확인해보세요:
1. **ListView**: ListView.builder 사용 여부
2. **const**: const 키워드 사용 여부
3. **build 메서드**: 복잡한 로직이 있는지 확인
4. **이미지**: 최적화된 이미지 사용 여부
5. **불필요한 rebuild**: BlocBuilder 범위 최소화

### Q20: 이미지 로딩이 느려요
**A:** CachedNetworkImage를 사용하고 있나요?
```dart
// ✅ 좋은 예시
CachedNetworkImage(
  imageUrl: material.imageUrl,
  placeholder: (context, url) => const CircularProgressIndicator(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
)
```

## 🔧 개발 도구

### Q21: VS Code vs Android Studio 무엇을 사용해야 하나요?
**A:** 둘 다 좋지만:
- **VS Code**: 가볍고 빠름, 확장성 좋음 (권장)
- **Android Studio**: 강력한 디버깅, Android 개발에 특화
- **권장**: VS Code로 시작하고 필요시 Android Studio 병행

### Q22: 디버깅은 어떻게 하나요?
**A:** 여러 방법이 있습니다:
1. **print() 사용**: 간단한 값 확인
2. **debugPrint()**: 릴리스 모드에서 자동 제거
3. **Debugger**: 브레이크포인트 설정하여 단계별 실행
4. **Flutter Inspector**: 위젯 트리 시각화

## 📱 빌드 및 배포

### Q23: Android/iOS 실제 기기에서 테스트하려면?
**A:**
- **Android**: USB 디버깅 활성화 후 케이블 연결
- **iOS**: Apple Developer 계정 필요, Xcode에서 Team 설정
- **권장**: 개발 초기에는 에뮬레이터/시뮬레이터 사용

### Q24: 앱 아이콘은 어떻게 변경하나요?
**A:** 다음 위치의 파일들을 교체하세요:
- **Android**: `android/app/src/main/res/mipmap-*/ic_launcher.png`
- **iOS**: `ios/Runner/Assets.xcassets/AppIcon.appiconset/`
- **도구**: `flutter_launcher_icons` 패키지 사용 권장

## 🤝 팀 협업

### Q25: Git 브랜치 전략은 어떻게 되나요?
**A:** 프로젝트의 브랜치 전략을 확인하세요:
- **main**: 프로덕션 배포 브랜치
- **develop**: 개발 통합 브랜치 (있다면)
- **feature/**: 기능 개발 브랜치
- **항상**: 새 기능은 별도 브랜치에서 개발 후 PR

### Q26: 코드 리뷰에서 자주 지적받는 내용은?
**A:** 다음을 미리 확인하세요:
- [ ] `flutter analyze` 오류 없음
- [ ] 코딩 컨벤션 준수
- [ ] const 키워드 사용
- [ ] 의미 있는 변수/함수명
- [ ] 적절한 주석
- [ ] 하드코딩된 값 없음

## ❓ 추가 질문

### 질문이 더 있다면?
1. **팀 슬랙/채팅**: 동료에게 빠른 질문
2. **코드 리뷰**: PR에서 구체적인 코드 관련 질문  
3. **1:1 멘토링**: 시니어 개발자와의 정기 면담
4. **문서 개선**: 이 FAQ에 없는 내용은 추가 제안

### 좋은 질문하는 방법
- **구체적**: "오류가 나요" → "이런 오류가 나요 (스크린샷/로그 첨부)"
- **시도한 것**: 어떤 해결책을 시도했는지 포함
- **환경 정보**: OS, Flutter 버전 등 포함
- **재현 방법**: 문제가 발생하는 단계별 설명

---

← [성능 최적화](14-performance.md) | [트러블슈팅](16-troubleshooting.md) →