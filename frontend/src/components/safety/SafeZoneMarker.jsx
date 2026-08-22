import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function SafeZoneMarker({ zone, isSelected }) {
  return (
    <View
      style={[
        styles.markerContainer,
        { backgroundColor: `${zone.color || '#3B82F6'}22` },
        isSelected && styles.selectedMarker,
      ]}
    >
      <Text style={styles.icon}>{zone.icon || '🛡️'}</Text>
      <Text style={styles.name} numberOfLines={1}>
        {zone.name}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  markerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#3B82F6',
  },
  selectedMarker: {
    borderColor: '#FFFFFF',
    borderWidth: 2,
  },
  icon: {
    fontSize: 12,
    marginRight: 4,
  },
  name: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
