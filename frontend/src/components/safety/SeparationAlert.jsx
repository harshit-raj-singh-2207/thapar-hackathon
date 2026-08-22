import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function SeparationAlert({
  distance = 24.5,
  threshold = 20,
  onDismiss,
  onTriggerBuzzer,
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.icon}>⚠️</Text>
        <Text style={styles.title}>Separation Breach Detected</Text>
      </View>
      <Text style={styles.desc}>
        Current distance is <Text style={styles.bold}>{distance}m</Text>, which exceeds your safety threshold of {threshold}m.
      </Text>
      <View style={styles.actions}>
        <TouchableOpacity style={styles.buzzerBtn} onPress={onTriggerBuzzer}>
          <Text style={styles.buzzerBtnText}>🔊 Sound Band Alarm</Text>
        </TouchableOpacity>
        {onDismiss && (
          <TouchableOpacity style={styles.dismissBtn} onPress={onDismiss}>
            <Text style={styles.dismissBtnText}>Dismiss</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
    borderLeftWidth: 5,
    borderLeftColor: '#DC2626',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
    gap: 8,
  },
  icon: {
    fontSize: 16,
  },
  title: {
    fontSize: 14,
    fontWeight: '900',
    color: '#991B1B',
  },
  desc: {
    fontSize: 12,
    color: '#475569',
    lineHeight: 18,
    marginBottom: 12,
  },
  bold: {
    fontWeight: '800',
    color: '#DC2626',
  },
  actions: {
    flexDirection: 'row',
    gap: 10,
  },
  buzzerBtn: {
    backgroundColor: '#DC2626',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  buzzerBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  dismissBtn: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  dismissBtnText: {
    color: '#475569',
    fontSize: 12,
    fontWeight: '700',
  },
});
