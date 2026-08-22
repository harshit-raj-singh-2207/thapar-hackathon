import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function RoutineCard({ routine, onToggleStep, onOpenDetails }) {
  const steps = routine.steps || [];
  const completedCount = steps.filter((s) => s.is_completed).length;
  const totalCount = steps.length;
  const pct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <TouchableOpacity style={styles.card} onPress={onOpenDetails} activeOpacity={0.88}>
      <View style={styles.header}>
        <View style={[styles.iconCircle, { backgroundColor: `${routine.color || '#3B82F6'}15` }]}>
          <Text style={styles.icon}>{routine.icon || '🌅'}</Text>
        </View>
        <View style={styles.titleCol}>
          <Text style={styles.title}>{routine.title}</Text>
          <Text style={styles.subtitle}>
            {completedCount} of {totalCount} steps completed • {pct}%
          </Text>
        </View>
        <View style={styles.streakBadge}>
          <Text style={styles.streakFlame}>🔥</Text>
          <Text style={styles.streakNum}>{routine.streak_days || 0}d</Text>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressBarTrack}>
        <View style={[styles.progressBarFill, { width: `${pct}%`, backgroundColor: routine.color || '#3B82F6' }]} />
      </View>

      {/* Mini Steps Preview */}
      <View style={styles.stepsRow}>
        {steps.slice(0, 4).map((s, idx) => (
          <TouchableOpacity
            key={s.id || idx}
            style={[styles.stepChip, s.is_completed && styles.stepChipDone]}
            onPress={() => onToggleStep && onToggleStep(routine.id, s.id)}
            activeOpacity={0.8}
          >
            <Text style={styles.stepChipIcon}>{s.icon || '✓'}</Text>
            <Text style={[styles.stepChipText, s.is_completed && styles.stepChipTextDone]} numberOfLines={1}>
              {s.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 18,
    marginBottom: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  iconCircle: {
    width: 46,
    height: 46,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  icon: {
    fontSize: 24,
  },
  titleCol: {
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
    fontWeight: '500',
  },
  streakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF7ED',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FFEDD5',
    gap: 4,
  },
  streakFlame: {
    fontSize: 14,
  },
  streakNum: {
    fontSize: 12,
    fontWeight: '800',
    color: '#EA580C',
  },
  progressBarTrack: {
    height: 8,
    backgroundColor: '#F1F5F9',
    borderRadius: 999,
    overflow: 'hidden',
    marginBottom: 14,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 999,
  },
  stepsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  stepChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    gap: 6,
    maxWidth: '48%',
  },
  stepChipDone: {
    backgroundColor: '#ECFDF5',
    borderColor: '#A7F3D0',
  },
  stepChipIcon: {
    fontSize: 13,
  },
  stepChipText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
    flexShrink: 1,
  },
  stepChipTextDone: {
    color: '#059669',
    textDecorationLine: 'line-through',
  },
});
