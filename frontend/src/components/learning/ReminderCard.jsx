import React from 'react';
import { View, Text, StyleSheet, Switch } from 'react-native';

export default function ReminderCard({ reminder, onToggle }) {
  return (
    <View style={styles.card}>
      <View style={styles.iconCircle}>
        <Text style={styles.icon}>{reminder.icon || '⏰'}</Text>
      </View>
      <View style={styles.textCol}>
        <Text style={styles.title}>{reminder.title}</Text>
        <Text style={styles.meta}>
          {reminder.time_str} • {reminder.frequency} • {reminder.category}
        </Text>
      </View>
      <Switch
        value={reminder.is_active}
        onValueChange={onToggle}
        trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
        thumbColor={reminder.is_active ? '#2563EB' : '#94A3B8'}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 14,
    gap: 12,
    marginVertical: 4,
  },
  iconCircle: {
    width: 42,
    height: 42,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    fontSize: 20,
  },
  textCol: {
    flex: 1,
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  meta: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
});
