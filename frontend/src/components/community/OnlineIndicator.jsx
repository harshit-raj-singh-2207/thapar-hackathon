import React from 'react';
import { View, StyleSheet } from 'react-native';

export default function OnlineIndicator({ isOnline }) {
  return <View style={[styles.dot, isOnline ? styles.online : styles.offline]} />;
}

const styles = StyleSheet.create({
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
  },
  online: {
    backgroundColor: '#22C55E',
  },
  offline: {
    backgroundColor: '#94A3B8',
  },
});
