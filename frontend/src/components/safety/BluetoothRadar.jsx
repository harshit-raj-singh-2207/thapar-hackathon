import React, { useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
} from 'react-native';

export default function BluetoothRadar({
  device,
  status = 'CONNECTED',
  separationThreshold = 10,
  isBuzzerActive = false,
  onFindMyBand,
  onSimulateDistance,
}) {
  const spinAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.timing(spinAnim, {
        toValue: 1,
        duration: 3000,
        useNativeDriver: true,
      })
    ).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.3,
          duration: 900,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1.0,
          duration: 900,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const spin = spinAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const dist = device?.distanceMeters || 1.4;
  const rssi = device?.rssi || -58;
  const zone = device?.proximityZone || 'IMMEDIATE';

  const getZoneConfig = () => {
    switch (zone) {
      case 'IMMEDIATE':
        return {
          label: 'Immediate (< 2m)',
          color: '#059669',
          bg: '#ECFDF5',
          borderColor: '#A7F3D0',
          dot: '#10B981',
          icon: '🟢',
          desc: 'Child is directly beside caregiver',
        };
      case 'NEAR':
        return {
          label: 'Near (2m - 5m)',
          color: '#2563EB',
          bg: '#EFF6FF',
          borderColor: '#BFDBFE',
          dot: '#3B82F6',
          icon: '🔵',
          desc: 'Safe room / line-of-sight proximity',
        };
      case 'FAR':
        return {
          label: 'Far (5m - 12m)',
          color: '#D97706',
          bg: '#FEF3C7',
          borderColor: '#FDE68A',
          dot: '#F59E0B',
          icon: '🟠',
          desc: 'Approaching separation boundary',
        };
      case 'OUT_OF_RANGE':
      default:
        return {
          label: 'Out of Range (> 12m)',
          color: '#DC2626',
          bg: '#FEE2E2',
          borderColor: '#FECACA',
          dot: '#EF4444',
          icon: '🔴',
          desc: '🚨 SEPARATION THRESHOLD BREACHED',
        };
    }
  };

  const zoneCfg = getZoneConfig();

  const maxRadius = 110;
  const blipDistance = Math.min(maxRadius, (dist / 20) * maxRadius);
  const blipAngle = 45;
  const blipX = Math.cos((blipAngle * Math.PI) / 180) * blipDistance;
  const blipY = Math.sin((blipAngle * Math.PI) / 180) * blipDistance;

  const getSignalBars = () => {
    if (rssi > -60) return 5;
    if (rssi > -70) return 4;
    if (rssi > -80) return 3;
    if (rssi > -90) return 2;
    return 1;
  };
  const bars = getSignalBars();

  return (
    <View style={styles.card}>
      {/* Header */}
      <View style={styles.headerRow}>
        <View style={styles.titleRow}>
          <View style={styles.iconCircle}>
            <Text style={styles.icon}>🔵</Text>
          </View>
          <View>
            <Text style={styles.title}>Bluetooth Proximity Radar</Text>
            <Text style={styles.subtitle}>Phone ↔ SmartBand BLE Tether</Text>
          </View>
        </View>

        <View style={[styles.zoneBadge, { backgroundColor: zoneCfg.bg, borderColor: zoneCfg.borderColor }]}>
          <Text style={[styles.zoneBadgeText, { color: zoneCfg.color }]}>
            {zoneCfg.icon} {zoneCfg.label}
          </Text>
        </View>
      </View>

      {/* Main Visual Radar Frame */}
      <View style={styles.radarFrame}>
        {/* Concentric Proximity Rings */}
        <View style={[styles.ring, styles.ringOuter]}>
          <Text style={styles.ringLabel}>15m (Alert)</Text>
        </View>
        <View style={[styles.ring, styles.ringMid]}>
          <Text style={styles.ringLabel}>10m (Far)</Text>
        </View>
        <View style={[styles.ring, styles.ringInner]}>
          <Text style={styles.ringLabel}>5m (Near)</Text>
        </View>
        <View style={[styles.ring, styles.ringCenter]}>
          <Text style={styles.ringCenterLabel}>2m</Text>
        </View>

        {/* Crosshair Axes */}
        <View style={styles.axisH} />
        <View style={styles.axisV} />

        {/* Rotating Radar Sweep Line */}
        <Animated.View style={[styles.radarSweep, { transform: [{ rotate: spin }] }]} />

        {/* Center Marker (Caregiver Phone) */}
        <View style={styles.centerMarker}>
          <Text style={styles.centerIcon}>📱</Text>
          <Text style={styles.centerLabel}>Phone</Text>
        </View>

        {/* Child SmartBand Blip */}
        {status === 'CONNECTED' && (
          <View
            style={[
              styles.blipContainer,
              {
                transform: [{ translateX: blipX }, { translateY: blipY }],
              },
            ]}
          >
            <Animated.View
              style={[
                styles.blipPulse,
                {
                  transform: [{ scale: pulseAnim }],
                  borderColor: zoneCfg.dot,
                },
              ]}
            />
            <View style={[styles.blipBody, { backgroundColor: zoneCfg.dot }]}>
              <Text style={styles.blipIcon}>⌚</Text>
            </View>
            <View style={styles.blipTag}>
              <Text style={styles.blipTagText}>Leo ({dist}m)</Text>
            </View>
          </View>
        )}
      </View>

      {/* Telemetry Bar: Distance, RSSI & Signal Quality */}
      <View style={styles.telemetryRow}>
        <View style={styles.telemetryItem}>
          <Text style={styles.telemetryLabel}>ESTIMATED DISTANCE</Text>
          <Text style={[styles.telemetryVal, { color: zoneCfg.color }]}>{dist} meters</Text>
          <Text style={styles.telemetrySub}>Threshold: {separationThreshold}m</Text>
        </View>

        <View style={styles.telemetryDivider} />

        <View style={styles.telemetryItem}>
          <Text style={styles.telemetryLabel}>BLE RSSI SIGNAL</Text>
          <Text style={styles.telemetryVal}>{rssi} dBm</Text>
          <View style={styles.barsRow}>
            {[1, 2, 3, 4, 5].map((b) => (
              <View
                key={b}
                style={[
                  styles.bar,
                  { height: 4 + b * 2 },
                  b <= bars ? { backgroundColor: zoneCfg.dot } : styles.barInactive,
                ]}
              />
            ))}
          </View>
        </View>

        <View style={styles.telemetryDivider} />

        <View style={styles.telemetryItem}>
          <Text style={styles.telemetryLabel}>TETHER STATUS</Text>
          <Text
            style={[
              styles.telemetryVal,
              { color: dist > separationThreshold ? '#DC2626' : '#059669' },
            ]}
          >
            {dist > separationThreshold ? '🚨 BREACHED' : '🛡️ SECURE'}
          </Text>
          <Text style={styles.telemetrySub}>{device?.model || 'CoreBand'}</Text>
        </View>
      </View>

      {/* Action Button: Find My Band Buzzer */}
      <View style={styles.actionsRow}>
        <TouchableOpacity
          style={[styles.buzzerBtn, isBuzzerActive && styles.buzzerBtnActive]}
          onPress={onFindMyBand}
          activeOpacity={0.85}
        >
          <Text style={styles.buzzerIcon}>🔊</Text>
          <Text style={styles.buzzerText}>
            {isBuzzerActive ? 'Buzzer Sounding on Band...' : 'Find My Band (Sound Acoustic Buzzer)'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Proximity Simulation Buttons */}
      {onSimulateDistance && (
        <View style={styles.simRow}>
          <Text style={styles.simLabel}>Demo Proximity Step Test:</Text>
          <View style={styles.simButtons}>
            {[
              { label: 'Beside (1.2m)', val: 1.2 },
              { label: 'Room (3.5m)', val: 3.5 },
              { label: 'Warning (8.5m)', val: 8.5 },
              { label: '🚨 Breach (16m)', val: 16.0 },
            ].map((p) => (
              <TouchableOpacity
                key={p.val}
                style={[styles.simBtn, dist === p.val && styles.simBtnActive]}
                onPress={() => onSimulateDistance(p.val)}
                activeOpacity={0.8}
              >
                <Text style={[styles.simBtnText, dist === p.val && styles.simBtnTextActive]}>
                  {p.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
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
  headerRow: {
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
  zoneBadge: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 999,
    borderWidth: 1,
  },
  zoneBadgeText: {
    fontSize: 11,
    fontWeight: '800',
  },
  radarFrame: {
    height: 280,
    backgroundColor: '#F8FAFC',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    overflow: 'hidden',
    marginBottom: 16,
  },
  ring: {
    position: 'absolute',
    borderRadius: 999,
    borderWidth: 1,
    borderColor: 'rgba(37, 99, 235, 0.25)',
    borderStyle: 'dashed',
    justifyContent: 'flex-start',
    alignItems: 'center',
  },
  ringOuter: {
    width: 240,
    height: 240,
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  ringMid: {
    width: 170,
    height: 170,
    borderColor: 'rgba(245, 158, 11, 0.3)',
  },
  ringInner: {
    width: 100,
    height: 100,
    borderColor: 'rgba(37, 99, 235, 0.35)',
  },
  ringCenter: {
    width: 44,
    height: 44,
    borderColor: 'rgba(16, 185, 129, 0.5)',
  },
  ringLabel: {
    fontSize: 8,
    color: '#94A3B8',
    fontWeight: '800',
    marginTop: 2,
  },
  ringCenterLabel: {
    fontSize: 7,
    color: '#059669',
    fontWeight: '800',
    marginTop: 1,
  },
  axisH: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: 'rgba(226, 232, 240, 0.8)',
  },
  axisV: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    width: 1,
    backgroundColor: 'rgba(226, 232, 240, 0.8)',
  },
  radarSweep: {
    position: 'absolute',
    width: 260,
    height: 260,
    borderRadius: 130,
    borderTopWidth: 2,
    borderTopColor: '#2563EB',
    opacity: 0.6,
  },
  centerMarker: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
    shadowColor: '#0F172A',
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  centerIcon: {
    fontSize: 14,
  },
  centerLabel: {
    fontSize: 7,
    color: '#2563EB',
    fontWeight: '800',
  },
  blipContainer: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 15,
  },
  blipPulse: {
    position: 'absolute',
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2,
  },
  blipBody: {
    width: 26,
    height: 26,
    borderRadius: 13,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  blipIcon: {
    fontSize: 12,
  },
  blipTag: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 999,
    marginTop: 2,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
  blipTagText: {
    fontSize: 9,
    fontWeight: '800',
    color: '#0F172A',
  },
  telemetryRow: {
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
    borderRadius: 18,
    padding: 14,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    marginBottom: 16,
    alignItems: 'center',
  },
  telemetryItem: {
    flex: 1,
    alignItems: 'center',
  },
  telemetryDivider: {
    width: 1,
    height: 32,
    backgroundColor: '#E2E8F0',
  },
  telemetryLabel: {
    fontSize: 8,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  telemetryVal: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  telemetrySub: {
    fontSize: 9,
    color: '#94A3B8',
    marginTop: 2,
    fontWeight: '600',
  },
  barsRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 3,
    marginTop: 3,
  },
  bar: {
    width: 4,
    borderRadius: 1,
  },
  barInactive: {
    backgroundColor: '#E2E8F0',
  },
  actionsRow: {
    marginBottom: 14,
  },
  buzzerBtn: {
    backgroundColor: '#2563EB',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 14,
    borderRadius: 999,
    shadowColor: '#2563EB',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  buzzerBtnActive: {
    backgroundColor: '#059669',
  },
  buzzerIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  buzzerText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
  },
  simRow: {
    borderTopWidth: 1,
    borderTopColor: '#EEF2F6',
    paddingTop: 14,
  },
  simLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#64748B',
    marginBottom: 8,
  },
  simButtons: {
    flexDirection: 'row',
    gap: 6,
    flexWrap: 'wrap',
  },
  simBtn: {
    flex: 1,
    minWidth: 80,
    backgroundColor: '#F8FAFC',
    paddingVertical: 8,
    paddingHorizontal: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
  },
  simBtnActive: {
    backgroundColor: '#EFF6FF',
    borderColor: '#3B82F6',
  },
  simBtnText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
  },
  simBtnTextActive: {
    color: '#2563EB',
    fontWeight: '800',
  },
});
