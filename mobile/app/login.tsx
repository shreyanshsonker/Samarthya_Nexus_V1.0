import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { Colors, Spacing, Border, Typography } from '@/constants/theme';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { useAuthStore } from '@/hooks/use-stores';
import { api } from '@/hooks/use-api';
import { useRouter } from 'expo-router';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();
  const router = useRouter();

  const handleLogin = async () => {
    if (!email || !password) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const res = await api.auth.login(formData);
      // Backend returns { access_token, user_id, ... }
      setAuth(res.data.access_token, { email });
      router.replace('/(tabs)');
    } catch (error) {
      Alert.alert('Login Failed', 'Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ThemedView style={styles.content}>
        <ThemedText type="title" style={styles.title}>Nexus Login</ThemedText>
        <ThemedText style={styles.subtitle}>Sign in to manage your household energy</ThemedText>

        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#687076"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#687076"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TouchableOpacity 
          style={[styles.loginBtn, { backgroundColor: loading ? Colors.dark.border : Colors.dark.primary }]}
          onPress={handleLogin}
          disabled={loading}
        >
          <ThemedText style={{ color: '#000', fontWeight: 'bold' }}>
            {loading ? 'Authenticating...' : 'Login'}
          </ThemedText>
        </TouchableOpacity>
      </ThemedView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.dark.background,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: Spacing.xxxl,
    backgroundColor: 'transparent',
  },
  title: {
    fontSize: 40,
    marginBottom: Spacing.s,
  },
  subtitle: {
    color: Colors.dark.textSecondary,
    marginBottom: Spacing.xxxl,
  },
  input: {
    height: 56,
    backgroundColor: '#1E1E2E',
    borderRadius: Border.r12,
    paddingHorizontal: Spacing.l,
    color: '#fff',
    marginBottom: Spacing.l,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  loginBtn: {
    height: 56,
    borderRadius: Border.r12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: Spacing.xl,
  }
});
