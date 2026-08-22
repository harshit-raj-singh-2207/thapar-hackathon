import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function GroupHeader({ name, onBack, onDetails, onMembers }) {
  return (
    <View style={styles.header}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>← Back</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={onDetails} style={styles.titleRow}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.subtext}>Caregiver Support Circle</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={onMembers}>
        <Text style={styles.membersText}>Members</Text>
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
  subtext: {
    fontSize: 11,
    color: '#64748B',
  },
  membersText: {
    fontSize: 15,
    color: '#4F46E5',
    fontWeight: '600',
  },
});
