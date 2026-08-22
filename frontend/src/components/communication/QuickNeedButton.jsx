import React from 'react';
import { Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function QuickNeedButton({ label, icon, onPress, color = '#2563EB', bgColor = '#EFF6FF' }) {
  return (
    <TouchableOpacity
      style={[styles.btn, { backgroundColor: bgColor, borderColor: color }]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <Text style={styles.icon}>{icon}</Text>
      <Text style={[styles.label, { color }]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: {
    width: '48%',
    minHeight: 110,
    borderRadius: 22,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
    marginVertical: 4,
  },
  icon: {
    fontSize: 34,
    marginBottom: 6,
  },
  label: {
    fontSize: 15,
    fontWeight: '900',
    textAlign: 'center',
  },
});
