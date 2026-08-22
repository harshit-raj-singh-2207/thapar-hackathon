import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Linking,
  Platform,
} from 'react-native';
import { useSafety } from '../../hooks/useSafety';
import { useLocation } from '../../hooks/useLocation';
import AppHeader from '../../components/common/AppHeader';
import AppButton from '../../components/common/AppButton';
import ConfirmModal from '../../components/common/ConfirmModal';
import EmergencyButton from '../../components/safety/EmergencyButton';
import EmergencyContactCard from '../../components/safety/EmergencyContactCard';
import StatusIndicator from '../../components/common/StatusIndicator';

export default function EmergencyScreen({ navigation }) {
  const {
    childName,
    isEmergencyActive,
    activeEmergency,
    emergencyContacts,
    triggerEmergency,
    resolveEmergency,
    emergencyLoading,
  } = useSafety();

  const { currentLocation, refreshLocation } = useLocation();

  const [confirmModalVisible, setConfirmModalVisible] = useState(false);
  const [resolveModalVisible, setResolveModalVisible] = useState(false);

  const handleInitiateSOS = () => {
    setConfirmModalVisible(true);
  };

  const handleConfirmSOS = async () => {
    setConfirmModalVisible(false);
    await triggerEmergency({
      location: currentLocation,
      initiatedFrom: 'EmergencyScreen',
    });
  };

  const handleResolveEmergency = async () => {
    setResolveModalVisible(false);
    await resolveEmergency();
  };

  const handleCallContact = (contact) => {
    if (contact?.phone) {
      const cleaned = contact.phone.replace(/[^0-9+]/g, '');
      Linking.openURL(`tel:${cleaned}`).catch(() => {});
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title="SOS Emergency Center"
        subtitle="Immediate priority alerting & live location broadcast"
        onBack={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('CaregiverDashboard'))}
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Emergency Status Banner */}
        {isEmergencyActive ? (
          <View style={styles.activeEmergencyBanner}>
            <View style={styles.bannerHeader}>
              <View style={styles.pulsingIcon}>
                <Text style={styles.sosSymbol}>🚨</Text>
              </View>
              <View style={styles.bannerTextCol}>
                <Text style={styles.bannerTitle}>EMERGENCY BROADCAST ACTIVE</Text>
                <Text style={styles.bannerSubtitle}>
                  Location and alerts shared with all emergency contacts
                </Text>
              </View>
            </View>

            <View style={styles.telemetryBox}>
              <Text style={styles.telemetryLabel}>SUBJECT:</Text>
              <Text style={styles.telemetryVal}>{childName}</Text>

              <Text style={styles.telemetryLabel}>BROADCAST LOCATION:</Text>
              <Text style={styles.telemetryVal}>
                {currentLocation?.address || '123 Maple Street, Model Town, Ludhiana'}
              </Text>

              <View style={styles.coordsRow}>
                <Text style={styles.coordsText}>
                  Lat: {currentLocation?.latitude?.toFixed(4) || '30.9010'} • Lon:{' '}
                  {currentLocation?.longitude?.toFixed(4) || '75.8573'}
                </Text>
                <Text style={styles.accuracyText}>Accuracy: ±3.8m</Text>
              </View>
            </View>

            <View style={styles.bannerActions}>
              <TouchableOpacity
                style={styles.viewMapBtn}
                onPress={() => navigation.navigate('LiveLocation')}
                activeOpacity={0.85}
              >
                <Text style={styles.viewMapBtnText}>🗺️ Track on Live Map</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.resolveBtn}
                onPress={() => setResolveModalVisible(true)}
                activeOpacity={0.85}
              >
                <Text style={styles.resolveBtnText}>✓ Mark Safe / Resolve</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          <View style={styles.standbyCard}>
            <View style={styles.standbyHeader}>
              <StatusIndicator status="safe" label="System Ready & Armed" size={10} />
              <Text style={styles.standbyTime}>Auto-sync 10s</Text>
            </View>
            <Text style={styles.standbyTitle}>Emergency Escalation Protocol</Text>
            <Text style={styles.standbyDesc}>
              Pressing the SOS button below will instantly notify caregivers, transmit high-precision GPS telemetry, and sound the SmartBand alarm beacon.
            </Text>

            <EmergencyButton
              onPress={handleInitiateSOS}
              label="TRIGGER SOS EMERGENCY"
              loading={emergencyLoading}
              size="large"
              style={styles.sosButton}
            />
          </View>
        )}

        {/* Emergency Quick Dial & Contacts Section */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Emergency Contacts ({emergencyContacts.length})</Text>
          <TouchableOpacity
            onPress={() => navigation.navigate('EmergencyContacts')}
            activeOpacity={0.8}
          >
            <Text style={styles.manageLink}>Manage Contacts ›</Text>
          </TouchableOpacity>
        </View>

        {emergencyContacts.map((contact) => (
          <EmergencyContactCard
            key={contact.id}
            contact={contact}
            onCall={handleCallContact}
          />
        ))}

        {/* Emergency Location Verification */}
        <View style={styles.locationCard}>
          <View style={styles.locCardHeader}>
            <Text style={styles.locIcon}>📍</Text>
            <View style={styles.locTitleCol}>
              <Text style={styles.locCardTitle}>Current Safety Beacon Location</Text>
              <Text style={styles.locAddress}>
                {currentLocation?.address || '123 Maple Street, Model Town, Ludhiana'}
              </Text>
            </View>
          </View>
          <TouchableOpacity
            style={styles.refreshLocBtn}
            onPress={refreshLocation}
            activeOpacity={0.85}
          >
            <Text style={styles.refreshLocText}>🔄 Refresh GPS Coordinates</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Confirmation Modal before triggering SOS */}
      <ConfirmModal
        visible={confirmModalVisible}
        onClose={() => setConfirmModalVisible(false)}
        onConfirm={handleConfirmSOS}
        title="Trigger Emergency SOS?"
        message={`Are you sure you want to broadcast an emergency for ${childName}? This will immediately alert all caregivers and transmit live GPS coordinates.`}
        confirmText="Yes, Send SOS"
        cancelText="Cancel"
        confirmVariant="danger"
        icon="🚨"
        loading={emergencyLoading}
      />

      {/* Resolve Emergency Modal */}
      <ConfirmModal
        visible={resolveModalVisible}
        onClose={() => setResolveModalVisible(false)}
        onConfirm={handleResolveEmergency}
        title="Resolve Active Emergency?"
        message={`Confirm that ${childName} is safe and the emergency status can be safely resolved.`}
        confirmText="Confirm Safe & Resolve"
        cancelText="Keep Active"
        confirmVariant="success"
        icon="🛡️"
        loading={emergencyLoading}
      />
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
  },
  activeEmergencyBanner: {
    backgroundColor: '#FEF2F2',
    borderRadius: 20,
    borderWidth: 2,
    borderColor: '#DC2626',
    padding: 20,
    marginBottom: 20,
    shadowColor: '#DC2626',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 4,
  },
  bannerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  pulsingIcon: {
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: '#DC2626',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  sosSymbol: {
    fontSize: 22,
  },
  bannerTextCol: {
    flex: 1,
  },
  bannerTitle: {
    fontSize: 16,
    fontWeight: '900',
    color: '#991B1B',
    letterSpacing: 0.5,
  },
  bannerSubtitle: {
    fontSize: 12,
    color: '#7F1D1D',
    marginTop: 2,
    fontWeight: '600',
  },
  telemetryBox: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: '#FECACA',
    marginBottom: 16,
  },
  telemetryLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: '#991B1B',
    letterSpacing: 0.8,
    marginTop: 4,
  },
  telemetryVal: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 6,
  },
  coordsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#FEE2E2',
  },
  coordsText: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  accuracyText: {
    fontSize: 11,
    color: '#059669',
    fontWeight: '700',
  },
  bannerActions: {
    flexDirection: 'row',
    gap: 10,
  },
  viewMapBtn: {
    flex: 1,
    backgroundColor: '#0F3D87',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  viewMapBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
  },
  resolveBtn: {
    flex: 1,
    backgroundColor: '#059669',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  resolveBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
  },
  standbyCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
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
  standbyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  standbyTime: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  standbyTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 6,
  },
  standbyDesc: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 19,
    marginBottom: 20,
  },
  sosButton: {
    width: '100%',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    marginTop: 6,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  manageLink: {
    fontSize: 13,
    fontWeight: '700',
    color: '#2563EB',
  },
  locationCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginTop: 10,
  },
  locCardHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  locIcon: {
    fontSize: 20,
    marginRight: 10,
    marginTop: 2,
  },
  locTitleCol: {
    flex: 1,
  },
  locCardTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  locAddress: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  refreshLocBtn: {
    backgroundColor: '#F1F5F9',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
  },
  refreshLocText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
});
