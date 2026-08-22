import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function SafetyEventCard({
  title = 'Safe Zone Exit: Home',
  time = 'Today, 1:15 PM',
  desc = "Subject departed the 'Home' geofence boundary.",
  icon = '🚪',
  isCritical = false,
  onPress,
}) {
  return (
    <TouchableOpacity
      style={[styles.card, isCritical && styles.cardCritical]}
      onPress={onPress}
      activeOpacity={0.85}
    >
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.icon}>{icon}</Text>
          <Text style={[styles.title, isCritical && styles.titleCritical]}>{title}</Text>
        </View>
        <Text style={styles.time}>{time}</Text>
      </View>
      <Text style={styles.desc}>{desc}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 10,
  },
  cardCritical: {
    borderColor: '#FECACA',
    backgroundColor: '#FEF2F2',
    borderLeftWidth: 4,
    borderLeftColor: '#DC2626',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  icon: {
    fontSize: 14,
  },
  title: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  titleCritical: {
    color: '#991B1B',
  },
  time: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  desc: {
    fontSize: 12,
    color: '#475569',
    lineHeight: 16,
  },
});
