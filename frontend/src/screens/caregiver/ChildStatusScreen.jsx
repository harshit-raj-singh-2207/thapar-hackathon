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
import ChildStatusCard from '../../components/caregiver/ChildStatusCard';
import ChildLocationCard from '../../components/caregiver/ChildLocationCard';
import DeviceStatusCard from '../../components/caregiver/DeviceStatusCard';
import RecentSafetyActivity from '../../components/caregiver/RecentSafetyActivity';

export default function ChildStatusScreen({ navigation }) {
  const { childName, childAge, batteryLevel, gpsStatus, bleConnected, separationDistance, safetyEvents } =
    useSafety();
  const { currentLocation } = useLocation();

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title="Live Child Telemetry"
        subtitle="Real-time biometric, GPS and proximity monitoring"
        onBack={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('CaregiverDashboard'))}
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Child Telemetry & Mood Card */}
        <ChildStatusCard
          childName={childName}
          age={childAge}
          currentMood="Calm & Regulated"
          moodType="calm"
          heartRate={76}
          lastUpdated="Just now"
        />

        {/* Location & Safe Zone Presence */}
        <ChildLocationCard
          childName={childName}
          locationName="Model Town Sanctuary"
          city="Ludhiana"
          accuracy="±3.8 meters"
          isInsideSafeZone={true}
          safeZoneName="Home Sanctuary"
          onPressMap={() => navigation.navigate('LiveLocation')}
        />

        {/* Device & Connection Health */}
        <DeviceStatusCard
          battery={batteryLevel}
          isCharging={false}
          gpsStatus={`Active (${gpsStatus})`}
          bleStatus={bleConnected ? `Tethered (${separationDistance}m)` : 'Disconnected'}
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
    padding: 16,
    paddingBottom: 40,
    maxWidth: 600,
    alignSelf: 'center',
    width: '100%',
  },
});
