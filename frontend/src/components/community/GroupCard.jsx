import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function GroupCard({ group, onPress, onJoinToggle }) {
  const { name, description, category, member_count, is_joined } = group || {};

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View style={styles.header}>
        <Text style={styles.name}>{name}</Text>
        {category && <Text style={styles.category}>{category}</Text>}
      </View>
      <Text style={styles.desc} numberOfLines={2}>{description}</Text>
      <View style={styles.footer}>
        <Text style={styles.members}>{member_count || 1} members</Text>
        {onJoinToggle && (
          <TouchableOpacity style={styles.btn} onPress={onJoinToggle}>
            <Text style={styles.btnText}>{is_joined ? 'Joined' : 'Join'}</Text>
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  name: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
  },
  category: {
    fontSize: 12,
    color: '#4F46E5',
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  desc: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  members: {
    fontSize: 12,
    color: '#94A3B8',
  },
  btn: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  btnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
});
