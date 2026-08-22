import colors from '../constants/colors';
import { spacing, radius } from '../constants/spacing';
import typography from '../constants/typography';

export const darkTheme = {
  dark: true,
  colors: {
    primary: colors.primary[500],
    primaryLight: 'rgba(59, 130, 246, 0.15)',
    primaryHover: colors.primary[400],
    background: '#0B1329',
    card: '#1E293B',
    text: '#F8FAFC',
    textSecondary: '#94A3B8',
    border: '#334155',
    safe: colors.safe[500],
    safeLight: 'rgba(16, 185, 129, 0.15)',
    danger: colors.danger[500],
    dangerLight: 'rgba(239, 68, 68, 0.15)',
    warning: colors.warning[500],
    warningLight: 'rgba(245, 158, 11, 0.15)',
  },
  spacing,
  radius,
  typography,
};

export default darkTheme;
