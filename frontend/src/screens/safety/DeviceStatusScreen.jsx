import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Dimensions,
  Platform,
} from 'react-native';

import { bluetoothService } from '../../services/bluetooth/bluetoothService';
import BluetoothRadar from '../../components/safety/BluetoothRadar';
import BLEConnectionCard from '../../components/safety/BLEConnectionCard';
import SeparationAlarmModal from '../../components/safety/SeparationAlarmModal';
import BandStatus from '../../components/safety/BandStatus';

const { width } = Dimensions.get('window');
const isDesktop = Platform.OS === 'web' ? width >= 1024 : width >= 768;

export default function DeviceStatusScreen({ navigation }) {
  const [bleState, setBleState] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  useEffect(() => {
    const unsub = bluetoothService.subscribe((state) => {
      setBleState(state);
    });
    return () => unsub();
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleToggleTether = async (val) => {
    await bluetoothService.setTetherAlarm(val);
    showToast(val ? '🚨 Anti-loss tether activated' : '⏸️ Tether alarm paused');
  };

  const handleChangeThreshold = async (meters) => {
    await bluetoothService.setSeparationThreshold(meters);
    showToast(`Separation distance threshold set to ${meters}m`);
  };

  const handleFindMyBand = async () => {
    await bluetoothService.triggerFindMyBand();
    showToast('🔊 Acoustic buzzer sounding on child SmartBand...');
  };

  const handleSilenceAlarm = () => {
    bluetoothService.clearSeparationBreach();
    showToast('Separation alarm silenced');
  };

  const handleScanConnect = async () => {
    const success = await bluetoothService.scanAndConnectRealBLE();
    showToast(success ? '✅ SmartBand connected via BLE 5.2' : 'Connected to SmartBand simulator');
  };

  const handleDisconnect = () => {
    bluetoothService.disconnectBand();
    showToast('SmartBand disconnected');
  };

  const handleSimulateDistance = (meters) => {
    bluetoothService.setSimulatedDistance(meters);
    showToast(`Simulated distance: ${meters}m`);
  };

  const {
    status,
    device,
    tetherAlarmEnabled,
    separationThreshold,
    autoReconnect,
    alertSoundEnabled,
    isBuzzerActive,
    separationBreachActive,
    breachDuration,
  } = bleState || {};

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Top Header */}
      <View style={styles.topBar}>
        <View style={styles.titleRow}>
          <TouchableOpacity
            style={styles.backBtn}
            onPress={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('LiveLocation'))}
          >
            <Text style={styles.backBtnText}>←</Text>
          </TouchableOpacity>
          <View>
            <Text style={styles.title}>Bluetooth Proximity & Tether</Text>
            <Text style={styles.subtitle}>Phone ↔ SmartBand BLE 5.2 Link</Text>
          </View>
        </View>

        <TouchableOpacity
          style={styles.mapSwitchBtn}
          onPress={() => navigation.navigate('LiveLocation')}
          activeOpacity={0.85}
        >
          <Text style={styles.mapSwitchText}>🗺️ Live Map</Text>
        </TouchableOpacity>
      </View>

      {/* Toast Notification */}
      {toastMessage && (
        <View style={styles.toastBanner}>
          <Text style={styles.toastText}>{toastMessage}</Text>
        </View>
      )}

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={isDesktop ? styles.desktopGrid : styles.mobileLayout}>
          {/* Left Column: Interactive Radar */}
          <View style={isDesktop ? styles.desktopLeftCol : styles.fullCol}>
            <BluetoothRadar
              device={device}
              status={status}
              separationThreshold={separationThreshold}
              isBuzzerActive={isBuzzerActive}
              onFindMyBand={handleFindMyBand}
              onSimulateDistance={handleSimulateDistance}
            />

            {/* Wearable Sensors Health Card */}
            <BandStatus
              device={device?.name}
              battery={device?.battery}
            />
          </View>

          {/* Right Column: Connection & Tether Settings Card */}
          <View style={isDesktop ? styles.desktopRightCol : styles.fullCol}>
            <BLEConnectionCard
              status={status}
              device={device}
              tetherAlarmEnabled={tetherAlarmEnabled}
              separationThreshold={separationThreshold}
              autoReconnect={autoReconnect}
              alertSoundEnabled={alertSoundEnabled}
              onToggleTether={handleToggleTether}
              onChangeThreshold={handleChangeThreshold}
              onToggleSound={(v) => bluetoothService.setAlertSound(v)}
              onToggleAutoReconnect={(v) => bluetoothService.setAutoReconnect(v)}
              onScanAndConnect={handleScanConnect}
              onDisconnect={handleDisconnect}
            />
          </View>
        </View>
      </ScrollView>

      {/* Separation Alarm Modal */}
      <SeparationAlarmModal
        visible={separationBreachActive}
        device={device}
        separationThreshold={separationThreshold}
        breachDuration={breachDuration}
        onSilenceAlarm={handleSilenceAlarm}
        onLocateOnMap={() => {
          handleSilenceAlarm();
          navigation.navigate('LiveLocation');
        }}
        onTriggerBuzzer={handleFindMyBand}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 6,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  backBtnText: {
    fontSize: 18,
    color: '#0F172A',
    fontWeight: '800',
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  mapSwitchBtn: {
    backgroundColor: '#2563EB',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 999,
  },
  mapSwitchText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  toastBanner: {
    backgroundColor: '#2563EB',
    paddingVertical: 10,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  toastText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  desktopGrid: {
    flexDirection: 'row',
    gap: 24,
    alignItems: 'flex-start',
  },
  desktopLeftCol: {
    flex: 6,
  },
  desktopRightCol: {
    flex: 4,
  },
  mobileLayout: {
    flexDirection: 'column',
  },
  fullCol: {
    width: '100%',
  },
});
