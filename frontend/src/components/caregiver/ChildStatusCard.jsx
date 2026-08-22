import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function ChildStatusCard({
  childName = 'Leo',
  age = 7,
  currentMood = 'Calm & Focused',
  moodType = 'calm', // calm, happy, sensory_alert, overwhelmed
  heartRate = 78,
  lastUpdated = '2 mins ago',
  onUpdateStatus,
}) {
  const getMoodBadgeStyle = () => {
    switch (moodType) {
      case 'happy':
        return { bg: '#065F46', text: '#34D399', icon: '😊' };
      case 'sensory_alert':
        return { bg: '#78350F', text: '#FBBF24', icon: '⚠️' };
      case 'overwhelmed':
        return { bg: '#7F1D1D', text: '#FCA5A5', icon: '🌩️' };
      default:
        return { bg: '#1E1B4B', text: '#818CF8', icon: '😌' };
    }
  };

  const badge = getMoodBadgeStyle();

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.childName}>{childName}</Text>
          <Text style={styles.childAge}>Age {age}</Text>
        </View>
        <Text style={styles.updatedText}>Updated {lastUpdated}</Text>
      </View>

      <View style={styles.statusSection}>
        <View style={[styles.moodBadge, { backgroundColor: badge.bg }]}>
          <Text style={styles.moodIcon}>{badge.icon}</Text>
          <Text style={[styles.moodText, { color: badge.text }]}>{currentMood}</Text>
        </View>

        <View style={styles.metricContainer}>
          <Text style={styles.metricValue}>❤️ {heartRate} <Text style={styles.metricUnit}>BPM</Text></Text>
          <Text style={styles.metricLabel}>Heart Rate</Text>
        </View>
      </View>

      {onUpdateStatus && (
        <TouchableOpacity style={styles.actionBtn} onPress={onUpdateStatus} activeOpacity={0.8}>
          <Text style={styles.actionBtnText}>Update Child Status</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 18,
    marginHorizontal: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: '#334155',
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  childName: {
    fontSize: 20,
    fontWeight: '700',
    color: '#F8FAFC',
    marginRight: 8,
  },
  childAge: {
    fontSize: 14,
    color: '#94A3B8',
    fontWeight: '500',
  },
  updatedText: {
    fontSize: 12,
    color: '#64748B',
  },
  statusSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  moodBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    flex: 1,
    marginRight: 12,
  },
  moodIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  moodText: {
    fontSize: 14,
    fontWeight: '600',
  },
  metricContainer: {
    alignItems: 'flex-end',
    backgroundColor: '#0F172A',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 12,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#F8FAFC',
  },
  metricUnit: {
    fontSize: 11,
    color: '#94A3B8',
    fontWeight: '400',
  },
  metricLabel: {
    fontSize: 10,
    color: '#64748B',
    marginTop: 2,
  },
  actionBtn: {
    backgroundColor: '#4F46E5',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  actionBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});
