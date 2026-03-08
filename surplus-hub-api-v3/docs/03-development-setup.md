# 개발 환경 설정

## 🎯 학습 목표
- Flutter 개발 환경을 성공적으로 설치하고 구성한다
- IDE를 설정하고 필수 플러그인을 설치한다
- Android/iOS 개발을 위한 도구를 준비한다
- 설치가 올바르게 완료되었는지 검증한다

**예상 소요 시간**: 2-4시간 (처음 설치 시)

## 📋 사전 요구사항

### 시스템 요구사항
- **macOS**: 10.14 (Mojave) 이상 (iOS 개발 시 필수)
- **Windows**: Windows 10 64-bit 이상
- **Linux**: Ubuntu 18.04 LTS 이상
- **저장공간**: 최소 10GB 이상 여유 공간
- **메모리**: 8GB RAM 이상 권장

## 🛠️ 설치 과정

### 1단계: Flutter SDK 설치 (30분)

#### macOS
```bash
# 1. Flutter 다운로드
cd ~/development
curl -O https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/flutter_macos_3.24.3-stable.zip

# 2. 압축 해제
unzip flutter_macos_3.24.3-stable.zip

# 3. PATH 추가 (.zshrc 또는 .bash_profile)
export PATH="$PATH:`pwd`/flutter/bin"

# 4. 설정 적용
source ~/.zshrc  # 또는 source ~/.bash_profile
```

#### Windows
1. [Flutter 공식 사이트](https://flutter.dev)에서 Windows용 SDK 다운로드
2. `C:\flutter`에 압축 해제
3. 시스템 환경 변수 Path에 `C:\flutter\bin` 추가
4. PowerShell 재시작

#### 설치 검증
```bash
flutter --version
```

### 2단계: Android 개발 환경 설정 (30분)

#### Android Studio 설치
1. [Android Studio](https://developer.android.com/studio) 다운로드 및 설치
2. Android Studio 실행 후 초기 설정 완료
3. SDK Manager에서 필요한 SDK 설치:
   - Android SDK Platform-Tools
   - Android SDK Build-Tools
   - Android SDK (최신 버전 및 API 29 이상)

#### Android 라이센스 동의
```bash
flutter doctor --android-licenses
```
모든 라이센스에 `y`로 동의

### 3단계: iOS 개발 환경 설정 (macOS만, 45분)

#### Xcode 설치
```bash
# App Store에서 Xcode 설치 (시간이 오래 걸림)
# 또는 터미널에서
xcode-select --install
```

#### Xcode 설정
```bash
# Xcode 라이센스 동의
sudo xcodebuild -license accept

# iOS Simulator 설치 확인
open -a Simulator
```

#### CocoaPods 설치
```bash
sudo gem install cocoapods
```

### 4단계: IDE 설정 (20분)

#### Option 1: VS Code (권장)
1. [VS Code](https://code.visualstudio.com/) 다운로드 및 설치
2. 필수 확장 프로그램 설치:
   - Flutter
   - Dart
   - GitLens (Git 관리)
   - Bracket Pair Colorizer (코드 가독성)
   - Material Icon Theme (파일 아이콘)

#### Option 2: Android Studio
1. Android Studio에서 Plugins 메뉴 이동
2. 다음 플러그인 설치:
   - Flutter
   - Dart

### 5단계: 설치 검증 (10분)

#### Flutter Doctor 실행
```bash
flutter doctor
```

**정상적인 결과 예시**:
```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.24.3, on macOS 12.0.0 21A5534d darwin-x64, locale ko-KR)
[✓] Android toolchain - develop for Android devices (Android SDK version 33.0.0)
[✓] Xcode - develop for iOS and macOS (Xcode 14.0)
[✓] Chrome - develop for the web
[✓] Android Studio (version 2022.3)
[✓] VS Code (version 1.73.0)
[✓] Connected device (2 available)
[✓] HTTP Host Availability

• No issues found!
```

#### 문제 해결
- **❌ 표시가 있는 경우**: `flutter doctor -v`로 자세한 정보 확인
- **Android 라이센스 문제**: `flutter doctor --android-licenses` 재실행
- **PATH 문제**: 터미널 재시작 후 다시 확인

### 6단계: 테스트 앱 생성 (15분)

#### 새 Flutter 프로젝트 생성
```bash
# 테스트용 프로젝트 생성
flutter create test_app
cd test_app

# 의존성 설치
flutter pub get
```

#### 앱 실행 테스트

**Android 에뮬레이터에서 실행**:
```bash
# 에뮬레이터 목록 확인
flutter emulators

# 에뮬레이터 실행 (이름은 실제 에뮬레이터 이름으로 변경)
flutter emulators --launch Pixel_4_API_30

# 앱 실행
flutter run
```

**iOS 시뮬레이터에서 실행** (macOS만):
```bash
# iOS 시뮬레이터 실행
open -a Simulator

# 앱 실행
flutter run
```

## 🔧 추가 도구 설정

### Git 설정
```bash
# Git 전역 설정
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Git 에디터 설정 (선택사항)
git config --global core.editor "code --wait"  # VS Code 사용 시
```

### 개발 도구 추천

#### 터미널 도구
- **macOS**: iTerm2 + Oh My Zsh
- **Windows**: Windows Terminal
- **Linux**: 기본 터미널 또는 Terminator

#### 유용한 VS Code 설정
```json
// settings.json에 추가
{
  "dart.flutterSdkPath": "/path/to/flutter",
  "dart.closingLabels": true,
  "dart.previewFlutterUiGuides": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  }
}
```

## ✅ 완료 기준

다음을 모두 확인했다면 환경 설정이 완료된 것입니다:

- [ ] `flutter doctor` 실행 시 모든 항목이 ✓ 표시됨
- [ ] Android 에뮬레이터에서 테스트 앱 실행 성공
- [ ] iOS 시뮬레이터에서 테스트 앱 실행 성공 (macOS)
- [ ] IDE에서 Flutter 프로젝트 열기 가능
- [ ] Hot Reload 기능 정상 작동

## 🚨 흔한 문제와 해결책

### Android Studio 관련
**문제**: "Android license status unknown" 오류
```bash
# 해결책
flutter doctor --android-licenses
```

**문제**: SDK를 찾을 수 없음
- Android Studio > SDK Manager에서 Android SDK 설치 확인
- ANDROID_HOME 환경 변수 설정 확인

### Flutter 관련
**문제**: "Flutter not found" 오류
- PATH 환경 변수 설정 확인
- 터미널 재시작

**문제**: 의존성 오류
```bash
# 해결책
flutter clean
flutter pub get
```

### iOS 관련 (macOS)
**문제**: "No development team selected" 오류
- Xcode에서 Apple ID로 로그인
- 개발 팀 선택

**문제**: CocoaPods 설치 오류
```bash
# 해결책
sudo gem install --user-install ffi -- --enable-libffi-alloc
sudo gem install cocoapods
```

## 🎓 학습 리소스

### 공식 문서
- [Flutter 공식 문서](https://docs.flutter.dev/)
- [Dart 언어 가이드](https://dart.dev/guides)

### 추천 학습 자료
- Flutter 공식 Codelab
- Flutter Widget of the Week (YouTube)
- Flutter 공식 예제 앱들

## 📞 도움 요청

환경 설정에 문제가 있다면:
1. `flutter doctor -v` 결과를 팀원과 공유
2. 오류 메시지 전체를 캡처해서 공유
3. 시스템 정보 (OS, 버전) 함께 제공

---

← [기술 스택](02-tech-stack.md) | [프로젝트 설정](04-project-setup.md) →