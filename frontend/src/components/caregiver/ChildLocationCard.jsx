import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function ChildLocationCard({
  childName = 'Alex',
  locationName = 'Model Town',
  city = 'Ludhiana',
  accuracy = '±8 meters',
  isInsideSafeZone = true,
  safeZoneName = 'Home',
  onPressMap,
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.iconCircle}>
          <Text style={styles.icon}>📍</Text>
        </View>
        <View style={styles.titleCol}>
          <Text style={styles.title}>{childName}'s Live Location</Text>
          <Text style={styles.subtitle}>{locationName}, {city}</Text>
        </View>
        <View style={styles.accuracyBadge}>
          <Text style={styles.accuracyText}>{accuracy}</Text>
        </View>
      </View>

      <View style={styles.safeZoneRow}>
        <Text style={styles.safeZoneLabel}>
          Status: <Text style={isInsideSafeZone ? styles.safeText : styles.alertText}>
            {isInsideSafeZone ? `Inside Safe Zone (${safeZoneName})` : 'Outside Safe Zones'}
          </Text>
        </Text>
      </View>

      {onPressMap && (
        <TouchableOpacity style={styles.mapBtn} onPress={onPressMap} activeOpacity={0.85}>
          <Text style={styles.mapBtnText}>🗺️ Open Full Tactical Map</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  iconCircle: {
    width: 38,
    height: 38,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  icon: {
    fontSize: 18,
  },
  titleCol: {
    flex: 1,
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 1,
  },
  accuracyBadge: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  accuracyText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#475569',
  },
  safeZoneRow: {
    backgroundColor: '#F8FAFC',
    padding: 10,
    borderRadius: 10,
    marginBottom: 12,
  },
  safeZoneLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  safeText: {
    color: '#059669',
    fontWeight: '800',
  },
  alertText: {
    color: '#DC2626',
    fontWeight: '800',
  },
  mapBtn: {
    backgroundColor: '#0F3D87',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
  },
  mapBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
});
