# 프로젝트 설정

## 🎯 학습 목표
- Surplus Hub Flutter 프로젝트를 로컬 환경에 설정한다
- 프로젝트를 성공적으로 실행한다
- 개발 환경별 설정을 이해한다
- 기본적인 개발 워크플로우를 익힌다

**예상 소요 시간**: 30분-1시간

## 📋 사전 요구사항
- [개발 환경 설정](03-development-setup.md) 완료
- Git 설치 및 기본 사용법 숙지
- 팀 저장소 접근 권한 획득

## 🔄 프로젝트 클론 및 설정

### 1단계: 프로젝트 클론 (5분)

#### 저장소 클론
```bash
# 프로젝트 클론
git clone <repository-url>
cd surplus-hub-flutter

# 현재 브랜치 확인
git branch
git status
```

#### 프로젝트 구조 확인
```bash
# 프로젝트 구조 확인
ls -la

# 주요 파일들 존재 확인
ls -la pubspec.yaml
ls -la lib/
ls -la android/
ls -la ios/
```

### 2단계: 의존성 설치 (10분)

#### Flutter 패키지 설치
```bash
# 의존성 설치
flutter pub get
```

**예상 출력**:
```
Running "flutter pub get" in surplus-hub-flutter...
Resolving dependencies... 
Got dependencies!
```

#### 에러 발생 시 해결
```bash
# 캐시 클리어 후 재시도
flutter clean
flutter pub get

# pub cache 초기화 (필요시)
flutter pub cache repair
```

### 3단계: 코드 생성 (5분)

현재 프로젝트에서는 의존성 주입을 위한 코드 생성이 준비되어 있습니다.

```bash
# 코드 생성 실행 (향후 활성화 예정)
# flutter packages pub run build_runner build

# 현재는 임시 설정으로 동작
echo "코드 생성은 향후 API 연동 시점에 활성화 예정"
```

### 4단계: 프로젝트 실행 (10분)

#### Android에서 실행
```bash
# 연결된 기기/에뮬레이터 확인
flutter devices

# Android 에뮬레이터 실행 (없다면)
flutter emulators --launch <emulator_name>

# 앱 실행
flutter run
```

#### iOS에서 실행 (macOS만)
```bash
# iOS 시뮬레이터 실행
open -a Simulator

# 앱 실행
flutter run
```

#### 웹에서 실행
```bash
# 웹 브라우저에서 실행
flutter run -d chrome
```

## 🎨 개발 환경 설정

### VS Code 워크스페이스 설정

#### 1. 프로젝트를 VS Code로 열기
```bash
code .
```

#### 2. 권장 설정 파일 생성
프로젝트 루트에 `.vscode/settings.json` 파일 생성:
```json
{
  "dart.flutterSdkPath": "",
  "dart.closingLabels": true,
  "dart.previewFlutterUiGuides": true,
  "editor.formatOnSave": true,
  "editor.rulers": [80],
  "editor.codeActionsOnSave": {
    "source.fixAll": true,
    "source.organizeImports": true
  },
  "files.associations": {
    "*.dart": "dart"
  },
  "search.exclude": {
    "**/build/**": true,
    "**/.dart_tool/**": true
  }
}
```

#### 3. 디버그 설정
`.vscode/launch.json` 파일 생성:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "surplus_hub_flutter",
      "request": "launch",
      "type": "dart"
    },
    {
      "name": "surplus_hub_flutter (profile mode)",
      "request": "launch",
      "type": "dart",
      "flutterMode": "profile"
    },
    {
      "name": "surplus_hub_flutter (release mode)",
      "request": "launch",
      "type": "dart",
      "flutterMode": "release"
    }
  ]
}
```

### Android Studio 설정

#### 1. 프로젝트 열기
- Android Studio 실행
- "Open an existing Android Studio project" 선택
- 프로젝트 루트 폴더 선택

#### 2. SDK 설정 확인
- File > Project Structure
- SDK Location 확인 및 설정

## 📱 기기 설정

### Android 실제 기기 연결

#### 1. 개발자 옵션 활성화
1. 설정 > 디바이스 정보
2. 빌드 번호를 7번 탭
3. 개발자 옵션 활성화

#### 2. USB 디버깅 허용
1. 개발자 옵션 > USB 디버깅 체크
2. 기기를 USB로 연결
3. 디버깅 허용 팝업에서 "허용" 선택

#### 3. 연결 확인
```bash
flutter devices
```

### iOS 실제 기기 연결 (macOS)

#### 1. 개발 프로비저닝 설정
1. Xcode에서 프로젝트 열기: `open ios/Runner.xcworkspace`
2. Team 설정: Runner > Signing & Capabilities > Team 선택
3. Bundle Identifier 확인

#### 2. 기기 신뢰 설정
1. 기기를 Mac에 연결
2. "이 컴퓨터를 신뢰하시겠습니까?" 팝업에서 신뢰 선택
3. Xcode에서 기기 선택 후 빌드

## 🔧 프로젝트별 설정

### 앱 아이콘 및 스플래시 설정

현재 프로젝트의 에셋 확인:
```bash
# 이미지 에셋 확인
ls -la assets/images/

# Android 아이콘 확인
ls -la android/app/src/main/res/mipmap-*/

# iOS 아이콘 확인
ls -la ios/Runner/Assets.xcassets/AppIcon.appiconset/
```

### 환경별 설정

#### 개발(Debug) 환경
- Hot Reload 활성화
- Debug 정보 표시
- 개발용 API 엔드포인트 사용 (향후)

#### 스테이징 환경 (향후)
- 프로덕션 유사 환경
- 테스트용 데이터
- 성능 프로파일링

#### 프로덕션(Release) 환경
- 최적화된 빌드
- 프로덕션 API 엔드포인트
- 에러 리포팅 활성화

## 🧪 프로젝트 동작 확인

### 기본 기능 테스트

#### 1. 앱 시작 확인
- [ ] 앱이 오류 없이 시작됨
- [ ] 스플래시 화면 표시
- [ ] 홈 화면 로딩

#### 2. 네비게이션 테스트
- [ ] 하단 네비게이션 탭 전환
- [ ] FAB 버튼 동작
- [ ] 페이지 간 이동

#### 3. UI 요소 확인
- [ ] 테마 색상 정상 적용
- [ ] 폰트 및 텍스트 스타일 정상
- [ ] 이미지 및 아이콘 표시

#### 4. Hot Reload 테스트
```dart
// lib/main.dart에서 타이틀 변경해보기
title: 'Surplus Hub - Test',  // 'Surplus Hub'에서 변경

// 저장 후 변화 확인 (Ctrl/Cmd + S)
```

### 성능 확인

#### 빌드 시간 측정
```bash
# 첫 빌드 (Cold build)
time flutter build apk --debug

# 증분 빌드 (Hot reload 시뮬레이션)
# 코드 변경 후
time flutter build apk --debug
```

#### 앱 크기 확인
```bash
# APK 크기 확인
flutter build apk --analyze-size

# 상세 분석 (향후 사용)
# flutter build apk --split-debug-info=./debug-symbols
```

## 🚨 일반적인 문제 해결

### Gradle 빌드 오류
```bash
# Gradle 캐시 클리어
cd android
./gradlew clean

# Flutter 클린
cd ..
flutter clean
flutter pub get
```

### iOS 빌드 오류
```bash
# CocoaPods 설치/업데이트
cd ios
pod install --repo-update
cd ..
```

### 의존성 충돌
```bash
# pubspec.lock 삭제 후 재설치
rm pubspec.lock
flutter pub get
```

### Hot Reload 동작 안함
1. 저장 확인 (Ctrl/Cmd + S)
2. 파일 경로 확인 (영어 경로 권장)
3. Flutter 재시작: `flutter run` 중 `R` 키 입력

## ✅ 완료 기준

다음을 모두 확인했다면 프로젝트 설정이 완료된 것입니다:

- [ ] 프로젝트 클론 성공
- [ ] `flutter pub get` 성공
- [ ] Android/iOS에서 앱 실행 성공
- [ ] Hot Reload 정상 동작
- [ ] 모든 탭 네비게이션 정상 작동
- [ ] 에러 없이 모든 페이지 접근 가능

## 📊 프로젝트 현재 상태

### 구현 완료된 기능
- ✅ 프로젝트 기본 구조
- ✅ 네비게이션 시스템
- ✅ 테마 시스템
- ✅ 기본 UI 컴포넌트
- ✅ 샘플 데이터 표시

### 개발 예정 기능
- ⏳ API 연동
- ⏳ 사용자 인증
- ⏳ 실시간 채팅
- ⏳ 이미지 업로드
- ⏳ 푸시 알림

## 🎓 다음 단계

프로젝트 설정을 완료했다면:
1. [프로젝트 구조](05-project-structure.md) 이해하기
2. [코딩 컨벤션](06-coding-conventions.md) 숙지하기
3. 간단한 UI 수정 연습하기

---

← [개발 환경 설정](03-development-setup.md) | [프로젝트 구조](05-project-structure.md) →