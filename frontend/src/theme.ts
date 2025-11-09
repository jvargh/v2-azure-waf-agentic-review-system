// Centralized theme palette for artifact badges and borders.
export const theme = {
  badge: {
    architectureDoc: { bg: '#ece8ff', fg: '#4b3fb3', border: '#d0c9f5' },
    supportCase: { bg: '#d5f7df', fg: '#1d6b32', border: '#b8eec5' },
    architectureDiagram: { bg: '#fff7b3', fg: '#7a6000', border: '#f5d9c9' }
  },
  surface: {
    panel: '#fafafa',
    border: '#e0e0e0'
  }
};
export type ThemeKey = keyof typeof theme.badge;
