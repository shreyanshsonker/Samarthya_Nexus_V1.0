import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedProps, 
  withTiming, 
  interpolateColor 
} from 'react-native-reanimated';
import Svg, { Circle, Text as SvgText, Defs, LinearGradient, Stop } from 'react-native-svg';
import { Colors, Typography } from '../constants/theme';
import { ThemedText } from './themed-text';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface EnergyGaugeProps {
  value: number; // Current Solar kW
  max: number;   // Capacity kW
  label?: string;
  theme?: 'light' | 'dark';
}

const RADIUS = 80;
const STROKE_WIDTH = 12;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export const EnergyGauge: React.FC<EnergyGaugeProps> = ({ 
  value, 
  max, 
  label = "Solar Generation",
  theme = 'dark' 
}) => {
  const progress = useSharedValue(0);
  const colors = Colors[theme];

  useEffect(() => {
    progress.value = withTiming(Math.min(value / max, 1), { duration: 1000 });
  }, [value, max]);

  const animatedProps = useAnimatedProps(() => ({
    strokeDashoffset: CIRCUMFERENCE * (1 - progress.value),
  }));

  return (
    <View style={styles.container}>
      <Svg height={RADIUS * 2 + STROKE_WIDTH} width={RADIUS * 2 + STROKE_WIDTH}>
        <Defs>
          <LinearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <Stop offset="0%" stopColor={colors.primary} stopOpacity="0.8" />
            <Stop offset="100%" stopColor={colors.primary} />
          </LinearGradient>
        </Defs>
        <Circle
          cx={RADIUS + STROKE_WIDTH / 2}
          cy={RADIUS + STROKE_WIDTH / 2}
          r={RADIUS}
          stroke={colors.border}
          strokeWidth={STROKE_WIDTH}
          fill="transparent"
        />
        <AnimatedCircle
          cx={RADIUS + STROKE_WIDTH / 2}
          cy={RADIUS + STROKE_WIDTH / 2}
          r={RADIUS}
          stroke="url(#grad)"
          strokeWidth={STROKE_WIDTH}
          strokeDasharray={CIRCUMFERENCE}
          animatedProps={animatedProps}
          strokeLinecap="round"
          fill="transparent"
          transform={`rotate(-90 ${RADIUS + STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2})`}
        />
      </Svg>
      
      <View style={styles.labelContainer}>
        <ThemedText style={[Typography.display, { color: colors.text }]}>
          {value.toFixed(1)}
        </ThemedText>
        <ThemedText style={[Typography.label, { color: colors.textSecondary }]}>
          kW
        </ThemedText>
        <ThemedText style={[Typography.bodySm, { color: colors.textSecondary, marginTop: 4 }]}>
          {label}
        </ThemedText>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  labelContainer: {
    position: 'absolute',
    alignItems: 'center',
  },
});
