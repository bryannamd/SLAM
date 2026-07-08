// tokens.dart — generated from spec/tokens.json. Do not hand-edit hex values here;
// change spec/tokens.json and regenerate. This is the only file in app/lib allowed
// to contain hex color literals — every other widget must reference AppColors/*.
import 'package:flutter/widgets.dart';

class AppColors {
  static const primary = Color(0xFF2563EB);
  static const primaryLight = Color(0xFFDBEAFE);
  static const secondary = Color(0xFF64748B);
  static const background = Color(0xFFFFFFFF);
  static const surface = Color(0xFFF8FAFC);
  static const error = Color(0xFFEF4444);
  static const success = Color(0xFF22C55E);
  static const warning = Color(0xFFF59E0B);
  static const textPrimary = Color(0xFF0F172A);
  static const textSecondary = Color(0xFF475569);
  static const textDisabled = Color(0xFF94A3B8);
  static const divider = Color(0xFFE2E8F0);
}

class AppSpacing {
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 16.0;
  static const lg = 24.0;
  static const xl = 32.0;
  static const xxl = 48.0;
}

class AppRadius {
  static const sm = 8.0;
  static const md = 12.0;
  static const lg = 16.0;
}

class AppTypography {
  static const h1 = TextStyle(
      fontSize: 24,
      fontWeight: FontWeight.w700,
      height: 32 / 24,
      color: AppColors.textPrimary);
  static const h2 = TextStyle(
      fontSize: 20,
      fontWeight: FontWeight.w600,
      height: 28 / 20,
      color: AppColors.textPrimary);
  static const body = TextStyle(
      fontSize: 16,
      fontWeight: FontWeight.w400,
      height: 24 / 16,
      color: AppColors.textPrimary);
  static const caption = TextStyle(
      fontSize: 12,
      fontWeight: FontWeight.w400,
      height: 16 / 12,
      color: AppColors.textSecondary);
}
