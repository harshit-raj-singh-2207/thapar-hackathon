import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function SafetyOverview({ isSafe = true, activeSafeZonesCount = 2, alertsCount = 0 }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Safety Overview</Text>
      <View style={styles.metricsRow}>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Safety State</Text>
          <Text style={styles.safeText}>{isSafe ? 'Protected' : 'Alert'}</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Active Safe Zones</Text>
          <Text style={styles.metricVal}>{activeSafeZonesCount}</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Pending Alerts</Text>
          <Text style={styles.metricVal}>{alertsCount}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 12,
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 10,
  },
  metricItem: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  metricLabel: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
    marginBottom: 4,
  },
  safeText: {
    fontSize: 14,
    fontWeight: '900',
    color: '#059669',
  },
  metricVal: {
    fontSize: 14,
    fontWeight: '900',
    color: '#0F172A',
  },
});
