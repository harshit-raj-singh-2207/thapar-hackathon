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
import EmergencyButton from '../../components/safety/EmergencyButton';
import SafetyStatusCard from '../../components/safety/SafetyStatusCard';
import LocationCard from '../../components/safety/LocationCard';
import RecentSafetyActivity from '../../components/caregiver/RecentSafetyActivity';

export default function SafetyHomeScreen({ navigation }) {
  const {
    childName,
    childAge,
    isSafe,
    currentZone,
    batteryLevel,
    gpsStatus,
    bleConnected,
    separationDistance,
    isEmergencyActive,
    safetyEvents,
  } = useSafety();

  const { currentLocation, refreshLocation, isLocationSharingOn, toggleSharing } =
    useLocation();

  const quickActions = [
    {
      title: 'Live Location',
      desc: 'Real-time GPS map & breadcrumbs',
      icon: '🗺️',
      color: '#2563EB',
      bg: '#EFF6FF',
      border: '#BFDBFE',
      route: 'LiveLocation',
    },
    {
      title: 'GPS Band',
      desc: 'Wearable tether & proximity radar',
      icon: '⌚',
      color: '#059669',
      bg: '#ECFDF5',
      border: '#A7F3D0',
      route: 'GPSBand',
    },
    {
      title: 'Safe Zones',
      desc: 'Geofence boundaries & alerts',
      icon: '🛡️',
      color: '#8B5CF6',
      bg: '#F5F3FF',
      border: '#DDD6FE',
      route: 'SafeZones',
    },
    {
      title: 'Emergency Contacts',
      desc: 'Caregiver escalation roster',
      icon: '📞',
      color: '#D97706',
      bg: '#FFFBEB',
      border: '#FDE68A',
      route: 'EmergencyContacts',
    },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title="Safety & Caregiver Center"
        subtitle="Real-time monitoring, geofences & smart tether"
        onBack={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('CaregiverDashboard'))}
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Prominent Active Emergency Banner */}
        {isEmergencyActive && (
          <TouchableOpacity
            style={styles.emergencyBanner}
            onPress={() => navigation.navigate('Emergency')}
            activeOpacity={0.85}
          >
            <Text style={styles.emergencyIcon}>🚨</Text>
            <View style={styles.emergencyTextCol}>
              <Text style={styles.emergencyTitle}>EMERGENCY ALERT BROADCAST ACTIVE</Text>
              <Text style={styles.emergencySub}>
                Coordinates transmitted to caregivers • Tap for response center
              </Text>
            </View>
            <Text style={styles.emergencyArrow}>›</Text>
          </TouchableOpacity>
        )}

        {/* Child Profile & Live Safety Status Header */}
        <TouchableOpacity
          style={styles.childHeaderCard}
          onPress={() => navigation.navigate('ChildProfile')}
          activeOpacity={0.88}
        >
          <Avatar name={childName} emoji="🧒" size={54} />
          <View style={styles.childHeaderInfo}>
            <View style={styles.childNameRow}>
              <Text style={styles.childName}>{childName}</Text>
              <Text style={styles.childAge}>Age {childAge}</Text>
            </View>
            <View style={styles.statusRow}>
              <StatusIndicator
                status={isSafe ? 'safe' : 'danger'}
                label={isSafe ? 'Child is Safe' : 'Safety Attention Active'}
                size={9}
              />
              <Text style={styles.dotSeparator}>•</Text>
              <Text style={styles.zoneText}>{currentZone}</Text>
            </View>
          </View>
          <Text style={styles.profileArrow}>›</Text>
        </TouchableOpacity>

        {/* Key Telemetry Quick Bar */}
        <View style={styles.telemetryRow}>
          <View style={styles.telemetryPill}>
            <Text style={styles.pillIcon}>🛰️</Text>
            <Text style={styles.pillText}>GPS: {gpsStatus}</Text>
          </View>
          <View style={styles.telemetryPill}>
            <Text style={styles.pillIcon}>ᛒ</Text>
            <Text style={styles.pillText}>
              {bleConnected ? `Band: ${separationDistance}m` : 'Band: Disconnected'}
            </Text>
          </View>
          <View style={styles.telemetryPill}>
            <Text style={styles.pillIcon}>🔋</Text>
            <Text style={styles.pillText}>Battery: {batteryLevel}%</Text>
          </View>
        </View>

        {/* SOS Emergency Trigger Button */}
        <EmergencyButton
          onPress={() => navigation.navigate('Emergency')}
          label="SOS EMERGENCY ESCALATION"
          style={styles.sosButton}
        />

        {/* Quick Action Navigation Grid */}
        <Text style={styles.sectionTitle}>SAFETY CONTROLS & MODULES</Text>
        <View style={styles.quickGrid}>
          {quickActions.map((action) => (
            <TouchableOpacity
              key={action.title}
              style={[
                styles.quickCard,
                { backgroundColor: action.bg, borderColor: action.border },
              ]}
              onPress={() => navigation.navigate(action.route)}
              activeOpacity={0.85}
            >
              <View style={[styles.quickIconCircle, { backgroundColor: '#FFFFFF' }]}>
                <Text style={styles.quickIcon}>{action.icon}</Text>
              </View>
              <Text style={[styles.quickTitle, { color: action.color }]}>
                {action.title}
              </Text>
              <Text style={styles.quickDesc}>{action.desc}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Location Snapshot Card */}
        {currentLocation && (
          <LocationCard
            childLocation={currentLocation}
            gpsStatus={gpsStatus}
            isLocationSharingOn={isLocationSharingOn}
            distanceToCaregiver={separationDistance}
            bearingToChild={{ degrees: 45, cardinal: 'NE' }}
            onLocateNow={refreshLocation}
            onToggleSharing={toggleSharing}
            onOpenHistory={() => navigation.navigate('LiveLocation')}
          />
        )}

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
  emergencyBanner: {
    backgroundColor: '#DC2626',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#DC2626',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  emergencyIcon: {
    fontSize: 22,
    marginRight: 12,
  },
  emergencyTextCol: {
    flex: 1,
  },
  emergencyTitle: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  emergencySub: {
    color: '#FECACA',
    fontSize: 11,
    marginTop: 2,
    fontWeight: '500',
  },
  emergencyArrow: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '800',
  },
  childHeaderCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  childHeaderInfo: {
    marginLeft: 14,
    flex: 1,
  },
  childNameRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 8,
  },
  childName: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  childAge: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  dotSeparator: {
    color: '#CBD5E1',
    marginHorizontal: 6,
    fontSize: 10,
  },
  zoneText: {
    fontSize: 11,
    color: '#475569',
    fontWeight: '700',
  },
  profileArrow: {
    fontSize: 22,
    color: '#94A3B8',
    fontWeight: '700',
  },
  telemetryRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  telemetryPill: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingVertical: 8,
    paddingHorizontal: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    justifyContent: 'center',
  },
  pillIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  pillText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#334155',
  },
  sosButton: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 12,
  },
  quickGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 20,
  },
  quickCard: {
    flex: 1,
    minWidth: '46%',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1.5,
  },
  quickIconCircle: {
    width: 38,
    height: 38,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  quickIcon: {
    fontSize: 18,
  },
  quickTitle: {
    fontSize: 14,
    fontWeight: '800',
    marginBottom: 2,
  },
  quickDesc: {
    fontSize: 11,
    color: '#64748B',
    lineHeight: 15,
  },
});
