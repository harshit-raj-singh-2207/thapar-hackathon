import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function MemberItem({ member, onPress }) {
  const { name, role, is_online } = member || {};

  return (
    <TouchableOpacity style={styles.item} onPress={onPress}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{name ? name[0] : 'M'}</Text>
      </View>
      <View style={styles.content}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.status}>{is_online ? '🟢 Online' : '⚪ Offline'}</Text>
      </View>
      {role === 'admin' && <Text style={styles.adminTag}>Admin</Text>}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  content: {
    flex: 1,
  },
  name: {
    fontSize: 15,
    fontWeight: '600',
    color: '#0F172A',
  },
  status: {
    fontSize: 12,
    color: '#64748B',
  },
  adminTag: {
    fontSize: 11,
    color: '#4F46E5',
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
});
