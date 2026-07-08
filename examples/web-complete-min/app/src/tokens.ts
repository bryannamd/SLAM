// tokens.ts — generated from spec/tokens.json. Do not hand-edit hex values here;
// change spec/tokens.json and regenerate. This is the only file in app/src allowed
// to contain hex color literals — every other component must reference colors/*.

export const colors = {
  primary: "#0F766E",
  primaryLight: "#CCFBF1",
  secondary: "#64748B",
  background: "#FFFFFF",
  surface: "#F8FAFC",
  error: "#DC2626",
  success: "#16A34A",
  warning: "#D97706",
  textPrimary: "#0F172A",
  textSecondary: "#475569",
  textDisabled: "#94A3B8",
  divider: "#E2E8F0",
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
} as const;

export const typography = {
  h1: { fontSize: 24, fontWeight: 700, lineHeight: 32 },
  h2: { fontSize: 20, fontWeight: 600, lineHeight: 28 },
  h3: { fontSize: 18, fontWeight: 600, lineHeight: 24 },
  body: { fontSize: 16, fontWeight: 400, lineHeight: 24 },
  caption: { fontSize: 12, fontWeight: 400, lineHeight: 16 },
} as const;
