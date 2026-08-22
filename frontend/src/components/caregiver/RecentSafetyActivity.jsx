import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function RecentSafetyActivity({ activities = [], onViewAll }) {
  const defaultActivities = [
    { id: '1', time: '9:15 AM', desc: 'Entered School Safe Zone', isSafe: true },
    { id: '2', time: '8:30 AM', desc: 'Left Home Safe Zone', isSafe: false },
  ];

  const list = activities.length ? activities : defaultActivities;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>Recent Safety Activity</Text>
        {onViewAll && (
          <TouchableOpacity onPress={onViewAll}>
            <Text style={styles.viewAll}>View All</Text>
          </TouchableOpacity>
        )}
      </View>
      <View style={styles.list}>
        {list.map((item, idx) => (
          <View key={item.id || idx} style={styles.item}>
            <View style={[styles.dot, item.isSafe ? styles.dotGreen : styles.dotGray]} />
            <View style={styles.itemBody}>
              <Text style={styles.time}>{item.time}</Text>
              <Text style={styles.desc}>{item.desc}</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  viewAll: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },
  list: {
    gap: 12,
  },
  item: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 4,
  },
  dotGreen: {
    backgroundColor: '#059669',
  },
  dotGray: {
    backgroundColor: '#94A3B8',
  },
  itemBody: {
    flex: 1,
  },
  time: {
    fontSize: 11,
    fontWeight: '700',
    color: '#0F172A',
  },
  desc: {
    fontSize: 12,
    color: '#475569',
    marginTop: 1,
  },
});
