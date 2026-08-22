import colors from '../constants/colors';
import { spacing, radius } from '../constants/spacing';
import typography from '../constants/typography';

export const lightTheme = {
  dark: false,
  colors: {
    primary: colors.primary[600],
    primaryLight: colors.primary[50],
    primaryHover: colors.primary[700],
    background: colors.surface.background,
    card: colors.surface.card,
    text: colors.neutral[900],
    textSecondary: colors.neutral[500],
    border: colors.surface.border,
    safe: colors.safe[600],
    safeLight: colors.safe[50],
    danger: colors.danger[600],
    dangerLight: colors.danger[50],
    warning: colors.warning[600],
    warningLight: colors.warning[50],
  },
  spacing,
  radius,
  typography,
};

export default lightTheme;
