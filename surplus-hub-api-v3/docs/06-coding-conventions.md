# 코딩 컨벤션

## 🎯 학습 목표
- 프로젝트의 코딩 스타일과 규칙을 이해한다
- 일관된 코드 작성 방법을 익힌다
- Dart/Flutter 베스트 프랙티스를 적용한다
- 코드 리뷰 시 체크할 포인트를 안다

**예상 소요 시간**: 1-2시간

## 📏 기본 규칙

### 린팅 규칙
프로젝트는 `flutter_lints` 패키지의 엄격한 규칙을 따릅니다.

```yaml
# analysis_options.yaml
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    # 추가 규칙들이 여기에 올 예정
```

### 자동 포맷팅
- **자동 저장 시 포맷팅 활성화** (권장)
- `dart format .` 명령어로 전체 코드 포맷팅
- IDE에서 `Shift + Alt + F` (VS Code) 또는 `Cmd + Alt + L` (Android Studio)

## 📝 명명 규칙

### 1. 클래스명 (PascalCase)
```dart
// ✅ 좋은 예시
class MaterialItem {}
class UserProfile {}
class MaterialDetailPage {}

// ❌ 나쁜 예시
class materialItem {}
class material_item {}
class MATERIAL_ITEM {}
```

### 2. 변수/함수명 (camelCase)
```dart
// ✅ 좋은 예시
String userName;
int itemCount;
void calculateTotal() {}
bool isLoading;

// ❌ 나쁜 예시
String user_name;
String UserName;
void CalculateTotal() {}
```

### 3. 상수 (lowerCamelCase)
```dart
// ✅ 좋은 예시
class AppColors {
  static const Color primary = Color(0xFF2563EB);
  static const Color backgroundPrimary = Color(0xFFFFFFFF);
}

// ❌ 나쁜 예시
static const Color PRIMARY = Color(0xFF2563EB);
static const Color BACKGROUND_PRIMARY = Color(0xFFFFFFFF);
```

### 4. 파일명 (snake_case)
```dart
// ✅ 좋은 예시
material_item.dart
user_profile.dart
material_detail_page.dart

// ❌ 나쁜 예시
MaterialItem.dart
materialItem.dart
material-item.dart
```

### 5. 폴더명 (snake_case)
```
// ✅ 좋은 예시
features/
material_detail/
data_sources/

// ❌ 나쁜 예시
Features/
materialDetail/
data-sources/
```

## 🏗️ 클래스 구조

### Widget 클래스 구조
```dart
class HomePage extends StatefulWidget {
  // 1. 생성자
  const HomePage({
    super.key,
    required this.title,  // required 파라미터
    this.subtitle,        // optional 파라미터
  });

  // 2. 프로퍼티 (final로 선언)
  final String title;
  final String? subtitle;

  // 3. createState()
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  // 1. 상태 변수들
  bool _isLoading = false;
  List<MaterialItem> _materials = [];

  // 2. 라이프사이클 메서드
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  // 3. 이벤트 핸들러 (private 메서드)
  void _loadData() {
    // 구현
  }

  void _onItemTap(MaterialItem item) {
    // 구현
  }

  // 4. UI 빌드 메서드들
  Widget _buildHeader() {
    // 구현
    return Container();
  }

  Widget _buildMaterialList() {
    // 구현
    return ListView();
  }

  // 5. build 메서드 (마지막)
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // 구현
    );
  }
}
```

### Entity 클래스 구조
```dart
class MaterialItem extends Equatable {
  // 1. 생성자
  const MaterialItem({
    required this.id,
    required this.title,
    required this.price,
    this.categoryPath,
  });

  // 2. 프로퍼티 (모두 final)
  final String id;
  final String title;
  final String price;
  final List<String>? categoryPath;

  // 3. Getter 메서드
  int get priceAsNumber {
    return int.tryParse(price.replaceAll(RegExp(r'[^0-9]'), '')) ?? 0;
  }

  // 4. 일반 메서드
  bool matches(List<String>? categoryPath) {
    // 구현
    return false;
  }

  // 5. copyWith 메서드
  MaterialItem copyWith({
    String? id,
    String? title,
    // ... 다른 파라미터들
  }) {
    return MaterialItem(
      id: id ?? this.id,
      title: title ?? this.title,
      // ... 다른 프로퍼티들
    );
  }

  // 6. Equatable props (마지막)
  @override
  List<Object?> get props => [
    id,
    title,
    price,
    categoryPath,
  ];
}
```

## 📐 코드 스타일

### 1. 임포트 정렬
```dart
// 1. Dart 기본 라이브러리
import 'dart:convert';

// 2. Flutter 라이브러리
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// 3. 외부 패키지 (알파벳 순)
import 'package:equatable/equatable.dart';
import 'package:go_router/go_router.dart';

// 4. 프로젝트 내부 파일 (상대 경로 사용)
import '../../core/theme/app_colors.dart';
import '../../shared/widgets/material_card.dart';
```

### 2. 문자열 처리
```dart
// ✅ 좋은 예시 - 단일 따옴표 사용
final String title = 'Surplus Hub';
final String message = '자재를 등록했습니다.';

// 문자열 보간 사용
final String greeting = '안녕하세요, $userName님';
final String info = '총 ${items.length}개의 자재가 있습니다.';

// ❌ 나쁜 예시 - 이중 따옴표 (특별한 경우 제외)
final String title = "Surplus Hub";  // 일반적으로 피함

// ✅ 이중 따옴표를 사용하는 경우
final String message = "I'm using single quote inside";
```

### 3. 리스트와 맵
```dart
// ✅ 좋은 예시 - trailing comma 사용
final List<String> categories = [
  'metal',
  'wood',
  'plastic',    // trailing comma
];

final Map<String, Color> categoryColors = {
  'metal': Colors.grey,
  'wood': Colors.brown,
  'plastic': Colors.green,    // trailing comma
};

// Widget 파라미터도 동일
return Container(
  margin: const EdgeInsets.all(16),
  padding: const EdgeInsets.symmetric(
    horizontal: 12,
    vertical: 8,
  ),    // trailing comma
);
```

### 4. 조건문과 반복문
```dart
// ✅ 좋은 예시 - 명확한 조건
if (materials.isNotEmpty) {
  return MaterialList(materials: materials);
}

if (user?.isLoggedIn == true) {
  showProfile();
}

// null 체크
final String displayName = user?.name ?? 'Unknown';

// ❌ 나쁜 예시
if (materials.length > 0) {    // isNotEmpty 사용 권장
  return MaterialList(materials: materials);
}

if (user != null && user.isLoggedIn) {    // ?. 연산자 사용 권장
  showProfile();
}
```

### 5. 비동기 처리
```dart
// ✅ 좋은 예시
Future<List<MaterialItem>> loadMaterials() async {
  try {
    final response = await apiService.getMaterials();
    return response.map((json) => MaterialItem.fromJson(json)).toList();
  } catch (e) {
    debugPrint('Failed to load materials: $e');
    rethrow;
  }
}

// 사용 시
void _loadMaterials() async {
  setState(() {
    _isLoading = true;
  });
  
  try {
    final materials = await loadMaterials();
    setState(() {
      _materials = materials;
      _isLoading = false;
    });
  } catch (e) {
    setState(() {
      _isLoading = false;
    });
    _showErrorMessage();
  }
}
```

## 🎨 Widget 작성 가이드

### 1. Widget 분리 원칙
```dart
// ✅ 좋은 예시 - 복잡한 UI는 별도 위젯으로 분리
class HomePage extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(),    // 메서드로 분리
      body: Column(
        children: [
          FilterBar(              // 별도 위젯으로 분리
            onSortChanged: _onSortChanged,
          ),
          Expanded(
            child: _buildMaterialList(),    // 메서드로 분리
          ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    // AppBar 구현
  }

  Widget _buildMaterialList() {
    // 리스트 구현
  }
}

// ❌ 나쁜 예시 - build 메서드가 너무 복잡
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: Text('Title'),
      actions: [
        IconButton(
          onPressed: () {
            // 긴 로직...
          },
          icon: Icon(Icons.search),
        ),
        // ... 더 많은 복잡한 코드
      ],
    ),
    body: Column(
      children: [
        Container(
          // 복잡한 필터 바 구현...
        ),
        Expanded(
          child: ListView.builder(
            // 복잡한 리스트 구현...
          ),
        ),
      ],
    ),
  );
}
```

### 2. 상수 사용
```dart
// ✅ 좋은 예시 - 하드코딩된 값 대신 상수 사용
class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundPrimary,
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Text(
          'Welcome',
          style: AppTextStyles.heading1,
        ),
      ),
    );
  }
}

// ❌ 나쁜 예시 - 하드코딩된 값들
Widget build(BuildContext context) {
  return Scaffold(
    backgroundColor: Color(0xFFFFFFFF),    // 상수 사용 권장
    body: Padding(
      padding: const EdgeInsets.all(16),   // 상수 사용 권장
      child: Text(
        'Welcome',
        style: TextStyle(             // 테마 사용 권장
          fontSize: 24,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),
  );
}
```

### 3. Key 사용
```dart
// ✅ 좋은 예시 - 동적 리스트에서 Key 사용
ListView.builder(
  itemCount: materials.length,
  itemBuilder: (context, index) {
    final material = materials[index];
    return MaterialCard(
      key: ValueKey('material-${material.id}'),    // 고유한 Key 사용
      material: material,
      onTap: () => _onMaterialTap(material),
    );
  },
);

// StatefulWidget에서도 Key 사용
class MaterialCard extends StatefulWidget {
  const MaterialCard({
    super.key,              // super.key 전달
    required this.material,
    required this.onTap,
  });
}
```

## 📝 주석 작성 가이드

### 1. 클래스 주석
```dart
/// 재료 아이템 엔티티
/// React Native MaterialItem 인터페이스의 Flutter 구현
class MaterialItem extends Equatable {
  // 구현
}

/// 홈 화면
/// React Native index.tsx의 Flutter 구현
class HomePage extends StatefulWidget {
  // 구현
}
```

### 2. 메서드 주석
```dart
/// 가격 문자열을 숫자로 변환합니다.
/// 
/// 예: "150,000원" → 150000
int get priceAsNumber {
  return int.tryParse(price.replaceAll(RegExp(r'[^0-9]'), '')) ?? 0;
}

/// 카테고리 경로와 매칭되는지 확인합니다.
/// 
/// [categoryPath]가 null이면 모든 카테고리와 매칭됩니다.
bool matches(List<String>? categoryPath) {
  // 구현
}
```

### 3. TODO 주석
```dart
class HomePage extends StatefulWidget {
  void _onSearchTap() {
    // TODO: 검색 기능 구현
    debugPrint('Search tapped');
  }

  void _onNotificationTap() {
    // TODO: 알림 기능 구현
    debugPrint('Notification tapped');
  }
}
```

## 🔍 코드 리뷰 체크리스트

### 필수 체크 포인트
- [ ] 린팅 오류가 없는가?
- [ ] 명명 규칙을 따르는가?
- [ ] 하드코딩된 값 대신 상수를 사용하는가?
- [ ] Widget이 적절히 분리되어 있는가?
- [ ] null safety를 고려했는가?
- [ ] 불필요한 import가 없는가?
- [ ] trailing comma를 적절히 사용했는가?

### 성능 체크 포인트
- [ ] ListView.builder를 사용했는가? (대신 ListView 생성자 사용 금지)
- [ ] const 생성자를 적절히 사용했는가?
- [ ] 불필요한 rebuild가 발생하지 않는가?
- [ ] Key를 적절히 사용했는가?

### 유지보수성 체크 포인트
- [ ] 코드가 읽기 쉬운가?
- [ ] 주석이 적절히 작성되었는가?
- [ ] 매직 넘버/문자열이 없는가?
- [ ] 메서드가 너무 길지 않은가? (50줄 이하 권장)

## 🛠️ IDE 설정

### VS Code 설정 (settings.json)
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true,
    "source.organizeImports": true
  },
  "dart.closingLabels": true,
  "dart.previewFlutterUiGuides": true,
  "editor.rulers": [80],
  "files.trimTrailingWhitespace": true
}
```

### 자동 완성 snippets
```json
// Dart snippets 예시
{
  "StatefulWidget": {
    "prefix": "stful",
    "body": [
      "class ${1:WidgetName} extends StatefulWidget {",
      "  const ${1:WidgetName}({super.key});",
      "",
      "  @override",
      "  State<${1:WidgetName}> createState() => _${1:WidgetName}State();",
      "}",
      "",
      "class _${1:WidgetName}State extends State<${1:WidgetName}> {",
      "  @override",
      "  Widget build(BuildContext context) {",
      "    return ${2:Container()};",
      "  }",
      "}"
    ]
  }
}
```

## ✅ 컨벤션 준수 확인

다음을 모두 지킨다면 코딩 컨벤션을 잘 따르는 것입니다:

- [ ] `flutter analyze` 실행 시 오류 없음
- [ ] 모든 명명 규칙 준수
- [ ] Widget 구조가 체계적임
- [ ] 상수를 적절히 사용함
- [ ] 주석이 의미있게 작성됨
- [ ] 코드가 읽기 쉽고 일관적임

---

← [프로젝트 구조](05-project-structure.md) | [기능 개발 가이드](07-feature-development.md) →