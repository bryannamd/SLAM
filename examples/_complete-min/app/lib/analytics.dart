// analytics.dart — data layer. Event names here must match spec/events.yaml exactly;
// trace.py checks this file against the spec for drift.
class AnalyticsEvent {
  static const appOpen = 'app_open';
  static const noteSaved = 'note_saved';
  static const reminderPermissionResult = 'reminder_permission_result';
}

void logEvent(String name, [Map<String, Object?> props = const {}]) {
  // MVP: local-only app, no network. Replace with local buffer + batched
  // upload if/when a backend is introduced (architecture.yaml: backend=none).
  assert(() {
    // ignore: avoid_print
    print('[analytics] $name $props');
    return true;
  }());
}
