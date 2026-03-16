import React from 'react';
import { View, StyleSheet, useColorScheme } from 'react-native';
import { Colors, Spacing, Border, Typography } from '../constants/theme';
import { ThemedText } from './themed-text';
import { IconSymbol } from './ui/icon-symbol';

interface CarbonStatsCardProps {
  savingsKg: number;
  treesEquiv: number;
  gridZone?: string;
}

export const CarbonStatsCard: React.FC<CarbonStatsCardProps> = ({ 
  savingsKg, 
  treesEquiv, 
  gridZone = "MP" 
}) => {
  const colorScheme = useColorScheme() ?? 'dark';
  const colors = Colors[colorScheme];

  return (
    <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
      <View style={styles.header}>
        <IconSymbol name="leaf.fill" size={20} color={colors.primary} />
        <ThemedText style={[Typography.h2, { marginLeft: Spacing.s }]}>
          Environmental Impact
        </ThemedText>
      </View>

      <View style={styles.row}>
        <View style={styles.stat}>
          <ThemedText style={[Typography.h1, { color: colors.primary }]}>
            {savingsKg.toFixed(2)}
          </ThemedText>
          <ThemedText style={[Typography.label, { color: colors.textSecondary }]}>
            kg CO₂ Saved
          </ThemedText>
        </View>

        <View style={styles.divider} />

        <View style={styles.stat}>
          <ThemedText style={[Typography.h1, { color: colors.primary }]}>
            {treesEquiv.toFixed(1)}
          </ThemedText>
          <ThemedText style={[Typography.label, { color: colors.textSecondary }]}>
            Trees Saved
          </ThemedText>
        </View>
      </View>

      <ThemedText style={[Typography.micro, { color: colors.textSecondary, marginTop: Spacing.m }]}>
        Based on {gridZone} Grid Intensity (Average)
      </ThemedText>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    margin: Spacing.l,
    padding: Spacing.xl,
    borderRadius: Border.r20,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  stat: {
    flex: 1,
    alignItems: 'center',
  },
  divider: {
    width: 1,
    height: 40,
    backgroundColor: '#E1E4E8',
    marginHorizontal: Spacing.m,
    opacity: 0.2,
  },
});
