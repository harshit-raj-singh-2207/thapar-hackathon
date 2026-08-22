import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function CurrentLocationCard({
  zoneName = 'Home Safe Zone',
  address = '742 Evergreen Terrace, Springfield',
  isInSafeZone = true,
  lastUpdated = 'Just now',
  gpsAccuracy = 'High (±3m)',
  onViewMap,
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.icon}>📍</Text>
          <Text style={styles.title}>Current Location</Text>
        </View>
        <View style={[styles.zoneBadge, isInSafeZone ? styles.safeBg : styles.warnBg]}>
          <Text style={[styles.zoneText, isInSafeZone ? styles.safeTxt : styles.warnTxt]}>
            {isInSafeZone ? '🛡️ Safe Zone' : '⚠️ Outside Safe Zone'}
          </Text>
        </View>
      </View>

      <Text style={styles.zoneName}>{zoneName}</Text>
      <Text style={styles.address}>{address}</Text>

      <View style={styles.metaRow}>
        <Text style={styles.metaText}>Updated: {lastUpdated}</Text>
        <Text style={styles.metaText}>Accuracy: {gpsAccuracy}</Text>
      </View>

      {onViewMap && (
        <TouchableOpacity style={styles.mapBtn} onPress={onViewMap} activeOpacity={0.8}>
          <Text style={styles.mapBtnText}>🗺️ View Live Location Map</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 16,
    marginRight: 6,
  },
  title: {
    fontSize: 14,
    fontWeight: '700',
    color: '#94A3B8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  zoneBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  safeBg: {
    backgroundColor: '#064E3B',
  },
  warnBg: {
    backgroundColor: '#78350F',
  },
  safeTxt: {
    color: '#34D399',
    fontSize: 11,
    fontWeight: '600',
  },
  warnTxt: {
    color: '#FBBF24',
    fontSize: 11,
    fontWeight: '600',
  },
  zoneName: {
    fontSize: 17,
    fontWeight: '700',
    color: '#F8FAFC',
  },
  address: {
    fontSize: 13,
    color: '#CBD5E1',
    marginTop: 4,
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  metaText: {
    fontSize: 11,
    color: '#64748B',
  },
  mapBtn: {
    backgroundColor: '#2563EB',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
    marginTop: 12,
  },
  mapBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
});
