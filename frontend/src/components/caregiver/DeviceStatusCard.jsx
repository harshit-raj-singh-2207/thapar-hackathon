import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function DeviceStatusCard({
  battery = 82,
  isCharging = true,
  gpsStatus = 'Active (3m)',
  bleStatus = 'Connected (Strong)',
}) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Device Status & Health</Text>
      <View style={styles.grid}>
        <View style={styles.tile}>
          <Text style={styles.tileLabel}>Battery</Text>
          <Text style={styles.tileVal}>{battery}%</Text>
          <Text style={styles.tileSub}>{isCharging ? 'Charging' : 'Discharging'}</Text>
        </View>
        <View style={styles.tile}>
          <Text style={styles.tileLabel}>GPS Connection</Text>
          <Text style={styles.tileVal}>Active</Text>
          <Text style={styles.tileSub}>{gpsStatus}</Text>
        </View>
        <View style={styles.tile}>
          <Text style={styles.tileLabel}>Bluetooth</Text>
          <Text style={styles.tileVal}>Connected</Text>
          <Text style={styles.tileSubGreen}>{bleStatus}</Text>
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
  grid: {
    flexDirection: 'row',
    gap: 10,
  },
  tile: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  tileLabel: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
    marginBottom: 4,
  },
  tileVal: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0F172A',
    marginBottom: 2,
  },
  tileSub: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '500',
  },
  tileSubGreen: {
    fontSize: 10,
    color: '#059669',
    fontWeight: '700',
  },
});
