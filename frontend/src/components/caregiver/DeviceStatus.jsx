import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function DeviceStatus({
  deviceName = 'Nivara Smart Band v2',
  batteryLevel = 84,
  isConnected = true,
  lastSync = '1 min ago',
  onSyncDevice,
}) {
  const getBatteryColor = () => {
    if (batteryLevel > 50) return '#22C55E';
    if (batteryLevel > 20) return '#EAB308';
    return '#EF4444';
  };

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.deviceRow}>
          <Text style={styles.icon}>⌚</Text>
          <View>
            <Text style={styles.deviceName}>{deviceName}</Text>
            <Text style={styles.lastSync}>Synced {lastSync}</Text>
          </View>
        </View>

        <View style={[styles.statusBadge, isConnected ? styles.connBg : styles.disconnBg]}>
          <Text style={[styles.statusText, isConnected ? styles.connTxt : styles.disconnTxt]}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </Text>
        </View>
      </View>

      <View style={styles.metricsRow}>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Battery</Text>
          <Text style={[styles.metricValue, { color: getBatteryColor() }]}>
            🔋 {batteryLevel}%
          </Text>
        </View>

        <View style={styles.divider} />

        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Bluetooth</Text>
          <Text style={styles.metricValue}>
            {isConnected ? '📶 Strong' : '❌ Offline'}
          </Text>
        </View>

        <View style={styles.divider} />

        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Sensors</Text>
          <Text style={styles.metricValue}>✅ Active</Text>
        </View>
      </View>

      {onSyncDevice && (
        <TouchableOpacity style={styles.syncBtn} onPress={onSyncDevice} activeOpacity={0.8}>
          <Text style={styles.syncBtnText}>🔄 Sync Device Now</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  deviceRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 24,
    marginRight: 10,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '700',
    color: '#F8FAFC',
  },
  lastSync: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  connBg: {
    backgroundColor: '#064E3B',
  },
  disconnBg: {
    backgroundColor: '#7F1D1D',
  },
  connTxt: {
    color: '#34D399',
    fontSize: 11,
    fontWeight: '600',
  },
  disconnTxt: {
    color: '#FCA5A5',
    fontSize: 11,
    fontWeight: '600',
  },
  metricsRow: {
    flexDirection: 'row',
    backgroundColor: '#0F172A',
    borderRadius: 12,
    padding: 12,
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  metricItem: {
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 11,
    color: '#64748B',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '700',
    color: '#F8FAFC',
  },
  divider: {
    width: 1,
    height: 24,
    backgroundColor: '#334155',
  },
  syncBtn: {
    backgroundColor: '#334155',
    borderRadius: 10,
    paddingVertical: 8,
    alignItems: 'center',
    marginTop: 12,
  },
  syncBtnText: {
    color: '#E2E8F0',
    fontSize: 13,
    fontWeight: '600',
  },
});
