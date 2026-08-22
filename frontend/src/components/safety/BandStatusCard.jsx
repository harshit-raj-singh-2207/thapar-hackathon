import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function BandStatusCard({
  battery = 82,
  deviceId = 'NV-BAND-1024',
  firmware = 'v2.4.1',
  isConnected = true,
  onFindDevice,
  onRefresh,
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.iconBox}>
          <Text style={styles.icon}>⌚</Text>
        </View>
        <View style={styles.titleCol}>
          <Text style={styles.title}>Nivara GPS Band</Text>
          <Text style={styles.subtitle}>ID: {deviceId} • {firmware}</Text>
        </View>
        <View style={[styles.badge, isConnected ? styles.badgeGreen : styles.badgeRed]}>
          <Text style={[styles.badgeText, isConnected ? styles.badgeTextGreen : styles.badgeTextRed]}>
            {isConnected ? '● Connected' : 'Disconnected'}
          </Text>
        </View>
      </View>

      <View style={styles.metricRow}>
        <Text style={styles.metricLabel}>Battery Level: <Text style={styles.metricVal}>{battery}% (Charging)</Text></Text>
        <Text style={styles.metricLabel}>BLE Signal: <Text style={styles.metricValGreen}>Strong</Text></Text>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionBtn} onPress={onFindDevice}>
          <Text style={styles.actionBtnText}>🔍 Find Device</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={onRefresh}>
          <Text style={styles.actionBtnText}>🔄 Refresh</Text>
        </TouchableOpacity>
      </View>
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
  iconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  icon: {
    fontSize: 20,
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
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  badgeGreen: {
    backgroundColor: '#ECFDF5',
  },
  badgeRed: {
    backgroundColor: '#FEF2F2',
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '800',
  },
  badgeTextGreen: {
    color: '#059669',
  },
  badgeTextRed: {
    color: '#DC2626',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#F8FAFC',
    padding: 10,
    borderRadius: 10,
    marginBottom: 12,
  },
  metricLabel: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  metricVal: {
    color: '#0F172A',
    fontWeight: '800',
  },
  metricValGreen: {
    color: '#059669',
    fontWeight: '800',
  },
  actions: {
    flexDirection: 'row',
    gap: 10,
  },
  actionBtn: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  actionBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#0F172A',
  },
});
