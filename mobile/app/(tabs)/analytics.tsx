import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { Colors, Spacing, Border } from '@/constants/theme';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { ForecastGraph } from '@/components/ForecastGraph';
import { useForecastStore } from '@/hooks/use-stores';
import { api } from '@/hooks/use-api';
import { IconSymbol } from '@/components/ui/icon-symbol';

export default function AnalyticsScreen() {
  const { forecast } = useForecastStore();
  const [explanations, setExplanations] = useState<any[]>([]);

  useEffect(() => {
    api.forecast.getExplanations().then(res => setExplanations(res.data));
  }, []);

  return (
    <ScrollView style={styles.container}>
      <ThemedView style={styles.header}>
        <ThemedText type="title">Solar Analytics</ThemedText>
        <ThemedText style={{ color: Colors.dark.textSecondary }}>
          Predictive data & AI drivers
        </ThemedText>
      </ThemedView>

      <ForecastGraph data={forecast} />

      <ThemedView style={styles.section}>
        <ThemedText type="subtitle" style={{ marginBottom: Spacing.l }}>Model Drivers (SHAP)</ThemedText>
        
        {explanations.map((exp, i) => (
          <ThemedView key={i} style={styles.insightCard}>
            <View style={styles.insightHeader}>
              <IconSymbol name="info.circle.fill" size={18} color={Colors.dark.primary} />
              <ThemedText style={{ marginLeft: 8, fontWeight: 'bold' }}>{exp.label}</ThemedText>
            </View>
            <ThemedText style={styles.insightText}>
              This factor is driving the current forecast {exp.impact > 0 ? 'upwards' : 'downwards'} by 
              {" "}{(Math.abs(exp.impact) * 100).toFixed(1)}%.
            </ThemedText>
          </ThemedView>
        ))}
      </ThemedView>
    </ScrollView>
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
    padding: Spacing.l,
    backgroundColor: 'transparent',
  },
  insightCard: {
    padding: Spacing.l,
    backgroundColor: '#1E1E2E',
    borderRadius: Border.r12,
    marginBottom: Spacing.m,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightText: {
    color: Colors.dark.textSecondary,
    fontSize: 13,
  }
});
