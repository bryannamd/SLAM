// BookmarksScreen.tsx — presentation layer for screens.yaml#bookmarks.
// Covers 5 of the 6 contract states as UI (auth_required is declared `na` in
// spec/screens.yaml because this is a fully local app with no login/session).
import { useEffect, useState } from "react";
import { colors, spacing, radius, typography } from "./tokens";
import { AnalyticsEvent, logEvent } from "./analytics";

export interface Bookmark {
  id: string;
  url: string;
  title: string;
  tags: string[];
}

type ViewState = "loading" | "empty" | "error" | "success" | "route404";

export const BOOKMARKS_STORAGE_KEY = "linkbox_bookmarks";
const KNOWN_PATHS = ["/", "/tags"];

function isValidUrl(raw: string): boolean {
  try {
    const parsed = new URL(raw);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

export function readBookmarks(): Bookmark[] {
  const raw = window.localStorage.getItem(BOOKMARKS_STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeBookmarks(items: Bookmark[]): void {
  window.localStorage.setItem(BOOKMARKS_STORAGE_KEY, JSON.stringify(items));
}

export function BookmarksScreen({ currentPath }: { currentPath: string }) {
  const [state, setState] = useState<ViewState>("loading");
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [urlInput, setUrlInput] = useState("");
  const [titleInput, setTitleInput] = useState("");
  const [tagsInput, setTagsInput] = useState("");

  useEffect(() => {
    if (!KNOWN_PATHS.includes(currentPath)) {
      setState("route404");
      return;
    }
    loadBookmarks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPath]);

  function loadBookmarks() {
    setState("loading");
    try {
      const items = readBookmarks();
      setBookmarks(items);
      setState(items.length === 0 ? "empty" : "success");
    } catch {
      setErrorMessage("불러오기에 실패했어요. 다시 시도해주세요");
      setState("error");
    }
  }

  function validateInputs(): string | null {
    if (!isValidUrl(urlInput.trim()))
      return "올바른 URL 형식이 아니에요(https://로 시작)";
    if (titleInput.trim().length === 0) return "제목을 입력해주세요";
    return null;
  }

  function handleSave() {
    const validationError = validateInputs();
    if (validationError) {
      setErrorMessage(validationError);
      setState("error");
      return;
    }
    const tags = tagsInput
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    const next: Bookmark = {
      id: `${Date.now()}`,
      url: urlInput.trim(),
      title: titleInput.trim(),
      tags,
    };
    try {
      const updated = [next, ...bookmarks];
      writeBookmarks(updated);
      logEvent(AnalyticsEvent.bookmarkAdded, { has_tag: tags.length > 0 });
      setBookmarks(updated);
      setUrlInput("");
      setTitleInput("");
      setTagsInput("");
      setState("success");
    } catch {
      setErrorMessage("저장에 실패했어요. 다시 시도해주세요");
      setState("error");
    }
  }

  function handleDelete(id: string) {
    const updated = bookmarks.filter((b) => b.id !== id);
    writeBookmarks(updated);
    logEvent(AnalyticsEvent.bookmarkDeleted, {});
    setBookmarks(updated);
    setState(updated.length === 0 ? "empty" : "success");
  }

  function handleTagClick(tag: string) {
    const next = activeTag === tag ? null : tag;
    setActiveTag(next);
    logEvent(AnalyticsEvent.tagFilterApplied, { tag: next ?? "" });
  }

  const visible = activeTag
    ? bookmarks.filter((b) => b.tags.includes(activeTag))
    : bookmarks;
  const allTags = Array.from(new Set(bookmarks.flatMap((b) => b.tags)));

  if (state === "route404") {
    return (
      <div role="alert" style={{ padding: spacing.lg, textAlign: "center" }}>
        <p style={{ ...typography.h2, color: colors.textPrimary }}>
          페이지를 찾을 수 없어요
        </p>
        <a
          href="/"
          aria-label="북마크 목록으로 돌아가기"
          style={{ color: colors.primary }}
        >
          북마크 목록으로 돌아가기
        </a>
      </div>
    );
  }

  if (state === "loading") {
    return (
      <div aria-label="북마크 목록 불러오는 중" style={{ padding: spacing.lg }}>
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

  return (
    <section style={{ padding: spacing.md, background: colors.background }}>
      <h1 style={{ ...typography.h1, color: colors.textPrimary }}>북마크</h1>

      {allTags.length > 0 && (
        <div
          role="group"
          aria-label="태그 필터"
          style={{ display: "flex", gap: spacing.xs, marginBottom: spacing.sm }}
        >
          {allTags.map((tag) => (
            <button
              key={tag}
              type="button"
              aria-pressed={activeTag === tag}
              aria-label={`${tag} 태그로 필터링`}
              onClick={() => handleTagClick(tag)}
              style={{
                background: activeTag === tag ? colors.primary : colors.surface,
                color:
                  activeTag === tag ? colors.background : colors.textSecondary,
                borderRadius: radius.sm,
                padding: `${spacing.xs}px ${spacing.sm}px`,
              }}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      <form
        aria-label="북마크 추가"
        onSubmit={(e) => {
          e.preventDefault();
          handleSave();
        }}
        style={{ marginBottom: spacing.md }}
      >
        <input
          aria-label="URL 입력"
          placeholder="https://example.com"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: spacing.xs }}
        />
        <input
          aria-label="제목 입력"
          placeholder="제목"
          value={titleInput}
          onChange={(e) => setTitleInput(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: spacing.xs }}
        />
        <input
          aria-label="태그 입력(쉼표로 구분)"
          placeholder="태그(쉼표로 구분)"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: spacing.sm }}
        />
        <button
          type="submit"
          aria-label="북마크 저장"
          style={{
            background: colors.primary,
            color: colors.background,
            borderRadius: radius.sm,
          }}
        >
          저장
        </button>
      </form>

      {state === "error" && (
        <p role="alert" style={{ color: colors.error }}>
          {errorMessage ?? "오류가 발생했어요"}
        </p>
      )}

      {state === "empty" && (
        <p style={{ color: colors.textSecondary }}>첫 북마크를 저장해보세요</p>
      )}

      {state === "success" && (
        <ul aria-label="북마크 목록" style={{ listStyle: "none", padding: 0 }}>
          {visible.map((b) => (
            <li
              key={b.id}
              style={{
                background: colors.surface,
                borderRadius: radius.md,
                padding: spacing.sm,
                marginBottom: spacing.xs,
              }}
            >
              <a
                href={b.url}
                style={{ ...typography.body, color: colors.textPrimary }}
              >
                {b.title}
              </a>
              <button
                type="button"
                aria-label={`${b.title} 삭제`}
                onClick={() => handleDelete(b.id)}
                style={{ color: colors.error, marginLeft: spacing.sm }}
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
