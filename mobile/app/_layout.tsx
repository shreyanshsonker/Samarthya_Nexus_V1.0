import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import 'react-native-reanimated';

import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuthStore } from '@/hooks/use-stores';

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const { isAuthenticated } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    const inTabsGroup = segments[0] === '(tabs)';

    if (!isAuthenticated && inTabsGroup) {
      // Redirect to login if not authenticated
      router.replace('/login');
    } else if (isAuthenticated && segments[0] === 'login') {
      // Redirect to home if already authenticated
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, segments]);

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="login" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
      </Stack>
      <StatusBar style="light" />
    </ThemeProvider>
  );
}
