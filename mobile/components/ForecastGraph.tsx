import React from 'react';
import { View, StyleSheet, useColorScheme, Dimensions } from 'react-native';
import { 
  VictoryChart, 
  VictoryLine, 
  VictoryArea, 
  VictoryAxis, 
  VictoryTheme,
  VictoryTooltip,
  VictoryVoronoiContainer 
} from 'victory-native';
import { Colors, Spacing, Typography } from '../constants/theme';
import { ThemedText } from './themed-text';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface ForecastGraphProps {
  data: Array<{ timestamp: string; predicted_kw: number }>;
  title?: string;
}

export const ForecastGraph: React.FC<ForecastGraphProps> = ({ data, title = "Solar Forecast (Next 4h)" }) => {
  const colorScheme = useColorScheme() ?? 'dark';
  const colors = Colors[colorScheme];

  // Map data for Victory: x as index or timestamp, y as kw
  const chartData = data.map((d, i) => ({
    x: new Date(d.timestamp),
    y: d.predicted_kw,
    label: `${d.predicted_kw.toFixed(2)} kW`
  }));

  if (chartData.length === 0) return null;

  return (
    <View style={styles.container}>
      <ThemedText style={[Typography.h2, { marginBottom: Spacing.m, paddingHorizontal: Spacing.l }]}>
        {title}
      </ThemedText>
      
      <VictoryChart
        width={SCREEN_WIDTH}
        height={220}
        theme={VictoryTheme.material}
        padding={{ top: 20, bottom: 40, left: 50, right: 30 }}
        containerComponent={<VictoryVoronoiContainer />}
      >
        <Defs>
          <LinearGradient id="areaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <Stop offset="0%" stopColor={colors.primary} stopOpacity="0.3" />
            <Stop offset="100%" stopColor={colors.primary} stopOpacity="0" />
          </LinearGradient>
        </Defs>

        <VictoryAxis
          style={{
            axis: { stroke: colors.border },
            tickLabels: { fill: colors.textSecondary, fontSize: 10 },
            grid: { stroke: 'transparent' }
          }}
          tickFormat={(t) => {
            const date = new Date(t);
            return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
          }}
          tickCount={4}
        />

        <VictoryAxis
          dependentAxis
          style={{
            axis: { stroke: 'transparent' },
            tickLabels: { fill: colors.textSecondary, fontSize: 10 },
            grid: { stroke: colors.border, strokeDasharray: '4, 4' }
          }}
          tickFormat={(t) => `${t}kW`}
        />

        <VictoryArea
          data={chartData}
          style={{
            data: { fill: 'url(#areaGrad)' }
          }}
          interpolation="monotoneX"
        />

        <VictoryLine
          data={chartData}
          style={{
            data: { stroke: colors.primary, strokeWidth: 3 }
          }}
          interpolation="monotoneX"
        />
      </VictoryChart>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: Spacing.xl,
    backgroundColor: 'transparent',
  },
});
