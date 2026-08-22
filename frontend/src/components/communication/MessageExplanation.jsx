import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function MessageExplanation({ originalText, simplifiedText, keyPoints = [] }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>SIMPLIFIED MESSAGE</Text>
      <Text style={styles.simpleText}>{simplifiedText}</Text>
      {keyPoints.length > 0 ? (
        <View style={styles.pointsList}>
          {keyPoints.map((pt, idx) => (
            <View key={idx} style={styles.pointRow}>
              <Text style={styles.pointDot}>•</Text>
              <Text style={styles.pointText}>{pt}</Text>
            </View>
          ))}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#EFF6FF',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#DBEAFE',
    padding: 16,
    marginVertical: 10,
  },
  title: {
    fontSize: 11,
    fontWeight: '900',
    color: '#1E40AF',
    letterSpacing: 0.8,
    marginBottom: 6,
  },
  simpleText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0F172A',
    lineHeight: 21,
    marginBottom: 8,
  },
  pointsList: {
    gap: 4,
  },
  pointRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  pointDot: {
    fontSize: 16,
    color: '#2563EB',
    fontWeight: '900',
  },
  pointText: {
    fontSize: 13,
    color: '#334155',
    fontWeight: '600',
  },
});
