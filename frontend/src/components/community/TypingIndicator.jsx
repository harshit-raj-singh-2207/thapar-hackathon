import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function TypingIndicator({ name = 'Caregiver' }) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>{name} is typing...</Text>
      <View style={styles.dotsRow}>
        <View style={styles.dot} />
        <View style={styles.dot} />
        <View style={styles.dot} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 6,
    gap: 6,
  },
  text: {
    fontSize: 12,
    color: '#64748B',
    fontStyle: 'italic',
  },
  dotsRow: {
    flexDirection: 'row',
    gap: 3,
  },
  dot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#64748B',
  },
});
