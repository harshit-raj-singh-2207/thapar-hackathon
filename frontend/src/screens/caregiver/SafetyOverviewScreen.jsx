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
import SafetyStatusCard from '../../components/safety/SafetyStatusCard';
import DeviceStatusCard from '../../components/caregiver/DeviceStatusCard';
import RecentSafetyActivity from '../../components/caregiver/RecentSafetyActivity';
import EmergencyButton from '../../components/safety/EmergencyButton';

export default function SafetyOverviewScreen({ navigation }) {
  const {
    childName,
    isSafe,
    currentZone,
    batteryLevel,
    gpsStatus,
    bleConnected,
    separationDistance,
    safeZones,
    safetyEvents,
    isEmergencyActive,
  } = useSafety();

  const { currentLocation } = useLocation();

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title="Comprehensive Safety Overview"
        subtitle="Holistic security, geofence status & live telemetry"
        onBack={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('CaregiverDashboard'))}
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Active Emergency Banner */}
        {isEmergencyActive && (
          <TouchableOpacity
            style={styles.emergencyAlertBanner}
            onPress={() => navigation.navigate('Emergency')}
            activeOpacity={0.85}
          >
            <Text style={styles.alertBannerIcon}>🚨</Text>
            <View style={styles.alertBannerTextCol}>
              <Text style={styles.alertBannerTitle}>EMERGENCY BROADCAST ACTIVE</Text>
              <Text style={styles.alertBannerSub}>Tap to view emergency response center</Text>
            </View>
            <Text style={styles.alertBannerArrow}>›</Text>
          </TouchableOpacity>
        )}

        {/* Primary Safety Status Card */}
        <SafetyStatusCard
          isSafe={isSafe}
          currentZone={currentZone}
          battery={batteryLevel}
          onPress={() => navigation.navigate('LiveLocation')}
        />

        {/* High-level Metrics Row */}
        <View style={styles.metricsGrid}>
          <TouchableOpacity
            style={styles.metricCard}
            onPress={() => navigation.navigate('SafeZones')}
            activeOpacity={0.85}
          >
            <Text style={styles.metricIcon}>🛡️</Text>
            <Text style={styles.metricLabel}>Safe Zones</Text>
            <Text style={styles.metricVal}>
              {safeZones.filter((z) => z.active).length} / {safeZones.length}
            </Text>
            <Text style={styles.metricSub}>Active Boundaries</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.metricCard}
            onPress={() => navigation.navigate('GPSBand')}
            activeOpacity={0.85}
          >
            <Text style={styles.metricIcon}>ᛒ</Text>
            <Text style={styles.metricLabel}>BLE Tether</Text>
            <Text style={[styles.metricVal, { color: bleConnected ? '#059669' : '#DC2626' }]}>
              {bleConnected ? `${separationDistance}m` : 'Offline'}
            </Text>
            <Text style={styles.metricSub}>Proximity Range</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.metricCard}
            onPress={() => navigation.navigate('DeviceStatus')}
            activeOpacity={0.85}
          >
            <Text style={styles.metricIcon}>🛰️</Text>
            <Text style={styles.metricLabel}>GPS Satellite</Text>
            <Text style={styles.metricVal}>{gpsStatus}</Text>
            <Text style={styles.metricSub}>High Precision</Text>
          </TouchableOpacity>
        </View>

        {/* Live Location Card */}
        <View style={styles.locationSectionCard}>
          <View style={styles.locCardHeader}>
            <View style={styles.locIconCircle}>
              <Text style={styles.locIcon}>📍</Text>
            </View>
            <View style={styles.locTitleCol}>
              <Text style={styles.locTitle}>{childName}'s Live Position</Text>
              <Text style={styles.locAddress}>
                {currentLocation?.address || '123 Maple Street, Model Town, Ludhiana'}
              </Text>
            </View>
          </View>
          <TouchableOpacity
            style={styles.viewMapButton}
            onPress={() => navigation.navigate('LiveLocation')}
            activeOpacity={0.85}
          >
            <Text style={styles.viewMapButtonText}>🗺️ Open Real-time Map & Breadcrumbs</Text>
          </TouchableOpacity>
        </View>

        {/* Device Health Card */}
        <DeviceStatusCard
          battery={batteryLevel}
          isCharging={false}
          gpsStatus={gpsStatus}
          bleStatus={bleConnected ? 'Connected (Strong)' : 'Disconnected'}
        />

        {/* Quick SOS Action */}
        <EmergencyButton
          onPress={() => navigation.navigate('Emergency')}
          label="OPEN EMERGENCY CENTER"
          style={styles.emergencyBtn}
        />

        {/* Recent Safety Activity */}
        <RecentSafetyActivity
          activities={safetyEvents}
          onViewAll={() => navigation.navigate('CaregiverDashboard')}
        />
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
  emergencyAlertBanner: {
    backgroundColor: '#DC2626',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    marginBottom: 16,
  },
  alertBannerIcon: {
    fontSize: 22,
    marginRight: 12,
  },
  alertBannerTextCol: {
    flex: 1,
  },
  alertBannerTitle: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  alertBannerSub: {
    color: '#FECACA',
    fontSize: 11,
    marginTop: 2,
  },
  alertBannerArrow: {
    color: '#FFFFFF',
    fontSize: 22,
    fontWeight: '800',
  },
  metricsGrid: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 16,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
  },
  metricIcon: {
    fontSize: 20,
    marginBottom: 6,
  },
  metricLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
    marginBottom: 2,
  },
  metricVal: {
    fontSize: 15,
    fontWeight: '900',
    color: '#0F172A',
  },
  metricSub: {
    fontSize: 9,
    color: '#94A3B8',
    marginTop: 2,
  },
  locationSectionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 16,
  },
  locCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  locIconCircle: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  locIcon: {
    fontSize: 20,
  },
  locTitleCol: {
    flex: 1,
  },
  locTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  locAddress: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  viewMapButton: {
    backgroundColor: '#0F3D87',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  viewMapButtonText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
  },
  emergencyBtn: {
    marginBottom: 16,
  },
});
