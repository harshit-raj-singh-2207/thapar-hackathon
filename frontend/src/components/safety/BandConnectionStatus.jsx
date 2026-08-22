import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function BandConnectionStatus({ isConnected = true, signalStrength = 'Strong' }) {
  return (
    <View style={styles.container}>
      <Text style={styles.icon}>ᛒ</Text>
      <Text style={styles.label}>Bluetooth Band:</Text>
      <Text style={[styles.status, isConnected ? styles.connected : styles.disconnected]}>
        {isConnected ? `Connected (${signalStrength})` : 'Disconnected'}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
    gap: 6,
  },
  icon: {
    fontSize: 14,
    color: '#1E40AF',
    fontWeight: '900',
  },
  label: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  status: {
    fontSize: 12,
    fontWeight: '800',
  },
  connected: {
    color: '#059669',
  },
  disconnected: {
    color: '#DC2626',
  },
});
