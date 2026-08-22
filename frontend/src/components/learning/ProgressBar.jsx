import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function ProgressBar({ progress = 0, color = '#2563EB', showLabel = true }) {
  const clampPct = Math.max(0, Math.min(100, progress));

  return (
    <View style={styles.container}>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${clampPct}%`, backgroundColor: color }]} />
      </View>
      {showLabel ? <Text style={styles.label}>{clampPct}%</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginVertical: 4,
  },
  track: {
    flex: 1,
    height: 8,
    backgroundColor: '#F1F5F9',
    borderRadius: 999,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    borderRadius: 999,
  },
  label: {
    fontSize: 12,
    fontWeight: '800',
    color: '#475569',
    minWidth: 32,
  },
});
