/**
 * Samarthya Nexus Design Tokens
 * Source: UI Design Rules §2, §3, §4
 */

import { Platform } from 'react-native';

export const Colors = {
  light: {
    background: '#F7F8FA',
    surface: '#FFFFFF',
    primary: '#00C896',
    text: '#0A0A0A',
    textSecondary: '#687076',
    border: '#E1E4E8',
    error: '#FF6B6B',
    success: '#00C896',
    card: '#FFFFFF',
    tint: '#00C896',
    tabIconDefault: '#9BA1A6',
    tabIconSelected: '#00C896',
  },
  dark: {
    background: '#141420', // Navy-dark background
    surface: '#1E1E2E',
    primary: '#00E5A8',
    text: '#FFFFFF',
    textSecondary: '#9BA1A6',
    border: '#2E2E3E',
    error: '#FF7070',
    success: '#00E5A8',
    card: '#1E1E2E',
    tint: '#00E5A8',
    tabIconDefault: '#9BA1A6',
    tabIconSelected: '#00E5A8',
  },
};

export const Spacing = {
  xs: 4,
  s: 8,
  m: 12,
  l: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

export const Border = {
  r4: 4,
  r8: 8,
  r12: 12,
  r16: 16,
  r20: 20,
  r28: 28,
  pill: 50,
};

export const Typography = {
  display: { fontSize: 32, fontWeight: '700' as const },
  h1: { fontSize: 24, fontWeight: '600' as const },
  h2: { fontSize: 18, fontWeight: '600' as const },
  h3: { fontSize: 15, fontWeight: '500' as const },
  bodyLg: { fontSize: 14, fontWeight: '400' as const },
  bodySm: { fontSize: 13, fontWeight: '400' as const },
  label: { fontSize: 11, fontWeight: '400' as const },
  micro: { fontSize: 10, fontWeight: '500' as const },
};
