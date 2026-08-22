import React from 'react';
import { View, Text, StyleSheet, Switch, TouchableOpacity } from 'react-native';

export default function PreferenceCard({
  sensoryAlerts = true,
  geofenceAlerts = true,
  quietHours = false,
  onToggleSensoryAlerts,
  onToggleGeofenceAlerts,
  onToggleQuietHours,
  onOpenSettings,
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>Caregiver Alert Preferences</Text>
        {onOpenSettings && (
          <TouchableOpacity onPress={onOpenSettings}>
            <Text style={styles.settingsBtn}>⚙️ Settings</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.optionRow}>
        <View style={styles.optionTextCol}>
          <Text style={styles.optionTitle}>Sensory Stress Alerts</Text>
          <Text style={styles.optionDesc}>Notify on high heart rate or sensory overload</Text>
        </View>
        <Switch
          value={sensoryAlerts}
          onValueChange={onToggleSensoryAlerts}
          trackColor={{ false: '#334155', true: '#4F46E5' }}
          thumbColor={sensoryAlerts ? '#818CF8' : '#94A3B8'}
        />
      </View>

      <View style={styles.divider} />

      <View style={styles.optionRow}>
        <View style={styles.optionTextCol}>
          <Text style={styles.optionTitle}>Geofence Exit Warnings</Text>
          <Text style={styles.optionDesc}>Alert when leaving home or school zone</Text>
        </View>
        <Switch
          value={geofenceAlerts}
          onValueChange={onToggleGeofenceAlerts}
          trackColor={{ false: '#334155', true: '#4F46E5' }}
          thumbColor={geofenceAlerts ? '#818CF8' : '#94A3B8'}
        />
      </View>

      <View style={styles.divider} />

      <View style={styles.optionRow}>
        <View style={styles.optionTextCol}>
          <Text style={styles.optionTitle}>Quiet Hours Mode</Text>
          <Text style={styles.optionDesc}>Mute non-urgent notifications (10 PM - 7 AM)</Text>
        </View>
        <Switch
          value={quietHours}
          onValueChange={onToggleQuietHours}
          trackColor={{ false: '#334155', true: '#4F46E5' }}
          thumbColor={quietHours ? '#818CF8' : '#94A3B8'}
        />
      </View>
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
    marginBottom: 14,
  },
  title: {
    fontSize: 14,
    fontWeight: '700',
    color: '#94A3B8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  settingsBtn: {
    color: '#818CF8',
    fontSize: 12,
    fontWeight: '600',
  },
  optionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
  },
  optionTextCol: {
    flex: 1,
    marginRight: 12,
  },
  optionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#F8FAFC',
  },
  optionDesc: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: '#334155',
    marginVertical: 10,
  },
});
