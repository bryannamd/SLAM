// TagsScreen.tsx — presentation layer for screens.yaml#tags.
// Covers 4 of the 6 contract states as UI. route_404 and auth_required are both
// declared `na` in spec/screens.yaml: routing is handled globally by the
// bookmarks screen's app shell, and there is no login/session in this app.
import { useEffect, useState } from "react";
import { colors, spacing, radius, typography } from "./tokens";
import { readBookmarks, type Bookmark } from "./BookmarksScreen";

type ViewState = "loading" | "empty" | "error" | "success";

function writeBookmarks(items: Bookmark[]): void {
  window.localStorage.setItem("linkbox_bookmarks", JSON.stringify(items));
}

function tagsFrom(bookmarks: Bookmark[]): string[] {
  return Array.from(new Set(bookmarks.flatMap((b) => b.tags))).sort();
}

export function TagsScreen() {
  const [state, setState] = useState<ViewState>("loading");
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [renameDrafts, setRenameDrafts] = useState<Record<string, string>>({});

  useEffect(() => {
    loadTags();
  }, []);

  function loadTags() {
    setState("loading");
    try {
      const items = readBookmarks();
      setBookmarks(items);
      setState(tagsFrom(items).length === 0 ? "empty" : "success");
    } catch {
      setErrorMessage("태그를 불러오지 못했어요. 다시 시도해주세요");
      setState("error");
    }
  }

  function handleRename(oldTag: string) {
    const newTag = (renameDrafts[oldTag] ?? "").trim();
    if (newTag.length === 0) {
      setErrorMessage("새 태그 이름을 입력해주세요");
      setState("error");
      return;
    }
    try {
      const updated = bookmarks.map((b) => ({
        ...b,
        tags: b.tags.map((t) => (t === oldTag ? newTag : t)),
      }));
      writeBookmarks(updated);
      setBookmarks(updated);
      setState(tagsFrom(updated).length === 0 ? "empty" : "success");
    } catch {
      setErrorMessage("태그 이름 변경에 실패했어요. 다시 시도해주세요");
      setState("error");
    }
  }

  function handleDeleteTag(tag: string) {
    try {
      const updated = bookmarks.map((b) => ({
        ...b,
        tags: b.tags.filter((t) => t !== tag),
      }));
      writeBookmarks(updated);
      setBookmarks(updated);
      setState(tagsFrom(updated).length === 0 ? "empty" : "success");
    } catch {
      setErrorMessage("태그 삭제에 실패했어요. 다시 시도해주세요");
      setState("error");
    }
  }

  if (state === "loading") {
    return (
      <div aria-label="태그 목록 불러오는 중" style={{ padding: spacing.lg }}>
        <div
          style={{
            height: 16,
            background: colors.divider,
            borderRadius: radius.sm,
          }}
        />
      </div>
    );
  }

  const tags = tagsFrom(bookmarks);

  return (
    <section style={{ padding: spacing.md, background: colors.background }}>
      <h1 style={{ ...typography.h1, color: colors.textPrimary }}>태그 관리</h1>

      {state === "error" && (
        <p role="alert" style={{ color: colors.error }}>
          {errorMessage ?? "오류가 발생했어요"}
        </p>
      )}

      {state === "empty" && (
        <p style={{ color: colors.textSecondary }}>
          아직 태그가 없어요. 북마크에 태그를 달아보세요
        </p>
      )}

      {state === "success" && (
        <ul aria-label="태그 목록" style={{ listStyle: "none", padding: 0 }}>
          {tags.map((tag) => (
            <li
              key={tag}
              style={{
                display: "flex",
                alignItems: "center",
                gap: spacing.xs,
                background: colors.surface,
                borderRadius: radius.md,
                padding: spacing.sm,
                marginBottom: spacing.xs,
              }}
            >
              <span style={{ ...typography.body, color: colors.textPrimary }}>
                {tag}
              </span>
              <input
                aria-label={`${tag} 새 이름 입력`}
                placeholder="새 이름"
                value={renameDrafts[tag] ?? ""}
                onChange={(e) =>
                  setRenameDrafts((prev) => ({
                    ...prev,
                    [tag]: e.target.value,
                  }))
                }
              />
              <button
                type="button"
                aria-label={`${tag} 이름 변경`}
                onClick={() => handleRename(tag)}
              >
                이름 변경
              </button>
              <button
                type="button"
                aria-label={`${tag} 삭제`}
                onClick={() => handleDeleteTag(tag)}
                style={{ color: colors.error }}
              >
                삭제
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
