import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function SpeechButton({ onPress, speaking = false, label = 'Speak' }) {
  return (
    <TouchableOpacity
      style={[styles.btn, speaking && styles.btnSpeaking]}
      onPress={onPress}
      activeOpacity={0.85}
    >
      <Text style={styles.icon}>🗣️</Text>
      <Text style={[styles.label, speaking && styles.labelSpeaking]}>
        {speaking ? 'Speaking...' : label}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 999,
    gap: 8,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  btnSpeaking: {
    backgroundColor: '#EFF6FF',
    borderColor: '#2563EB',
  },
  icon: {
    fontSize: 16,
  },
  label: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  labelSpeaking: {
    color: '#2563EB',
  },
});
