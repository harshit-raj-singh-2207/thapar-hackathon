import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';

export default function EmergencyStatus({
  isEmergency = false,
  activeAlertTitle = 'All Systems Normal',
  lastAlertTime = 'No recent alerts',
  onTriggerSOS,
  onResolveEmergency,
}) {
  const handleSOSPress = () => {
    if (onTriggerSOS) return onTriggerSOS();
    Alert.alert(
      '🚨 Trigger SOS Emergency Alert?',
      'This will immediately notify emergency contacts, therapists, and broadcast location.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'SEND SOS', style: 'destructive', onPress: () => console.log('SOS Triggered') },
      ]
    );
  };

  return (
    <View style={[styles.card, isEmergency ? styles.emergencyBorder : styles.normalBorder]}>
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.titleIcon}>{isEmergency ? '🚨' : '🛡️'}</Text>
          <Text style={styles.titleText}>Emergency & Safety Status</Text>
        </View>
        <View style={[styles.statusTag, isEmergency ? styles.alertTag : styles.normalTag]}>
          <Text style={[styles.statusTagText, isEmergency ? styles.alertTagTxt : styles.normalTagTxt]}>
            {isEmergency ? 'ALERT ACTIVE' : 'NORMAL'}
          </Text>
        </View>
      </View>

      <Text style={styles.alertTitle}>{activeAlertTitle}</Text>
      <Text style={styles.lastAlert}>{lastAlertTime}</Text>

      <View style={styles.actionRow}>
        {isEmergency && onResolveEmergency ? (
          <TouchableOpacity style={styles.resolveBtn} onPress={onResolveEmergency} activeOpacity={0.8}>
            <Text style={styles.btnText}>✅ Resolve Alert</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={styles.sosBtn} onPress={handleSOSPress} activeOpacity={0.8}>
            <Text style={styles.btnText}>🚨 Panic SOS Button</Text>
          </TouchableOpacity>
        )}
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
    borderWidth: 1.5,
  },
  normalBorder: {
    borderColor: '#334155',
  },
  emergencyBorder: {
    borderColor: '#EF4444',
    backgroundColor: '#450A0A',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  titleIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  titleText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#94A3B8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  statusTag: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  normalTag: {
    backgroundColor: '#064E3B',
  },
  alertTag: {
    backgroundColor: '#991B1B',
  },
  normalTagTxt: {
    color: '#34D399',
    fontSize: 10,
    fontWeight: '700',
  },
  alertTagTxt: {
    color: '#FCA5A5',
    fontSize: 10,
    fontWeight: '700',
  },
  alertTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#F8FAFC',
    marginTop: 4,
  },
  lastAlert: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  actionRow: {
    marginTop: 14,
  },
  sosBtn: {
    backgroundColor: '#DC2626',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  resolveBtn: {
    backgroundColor: '#059669',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  btnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
});
