import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function LearningCard({ topic, onPress }) {
  return (
    <TouchableOpacity
      style={[styles.card, { borderLeftColor: topic.color || '#10B981' }]}
      onPress={onPress}
      activeOpacity={0.88}
    >
      <View style={styles.header}>
        <Text style={styles.icon}>{topic.icon || '📖'}</Text>
        <View style={styles.textCol}>
          <Text style={styles.category}>{topic.category}</Text>
          <Text style={styles.title}>{topic.title}</Text>
        </View>
        {topic.is_completed ? (
          <View style={styles.doneBadge}>
            <Text style={styles.doneText}>✓ Done</Text>
          </View>
        ) : null}
      </View>
      {topic.description ? <Text style={styles.desc}>{topic.description}</Text> : null}
      <View style={styles.progressTrack}>
        <View
          style={[
            styles.progressFill,
            { width: `${topic.progress_pct || 0}%`, backgroundColor: topic.color || '#10B981' },
          ]}
        />
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
    borderLeftWidth: 5,
    padding: 16,
    marginVertical: 6,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 8,
  },
  icon: {
    fontSize: 26,
  },
  textCol: {
    flex: 1,
  },
  category: {
    fontSize: 11,
    fontWeight: '800',
    color: '#64748B',
    textTransform: 'uppercase',
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
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
  desc: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 10,
    lineHeight: 16,
  },
  progressTrack: {
    height: 6,
    backgroundColor: '#F1F5F9',
    borderRadius: 999,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 999,
  },
});
