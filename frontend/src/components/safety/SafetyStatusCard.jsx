import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function SafetyStatusCard({ isSafe = true, currentZone = 'Home', battery = 82, onPress }) {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.85}>
      <View style={styles.header}>
        <View style={styles.iconCircle}>
          <Text style={styles.icon}>{isSafe ? '🛡️' : '⚠️'}</Text>
        </View>
        <View style={styles.info}>
          <Text style={styles.title}>{isSafe ? 'Child is Safe' : 'Safety Alert Active'}</Text>
          <Text style={styles.subtitle}>Current Area: {currentZone}</Text>
        </View>
        <View style={styles.safeBadge}>
          <Text style={styles.safeBadgeText}>{isSafe ? '✓ Safe' : 'Alert'}</Text>
        </View>
      </View>
      <View style={styles.footer}>
        <Text style={styles.batteryText}>🔋 Battery: {battery}%</Text>
        <Text style={styles.viewDetailsText}>View Live Map ›</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
    marginBottom: 14,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#ECFDF5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  icon: {
    fontSize: 20,
  },
  info: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  safeBadge: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  safeBadgeText: {
    color: '#059669',
    fontSize: 11,
    fontWeight: '800',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 14,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  batteryText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
  },
  viewDetailsText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#2563EB',
  },
});
