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
import SafeZoneCard from '../../components/safety/SafeZoneCard';
import LocationSettingsModal from '../../components/safety/LocationSettingsModal';

export default function SafeZonesScreen({ navigation }) {
  const [safeZones, setSafeZones] = useState([]);
  const [childLocation, setChildLocation] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    const unsub = locationService.subscribe((state) => {
      setSafeZones(state.safeZones || []);
      setChildLocation(state.childLocation || null);
    });
    return () => unsub();
  }, []);

  const handleToggleActive = async (zoneId) => {
    await locationService.toggleSafeZoneActive(zoneId);
  };

  const handleDelete = async (zoneId) => {
    Alert.alert('Delete Safe Zone', 'Are you sure you want to remove this safe zone?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          await locationService.deleteSafeZone(zoneId);
        },
      },
    ]);
  };

  const handleAddZone = async (zoneData) => {
    await locationService.addSafeZone(zoneData);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Top Bar */}
      <View style={styles.topBar}>
        <View style={styles.titleRow}>
          <TouchableOpacity
            style={styles.backBtn}
            onPress={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('LiveLocation'))}
          >
            <Text style={styles.backBtnText}>←</Text>
          </TouchableOpacity>
          <View>
            <Text style={styles.title}>Safe Zones & Geofences</Text>
            <Text style={styles.subtitle}>
              {safeZones.filter((z) => z.active).length} of {safeZones.length} geofences active
            </Text>
          </View>
        </View>

        <TouchableOpacity
          style={styles.addBtn}
          onPress={() => setModalVisible(true)}
          activeOpacity={0.8}
        >
          <Text style={styles.addBtnText}>＋ Add Zone</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Info Banner */}
        <View style={styles.infoBanner}>
          <Text style={styles.infoIcon}>ℹ️</Text>
          <Text style={styles.infoText}>
            Safe zones trigger instant notifications whenever the child enters or exits a defined perimeter.
          </Text>
        </View>

        {/* Zones List */}
        {safeZones.map((zone) => (
          <SafeZoneCard
            key={zone.id}
            zone={zone}
            isChildInside={childLocation?.currentZoneId === zone.id}
            onToggleActive={handleToggleActive}
            onDelete={handleDelete}
            onFocusMap={() => navigation.navigate('LiveLocation')}
          />
        ))}
      </ScrollView>

      <LocationSettingsModal
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
        onAddSafeZone={handleAddZone}
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
  addBtn: {
    backgroundColor: '#2563EB',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 999,
  },
  addBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  infoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#BFDBFE',
    marginBottom: 16,
  },
  infoIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#1E40AF',
    lineHeight: 18,
    fontWeight: '600',
  },
});
