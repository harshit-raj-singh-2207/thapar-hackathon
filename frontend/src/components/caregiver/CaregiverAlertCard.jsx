import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function CaregiverAlertCard({
  title = 'Critical Alert',
  message = 'Separation threshold breached.',
  time = 'Just now',
  onAcknowledge,
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.icon}>🚨</Text>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.time}>{time}</Text>
      </View>
      <Text style={styles.message}>{message}</Text>
      {onAcknowledge && (
        <TouchableOpacity style={styles.ackBtn} onPress={onAcknowledge} activeOpacity={0.85}>
          <Text style={styles.ackText}>✓ Acknowledge Alert</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FEF2F2',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: '#FECACA',
    marginBottom: 10,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
    gap: 6,
  },
  icon: {
    fontSize: 14,
  },
  title: {
    fontSize: 13,
    fontWeight: '900',
    color: '#991B1B',
    flex: 1,
  },
  time: {
    fontSize: 11,
    color: '#64748B',
  },
  message: {
    fontSize: 12,
    color: '#475569',
    marginBottom: 8,
  },
  ackBtn: {
    backgroundColor: '#B91C1C',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  ackText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '800',
  },
});
