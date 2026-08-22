import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function TaskCard({ task, onPress }) {
  const steps = task.steps_data || [];
  const completedCount = steps.filter((s) => s.is_completed).length;

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.88}>
      <View style={styles.header}>
        <Text style={styles.icon}>{task.icon || '📋'}</Text>
        <View style={styles.textCol}>
          <Text style={styles.title}>{task.title}</Text>
          <Text style={styles.sub}>
            {completedCount} of {steps.length} steps completed
          </Text>
        </View>
        {task.is_completed ? (
          <View style={styles.doneBadge}>
            <Text style={styles.doneText}>✓ Done</Text>
          </View>
        ) : null}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 16,
    marginVertical: 6,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  icon: {
    fontSize: 26,
  },
  textCol: {
    flex: 1,
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  sub: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  doneBadge: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  doneText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#059669',
  },
});
