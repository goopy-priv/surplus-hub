# 상태 관리 (BLoC 패턴)

## 🎯 학습 목표
- BLoC 패턴의 개념과 장점을 이해한다
- Event, State, BLoC의 역할을 파악한다
- 실제 BLoC 구현 방법을 익힌다
- Equatable을 사용한 상태 비교를 이해한다

**예상 소요 시간**: 2-3시간

## 🧠 BLoC 패턴 개념

### BLoC (Business Logic Component)
- **목적**: UI와 비즈니스 로직 분리
- **원칙**: 입력(Event) → 처리(BLoC) → 출력(State)
- **장점**: 테스트 가능, 재사용 가능, 플랫폼 독립적

```
┌─────────┐    Event    ┌──────┐    State    ┌─────────┐
│   UI    │ ────────────► BLoC │ ────────────► Widget  │
│ (Page)  │             │Logic │             │(Builder)│
└─────────┘             └──────┘             └─────────┘
```

## 📊 BLoC 구성 요소

### 1. Event (이벤트)
사용자의 액션이나 시스템 이벤트를 나타냅니다.

```dart
// lib/features/home/presentation/bloc/home_event.dart
abstract class HomeEvent extends Equatable {
  const HomeEvent();
  
  @override
  List<Object?> get props => [];
}

/// 자료 로딩 이벤트
class LoadMaterials extends HomeEvent {
  const LoadMaterials();
}

/// 정렬 변경 이벤트
class ChangeSorting extends HomeEvent {
  const ChangeSorting(this.sortOption);
  
  final String sortOption;
  
  @override
  List<Object> get props => [sortOption];
}

/// 카테고리 필터 변경 이벤트
class ChangeCategoryFilter extends HomeEvent {
  const ChangeCategoryFilter(this.category);
  
  final SelectedCategory? category;
  
  @override
  List<Object?> get props => [category];
}

/// 자료 새로고침 이벤트
class RefreshMaterials extends HomeEvent {
  const RefreshMaterials();
}
```

### 2. State (상태)
현재 화면의 상태를 나타냅니다.

```dart
// lib/features/home/presentation/bloc/home_state.dart
abstract class HomeState extends Equatable {
  const HomeState();
  
  @override
  List<Object?> get props => [];
}

/// 초기 상태
class HomeInitial extends HomeState {
  const HomeInitial();
}

/// 로딩 중 상태
class HomeLoading extends HomeState {
  const HomeLoading();
}

/// 로딩 완료 상태
class HomeLoaded extends HomeState {
  const HomeLoaded({
    required this.materials,
    required this.filteredMaterials,
    required this.selectedSort,
    this.selectedCategory,
  });
  
  final List<MaterialItem> materials;
  final List<MaterialItem> filteredMaterials;
  final String selectedSort;
  final SelectedCategory? selectedCategory;
  
  @override
  List<Object?> get props => [
    materials,
    filteredMaterials,
    selectedSort,
    selectedCategory,
  ];
}

/// 에러 상태
class HomeError extends HomeState {
  const HomeError(this.message);
  
  final String message;
  
  @override
  List<Object> get props => [message];
}
```

### 3. BLoC (비즈니스 로직)
이벤트를 받아서 상태를 변환하는 로직을 담당합니다.

```dart
// lib/features/home/presentation/bloc/home_bloc.dart
import 'dart:convert';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

import '../../../../core/constants/app_constants.dart';
import '../../domain/entities/material_item.dart';
import '../../domain/entities/selected_category.dart';

part 'home_event.dart';
part 'home_state.dart';

class HomeBloc extends Bloc<HomeEvent, HomeState> {
  HomeBloc() : super(const HomeInitial()) {
    on<LoadMaterials>(_onLoadMaterials);
    on<ChangeSorting>(_onChangeSorting);
    on<ChangeCategoryFilter>(_onChangeCategoryFilter);
    on<RefreshMaterials>(_onRefreshMaterials);
  }

  // 자료 로딩
  Future<void> _onLoadMaterials(
    LoadMaterials event,
    Emitter<HomeState> emit,
  ) async {
    emit(const HomeLoading());
    
    try {
      // TODO: 실제 API 호출로 대체
      await Future.delayed(const Duration(milliseconds: 500)); // 로딩 시뮬레이션
      
      final List<dynamic> jsonData = json.decode(AppConstants.sampleMaterialsJson);
      final materials = jsonData.map((item) => _parseMaterialItem(item)).toList();
      
      emit(HomeLoaded(
        materials: materials,
        filteredMaterials: materials,
        selectedSort: '최신순',
      ));
    } catch (e) {
      emit(HomeError('자료를 불러오는데 실패했습니다: $e'));
    }
  }

  // 정렬 변경
  void _onChangeSorting(
    ChangeSorting event,
    Emitter<HomeState> emit,
  ) {
    final currentState = state;
    if (currentState is HomeLoaded) {
      final sortedMaterials = _sortMaterials(
        currentState.materials,
        event.sortOption,
        currentState.selectedCategory,
      );
      
      emit(currentState.copyWith(
        filteredMaterials: sortedMaterials,
        selectedSort: event.sortOption,
      ));
    }
  }

  // 카테고리 필터 변경
  void _onChangeCategoryFilter(
    ChangeCategoryFilter event,
    Emitter<HomeState> emit,
  ) {
    final currentState = state;
    if (currentState is HomeLoaded) {
      final filteredMaterials = _sortMaterials(
        currentState.materials,
        currentState.selectedSort,
        event.category,
      );
      
      emit(currentState.copyWith(
        filteredMaterials: filteredMaterials,
        selectedCategory: event.category,
      ));
    }
  }

  // 새로고침
  Future<void> _onRefreshMaterials(
    RefreshMaterials event,
    Emitter<HomeState> emit,
  ) async {
    // 현재 상태 유지하면서 백그라운드에서 새로고침
    try {
      final List<dynamic> jsonData = json.decode(AppConstants.sampleMaterialsJson);
      final materials = jsonData.map((item) => _parseMaterialItem(item)).toList();
      
      final currentState = state;
      if (currentState is HomeLoaded) {
        final filteredMaterials = _sortMaterials(
          materials,
          currentState.selectedSort,
          currentState.selectedCategory,
        );
        
        emit(currentState.copyWith(
          materials: materials,
          filteredMaterials: filteredMaterials,
        ));
      }
    } catch (e) {
      emit(HomeError('새로고침에 실패했습니다: $e'));
    }
  }

  // 헬퍼 메서드들
  MaterialItem _parseMaterialItem(Map<String, dynamic> json) {
    return MaterialItem(
      id: json['id'] as String,
      title: json['title'] as String,
      price: json['price'] as String,
      location: json['location'] as String,
      seller: json['seller'] as String,
      imageUrl: json['imageUrl'] as String,
      likes: json['likes'] as int,
      chats: json['chats'] as int,
      category: json['category'] as String,
      categoryPath: (json['categoryPath'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
    );
  }

  List<MaterialItem> _sortMaterials(
    List<MaterialItem> materials,
    String sortOption,
    SelectedCategory? category,
  ) {
    // 먼저 카테고리 필터 적용
    List<MaterialItem> filtered = List.from(materials);
    
    if (category != null) {
      filtered = filtered.where((material) {
        return category.matches(material.categoryPath);
      }).toList();
    }

    // 그다음 정렬 적용
    switch (sortOption) {
      case '최신순':
        // 기본 순서 유지
        break;
      case '거리순':
        filtered.sort((a, b) => a.location.compareTo(b.location));
        break;
      case '인기순':
        filtered.sort((a, b) => b.popularityScore.compareTo(a.popularityScore));
        break;
      case '낮은가격순':
        filtered.sort((a, b) => a.priceAsNumber.compareTo(b.priceAsNumber));
        break;
    }

    return filtered;
  }
}

// HomeLoaded state extension for copyWith
extension HomeLoadedX on HomeLoaded {
  HomeLoaded copyWith({
    List<MaterialItem>? materials,
    List<MaterialItem>? filteredMaterials,
    String? selectedSort,
    SelectedCategory? selectedCategory,
  }) {
    return HomeLoaded(
      materials: materials ?? this.materials,
      filteredMaterials: filteredMaterials ?? this.filteredMaterials,
      selectedSort: selectedSort ?? this.selectedSort,
      selectedCategory: selectedCategory ?? this.selectedCategory,
    );
  }
}
```

## 🖼️ BLoC과 UI 연결

### BlocProvider로 BLoC 제공
```dart
// lib/features/home/presentation/pages/home_page.dart
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => HomeBloc()..add(const LoadMaterials()),
      child: const HomePageView(),
    );
  }
}

class HomePageView extends StatelessWidget {
  const HomePageView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(context),
      body: Column(
        children: [
          _buildFilterBar(context),
          Expanded(
            child: _buildMaterialList(context),
          ),
        ],
      ),
    );
  }

  Widget _buildMaterialList(BuildContext context) {
    return BlocBuilder<HomeBloc, HomeState>(
      builder: (context, state) {
        if (state is HomeLoading) {
          return const Center(
            child: CircularProgressIndicator(),
          );
        }
        
        if (state is HomeError) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(state.message),
                ElevatedButton(
                  onPressed: () {
                    context.read<HomeBloc>().add(const LoadMaterials());
                  },
                  child: const Text('다시 시도'),
                ),
              ],
            ),
          );
        }
        
        if (state is HomeLoaded) {
          if (state.filteredMaterials.isEmpty) {
            return const Center(
              child: Text('검색 결과가 없습니다'),
            );
          }
          
          return RefreshIndicator(
            onRefresh: () async {
              context.read<HomeBloc>().add(const RefreshMaterials());
            },
            child: ListView.builder(
              itemCount: state.filteredMaterials.length,
              itemBuilder: (context, index) {
                final material = state.filteredMaterials[index];
                return MaterialCard(
                  key: ValueKey('material-${material.id}'),
                  material: material,
                  onTap: () {
                    // 상세 페이지로 이동
                    context.push('/material/${material.id}');
                  },
                );
              },
            ),
          );
        }
        
        return const SizedBox.shrink();
      },
    );
  }

  Widget _buildFilterBar(BuildContext context) {
    return BlocBuilder<HomeBloc, HomeState>(
      builder: (context, state) {
        if (state is HomeLoaded) {
          return FilterBar(
            selectedSort: state.selectedSort,
            selectedCategory: state.selectedCategory?.displayName,
            materialCount: state.filteredMaterials.length,
            onSortChanged: (newSort) {
              if (newSort != null) {
                context.read<HomeBloc>().add(ChangeSorting(newSort));
              }
            },
            onCategoryTap: () {
              _showCategoryModal(context);
            },
            onCategoryClear: () {
              context.read<HomeBloc>().add(const ChangeCategoryFilter(null));
            },
          );
        }
        return const SizedBox.shrink();
      },
    );
  }
}
```

### BlocListener로 사이드 이펙트 처리
```dart
// 스낵바, 다이얼로그, 네비게이션 등
BlocListener<HomeBloc, HomeState>(
  listener: (context, state) {
    if (state is HomeError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(state.message),
          backgroundColor: AppColors.error,
        ),
      );
    }
  },
  child: BlocBuilder<HomeBloc, HomeState>(
    builder: (context, state) {
      // UI 빌드 로직
    },
  ),
);
```

## 🧪 BLoC 테스트

### BLoC 단위 테스트
```dart
// test/features/home/presentation/bloc/home_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:surplus_hub_flutter/features/home/presentation/bloc/home_bloc.dart';

void main() {
  group('HomeBloc', () {
    late HomeBloc homeBloc;

    setUp(() {
      homeBloc = HomeBloc();
    });

    tearDown(() {
      homeBloc.close();
    });

    test('initial state is HomeInitial', () {
      expect(homeBloc.state, const HomeInitial());
    });

    blocTest<HomeBloc, HomeState>(
      'emits [HomeLoading, HomeLoaded] when LoadMaterials is added',
      build: () => homeBloc,
      act: (bloc) => bloc.add(const LoadMaterials()),
      expect: () => [
        const HomeLoading(),
        isA<HomeLoaded>(),
      ],
    );

    blocTest<HomeBloc, HomeState>(
      'emits updated state when ChangeSorting is added',
      build: () => homeBloc,
      seed: () => const HomeLoaded(
        materials: [],
        filteredMaterials: [],
        selectedSort: '최신순',
      ),
      act: (bloc) => bloc.add(const ChangeSorting('인기순')),
      expect: () => [
        isA<HomeLoaded>()
            .having((state) => state.selectedSort, 'selectedSort', '인기순'),
      ],
    );
  });
}
```

## 🎯 BLoC 베스트 프랙티스

### 1. State 불변성 유지
```dart
// ✅ 좋은 예시 - 새 객체 생성
class HomeLoaded extends HomeState {
  const HomeLoaded({required this.materials});
  
  final List<MaterialItem> materials;
  
  HomeLoaded copyWith({List<MaterialItem>? materials}) {
    return HomeLoaded(
      materials: materials ?? this.materials,
    );
  }
}

// ❌ 나쁜 예시 - 기존 객체 수정
void _updateMaterials(List<MaterialItem> newMaterials) {
  materials.clear();  // 기존 리스트 변경
  materials.addAll(newMaterials);
}
```

### 2. Equatable 활용
```dart
// 상태 비교를 위해 props 정의
abstract class HomeState extends Equatable {
  const HomeState();
  
  @override
  List<Object?> get props => [];
}

class HomeLoaded extends HomeState {
  const HomeLoaded({required this.materials});
  
  final List<MaterialItem> materials;
  
  @override
  List<Object?> get props => [materials];
}
```

### 3. 에러 처리
```dart
Future<void> _onLoadMaterials(
  LoadMaterials event,
  Emitter<HomeState> emit,
) async {
  emit(const HomeLoading());
  
  try {
    final materials = await repository.getMaterials();
    emit(HomeLoaded(materials: materials));
  } on NetworkException catch (e) {
    emit(HomeError('네트워크 연결을 확인해주세요'));
  } catch (e) {
    emit(HomeError('알 수 없는 오류가 발생했습니다'));
  }
}
```

### 4. 의존성 주입
```dart
class HomeBloc extends Bloc<HomeEvent, HomeState> {
  HomeBloc({
    required this.materialRepository,
  }) : super(const HomeInitial()) {
    on<LoadMaterials>(_onLoadMaterials);
  }
  
  final MaterialRepository materialRepository;
  
  // BLoC 로직에서 repository 사용
}
```

## ✅ BLoC 패턴 체크리스트

- [ ] Event, State, BLoC 파일이 분리되어 있다
- [ ] 모든 State가 Equatable을 상속한다
- [ ] BLoC에서 UI 관련 코드가 없다
- [ ] 비동기 작업을 적절히 처리한다
- [ ] 에러 상태를 정의하고 처리한다
- [ ] 단위 테스트를 작성했다

---

← [기능 개발 가이드](07-feature-development.md) | [네비게이션](09-navigation.md) →