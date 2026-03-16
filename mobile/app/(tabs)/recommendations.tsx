import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Colors, Spacing, Border, Typography } from '@/constants/theme';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { api } from '@/hooks/use-api';

interface Recommendation {
  id: string;
  category: 'load_shifting' | 'efficiency' | 'optimization';
  message: string;
  saving_kg: number;
  followed: boolean;
}

export default function RecommendationsScreen() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  const fetchRecommendations = async () => {
    try {
      const res = await api.recommendations.getToday();
      setRecommendations(res.data);
    } catch (error) {
      console.error("Recs fetch error:", error);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const toggleFollow = async (id: string, current: boolean) => {
    try {
      await api.recommendations.follow(id, !current);
      fetchRecommendations(); // Refresh list
    } catch (error) {
      console.error("Recs follow error:", error);
    }
  };

  const getIcon = (cat: string) => {
    switch (cat) {
      case 'load_shifting': return 'clock.fill';
      case 'efficiency': return 'bolt.fill';
      default: return 'sparkles';
    }
  };

  return (
    <ScrollView style={styles.container}>
      <ThemedView style={styles.header}>
        <ThemedText type="title">AI Insights</ThemedText>
        <ThemedText style={{ color: Colors.dark.textSecondary }}>
          Actionable tips to maximize your solar yield
        </ThemedText>
      </ThemedView>

      {recommendations.map((rec) => (
        <ThemedView 
          key={rec.id} 
          style={[styles.card, { opacity: rec.followed ? 0.6 : 1 }]}
        >
          <View style={styles.row}>
            <View style={[styles.iconContainer, { backgroundColor: Colors.dark.surface }]}>
              <IconSymbol name={getIcon(rec.category)} size={24} color={Colors.dark.primary} />
            </View>
            <View style={{ flex: 1, marginLeft: Spacing.m }}>
              <ThemedText type="subtitle" style={{ fontSize: 16 }}>{rec.category.replace('_', ' ').toUpperCase()}</ThemedText>
              <ThemedText style={styles.message}>{rec.message}</ThemedText>
            </View>
          </View>

          <View style={styles.footer}>
            <ThemedText style={{ color: Colors.dark.primary, fontWeight: '600' }}>
              Potential Saving: {rec.saving_kg} kg
            </ThemedText>
            <TouchableOpacity 
              style={[styles.btn, { backgroundColor: rec.followed ? Colors.dark.border : Colors.dark.primary }]}
              onPress={() => toggleFollow(rec.id, rec.followed)}
            >
              <ThemedText style={{ color: rec.followed ? Colors.dark.text : '#000', fontWeight: 'bold' }}>
                {rec.followed ? 'Followed' : 'Follow Tip'}
              </ThemedText>
            </TouchableOpacity>
          </View>
        </ThemedView>
      ))}
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
  card: {
    margin: Spacing.l,
    marginVertical: Spacing.s,
    padding: Spacing.xl,
    backgroundColor: '#1E1E2E',
    borderRadius: Border.r20,
  },
  row: {
    flexDirection: 'row',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  message: {
    marginTop: 4,
    color: Colors.dark.textSecondary,
    lineHeight: 20,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Spacing.xl,
    paddingTop: Spacing.m,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  btn: {
    paddingHorizontal: Spacing.l,
    paddingVertical: Spacing.s,
    borderRadius: 8,
  }
});
