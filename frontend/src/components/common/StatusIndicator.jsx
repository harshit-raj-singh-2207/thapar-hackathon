import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function StatusIndicator({ status = 'online', label, size = 8 }) {
  const getStatusColor = () => {
    switch (status.toLowerCase()) {
      case 'online':
      case 'active':
      case 'safe':
      case 'connected':
        return '#10B981';
      case 'warning':
      case 'weak':
        return '#F59E0B';
      case 'offline':
      case 'separated':
      case 'danger':
      case 'critical':
        return '#DC2626';
      default:
        return '#64748B';
    }
  };

  const color = getStatusColor();

  return (
    <View style={styles.container}>
      <View
        style={[
          styles.dot,
          { width: size, height: size, borderRadius: size / 2, backgroundColor: color },
        ]}
      />
      {label && <Text style={[styles.label, { color }]}>{label}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  dot: {
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
  },
  label: {
    fontSize: 12,
    fontWeight: '700',
  },
});
