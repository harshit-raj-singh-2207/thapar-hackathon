import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useSafety } from '../../hooks/useSafety';
import { useLocation } from '../../hooks/useLocation';
import AppHeader from '../../components/common/AppHeader';
import Avatar from '../../components/common/Avatar';
import StatusIndicator from '../../components/common/StatusIndicator';

export default function ChildProfileScreen({ navigation }) {
  const { childName, childAge, isSafe, safeZones, emergencyContacts, batteryLevel, bleConnected } =
    useSafety();
  const { currentLocation } = useLocation();

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title="Child Profile & Safety"
        subtitle="Individualized care, safety telemetry & assigned devices"
        onBack={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('CaregiverDashboard'))}
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Profile Card */}
        <View style={styles.profileCard}>
          <View style={styles.profileHeader}>
            <Avatar name={childName} emoji="🧒" size={68} />
            <View style={styles.profileInfo}>
              <Text style={styles.profileName}>{childName}</Text>
              <Text style={styles.profileAge}>Age {childAge} • Neurodivergent Care Track</Text>
              <View style={styles.statusRow}>
                <StatusIndicator
                  status={isSafe ? 'safe' : 'danger'}
                  label={isSafe ? 'Protected Inside Safe Zone' : 'Safety Attention Required'}
                  size={10}
                />
              </View>
            </View>
          </View>

          <View style={styles.badgesRow}>
            <View style={styles.profilePill}>
              <Text style={styles.pillLabel}>Sensory Profile</Text>
              <Text style={styles.pillVal}>Sound Sensitive</Text>
            </View>
            <View style={styles.profilePill}>
              <Text style={styles.pillLabel}>Communication</Text>
              <Text style={styles.pillVal}>AAC & Verbal</Text>
            </View>
            <View style={styles.profilePill}>
              <Text style={styles.pillLabel}>Wearable</Text>
              <Text style={styles.pillVal}>{bleConnected ? 'Band Paired' : 'Band Offline'}</Text>
            </View>
          </View>
        </View>

        {/* Location & Safe Zones Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>Current Location & Active Safe Zones</Text>
            <TouchableOpacity onPress={() => navigation.navigate('SafeZones')}>
              <Text style={styles.sectionLink}>View All ({safeZones.length}) ›</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.card}>
            <View style={styles.locHeader}>
              <Text style={styles.locIcon}>📍</Text>
              <View style={styles.locTextCol}>
                <Text style={styles.locTitle}>Last Recorded Location</Text>
                <Text style={styles.locAddress}>
                  {currentLocation?.address || '123 Maple Street, Model Town, Ludhiana'}
                </Text>
              </View>
            </View>
            <TouchableOpacity
              style={styles.mapActionBtn}
              onPress={() => navigation.navigate('LiveLocation')}
            >
              <Text style={styles.mapActionBtnText}>🗺️ Open Real-time Map View</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Assigned GPS SmartBand */}
        <View style={styles.section}>
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>Assigned Wearable Band</Text>
            <TouchableOpacity onPress={() => navigation.navigate('GPSBand')}>
              <Text style={styles.sectionLink}>Device Settings ›</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.card}>
            <View style={styles.deviceRow}>
              <View style={styles.deviceIconCircle}>
                <Text style={styles.deviceIcon}>⌚</Text>
              </View>
              <View style={styles.deviceInfo}>
                <Text style={styles.deviceName}>Nivara CoreBand Pro v2.4</Text>
                <Text style={styles.deviceId}>Device ID: NV-BAND-8821 • BLE Tether</Text>
              </View>
              <View style={styles.batteryPill}>
                <Text style={styles.batteryPillText}>🔋 {batteryLevel}%</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Emergency Escalation Contacts */}
        <View style={styles.section}>
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>Assigned Emergency Contacts</Text>
            <TouchableOpacity onPress={() => navigation.navigate('EmergencyContacts')}>
              <Text style={styles.sectionLink}>Manage ({emergencyContacts.length}) ›</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.contactsList}>
            {emergencyContacts.slice(0, 2).map((contact) => (
              <View key={contact.id} style={styles.contactItem}>
                <Text style={styles.contactAvatar}>{contact.avatar || '👤'}</Text>
                <View style={styles.contactInfo}>
                  <Text style={styles.contactName}>{contact.name}</Text>
                  <Text style={styles.contactRole}>{contact.relationship}</Text>
                </View>
                {contact.isPrimary && (
                  <View style={styles.primaryBadge}>
                    <Text style={styles.primaryBadgeText}>Primary</Text>
                  </View>
                )}
              </View>
            ))}
          </View>
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
  profileCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  profileInfo: {
    marginLeft: 16,
    flex: 1,
  },
  profileName: {
    fontSize: 20,
    fontWeight: '900',
    color: '#0F172A',
  },
  profileAge: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '600',
  },
  statusRow: {
    marginTop: 6,
  },
  badgesRow: {
    flexDirection: 'row',
    gap: 8,
    paddingTop: 14,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  profilePill: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  pillLabel: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
    marginBottom: 2,
  },
  pillVal: {
    fontSize: 11,
    fontWeight: '800',
    color: '#0F172A',
  },
  section: {
    marginBottom: 20,
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  sectionLink: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  locHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  locIcon: {
    fontSize: 20,
    marginRight: 10,
  },
  locTextCol: {
    flex: 1,
  },
  locTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  locAddress: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  mapActionBtn: {
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#BFDBFE',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
  },
  mapActionBtnText: {
    color: '#2563EB',
    fontSize: 12,
    fontWeight: '800',
  },
  deviceRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  deviceIconCircle: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  deviceIcon: {
    fontSize: 20,
  },
  deviceInfo: {
    flex: 1,
  },
  deviceName: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  deviceId: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  batteryPill: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  batteryPillText: {
    color: '#059669',
    fontSize: 11,
    fontWeight: '800',
  },
  contactsList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    gap: 8,
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
  },
  contactAvatar: {
    fontSize: 20,
    marginRight: 10,
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  contactRole: {
    fontSize: 11,
    color: '#64748B',
  },
  primaryBadge: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  primaryBadgeText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#2563EB',
  },
});
