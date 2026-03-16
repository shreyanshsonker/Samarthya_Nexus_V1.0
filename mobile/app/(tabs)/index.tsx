import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, RefreshControl } from 'react-native';
import { Colors, Spacing } from '@/constants/theme';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { EnergyGauge } from '@/components/EnergyGauge';
import { CarbonStatsCard } from '@/components/CarbonStatsCard';
import { ForecastGraph } from '@/components/ForecastGraph';
import { useEnergyStore, useForecastStore } from '@/hooks/use-stores';
import { api } from '@/hooks/use-api';

export default function DashboardScreen() {
  const { solar_kw, setReading } = useEnergyStore();
  const { forecast, greenWindow, setForecast, setGreenWindow } = useForecastStore();
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      // 1. Live Energy
      const energyRes = await api.energy.getCurrent();
      setReading(energyRes.data);

      // 2. Forecasts
      const forecastRes = await api.forecast.getSolar();
      setForecast(forecastRes.data);

      // 3. Green Window
      const gwRes = await api.forecast.getGreenWindow();
      setGreenWindow(gwRes.data);
    } catch (error) {
      console.error("Dashboard fetch error:", error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchData();
    // Poll energy every 30s
    const interval = setInterval(() => {
      api.energy.getCurrent().then(res => setReading(res.data));
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ScrollView 
      style={styles.container} 
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <ThemedView style={styles.header}>
        <ThemedText type="title">Nexus Dashboard</ThemedText>
        <ThemedText style={{ color: Colors.dark.textSecondary, fontSize: 14 }}>
          Gwalior, India
        </ThemedText>
      </ThemedView>

      <EnergyGauge 
        value={solar_kw} 
        max={5.0} 
        label="Current Generation" 
      />

      <CarbonStatsCard 
        savingsKg={12.45} // Demo aggregate
        treesEquiv={0.8}
      />

      {forecast.length > 0 && (
        <ForecastGraph data={forecast} />
      )}

      {greenWindow && greenWindow.window && (
        <ThemedView style={styles.gwBanner}>
          <ThemedText type="subtitle">Next Green Window</ThemedText>
          <ThemedText style={{ marginTop: 4, color: '#fff' }}>
            {new Date(greenWindow.window.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} 
            {" - "}
            {new Date(greenWindow.window.end).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </ThemedText>
        </ThemedView>
      )}
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
  gwBanner: {
    margin: Spacing.l,
    padding: Spacing.xl,
    backgroundColor: '#1E1E2E',
    borderRadius: 16,
    borderLeftWidth: 4,
    borderLeftColor: Colors.dark.primary,
  }
});
