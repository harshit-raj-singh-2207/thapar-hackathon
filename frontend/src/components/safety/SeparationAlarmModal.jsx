import React, { useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Animated,
} from 'react-native';

export default function SeparationAlarmModal({
  visible,
  device,
  separationThreshold = 10,
  breachDuration = 0,
  onSilenceAlarm,
  onLocateOnMap,
  onTriggerBuzzer,
}) {
  const flashAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(flashAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: false,
          }),
          Animated.timing(flashAnim, {
            toValue: 0,
            duration: 600,
            useNativeDriver: false,
          }),
        ])
      ).start();
    }
  }, [visible]);

  const flashBg = flashAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['rgba(127, 29, 29, 0.95)', 'rgba(239, 68, 68, 0.95)'],
  });

  if (!visible) return null;

  return (
    <Modal visible={visible} animationType="fade" transparent>
      <View style={styles.backdrop}>
        <Animated.View style={[styles.card, { backgroundColor: flashBg }]}>
          {/* Flashing Siren Icon */}
          <View style={styles.sirenCircle}>
            <Text style={styles.sirenIcon}>🚨</Text>
          </View>

          <Text style={styles.alertTitle}>SEPARATION ALERT</Text>
          <Text style={styles.alertSubtitle}>
            Child SmartBand has breached the {separationThreshold}m safety tether perimeter!
          </Text>

          {/* Metrics Box */}
          <View style={styles.metricsBox}>
            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>CURRENT DISTANCE</Text>
              <Text style={styles.metricVal}>
                {device?.distanceMeters || 16.0} meters
              </Text>
            </View>

            <View style={styles.metricDivider} />

            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>SIGNAL STRENGTH</Text>
              <Text style={styles.metricVal}>
                {device?.rssi || -95} dBm (Weak)
              </Text>
            </View>

            <View style={styles.metricDivider} />

            <View style={styles.metricItem}>
              <Text style={styles.metricLabel}>BREACH DURATION</Text>
              <Text style={styles.metricVal}>
                {Math.round(breachDuration)}s ago
              </Text>
            </View>
          </View>

          <Text style={styles.lastKnownText}>
            Last verified fix: {device?.lastSeenLocation || 'Near backyard patio'}
          </Text>

          {/* Action Buttons */}
          <View style={styles.actionsCol}>
            {onLocateOnMap && (
              <TouchableOpacity
                style={styles.mapBtn}
                onPress={onLocateOnMap}
                activeOpacity={0.85}
              >
                <Text style={styles.mapBtnText}>🗺️ Open Live GPS Map</Text>
              </TouchableOpacity>
            )}

            {onTriggerBuzzer && (
              <TouchableOpacity
                style={styles.buzzerBtn}
                onPress={onTriggerBuzzer}
                activeOpacity={0.85}
              >
                <Text style={styles.buzzerBtnText}>🔊 Sound Wearable Buzzer</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity
              style={styles.silenceBtn}
              onPress={onSilenceAlarm}
              activeOpacity={0.85}
            >
              <Text style={styles.silenceBtnText}>Silence / Acknowledge Alarm</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 18,
  },
  card: {
    width: '100%',
    maxWidth: 500,
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
    shadowColor: '#EF4444',
    shadowOpacity: 0.8,
    shadowRadius: 20,
    elevation: 12,
  },
  sirenCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
  },
  sirenIcon: {
    fontSize: 32,
  },
  alertTitle: {
    fontSize: 22,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: 1.5,
    marginBottom: 6,
  },
  alertSubtitle: {
    fontSize: 14,
    color: '#FEE2E2',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 16,
    fontWeight: '600',
  },
  metricsBox: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    borderRadius: 14,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    marginBottom: 14,
    width: '100%',
  },
  metricItem: {
    flex: 1,
    alignItems: 'center',
  },
  metricDivider: {
    width: 1,
    height: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  metricLabel: {
    fontSize: 8,
    fontWeight: '800',
    color: '#FCA5A5',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  metricVal: {
    fontSize: 13,
    fontWeight: '900',
    color: '#FFFFFF',
  },
  lastKnownText: {
    fontSize: 12,
    color: '#FEE2E2',
    marginBottom: 18,
    fontWeight: '600',
  },
  actionsCol: {
    width: '100%',
    gap: 10,
  },
  mapBtn: {
    backgroundColor: '#2563EB',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  mapBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '800',
  },
  buzzerBtn: {
    backgroundColor: '#0F172A',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  buzzerBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
  },
  silenceBtn: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  silenceBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
  },
});
