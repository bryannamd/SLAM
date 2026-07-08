// analytics.ts — data layer. Event names here must match spec/events.yaml exactly;
// trace.py checks this file against the spec for drift.

export const AnalyticsEvent = {
  bookmarkAdded: "bookmark_added",
  bookmarkDeleted: "bookmark_deleted",
  tagFilterApplied: "tag_filter_applied",
} as const;

export function logEvent(
  name: string,
  props: Record<string, unknown> = {},
): void {
  // MVP: local-only app, no network. Replace with a batched upload
  // if/when a backend is introduced (architecture.yaml: backend=none).
  if (
    typeof window !== "undefined" &&
    window.location.hostname === "localhost"
  ) {
    // eslint-disable-next-line no-console
    console.log("[analytics]", name, props);
  }
}
