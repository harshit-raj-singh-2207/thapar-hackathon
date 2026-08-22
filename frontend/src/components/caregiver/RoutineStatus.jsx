import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function RoutineStatus({
  completedCount = 3,
  totalCount = 5,
  nextActivity = 'Evening Sensory Calm Time (6:30 PM)',
  onAddActivity,
  onViewSchedule,
}) {
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.icon}>📅</Text>
          <Text style={styles.title}>Daily Routine Progress</Text>
        </View>
        <Text style={styles.progressBadge}>{completedCount} of {totalCount} Done</Text>
      </View>

      <View style={styles.progressBarBg}>
        <View style={[styles.progressBarFill, { width: `${progressPercent}%` }]} />
      </View>

      <View style={styles.nextSection}>
        <Text style={styles.nextLabel}>NEXT SCHEDULED ACTIVITY</Text>
        <Text style={styles.nextText}>🕒 {nextActivity}</Text>
      </View>

      <View style={styles.actionRow}>
        {onViewSchedule && (
          <TouchableOpacity style={styles.viewBtn} onPress={onViewSchedule} activeOpacity={0.8}>
            <Text style={styles.viewBtnText}>View Full Routine</Text>
          </TouchableOpacity>
        )}
        {onAddActivity && (
          <TouchableOpacity style={styles.addBtn} onPress={onAddActivity} activeOpacity={0.8}>
            <Text style={styles.addBtnText}>+ Add Activity</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 16,
    marginRight: 6,
  },
  title: {
    fontSize: 13,
    fontWeight: '700',
    color: '#94A3B8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  progressBadge: {
    color: '#34D399',
    fontSize: 12,
    fontWeight: '700',
    backgroundColor: '#064E3B',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  progressBarBg: {
    height: 8,
    backgroundColor: '#0F172A',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 14,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#4F46E5',
    borderRadius: 4,
  },
  nextSection: {
    backgroundColor: '#0F172A',
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
  },
  nextLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  nextText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#F8FAFC',
  },
  actionRow: {
    flexDirection: 'row',
    gap: 10,
  },
  viewBtn: {
    flex: 1,
    backgroundColor: '#334155',
    borderRadius: 10,
    paddingVertical: 9,
    alignItems: 'center',
  },
  viewBtnText: {
    color: '#E2E8F0',
    fontSize: 13,
    fontWeight: '600',
  },
  addBtn: {
    flex: 1,
    backgroundColor: '#4F46E5',
    borderRadius: 10,
    paddingVertical: 9,
    alignItems: 'center',
  },
  addBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
});
