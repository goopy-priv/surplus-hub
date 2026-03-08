# 기능 개발 가이드

## 🎯 학습 목표
- 새로운 기능을 추가하는 전체 과정을 이해한다
- Clean Architecture 패턴으로 기능을 구현할 수 있다
- 기존 코드 스타일을 유지하며 개발할 수 있다
- 코드 예시를 통해 실제 구현 방법을 익힌다

**예상 소요 시간**: 2-3시간

## 🚀 기능 개발 워크플로우

### 1단계: 요구사항 분석 (15분)
- 기능의 목적과 범위 파악
- UI/UX 요구사항 정리
- 데이터 구조 설계
- API 스펙 확인 (있는 경우)

### 2단계: 설계 (30분)
- Entity 설계 (Domain Layer)
- UI 화면 구조 설계 (Presentation Layer)
- 데이터 흐름 설계
- 필요한 위젯 목록 작성

### 3단계: 구현 (1-2시간)
- Domain Layer → Presentation Layer 순서로 구현
- 테스트 가능한 단위로 나누어 개발
- 기존 컴포넌트 재사용 우선

### 4단계: 테스트 및 검증 (30분)
- 기능 동작 테스트
- UI 테스트
- 코드 품질 검증
- 성능 확인

## 📝 실제 예시: 알림 기능 추가

### 요구사항
- 사용자가 받은 알림을 목록으로 표시
- 읽음/안읽음 상태 구분
- 알림 타입별 아이콘 표시
- 알림 클릭 시 해당 페이지로 이동

### 1단계: Entity 설계

```dart
// lib/features/notification/domain/entities/notification_item.dart
import 'package:equatable/equatable.dart';

/// 알림 아이템 엔티티
class NotificationItem extends Equatable {
  const NotificationItem({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    required this.createdAt,
    required this.isRead,
    this.targetId,
    this.imageUrl,
  });

  final String id;
  final String title;
  final String message;
  final NotificationType type;
  final DateTime createdAt;
  final bool isRead;
  final String? targetId;  // 이동할 대상의 ID (자재 ID 등)
  final String? imageUrl;

  @override
  List<Object?> get props => [
    id,
    title,
    message,
    type,
    createdAt,
    isRead,
    targetId,
    imageUrl,
  ];

  NotificationItem copyWith({
    String? id,
    String? title,
    String? message,
    NotificationType? type,
    DateTime? createdAt,
    bool? isRead,
    String? targetId,
    String? imageUrl,
  }) {
    return NotificationItem(
      id: id ?? this.id,
      title: title ?? this.title,
      message: message ?? this.message,
      type: type ?? this.type,
      createdAt: createdAt ?? this.createdAt,
      isRead: isRead ?? this.isRead,
      targetId: targetId ?? this.targetId,
      imageUrl: imageUrl ?? this.imageUrl,
    );
  }
}

/// 알림 타입
enum NotificationType {
  chat,      // 채팅 메시지
  like,      // 좋아요
  comment,   // 댓글
  system,    // 시스템 알림
}

/// 알림 타입별 설정
extension NotificationTypeExtension on NotificationType {
  String get displayName {
    switch (this) {
      case NotificationType.chat:
        return '채팅';
      case NotificationType.like:
        return '좋아요';
      case NotificationType.comment:
        return '댓글';
      case NotificationType.system:
        return '시스템';
    }
  }

  IconData get icon {
    switch (this) {
      case NotificationType.chat:
        return Icons.chat;
      case NotificationType.like:
        return Icons.favorite;
      case NotificationType.comment:
        return Icons.comment;
      case NotificationType.system:
        return Icons.info;
    }
  }

  Color get color {
    switch (this) {
      case NotificationType.chat:
        return AppColors.chat;
      case NotificationType.like:
        return AppColors.liked;
      case NotificationType.comment:
        return AppColors.info;
      case NotificationType.system:
        return AppColors.primary;
    }
  }
}
```

### 2단계: 페이지 구현

```dart
// lib/features/notification/presentation/pages/notification_page.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../domain/entities/notification_item.dart';
import '../widgets/notification_card.dart';

class NotificationPage extends StatefulWidget {
  const NotificationPage({super.key});

  @override
  State<NotificationPage> createState() => _NotificationPageState();
}

class _NotificationPageState extends State<NotificationPage> {
  List<NotificationItem> _notifications = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  void _loadNotifications() {
    setState(() {
      _isLoading = true;
    });

    // TODO: 실제 API 호출로 대체
    _loadSampleNotifications();
  }

  void _loadSampleNotifications() {
    // 샘플 데이터
    final sampleNotifications = [
      NotificationItem(
        id: '1',
        title: '새로운 채팅 메시지',
        message: '김건설님이 시멘트 관련 문의를 보내셨습니다.',
        type: NotificationType.chat,
        createdAt: DateTime.now().subtract(const Duration(minutes: 5)),
        isRead: false,
        targetId: 'chat_1',
      ),
      NotificationItem(
        id: '2',
        title: '좋아요 알림',
        message: '내가 등록한 "시멘트 50포"에 좋아요가 1개 추가되었습니다.',
        type: NotificationType.like,
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
        isRead: true,
        targetId: 'material_123',
      ),
      // 더 많은 샘플 데이터...
    ];

    setState(() {
      _notifications = sampleNotifications;
      _isLoading = false;
    });
  }

  void _onNotificationTap(NotificationItem notification) {
    // 알림을 읽음으로 표시
    if (!notification.isRead) {
      _markAsRead(notification.id);
    }

    // 해당 페이지로 이동
    _navigateToTarget(notification);
  }

  void _markAsRead(String notificationId) {
    setState(() {
      _notifications = _notifications.map((notification) {
        if (notification.id == notificationId) {
          return notification.copyWith(isRead: true);
        }
        return notification;
      }).toList();
    });

    // TODO: API 호출로 서버에 상태 업데이트
  }

  void _navigateToTarget(NotificationItem notification) {
    // TODO: 알림 타입과 targetId에 따라 적절한 페이지로 이동
    switch (notification.type) {
      case NotificationType.chat:
        // context.push('/chat/${notification.targetId}');
        break;
      case NotificationType.like:
      case NotificationType.comment:
        // context.push('/material/${notification.targetId}');
        break;
      case NotificationType.system:
        // 특별한 동작 없음
        break;
    }
  }

  void _markAllAsRead() {
    setState(() {
      _notifications = _notifications.map((notification) {
        return notification.copyWith(isRead: true);
      }).toList();
    });

    // TODO: API 호출
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.grey[50],
      appBar: _buildAppBar(),
      body: _buildBody(),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    final unreadCount = _notifications.where((n) => !n.isRead).length;
    
    return AppBar(
      title: Text(
        '알림',
        style: AppTextStyles.heading2,
      ),
      backgroundColor: AppColors.backgroundPrimary,
      elevation: 0,
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(1),
        child: Container(
          height: 1,
          color: AppColors.borderPrimary,
        ),
      ),
      actions: [
        if (unreadCount > 0)
          TextButton(
            onPressed: _markAllAsRead,
            child: Text(
              '모두 읽음',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_notifications.isEmpty) {
      return _buildEmptyState();
    }

    return _buildNotificationList();
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.notifications_none,
            size: 64,
            color: AppColors.grey[400],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            '알림이 없습니다',
            style: AppTextStyles.bodyLarge.copyWith(
              color: AppColors.grey[600],
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            '새로운 알림이 오면 여기에 표시됩니다',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationList() {
    return RefreshIndicator(
      onRefresh: () async {
        _loadNotifications();
      },
      child: ListView.builder(
        padding: const EdgeInsets.only(
          top: AppSpacing.sm,
          bottom: AppSpacing.xl,
        ),
        itemCount: _notifications.length,
        itemBuilder: (context, index) {
          final notification = _notifications[index];
          return NotificationCard(
            key: ValueKey('notification-${notification.id}'),
            notification: notification,
            onTap: () => _onNotificationTap(notification),
          );
        },
      ),
    );
  }
}
```

### 3단계: 위젯 구현

```dart
// lib/features/notification/presentation/widgets/notification_card.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../domain/entities/notification_item.dart';

class NotificationCard extends StatelessWidget {
  const NotificationCard({
    super.key,
    required this.notification,
    required this.onTap,
  });

  final NotificationItem notification;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: notification.isRead 
            ? AppColors.backgroundPrimary 
            : AppColors.primaryLight.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: notification.isRead 
              ? AppColors.borderPrimary 
              : AppColors.primary.withValues(alpha: 0.2),
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildIcon(),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: _buildContent(),
              ),
              _buildReadIndicator(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIcon() {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: notification.type.color.withValues(alpha: 0.1),
        shape: BoxShape.circle,
      ),
      child: Icon(
        notification.type.icon,
        color: notification.type.color,
        size: 20,
      ),
    );
  }

  Widget _buildContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          notification.title,
          style: AppTextStyles.bodyLarge.copyWith(
            fontWeight: notification.isRead 
                ? FontWeight.normal 
                : FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          notification.message,
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          _formatTime(notification.createdAt),
          style: AppTextStyles.captionMedium.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildReadIndicator() {
    if (notification.isRead) {
      return const SizedBox.shrink();
    }

    return Container(
      width: 8,
      height: 8,
      decoration: const BoxDecoration(
        color: AppColors.primary,
        shape: BoxShape.circle,
      ),
    );
  }

  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return '방금 전';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}분 전';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}시간 전';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}일 전';
    } else {
      return '${dateTime.month}/${dateTime.day}';
    }
  }
}
```

### 4단계: 네비게이션 연결

```dart
// lib/core/navigation/app_router.dart에 추가
GoRoute(
  path: '/notifications',
  name: 'notifications',
  builder: (context, state) => const NotificationPage(),
),
```

### 5단계: 기존 UI에 연결

```dart
// lib/features/home/presentation/pages/home_page.dart의 AppBar 수정
AppBar(
  // ... 기존 코드
  actions: [
    // ... 기존 액션들
    IconButton(
      onPressed: () {
        context.push('/notifications');  // 이제 실제 페이지로 이동
      },
      icon: Icon(
        Icons.notifications_outlined,
        color: AppColors.grey[700],
      ),
    ),
  ],
),
```

## 🔄 기존 기능 수정 예시

### 기존 위젯에 새로운 기능 추가

```dart
// lib/shared/widgets/material_card.dart 수정 예시
class MaterialCard extends StatelessWidget {
  const MaterialCard({
    super.key,
    required this.material,
    required this.onTap,
    this.onLikeTap,        // 새로운 콜백 추가
    this.isLiked = false,  // 좋아요 상태 추가
  });

  final MaterialItem material;
  final VoidCallback onTap;
  final VoidCallback? onLikeTap;     // 새로운 프로퍼티
  final bool isLiked;                // 새로운 프로퍼티

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            children: [
              // ... 기존 UI
              
              // 새로운 액션 버튼 영역 추가
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // ... 기존 정보들
                  
                  // 좋아요 버튼 추가
                  if (onLikeTap != null)
                    IconButton(
                      onPressed: onLikeTap,
                      icon: Icon(
                        isLiked ? Icons.favorite : Icons.favorite_border,
                        color: isLiked ? AppColors.liked : AppColors.grey[500],
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

## 🧪 테스트 작성

### 단위 테스트 (Entity)
```dart
// test/features/notification/domain/entities/notification_item_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:surplus_hub_flutter/features/notification/domain/entities/notification_item.dart';

void main() {
  group('NotificationItem', () {
    test('should create notification item with required fields', () {
      // Arrange
      const notification = NotificationItem(
        id: '1',
        title: 'Test Title',
        message: 'Test Message',
        type: NotificationType.chat,
        createdAt: DateTime(2023, 1, 1),
        isRead: false,
      );

      // Assert
      expect(notification.id, '1');
      expect(notification.title, 'Test Title');
      expect(notification.isRead, false);
    });

    test('should support copyWith', () {
      // Arrange
      const original = NotificationItem(
        id: '1',
        title: 'Original Title',
        message: 'Original Message',
        type: NotificationType.chat,
        createdAt: DateTime(2023, 1, 1),
        isRead: false,
      );

      // Act
      final updated = original.copyWith(isRead: true);

      // Assert
      expect(updated.isRead, true);
      expect(updated.title, 'Original Title');  // 변경되지 않은 값 유지
    });
  });
}
```

### 위젯 테스트
```dart
// test/features/notification/presentation/widgets/notification_card_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:surplus_hub_flutter/features/notification/presentation/widgets/notification_card.dart';

void main() {
  group('NotificationCard', () {
    testWidgets('should display notification information', (tester) async {
      // Arrange
      const notification = NotificationItem(
        id: '1',
        title: 'Test Title',
        message: 'Test Message',
        type: NotificationType.chat,
        createdAt: DateTime(2023, 1, 1),
        isRead: false,
      );

      bool tapped = false;

      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NotificationCard(
              notification: notification,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('Test Title'), findsOneWidget);
      expect(find.text('Test Message'), findsOneWidget);
      
      // Tap test
      await tester.tap(find.byType(NotificationCard));
      expect(tapped, true);
    });
  });
}
```

## ✅ 개발 완료 체크리스트

새로운 기능을 개발했다면 다음을 확인하세요:

### 코드 품질
- [ ] 린팅 오류 없음 (`flutter analyze`)
- [ ] 코딩 컨벤션 준수
- [ ] 적절한 주석 작성
- [ ] 하드코딩된 값 없음

### 기능 검증
- [ ] 모든 기본 기능 정상 동작
- [ ] 에러 상황 처리 (네트워크 오류, 빈 데이터 등)
- [ ] 로딩 상태 표시
- [ ] 사용자 피드백 제공

### UI/UX
- [ ] 디자인 가이드라인 준수
- [ ] 반응형 레이아웃
- [ ] 접근성 고려
- [ ] 터치 타겟 크기 적절함

### 성능
- [ ] 불필요한 rebuild 없음
- [ ] 메모리 누수 없음
- [ ] 적절한 Key 사용
- [ ] 이미지 최적화

### 테스트
- [ ] 단위 테스트 작성
- [ ] 위젯 테스트 작성 (필요시)
- [ ] 수동 테스트 완료

## 🎓 다음 단계

기능 개발 가이드를 숙지했다면:
1. [상태 관리](08-state-management.md)로 BLoC 패턴 학습
2. [네비게이션](09-navigation.md)으로 Go Router 심화 학습
3. 실제 간단한 기능 구현해보기

---

← [코딩 컨벤션](06-coding-conventions.md) | [상태 관리](08-state-management.md) →