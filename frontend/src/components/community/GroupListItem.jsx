import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function GroupListItem({ group, onPress, onJoinToggle }) {
  const { name, description, category, member_count, is_joined } = group;

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View style={styles.iconContainer}>
        <Text style={styles.iconText}>👥</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.topRow}>
          <Text style={styles.name}>{name}</Text>
          {category && <Text style={styles.categoryBadge}>{category}</Text>}
        </View>
        <Text style={styles.description} numberOfLines={2}>
          {description || 'Caregiver group'}
        </Text>
        <Text style={styles.memberText}>{member_count || 1} members</Text>
      </View>

      <TouchableOpacity
        style={[styles.joinBtn, is_joined ? styles.leaveBtn : styles.activeJoinBtn]}
        onPress={onJoinToggle}
      >
        <Text style={[styles.joinBtnText, is_joined && styles.leaveBtnText]}>
          {is_joined ? 'Joined' : 'Join'}
        </Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  iconText: {
    fontSize: 22,
  },
  content: {
    flex: 1,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 2,
  },
  name: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    flex: 1,
  },
  categoryBadge: {
    fontSize: 11,
    color: '#4F46E5',
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    fontWeight: '600',
  },
  description: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 4,
  },
  memberText: {
    fontSize: 12,
    color: '#94A3B8',
  },
  joinBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginLeft: 8,
  },
  activeJoinBtn: {
    backgroundColor: '#4F46E5',
  },
  leaveBtn: {
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  joinBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
  leaveBtnText: {
    color: '#475569',
  },
});
