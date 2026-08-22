import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function ChatHeader({ name, onBack, onProfile }) {
  return (
    <View style={styles.header}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>← Back</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={onProfile} style={styles.titleRow}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.verifiedTag}>✓ Verified</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={onProfile}>
        <Text style={styles.profileText}>Profile</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backText: {
    fontSize: 16,
    color: '#4F46E5',
    fontWeight: '600',
  },
  titleRow: {
    alignItems: 'center',
  },
  name: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
  },
  verifiedTag: {
    fontSize: 11,
    color: '#16A34A',
    fontWeight: '600',
  },
  profileText: {
    fontSize: 15,
    color: '#4F46E5',
    fontWeight: '600',
  },
});
