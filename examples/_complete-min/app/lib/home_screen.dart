// home_screen.dart — presentation layer for screens.yaml#home.
// Covers 5 of the 6 contract states as UI (offline is declared `na` in spec/screens.yaml
// because this is a fully local app with no online dependency).
import 'package:flutter/material.dart';
import 'analytics.dart';
import 'tokens.dart';

enum HomeState { loading, empty, error, success, permissionDenied }

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const _maxNoteLength = 140;

  HomeState _state = HomeState.loading;
  String? _todayNote;
  String? _errorMessage;
  bool _notificationsGranted = true;
  final _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    logEvent(
        AnalyticsEvent.appOpen, const {'os': 'unknown', 'version': '1.0.0'});
    _loadToday();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _loadToday() async {
    setState(() => _state = HomeState.loading);
    // Domain/data layer stub: a real build wires this to a Drift repository.
    final existing = await _readTodayNoteFromLocalDb();
    if (!mounted) return;
    setState(() {
      _todayNote = existing;
      _state = existing == null
          ? HomeState.empty
          : (_notificationsGranted
              ? HomeState.success
              : HomeState.permissionDenied);
    });
  }

  Future<String?> _readTodayNoteFromLocalDb() async => null;

  String? _validateNote(String raw) {
    final text = raw.trim();
    if (text.isEmpty) return '한 줄을 입력해주세요';
    if (text.length > _maxNoteLength) return '$_maxNoteLength자 이내로 줄여주세요';
    return null;
  }

  Future<void> _save() async {
    final validationError = _validateNote(_controller.text);
    if (validationError != null) {
      setState(() {
        _state = HomeState.error;
        _errorMessage = validationError;
      });
      return;
    }
    final isEdit = _todayNote != null;
    try {
      final text = _controller.text.trim();
      await _writeTodayNoteToLocalDb(text);
      logEvent(
          AnalyticsEvent.noteSaved, {'length': text.length, 'is_edit': isEdit});
      if (!mounted) return;
      setState(() {
        _todayNote = text;
        _state = _notificationsGranted
            ? HomeState.success
            : HomeState.permissionDenied;
      });
    } catch (e) {
      // 에러를 삼키지 않는다: 사용자에게 안내 + (실제 빌드에서는) 로깅 서비스 전달.
      if (!mounted) return;
      setState(() {
        _state = HomeState.error;
        _errorMessage = '저장에 실패했어요. 다시 시도해주세요';
      });
    }
  }

  Future<void> _writeTodayNoteToLocalDb(String text) async {}

  Future<void> _requestNotificationPermission() async {
    final granted = await _askNotificationPermission();
    logEvent(AnalyticsEvent.reminderPermissionResult, {'granted': granted});
    if (!mounted) return;
    setState(() {
      _notificationsGranted = granted;
      if (_todayNote != null) {
        _state = granted ? HomeState.success : HomeState.permissionDenied;
      }
    });
  }

  Future<bool> _askNotificationPermission() async => true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        title: Text('오늘 한 줄', style: AppTypography.h2),
      ),
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_state == HomeState.permissionDenied) _buildPermissionBanner(),
            Expanded(child: _buildBody()),
          ],
        ),
      ),
    );
  }

  Widget _buildPermissionBanner() {
    return Semantics(
      label: '알림 권한이 꺼져 있어요. 저녁 리마인더를 받으려면 켜주세요',
      child: Container(
        margin: const EdgeInsets.only(bottom: AppSpacing.md),
        padding: const EdgeInsets.all(AppSpacing.sm),
        decoration: BoxDecoration(
          color: AppColors.warning.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(AppRadius.sm),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text('알림 권한이 꺼져 있어요. 저녁 리마인더를 받으려면 켜주세요',
                  style: AppTypography.caption),
            ),
            TextButton(
              onPressed: _requestNotificationPermission,
              child: const Text('권한 요청'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBody() {
    switch (_state) {
      case HomeState.loading:
        return const Center(
          child: Semantics(
              label: '오늘 메모 불러오는 중', child: CircularProgressIndicator()),
        );
      case HomeState.empty:
        return _buildEditor(hint: '오늘 한 줄을 남겨보세요');
      case HomeState.error:
        return _buildErrorCard();
      case HomeState.success:
      case HomeState.permissionDenied:
        return _todayNote == null
            ? _buildEditor(hint: '오늘 한 줄을 남겨보세요')
            : _buildSavedNote();
    }
  }

  Widget _buildEditor({required String hint}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Semantics(
          textField: true,
          label: '오늘 한 줄 입력',
          child: TextField(
            controller: _controller,
            maxLength: _maxNoteLength,
            style: AppTypography.body,
            decoration: InputDecoration(
              hintText: hint,
              hintStyle:
                  AppTypography.body.copyWith(color: AppColors.textDisabled),
              filled: true,
              fillColor: AppColors.surface,
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(AppRadius.md)),
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.sm),
        Semantics(
          button: true,
          label: '저장',
          child: ElevatedButton(onPressed: _save, child: const Text('저장')),
        ),
      ],
    );
  }

  Widget _buildErrorCard() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Semantics(
            liveRegion: true,
            label: _errorMessage ?? '오류가 발생했어요',
            child: Text(_errorMessage ?? '오류가 발생했어요',
                style: AppTypography.body.copyWith(color: AppColors.error)),
          ),
          const SizedBox(height: AppSpacing.sm),
          Semantics(
            button: true,
            label: '재시도',
            child: ElevatedButton(onPressed: _save, child: const Text('재시도')),
          ),
        ],
      ),
    );
  }

  Widget _buildSavedNote() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.md),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          child: Semantics(
            label: '오늘의 한 줄: $_todayNote',
            child: Text(_todayNote ?? '', style: AppTypography.body),
          ),
        ),
        const SizedBox(height: AppSpacing.sm),
        Semantics(
          button: true,
          label: '수정',
          child: OutlinedButton(
            onPressed: () {
              _controller.text = _todayNote ?? '';
              setState(() => _state = HomeState.empty);
            },
            child: const Text('수정'),
          ),
        ),
      ],
    );
  }
}
