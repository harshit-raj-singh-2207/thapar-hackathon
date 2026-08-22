import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useBluetooth } from '../../hooks/useBluetooth';
import { useSafety } from '../../hooks/useSafety';
import AppHeader from '../../components/common/AppHeader';
import AppButton from '../../components/common/AppButton';
import StatusIndicator from '../../components/common/StatusIndicator';

export default function DeviceStatusScreen({ navigation }) {
  const {
    status: bleStatus,
    device,
    isScanning,
    isBuzzerActive,
    scanAndConnect,
    disconnectDevice,
    triggerBuzzer,
    setSeparationThreshold,
    separationThreshold,
  } = useBluetooth();

  const { gpsStatus, batteryLevel } = useSafety();

  const [tetherEnabled, setTetherEnabled] = useState(true);

  const isConnected = bleStatus === 'CONNECTED';

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title="Device Diagnostics & Status"
        subtitle="Hardware telemetry, BLE signal calibration & health"
        onBack={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('CaregiverDashboard'))}
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Device Overview Card */}
        <View style={styles.card}>
          <View style={styles.deviceHeader}>
            <View style={styles.deviceIconCircle}>
              <Text style={styles.deviceIcon}>⌚</Text>
            </View>
            <View style={styles.deviceTitleCol}>
              <Text style={styles.deviceName}>{device?.name || 'Nivara GPS SmartBand v2'}</Text>
              <Text style={styles.deviceModel}>{device?.model || 'CoreBand Pro v2.4'}</Text>
            </View>
            <StatusIndicator
              status={isConnected ? 'connected' : 'offline'}
              label={isConnected ? 'Connected' : 'Disconnected'}
            />
          </View>

          <View style={styles.gridRow}>
            <View style={styles.gridTile}>
              <Text style={styles.tileLabel}>MAC ADDRESS</Text>
              <Text style={styles.tileVal}>{device?.mac || 'E4:95:6E:41:88:21'}</Text>
            </View>
            <View style={styles.gridTile}>
              <Text style={styles.tileLabel}>FIRMWARE</Text>
              <Text style={styles.tileVal}>{device?.firmware || 'v2.4.12-secure'}</Text>
            </View>
          </View>

          <View style={styles.gridRow}>
            <View style={styles.gridTile}>
              <Text style={styles.tileLabel}>BATTERY</Text>
              <Text style={styles.tileVal}>🔋 {batteryLevel || 84}%</Text>
            </View>
            <View style={styles.gridTile}>
              <Text style={styles.tileLabel}>BLE RSSI SIGNAL</Text>
              <Text style={[styles.tileVal, { color: '#059669' }]}>
                {device?.rssi || -58} dBm (Strong)
              </Text>
            </View>
          </View>
        </View>

        {/* GPS Sensor Telemetry */}
        <View style={styles.card}>
          <Text style={styles.cardSectionTitle}>SATELLITE GPS BEACON</Text>
          <View style={styles.gpsRow}>
            <View style={styles.gpsIndicator}>
              <Text style={styles.gpsSymbol}>🛰️</Text>
              <View>
                <Text style={styles.gpsTitle}>GNSS Multi-Constellation Fix</Text>
                <Text style={styles.gpsSub}>GPS + GLONASS + Galileo active</Text>
              </View>
            </View>
            <View style={styles.precisionBadge}>
              <Text style={styles.precisionText}>±3.8m Precision</Text>
            </View>
          </View>

          <View style={styles.gpsDetailsRow}>
            <Text style={styles.gpsDetailText}>Status: <Text style={styles.boldText}>{gpsStatus}</Text></Text>
            <Text style={styles.gpsDetailText}>Lock: <Text style={styles.boldText}>3D Fix (9 Sats)</Text></Text>
          </View>
        </View>

        {/* Proximity Tether Calibration */}
        <View style={styles.card}>
          <Text style={styles.cardSectionTitle}>SEPARATION RADAR CALIBRATION</Text>
          <Text style={styles.radarDesc}>
            Current measured distance: <Text style={styles.boldText}>{device?.distanceMeters || 3.8} meters</Text>
          </Text>

          <Text style={styles.sliderLabel}>Alert Boundary Threshold: {separationThreshold || 12}m</Text>
          <View style={styles.thresholdButtonsRow}>
            {[5, 10, 12, 15, 20].map((val) => (
              <TouchableOpacity
                key={val}
                style={[
                  styles.threshBtn,
                  (separationThreshold || 12) === val && styles.threshBtnActive,
                ]}
                onPress={() => setSeparationThreshold(val)}
              >
                <Text
                  style={[
                    styles.threshBtnText,
                    (separationThreshold || 12) === val && styles.threshBtnTextActive,
                  ]}
                >
                  {val}m
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity
            style={styles.tetherToggle}
            onPress={() => setTetherEnabled(!tetherEnabled)}
            activeOpacity={0.8}
          >
            <View style={[styles.switchBox, tetherEnabled && styles.switchBoxActive]}>
              {tetherEnabled && <Text style={styles.checkmark}>✓</Text>}
            </View>
            <View style={styles.tetherTextCol}>
              <Text style={styles.tetherTitle}>Proximity Separation Alarm</Text>
              <Text style={styles.tetherSub}>
                Emit audible alert if phone and band move beyond threshold.
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Hardware Action Buttons */}
        <View style={styles.actionButtons}>
          <AppButton
            title={isBuzzerActive ? '🔊 Sounding Alarm...' : '🔊 Test Band Buzzer'}
            onPress={triggerBuzzer}
            variant="outline"
            size="md"
            loading={isBuzzerActive}
            style={styles.actionBtn}
          />

          <AppButton
            title={isConnected ? 'Disconnect Band' : 'Connect SmartBand'}
            onPress={isConnected ? disconnectDevice : scanAndConnect}
            variant={isConnected ? 'secondary' : 'primary'}
            size="md"
            loading={isScanning}
            style={styles.actionBtn}
          />
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
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
    paddingBottom: 40,
    maxWidth: 600,
    alignSelf: 'center',
    width: '100%',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 16,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
  },
  deviceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  deviceIconCircle: {
    width: 48,
    height: 48,
    borderRadius: 16,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  deviceIcon: {
    fontSize: 24,
  },
  deviceTitleCol: {
    flex: 1,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  deviceModel: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  gridRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 10,
  },
  gridTile: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  tileLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
    marginBottom: 4,
  },
  tileVal: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  cardSectionTitle: {
    fontSize: 11,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 12,
  },
  gpsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  gpsIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  gpsSymbol: {
    fontSize: 24,
    marginRight: 12,
  },
  gpsTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  gpsSub: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  precisionBadge: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  precisionText: {
    color: '#059669',
    fontSize: 11,
    fontWeight: '800',
  },
  gpsDetailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  gpsDetailText: {
    fontSize: 12,
    color: '#64748B',
  },
  boldText: {
    color: '#0F172A',
    fontWeight: '700',
  },
  radarDesc: {
    fontSize: 13,
    color: '#475569',
    marginBottom: 12,
  },
  sliderLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 8,
  },
  thresholdButtonsRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 14,
  },
  threshBtn: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    paddingVertical: 8,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  threshBtnActive: {
    backgroundColor: '#2563EB',
    borderColor: '#2563EB',
  },
  threshBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
  threshBtnTextActive: {
    color: '#FFFFFF',
    fontWeight: '800',
  },
  tetherToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  switchBox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    backgroundColor: '#FFFFFF',
  },
  switchBoxActive: {
    backgroundColor: '#059669',
    borderColor: '#059669',
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '900',
  },
  tetherTextCol: {
    flex: 1,
  },
  tetherTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  tetherSub: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  actionBtn: {
    flex: 1,
  },
});
