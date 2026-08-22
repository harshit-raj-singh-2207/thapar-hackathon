import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Switch,
  ActivityIndicator,
} from 'react-native';

export default function BLEConnectionCard({
  status = 'CONNECTED',
  device,
  tetherAlarmEnabled = true,
  separationThreshold = 10,
  autoReconnect = true,
  alertSoundEnabled = true,
  onToggleTether,
  onChangeThreshold,
  onToggleSound,
  onToggleAutoReconnect,
  onScanAndConnect,
  onDisconnect,
}) {
  const [connecting, setConnecting] = useState(false);

  const handleConnect = async () => {
    setConnecting(true);
    try {
      if (onScanAndConnect) await onScanAndConnect();
    } finally {
      setConnecting(false);
    }
  };

  const isConnected = status === 'CONNECTED';

  return (
    <View style={styles.card}>
      {/* Device Info & Status Header */}
      <View style={styles.header}>
        <View style={styles.deviceRow}>
          <View style={styles.bandIconBox}>
            <Text style={styles.bandIcon}>⌚</Text>
          </View>
          <View style={styles.deviceTextCol}>
            <Text style={styles.deviceName}>{device?.name || 'NIVARA SmartBand'}</Text>
            <Text style={styles.deviceModel}>
              Model: {device?.model || 'NV-CoreBand v2.4'} • MAC: {device?.mac || 'E4:95:6E:41:88:21'}
            </Text>
          </View>
        </View>

        <View
          style={[
            styles.statusPill,
            isConnected ? styles.statusConnected : styles.statusDisconnected,
          ]}
        >
          <View
            style={[
              styles.statusDot,
              { backgroundColor: isConnected ? '#10B981' : '#EF4444' },
            ]}
          />
          <Text
            style={[
              styles.statusText,
              { color: isConnected ? '#059669' : '#DC2626' },
            ]}
          >
            {isConnected ? 'BLE Connected' : 'Disconnected'}
          </Text>
        </View>
      </View>

      {/* Hardware Specs Row */}
      <View style={styles.specsRow}>
        <View style={styles.specItem}>
          <Text style={styles.specLabel}>BATTERY</Text>
          <Text style={styles.specVal}>🔋 {device?.battery || 88}%</Text>
        </View>

        <View style={styles.specDivider} />

        <View style={styles.specItem}>
          <Text style={styles.specLabel}>FIRMWARE</Text>
          <Text style={styles.specVal}>{device?.firmware || 'v2.4.12'}</Text>
        </View>

        <View style={styles.specDivider} />

        <View style={styles.specItem}>
          <Text style={styles.specLabel}>TX POWER</Text>
          <Text style={styles.specVal}>{device?.txPower || -59} dBm</Text>
        </View>

        <View style={styles.specDivider} />

        <View style={styles.specItem}>
          <Text style={styles.specLabel}>PROTOCOL</Text>
          <Text style={styles.specVal}>BLE 5.2</Text>
        </View>
      </View>

      {/* Anti-Loss Tether Alarm Setting */}
      <View style={styles.settingCard}>
        <View style={styles.settingHeader}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>🚨 Anti-Separation Tether Alarm</Text>
            <Text style={styles.settingDesc}>
              Sound alarm immediately if child moves beyond the proximity safety perimeter.
            </Text>
          </View>
          <Switch
            value={tetherAlarmEnabled}
            onValueChange={onToggleTether}
            trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
            thumbColor={tetherAlarmEnabled ? '#2563EB' : '#94A3B8'}
          />
        </View>

        {/* Threshold Distance Selector */}
        {tetherAlarmEnabled && (
          <View style={styles.thresholdSection}>
            <Text style={styles.thresholdLabel}>
              Separation Trigger Distance: <Text style={styles.boldThresh}>{separationThreshold} meters</Text>
            </Text>
            <View style={styles.thresholdPills}>
              {[5, 10, 15, 20].map((t) => {
                const isSelected = separationThreshold === t;
                return (
                  <TouchableOpacity
                    key={t}
                    style={[styles.threshPill, isSelected && styles.threshPillActive]}
                    onPress={() => onChangeThreshold && onChangeThreshold(t)}
                  >
                    <Text style={[styles.threshText, isSelected && styles.threshTextActive]}>
                      {t}m {t === 5 ? '(Tight)' : t === 10 ? '(Standard)' : t === 15 ? '(Open)' : '(Max)'}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>
        )}
      </View>

      {/* Auxiliary Toggles */}
      <View style={styles.auxRow}>
        <View style={styles.auxItem}>
          <Text style={styles.auxText}>🔊 Alarm Audio Siren</Text>
          <Switch
            value={alertSoundEnabled}
            onValueChange={onToggleSound}
            trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
            thumbColor={alertSoundEnabled ? '#2563EB' : '#94A3B8'}
          />
        </View>

        <View style={styles.auxItem}>
          <Text style={styles.auxText}>🔄 Auto-Reconnect</Text>
          <Switch
            value={autoReconnect}
            onValueChange={onToggleAutoReconnect}
            trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
            thumbColor={autoReconnect ? '#2563EB' : '#94A3B8'}
          />
        </View>
      </View>

      {/* Connect / Disconnect Button */}
      <View style={styles.btnRow}>
        {isConnected ? (
          <TouchableOpacity
            style={styles.disconnectBtn}
            onPress={onDisconnect}
            activeOpacity={0.85}
          >
            <Text style={styles.disconnectText}>Disconnect SmartBand</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={styles.connectBtn}
            onPress={handleConnect}
            disabled={connecting}
            activeOpacity={0.85}
          >
            {connecting ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.connectText}>🔍 Scan & Connect SmartBand</Text>
            )}
          </TouchableOpacity>
        )}
      </View>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    flexWrap: 'wrap',
    gap: 8,
  },
  deviceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  bandIconBox: {
    width: 44,
    height: 44,
    borderRadius: 14,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  bandIcon: {
    fontSize: 22,
  },
  deviceTextCol: {
    flex: 1,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  deviceModel: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 999,
    borderWidth: 1,
  },
  statusConnected: {
    backgroundColor: '#ECFDF5',
    borderColor: '#A7F3D0',
  },
  statusDisconnected: {
    backgroundColor: '#FEE2E2',
    borderColor: '#FECACA',
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 3.5,
    marginRight: 6,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '800',
  },
  specsRow: {
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
    borderRadius: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    marginBottom: 16,
    alignItems: 'center',
  },
  specItem: {
    flex: 1,
    alignItems: 'center',
  },
  specDivider: {
    width: 1,
    height: 24,
    backgroundColor: '#E2E8F0',
  },
  specLabel: {
    fontSize: 8,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  specVal: {
    fontSize: 12,
    fontWeight: '800',
    color: '#0F172A',
  },
  settingCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    marginBottom: 14,
  },
  settingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flex: 1,
    marginRight: 10,
  },
  settingTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 3,
  },
  settingDesc: {
    fontSize: 11,
    color: '#64748B',
    lineHeight: 16,
    fontWeight: '500',
  },
  thresholdSection: {
    marginTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#EEF2F6',
    paddingTop: 10,
  },
  thresholdLabel: {
    fontSize: 12,
    color: '#334155',
    marginBottom: 8,
    fontWeight: '600',
  },
  boldThresh: {
    color: '#2563EB',
    fontWeight: '800',
  },
  thresholdPills: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  threshPill: {
    flex: 1,
    minWidth: 65,
    backgroundColor: '#FFFFFF',
    paddingVertical: 9,
    paddingHorizontal: 8,
    borderRadius: 999,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  threshPillActive: {
    backgroundColor: '#2563EB',
    borderColor: '#1D4ED8',
  },
  threshText: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '700',
  },
  threshTextActive: {
    color: '#FFFFFF',
  },
  auxRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  auxItem: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  auxText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#0F172A',
  },
  btnRow: {},
  connectBtn: {
    backgroundColor: '#2563EB',
    paddingVertical: 14,
    borderRadius: 999,
    alignItems: 'center',
    shadowColor: '#2563EB',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  connectText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '800',
  },
  disconnectBtn: {
    backgroundColor: '#FEE2E2',
    paddingVertical: 14,
    borderRadius: 999,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  disconnectText: {
    color: '#DC2626',
    fontSize: 13,
    fontWeight: '800',
  },
});
