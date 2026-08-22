import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function BandStatus({
  device = 'NIVARA SmartBand #NV-8821',
  battery = 88,
  isCharging = false,
  connectionState = 'CONNECTED',
  heartRate = 78,
  skinTemp = '36.4°C',
  onTriggerSOS,
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <View style={styles.iconCircle}>
            <Text style={styles.icon}>⌚</Text>
          </View>
          <View>
            <Text style={styles.title}>{device}</Text>
            <Text style={styles.subtitle}>Child Wearable Health & Telemetry</Text>
          </View>
        </View>

        <View style={styles.connectionBadge}>
          <View style={styles.liveDot} />
          <Text style={styles.connectionText}>4G + BLE 5.2 Link</Text>
        </View>
      </View>

      {/* Sensor Metrics Row */}
      <View style={styles.metricsRow}>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>BATTERY</Text>
          <Text style={styles.metricVal}>
            🔋 {battery}% {isCharging ? '⚡' : ''}
          </Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>HEART RATE</Text>
          <Text style={styles.metricVal}>❤️ {heartRate} bpm</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>SKIN TEMP</Text>
          <Text style={styles.metricVal}>🌡️ {skinTemp}</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>MOTION</Text>
          <Text style={styles.metricVal}>🚶 Calm</Text>
        </View>
      </View>

      {/* SOS Button */}
      {onTriggerSOS && (
        <TouchableOpacity
          style={styles.sosButton}
          onPress={onTriggerSOS}
          activeOpacity={0.85}
        >
          <Text style={styles.sosText}>🚨 Trigger Emergency Caregiver Alert</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    flexWrap: 'wrap',
    gap: 8,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconCircle: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  icon: {
    fontSize: 20,
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  connectionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#A7F3D0',
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#10B981',
    marginRight: 6,
  },
  connectionText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#059669',
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 14,
    flexWrap: 'wrap',
  },
  metricCard: {
    flex: 1,
    minWidth: 70,
    backgroundColor: '#F8FAFC',
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 8,
    fontWeight: '800',
    color: '#64748B',
    marginBottom: 2,
    letterSpacing: 0.5,
  },
  metricVal: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  sosButton: {
    backgroundColor: '#FEE2E2',
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  sosText: {
    color: '#DC2626',
    fontSize: 13,
    fontWeight: '800',
  },
});
