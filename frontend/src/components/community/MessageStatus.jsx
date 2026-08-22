import React from 'react';
import { Text, StyleSheet } from 'react-native';

export default function MessageStatus({ status = 'sent' }) {
  const getStatusSymbol = () => {
    switch (status) {
      case 'read':
        return '✓✓';
      case 'delivered':
        return '✓✓';
      case 'sending':
        return '🕒';
      default:
        return '✓';
    }
  };

  return <Text style={[styles.text, status === 'read' && styles.read]}>{getStatusSymbol()}</Text>;
}

const styles = StyleSheet.create({
  text: {
    fontSize: 11,
    color: '#94A3B8',
    marginLeft: 4,
  },
  read: {
    color: '#3B82F6',
  },
});
