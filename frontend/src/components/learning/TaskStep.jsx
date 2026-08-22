import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function TaskStep({ step, isCompleted, onToggle }) {
  return (
    <TouchableOpacity
      style={[styles.card, isCompleted && styles.cardDone]}
      onPress={onToggle}
      activeOpacity={0.85}
    >
      <View style={[styles.badge, isCompleted && styles.badgeDone]}>
        <Text style={styles.badgeText}>{isCompleted ? '✓' : step.step_number}</Text>
      </View>
      <View style={styles.textCol}>
        <Text style={[styles.title, isCompleted && styles.titleDone]}>{step.title}</Text>
        {step.instruction ? <Text style={styles.instruction}>{step.instruction}</Text> : null}
        {step.duration_sec ? <Text style={styles.duration}>⏱️ {step.duration_sec}s</Text> : null}
      </View>
      <Text style={styles.icon}>{step.icon || '⭐'}</Text>
    </TouchableOpacity>
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
  cardDone: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  badge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#EFF6FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeDone: {
    backgroundColor: '#10B981',
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '900',
    color: '#2563EB',
  },
  textCol: {
    flex: 1,
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  titleDone: {
    color: '#047857',
    textDecorationLine: 'line-through',
  },
  instruction: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  duration: {
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 2,
    fontWeight: '700',
  },
  icon: {
    fontSize: 22,
  },
});
