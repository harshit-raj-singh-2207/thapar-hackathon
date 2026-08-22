import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function GPSStatusPanel({
  gpsStatus = 'ACTIVE',
  childLocation,
  onSimulateStatus,
}) {
  const statusOptions = [
    {
      id: 'ACTIVE',
      label: 'Active',
      color: '#059669',
      bg: '#ECFDF5',
      borderColor: '#A7F3D0',
      icon: '🟢',
      satellites: '14 / 16',
      accuracy: '±3.2m',
      hdop: '0.8 (Excellent)',
      signal: '-68 dBm (Strong)',
      desc: 'Dual-band GNSS locked with sub-meter differential correction.',
    },
    {
      id: 'WEAK',
      label: 'Weak',
      color: '#D97706',
      bg: '#FEF3C7',
      borderColor: '#FDE68A',
      icon: '🟡',
      satellites: '5 / 16',
      accuracy: '±22.5m',
      hdop: '3.4 (Fair)',
      signal: '-94 dBm (Marginal)',
      desc: 'Urban canyon or indoor interference detected. Triangulating via cell towers.',
    },
    {
      id: 'UNAVAILABLE',
      label: 'Unavailable',
      color: '#EA580C',
      bg: '#FFEDD5',
      borderColor: '#FED7AA',
      icon: '🟠',
      satellites: '1 / 16',
      accuracy: '±75.0m',
      hdop: '8.2 (Poor)',
      signal: '-110 dBm (Weak)',
      desc: 'No direct line of sight to GNSS constellation (Underground or deep indoors).',
    },
    {
      id: 'OFFLINE',
      label: 'Offline',
      color: '#DC2626',
      bg: '#FEE2E2',
      borderColor: '#FECACA',
      icon: '🔴',
      satellites: '0 / 16',
      accuracy: 'Cached',
      hdop: 'N/A',
      signal: 'No Signal',
      desc: 'SmartBand telemetry disconnected. Showing last verified location point.',
    },
  ];

  const currentConfig =
    statusOptions.find((s) => s.id === gpsStatus) || statusOptions[0];

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <View style={styles.iconCircle}>
            <Text style={styles.icon}>📡</Text>
          </View>
          <View>
            <Text style={styles.title}>GPS Telemetry & Diagnostics</Text>
            <Text style={styles.subtitle}>GNSS Transceiver & Satellite Lock</Text>
          </View>
        </View>

        <View
          style={[
            styles.activeBadge,
            { backgroundColor: currentConfig.bg, borderColor: currentConfig.borderColor },
          ]}
        >
          <Text style={[styles.activeBadgeText, { color: currentConfig.color }]}>
            {currentConfig.icon} {currentConfig.label}
          </Text>
        </View>
      </View>

      {/* Main Status Description Banner */}
      <View
        style={[
          styles.descBanner,
          { backgroundColor: currentConfig.bg, borderColor: currentConfig.borderColor },
        ]}
      >
        <Text style={[styles.descTitle, { color: currentConfig.color }]}>
          Signal State: {currentConfig.label.toUpperCase()}
        </Text>
        <Text style={styles.descText}>{currentConfig.desc}</Text>
      </View>

      {/* Telemetry Hardware Grid */}
      <View style={styles.telemetryGrid}>
        <View style={styles.gridCard}>
          <Text style={styles.gridLabel}>SATELLITE FIX</Text>
          <Text style={styles.gridValue}>🛰️ {childLocation?.satellites || 14} locked</Text>
          <Text style={styles.gridSub}>{currentConfig.satellites} visible</Text>
        </View>

        <View style={styles.gridCard}>
          <Text style={styles.gridLabel}>SIGNAL STRENGTH</Text>
          <Text style={styles.gridValue}>📶 {currentConfig.signal}</Text>
          <Text style={styles.gridSub}>4G LTE Cat-M1</Text>
        </View>

        <View style={styles.gridCard}>
          <Text style={styles.gridLabel}>HDOP PRECISION</Text>
          <Text style={styles.gridValue}>🎯 {currentConfig.hdop}</Text>
          <Text style={styles.gridSub}>Variance: ±{childLocation?.accuracy || 3.2}m</Text>
        </View>

        <View style={styles.gridCard}>
          <Text style={styles.gridLabel}>DEVICE BATTERY</Text>
          <Text style={styles.gridValue}>🔋 {childLocation?.battery || 88}%</Text>
          <Text style={styles.gridSub}>~18 hrs remaining</Text>
        </View>
      </View>

      {/* State Switcher (Demo Simulator) */}
      <View style={styles.simulatorSection}>
        <Text style={styles.simulatorTitle}>Test GPS Telemetry States (Demo Switcher):</Text>
        <View style={styles.stateButtonsRow}>
          {statusOptions.map((opt) => {
            const isSelected = gpsStatus === opt.id;
            return (
              <TouchableOpacity
                key={opt.id}
                style={[
                  styles.stateBtn,
                  isSelected && {
                    backgroundColor: opt.bg,
                    borderColor: opt.color,
                    borderWidth: 1.5,
                  },
                ]}
                onPress={() => onSimulateStatus && onSimulateStatus(opt.id)}
                activeOpacity={0.8}
              >
                <Text style={styles.stateBtnIcon}>{opt.icon}</Text>
                <Text
                  style={[
                    styles.stateBtnLabel,
                    isSelected ? { color: opt.color, fontWeight: '800' } : null,
                  ]}
                >
                  {opt.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 22,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.05,
    shadowRadius: 16,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    flexWrap: 'wrap',
    gap: 8,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  icon: {
    fontSize: 20,
  },
  title: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  activeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 999,
    borderWidth: 1,
  },
  activeBadgeText: {
    fontSize: 12,
    fontWeight: '800',
  },
  descBanner: {
    padding: 14,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 16,
  },
  descTitle: {
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.5,
    marginBottom: 3,
  },
  descText: {
    fontSize: 12,
    color: '#334155',
    lineHeight: 18,
    fontWeight: '500',
  },
  telemetryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 18,
  },
  gridCard: {
    flex: 1,
    minWidth: 130,
    backgroundColor: '#F8FAFC',
    borderRadius: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  gridLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  gridValue: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  gridSub: {
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 2,
    fontWeight: '600',
  },
  simulatorSection: {
    borderTopWidth: 1,
    borderTopColor: '#EEF2F6',
    paddingTop: 14,
  },
  simulatorTitle: {
    fontSize: 11,
    fontWeight: '700',
    color: '#64748B',
    marginBottom: 10,
  },
  stateButtonsRow: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  stateBtn: {
    flex: 1,
    minWidth: 80,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F8FAFC',
    paddingVertical: 9,
    paddingHorizontal: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  stateBtnIcon: {
    fontSize: 12,
    marginRight: 6,
  },
  stateBtnLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
  },
});
