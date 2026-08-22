import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Alert,
} from 'react-native';

import { locationService } from '../../services/location/locationService';
import BandStatus from '../../components/safety/BandStatus';
import GPSStatusPanel from '../../components/safety/GPSStatusPanel';

export default function GPSBandScreen({ navigation }) {
  const [locationState, setLocationState] = useState(null);

  useEffect(() => {
    const unsub = locationService.subscribe((state) => {
      setLocationState(state);
    });
    return () => unsub();
  }, []);

  const handleTriggerSOS = () => {
    Alert.alert('SOS Triggered', 'Emergency SOS signal broadcast.');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topBar}>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('LiveLocation'))}
        >
          <Text style={styles.backBtnText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>NIVARA GPS SmartBand</Text>
      </View>

      <ScrollView style={styles.content}>
        <BandStatus
          device={locationState?.childLocation?.device}
          battery={locationState?.childLocation?.battery}
          onTriggerSOS={handleTriggerSOS}
        />

        <GPSStatusPanel
          gpsStatus={locationState?.gpsStatus}
          childLocation={locationState?.childLocation}
          onSimulateStatus={(st) => locationService.setGpsStatus(st)}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#1E293B',
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  backBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  backBtnText: {
    fontSize: 18,
    color: '#F8FAFC',
    fontWeight: '800',
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    color: '#F8FAFC',
  },
  content: {
    padding: 16,
  },
});
