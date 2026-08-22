import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function SentenceSuggestion({ suggestions = [], onSelectSuggestion }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>💡 SUGGESTED WAYS TO SAY THIS:</Text>
      <View style={styles.chipsRow}>
        {suggestions.map((item, idx) => (
          <TouchableOpacity
            key={idx}
            style={styles.chip}
            onPress={() => onSelectSuggestion && onSelectSuggestion(item)}
            activeOpacity={0.8}
          >
            <Text style={styles.chipText}>"{item}"</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 8,
  },
  heading: {
    fontSize: 10,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 6,
  },
  chipsRow: {
    flexDirection: 'column',
    gap: 6,
  },
  chip: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  chipText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1E40AF',
  },
});
