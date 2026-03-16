import React, { useEffect, useState } from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { Colors, Spacing, Border, Typography } from '@/constants/theme';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { api } from '@/hooks/use-api';
import { useAuthStore } from '@/hooks/use-stores';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const [inverterStatus, setInverterStatus] = useState<any>(null);

  useEffect(() => {
    api.apiClient.get('/api/inverter/status').then(res => setInverterStatus(res.data));
  }, []);

  return (
    <ThemedView style={styles.container}>
      <ThemedView style={styles.header}>
        <ThemedText type="title">Settings</ThemedText>
      </ThemedView>

      <View style={styles.section}>
        <ThemedText style={styles.sectionTitle}>Inverter Status</ThemedText>
        <ThemedView style={styles.card}>
          <View style={styles.row}>
            <IconSymbol 
              name="antenna.radiowaves.left.and.right" 
              size={24} 
              color={inverterStatus?.connected ? Colors.dark.primary : Colors.dark.error} 
            />
            <View style={{ marginLeft: Spacing.m }}>
              <ThemedText type="defaultSemiBold">
                {inverterStatus?.brand || "Loading..."} Inverter
              </ThemedText>
              <ThemedText style={{ color: Colors.dark.textSecondary, fontSize: 13 }}>
                Status: {inverterStatus?.status || "Unknown"}
              </ThemedText>
            </View>
          </View>
        </ThemedView>
      </View>

      <View style={styles.section}>
        <ThemedText style={styles.sectionTitle}>Account</ThemedText>
        <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
          <ThemedText style={{ color: Colors.dark.error, fontWeight: 'bold' }}>Sign Out</ThemedText>
        </TouchableOpacity>
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.dark.background,
  },
  header: {
    padding: Spacing.xl,
    paddingTop: 60,
    backgroundColor: 'transparent',
  },
  section: {
    marginTop: Spacing.xl,
    paddingHorizontal: Spacing.xl,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: Colors.dark.textSecondary,
    textTransform: 'uppercase',
    marginBottom: Spacing.m,
  },
  card: {
    padding: Spacing.l,
    backgroundColor: '#1E1E2E',
    borderRadius: Border.r12,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoutBtn: {
    padding: Spacing.l,
    backgroundColor: 'rgba(255, 112, 112, 0.1)',
    borderRadius: Border.r12,
    alignItems: 'center',
  }
});
