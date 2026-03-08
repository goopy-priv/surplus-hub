# 트러블슈팅 가이드

## 🎯 이 문서의 목적
- 개발 중 자주 발생하는 문제의 해결 방법 제시
- 단계별 문제 해결 접근법 안내
- 에러 메시지별 구체적인 솔루션 제공

## 🚨 일반적인 문제 해결 순서

### 1단계: 기본 확인사항
```bash
# Flutter 버전 확인
flutter --version

# 프로젝트 상태 확인
flutter doctor

# 캐시 클리어
flutter clean
flutter pub get
```

### 2단계: 에러 로그 확인
- **VS Code**: 디버그 콘솔 확인
- **Android Studio**: Run 탭 확인  
- **터미널**: `flutter run -v` (상세 로그)

### 3단계: 점진적 문제 분리
- 최근 변경사항 되돌리기
- 문제가 되는 코드 범위 좁히기
- 다른 기기/에뮬레이터에서 테스트

## 💻 환경 설정 문제

### Flutter Doctor 오류

#### "✗ Android toolchain"
**문제**: Android SDK를 찾을 수 없음
```bash
# 해결책 1: Android 라이센스 동의
flutter doctor --android-licenses

# 해결책 2: Android SDK 경로 확인
export ANDROID_HOME=/path/to/android/sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# 해결책 3: Android Studio에서 SDK 재설치
# File > Settings > Appearance & Behavior > System Settings > Android SDK
```

#### "✗ Xcode" (macOS)
**문제**: Xcode 설치 또는 설정 문제
```bash
# 해결책 1: Xcode 설치 확인
xcode-select -p

# 해결책 2: Xcode 라이센스 동의
sudo xcodebuild -license accept

# 해결책 3: Command Line Tools 설치
xcode-select --install
```

#### "✗ VS Code"
**문제**: Flutter 확장 프로그램 미설치
```bash
# 해결책: VS Code에서 Flutter 확장 프로그램 설치
# Extensions > "Flutter" 검색 > 설치
# "Dart" 확장 프로그램도 자동 설치됨
```

### 의존성 설치 문제

#### "pub get failed"
```bash
# 문제: pubspec.yaml 구문 오류 또는 네트워크 문제

# 해결책 1: pubspec.yaml 문법 확인 (들여쓰기 중요)
# 해결책 2: 캐시 클리어
flutter pub cache repair
flutter clean
flutter pub get

# 해결책 3: 네트워크 확인
# 회사 방화벽 또는 프록시 설정 확인
```

#### "version solving failed"
```bash
# 문제: 패키지 버전 충돌

# 해결책 1: pubspec.lock 삭제 후 재설치
rm pubspec.lock
flutter pub get

# 해결책 2: 문제가 되는 패키지 버전 조정
dependencies:
  package_name: ^1.0.0  # 더 넓은 버전 범위 허용
```

## 🏗️ 빌드 오류

### Android 빌드 오류

#### "Gradle task assembleDebug failed"
```bash
# 문제: Gradle 빌드 실패

# 해결책 1: Gradle 캐시 클리어
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get

# 해결책 2: Gradle 래퍼 업데이트
cd android
./gradlew wrapper --gradle-version=7.4
```

#### "Minimum SDK version"
```bash
# 문제: minSdkVersion이 낮음

# 해결책: android/app/build.gradle 수정
android {
    compileSdkVersion 33
    
    defaultConfig {
        minSdkVersion 21  // 이 값을 높이기
        targetSdkVersion 33
    }
}
```

#### "Duplicate class found"
```bash
# 문제: 중복 의존성

# 해결책: android/app/build.gradle에 exclude 추가
dependencies {
    implementation('com.example.library') {
        exclude group: 'com.android.support'
    }
}
```

### iOS 빌드 오류

#### "CocoaPods not installed"
```bash
# 해결책: CocoaPods 설치
sudo gem install cocoapods
cd ios
pod install
```

#### "No development team selected"
```bash
# 해결책: Xcode에서 팀 설정
# 1. ios/Runner.xcworkspace 열기
# 2. Runner > Signing & Capabilities
# 3. Team 선택 (Apple ID 추가 필요)
```

#### "Pod install failed"
```bash
# 해결책 1: CocoaPods 캐시 클리어
cd ios
pod deintegrate
pod install --repo-update

# 해결책 2: iOS Deployment Target 확인
# ios/Podfile에서 platform :ios, '11.0' 이상 설정
```

## 🚀 런타임 오류

### 일반적인 런타임 에러

#### "RenderFlex overflowed"
**문제**: UI가 화면을 벗어남
```dart
// 문제 코드
Row(
  children: [
    Text('Very long text that might overflow'),
    Text('Another long text'),
  ],
)

// 해결책 1: Flexible 사용
Row(
  children: [
    Flexible(
      child: Text('Very long text that might overflow'),
    ),
    Flexible(
      child: Text('Another long text'),
    ),
  ],
)

// 해결책 2: SingleChildScrollView 사용
SingleChildScrollView(
  scrollDirection: Axis.horizontal,
  child: Row(
    children: [
      Text('Very long text that might overflow'),
      Text('Another long text'),
    ],
  ),
)
```

#### "Null check operator used on null value"
**문제**: null 값에 ! 연산자 사용
```dart
// 문제 코드
String text = getValue()!;  // getValue()가 null을 반환하는 경우

// 해결책 1: null 체크
String? value = getValue();
if (value != null) {
  String text = value;
}

// 해결책 2: ?? 연산자 사용
String text = getValue() ?? 'Default value';
```

#### "setState() called after dispose()"
**문제**: 위젯이 dispose된 후 setState 호출
```dart
// 문제 코드
class MyWidget extends StatefulWidget {
  Future<void> loadData() async {
    final data = await api.getData();
    setState(() {  // 위젯이 이미 dispose되었을 수 있음
      this.data = data;
    });
  }
}

// 해결책: mounted 체크
Future<void> loadData() async {
  final data = await api.getData();
  if (mounted) {  // 위젯이 여전히 활성 상태인지 확인
    setState(() {
      this.data = data;
    });
  }
}
```

### 네비게이션 오류

#### "GoRouter not found"
```dart
// 문제: context에서 GoRouter에 접근할 수 없음

// 해결책: MaterialApp.router 확인
MaterialApp.router(
  routerConfig: AppRouter.router,  // 이 부분이 설정되어 있는지 확인
)
```

#### "Route not found"
```bash
# 문제: 정의되지 않은 라우트 접근

# 해결책: AppRouter에 라우트 추가 확인
GoRoute(
  path: '/your-path',
  builder: (context, state) => YourPage(),
)
```

### 상태 관리 오류

#### "BlocProvider not found"
```dart
// 문제: BLoC에 접근할 수 없음

// 해결책: BlocProvider 확인
BlocProvider<HomeBloc>(
  create: (context) => HomeBloc(),
  child: HomePage(),  // 이 위젯에서만 BLoC 접근 가능
)

// 또는 context.read<HomeBloc>() 대신 Repository DI 사용 검토
```

#### "Bad state: add event after close"
```dart
// 문제: 이미 닫힌 BLoC에 이벤트 추가

// 해결책: BLoC 생명주기 확인
if (!bloc.isClosed) {
  bloc.add(YourEvent());
}
```

## 🎨 UI 문제

### 성능 문제

#### "Jank detected"
**문제**: UI가 버벅거림
```dart
// 문제 코드: build에서 무거운 작업
Widget build(BuildContext context) {
  final expensiveData = heavyCalculation();  // 매번 계산
  return Text(expensiveData);
}

// 해결책 1: 계산 결과 캐싱
class MyWidget extends StatefulWidget {
  String? _cachedData;
  
  Widget build(BuildContext context) {
    _cachedData ??= heavyCalculation();  // 한 번만 계산
    return Text(_cachedData!);
  }
}

// 해결책 2: FutureBuilder 사용
FutureBuilder<String>(
  future: heavyCalculationAsync(),
  builder: (context, snapshot) {
    if (snapshot.hasData) {
      return Text(snapshot.data!);
    }
    return CircularProgressIndicator();
  },
)
```

#### "ListView 성능 저하"
```dart
// 문제 코드: ListView 생성자 사용
ListView(
  children: items.map((item) => ItemWidget(item)).toList(),  // 모든 아이템 생성
)

// 해결책: ListView.builder 사용
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {  // 필요한 아이템만 생성
    return ItemWidget(items[index]);
  },
)
```

### 레이아웃 문제

#### "키보드가 올라올 때 UI 깨짐"
```dart
// 해결책 1: resizeToAvoidBottomInset 사용
Scaffold(
  resizeToAvoidBottomInset: true,  // 기본값
  body: YourContent(),
)

// 해결책 2: SingleChildScrollView 사용
Scaffold(
  body: SingleChildScrollView(
    child: YourForm(),
  ),
)
```

#### "SafeArea 문제"
```dart
// 문제: 노치나 상태바 영역에 UI가 겹침

// 해결책: SafeArea 사용
SafeArea(
  child: YourWidget(),
)

// 또는 MediaQuery 사용
Container(
  margin: EdgeInsets.only(
    top: MediaQuery.of(context).padding.top,
  ),
  child: YourWidget(),
)
```

## 🌐 네트워크 문제

### API 호출 오류

#### "SocketException: Failed host lookup"
```dart
// 문제: 네트워크 연결 실패

// 해결책 1: 네트워크 권한 확인 (Android)
// android/app/src/main/AndroidManifest.xml
<uses-permission android:name="android.permission.INTERNET" />

// 해결책 2: HTTP 대신 HTTPS 사용
// iOS는 기본적으로 HTTP 차단

// 해결책 3: 타임아웃 설정
final dio = Dio();
dio.options.connectTimeout = Duration(seconds: 5);
dio.options.receiveTimeout = Duration(seconds: 3);
```

#### "Certificate verify failed"
```dart
// 문제: SSL 인증서 오류

// 해결책 1: 올바른 인증서 사용 (권장)
// 해결책 2: 개발 환경에서만 인증서 무시 (주의!)
class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback = (X509Certificate cert, String host, int port) => true;
  }
}

// main.dart에서
HttpOverrides.global = MyHttpOverrides();
```

## 📱 플랫폼별 문제

### Android

#### "Cleartext HTTP traffic not permitted"
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<application
    android:usesCleartextTraffic="true">  <!-- HTTP 허용 -->
```

#### "INSTALL_FAILED_INSUFFICIENT_STORAGE"
```bash
# 해결책: 에뮬레이터 저장공간 확대
# AVD Manager > 해당 에뮬레이터 > Edit > Advanced Settings > Internal Storage 증가
```

### iOS

#### "Thread 1: signal SIGABRT"
```bash
# 해결책 1: iOS 시뮬레이터 재시작
# 해결책 2: 프로젝트 클린 빌드
flutter clean
cd ios
rm -rf build/
cd ..
flutter run
```

#### "Flutter iOS build hangs"
```bash
# 해결책: CocoaPods 재설치
cd ios
rm -rf Pods/
rm Podfile.lock
pod install --repo-update
```

## 🛠️ 개발 도구 문제

### VS Code

#### "Flutter commands not working"
```bash
# 해결책 1: Flutter 확장 프로그램 재설치
# 해결책 2: Command Palette에서 "Flutter: Reload"

# 해결책 3: settings.json 확인
{
  "dart.flutterSdkPath": "/path/to/flutter"
}
```

### Hot Reload 문제

#### "Hot reload not working"
```bash
# 해결책 1: 파일 저장 확인
# 해결책 2: Hot Restart 시도 (R 키)
# 해결책 3: 완전 재시작
flutter run
```

## 🔍 디버깅 팁

### 로그 확인
```dart
// 개발 중 로그
print('Debug: $value');
debugPrint('Debug: $value');  // 릴리스에서 자동 제거

// 조건부 로그
assert(() {
  print('Debug mode only');
  return true;
}());
```

### Flutter Inspector 사용
1. VS Code: `Ctrl+Shift+P` → "Flutter: Open Widget Inspector"
2. 위젯 트리 시각화
3. 선택한 위젯의 속성 확인

### 성능 프로파일링
```bash
# 성능 분석
flutter run --profile
# Flutter DevTools에서 Performance 탭 확인
```

## 📞 추가 도움

### 문제가 해결되지 않는다면
1. **Flutter 공식 문서**: https://docs.flutter.dev
2. **Stack Overflow**: 에러 메시지로 검색
3. **Flutter GitHub Issues**: 알려진 버그 확인
4. **팀 슬랙**: 동료에게 도움 요청
5. **1:1 멘토링**: 시니어 개발자와 상담

### 효과적인 도움 요청 방법
- **에러 메시지 전문** 첨부
- **재현 단계** 상세 설명  
- **환경 정보** (OS, Flutter 버전 등)
- **시도한 해결책** 명시
- **관련 코드** 일부 공유

---

← [FAQ](15-faq.md) | [메인 문서](README.md) →