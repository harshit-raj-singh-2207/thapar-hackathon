import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';

export default function SafetyEventDetailsScreen({ navigation, route }) {
  const event = route?.params?.event || {
    title: 'SOS Activated',
    time: 'Today, 2:45 PM',
    location: 'Near Elm Street intersection, Model Town, Ludhiana',
    desc: 'Device panic button was triggered manually from Nivara GPS Band. High-frequency live GPS tracking escalated.',
    battery: '82%',
    gpsAccuracy: '±3m',
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.headerRow}>
          <TouchableOpacity onPress={() => navigation?.goBack?.()} style={styles.backBtn}>
            <Text style={styles.backText}>‹ Back</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Safety Event Details</Text>
        </View>

        <View style={styles.eventCard}>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>🚨 CRITICAL ALERT</Text>
          </View>
          <Text style={styles.eventTitle}>{event.title}</Text>
          <Text style={styles.eventTime}>{event.time}</Text>

          <View style={styles.divider} />

          <Text style={styles.sectionLabel}>DESCRIPTION</Text>
          <Text style={styles.eventDesc}>{event.desc}</Text>

          <Text style={styles.sectionLabel}>LOCATION FIX</Text>
          <Text style={styles.locationVal}>{event.location}</Text>

          <View style={styles.metricsRow}>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>Device Battery</Text>
              <Text style={styles.metricVal}>{event.battery}</Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>GPS Precision</Text>
              <Text style={styles.metricVal}>{event.gpsAccuracy}</Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.mapBtn}
            onPress={() => navigation?.navigate?.('LiveLocation')}
            activeOpacity={0.85}
          >
            <Text style={styles.mapBtnText}>🗺️ View on Live Map</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  container: {
    flex: 1,
  },
  content: {
    padding: 20,
    maxWidth: 600,
    alignSelf: 'center',
    width: '100%',
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  backBtn: {
    paddingRight: 14,
    paddingVertical: 6,
  },
  backText: {
    fontSize: 16,
    color: '#2563EB',
    fontWeight: '800',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  eventCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
  },
  statusBadge: {
    backgroundColor: '#FEE2E2',
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    marginBottom: 10,
  },
  statusText: {
    color: '#991B1B',
    fontSize: 11,
    fontWeight: '900',
  },
  eventTitle: {
    fontSize: 20,
    fontWeight: '900',
    color: '#0F172A',
    marginBottom: 4,
  },
  eventTime: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  divider: {
    height: 1,
    backgroundColor: '#EEF2F6',
    marginVertical: 18,
  },
  sectionLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 6,
    marginTop: 10,
  },
  eventDesc: {
    fontSize: 13,
    color: '#334155',
    lineHeight: 20,
  },
  locationVal: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
    lineHeight: 18,
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 18,
    marginBottom: 20,
  },
  metricBox: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  metricLabel: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
    marginBottom: 4,
  },
  metricVal: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  mapBtn: {
    backgroundColor: '#0F3D87',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  mapBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
  },
});
