import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function EmergencyAlert({
  title = 'CRITICAL ALERT: SOS Activated',
  message = 'Device panic button triggered near Elm Street intersection.',
  time = 'Today, 2:45 PM',
  onAcknowledge,
  onViewLocation,
  isAcknowledged = false,
}) {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.iconCircle}>
          <Text style={styles.icon}>🚨</Text>
        </View>
        <View style={styles.titleCol}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.time}>{time}</Text>
        </View>
      </View>
      <Text style={styles.message}>{message}</Text>
      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.ackBtn, isAcknowledged && styles.ackBtnDone]}
          onPress={onAcknowledge}
          activeOpacity={0.85}
        >
          <Text style={styles.ackBtnText}>{isAcknowledged ? '✓ Acknowledged' : 'Acknowledge'}</Text>
        </TouchableOpacity>
        {onViewLocation && (
          <TouchableOpacity style={styles.locBtn} onPress={onViewLocation} activeOpacity={0.85}>
            <Text style={styles.locBtnText}>🗺️ View Location</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
    borderLeftWidth: 5,
    borderLeftColor: '#DC2626',
    borderRadius: 16,
    padding: 16,
    marginBottom: 14,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  iconCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#DC2626',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  icon: {
    fontSize: 16,
  },
  titleCol: {
    flex: 1,
  },
  title: {
    fontSize: 14,
    fontWeight: '900',
    color: '#991B1B',
  },
  time: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  message: {
    fontSize: 12,
    color: '#475569',
    lineHeight: 18,
    marginBottom: 12,
  },
  actions: {
    flexDirection: 'row',
    gap: 10,
  },
  ackBtn: {
    backgroundColor: '#B91C1C',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  ackBtnDone: {
    backgroundColor: '#059669',
  },
  ackBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  locBtn: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  locBtnText: {
    color: '#0F172A',
    fontSize: 12,
    fontWeight: '700',
  },
});
