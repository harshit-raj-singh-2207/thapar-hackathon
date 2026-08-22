import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Platform,
} from 'react-native';
import { useSafety } from '../../hooks/useSafety';
import { useLocation } from '../../hooks/useLocation';
import AppHeader from '../../components/common/AppHeader';
import AppButton from '../../components/common/AppButton';
import AppInput from '../../components/common/AppInput';
import { ZONE_TYPES, SAFE_ZONE_ICONS } from '../../constants/safetyConstants';

export default function AddSafeZoneScreen({ navigation, route }) {
  const { addSafeZone, updateSafeZone } = useSafety();
  const { currentLocation } = useLocation();

  const editingZone = route?.params?.zone;

  const [name, setName] = useState(editingZone?.name || '');
  const [address, setAddress] = useState(editingZone?.address || '');
  const [latitude, setLatitude] = useState(
    editingZone ? String(editingZone.latitude) : String(currentLocation?.latitude || 30.9010)
  );
  const [longitude, setLongitude] = useState(
    editingZone ? String(editingZone.longitude) : String(currentLocation?.longitude || 75.8573)
  );
  const [radius, setRadius] = useState(editingZone?.radius ? String(editingZone.radius) : '100');
  const [selectedType, setSelectedType] = useState(editingZone?.zoneType || 'Home');
  const [selectedIcon, setSelectedIcon] = useState(editingZone?.icon || '🏠');
  const [isActive, setIsActive] = useState(editingZone ? editingZone.active : true);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleSelectType = (typeObj) => {
    setSelectedType(typeObj.key);
    setSelectedIcon(typeObj.icon);
  };

  const handleUseCurrentLocation = () => {
    if (currentLocation) {
      setLatitude(String(currentLocation.latitude));
      setLongitude(String(currentLocation.longitude));
      if (currentLocation.address) {
        setAddress(currentLocation.address);
      }
    }
  };

  const validate = () => {
    const errs = {};
    if (!name.trim()) errs.name = 'Safe Zone name is required';
    if (!address.trim()) errs.address = 'Address or location description is required';

    const lat = parseFloat(latitude);
    const lon = parseFloat(longitude);
    if (isNaN(lat) || lat < -90 || lat > 90) {
      errs.latitude = 'Latitude must be a valid number between -90 and 90';
    }
    if (isNaN(lon) || lon < -180 || lon > 180) {
      errs.longitude = 'Longitude must be a valid number between -180 and 180';
    }

    const rad = parseInt(radius, 10);
    if (isNaN(rad) || rad < 20 || rad > 5000) {
      errs.radius = 'Radius must be between 20 meters and 5000 meters';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) return;

    setLoading(true);
    const selectedTypeObj = ZONE_TYPES.find((t) => t.key === selectedType);
    const zoneData = {
      name: name.trim(),
      address: address.trim(),
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      radius: parseInt(radius, 10),
      zoneType: selectedType,
      icon: selectedIcon,
      color: selectedTypeObj?.color || '#2563EB',
      active: isActive,
      schedule: 'Always Active',
    };

    try {
      if (editingZone) {
        await updateSafeZone(editingZone.id, zoneData);
      } else {
        await addSafeZone(zoneData);
      }
      navigation.goBack();
    } catch (e) {
      setErrors({ form: 'Failed to save safe zone. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const radiusPresets = [50, 100, 150, 250, 500];

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title={editingZone ? 'Edit Safe Zone' : 'Create Safe Zone'}
        subtitle="Define dynamic geofence boundaries and alert thresholds"
        onBack={() => navigation.goBack()}
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Zone Category Selection */}
        <Text style={styles.sectionHeader}>ZONE CATEGORY</Text>
        <View style={styles.typeGrid}>
          {ZONE_TYPES.map((t) => {
            const isSelected = selectedType === t.key;
            return (
              <TouchableOpacity
                key={t.key}
                style={[
                  styles.typeCard,
                  isSelected && { borderColor: t.color, backgroundColor: `${t.color}15` },
                ]}
                onPress={() => handleSelectType(t)}
                activeOpacity={0.8}
              >
                <Text style={styles.typeIcon}>{t.icon}</Text>
                <Text style={[styles.typeLabel, isSelected && { color: t.color, fontWeight: '800' }]}>
                  {t.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Icon Picker */}
        <Text style={styles.sectionHeader}>CHOOSE ICON</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.iconPickerRow}>
          {SAFE_ZONE_ICONS.map((emoji) => (
            <TouchableOpacity
              key={emoji}
              style={[
                styles.iconOption,
                selectedIcon === emoji && styles.iconOptionSelected,
              ]}
              onPress={() => setSelectedIcon(emoji)}
            >
              <Text style={styles.iconOptionText}>{emoji}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Name & Address */}
        <Text style={styles.sectionHeader}>GENERAL INFORMATION</Text>
        <AppInput
          label="Zone Name *"
          value={name}
          onChangeText={(t) => {
            setName(t);
            setErrors((prev) => ({ ...prev, name: null }));
          }}
          placeholder="e.g. Home Sanctuary, Therapy Clinic"
          error={errors.name}
        />

        <AppInput
          label="Address / Street Location *"
          value={address}
          onChangeText={(t) => {
            setAddress(t);
            setErrors((prev) => ({ ...prev, address: null }));
          }}
          placeholder="e.g. 123 Maple Street, Model Town, Ludhiana"
          error={errors.address}
        />

        {/* Coordinates Section */}
        <View style={styles.coordsHeaderRow}>
          <Text style={styles.sectionHeader}>GPS COORDINATES</Text>
          <TouchableOpacity onPress={handleUseCurrentLocation} style={styles.useCurrentBtn}>
            <Text style={styles.useCurrentText}>📍 Use Current Child Location</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.coordsRow}>
          <View style={styles.coordCol}>
            <AppInput
              label="Latitude *"
              value={latitude}
              onChangeText={(t) => {
                setLatitude(t);
                setErrors((prev) => ({ ...prev, latitude: null }));
              }}
              placeholder="30.9010"
              keyboardType="numeric"
              error={errors.latitude}
            />
          </View>
          <View style={styles.coordCol}>
            <AppInput
              label="Longitude *"
              value={longitude}
              onChangeText={(t) => {
                setLongitude(t);
                setErrors((prev) => ({ ...prev, longitude: null }));
              }}
              placeholder="75.8573"
              keyboardType="numeric"
              error={errors.longitude}
            />
          </View>
        </View>

        {/* Radius Setting */}
        <Text style={styles.sectionHeader}>GEOFENCE RADIUS (METERS)</Text>
        <View style={styles.radiusPresetsRow}>
          {radiusPresets.map((r) => {
            const isSelected = String(r) === radius;
            return (
              <TouchableOpacity
                key={r}
                style={[styles.presetBtn, isSelected && styles.presetBtnActive]}
                onPress={() => {
                  setRadius(String(r));
                  setErrors((prev) => ({ ...prev, radius: null }));
                }}
              >
                <Text style={[styles.presetText, isSelected && styles.presetTextActive]}>
                  {r}m
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <AppInput
          label="Custom Radius (Meters) *"
          value={radius}
          onChangeText={(t) => {
            setRadius(t);
            setErrors((prev) => ({ ...prev, radius: null }));
          }}
          placeholder="e.g. 100"
          keyboardType="numeric"
          error={errors.radius}
          helperText="Standard safe radius is 100m for residential properties, 200m for schools."
        />

        {/* Active Geofence Switch */}
        <TouchableOpacity
          style={styles.activeSwitchRow}
          onPress={() => setIsActive(!isActive)}
          activeOpacity={0.8}
        >
          <View style={[styles.switchBox, isActive && styles.switchBoxActive]}>
            {isActive && <Text style={styles.checkmark}>✓</Text>}
          </View>
          <View style={styles.switchTextCol}>
            <Text style={styles.switchTitle}>Enable Active Boundary Monitoring</Text>
            <Text style={styles.switchSub}>
              Trigger instant notifications whenever child enters or exits this perimeter.
            </Text>
          </View>
        </TouchableOpacity>

        {errors.form && <Text style={styles.formError}>{errors.form}</Text>}

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <AppButton
            title="Cancel"
            onPress={() => navigation.goBack()}
            variant="secondary"
            size="lg"
            style={styles.cancelBtn}
          />
          <AppButton
            title={editingZone ? 'Update Zone' : 'Save Safe Zone'}
            onPress={handleSave}
            variant="primary"
            size="lg"
            loading={loading}
            style={styles.saveBtn}
          />
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
  sectionHeader: {
    fontSize: 11,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 8,
    marginTop: 12,
  },
  typeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 12,
  },
  typeCard: {
    flex: 1,
    minWidth: '28%',
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 12,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    alignItems: 'center',
  },
  typeIcon: {
    fontSize: 22,
    marginBottom: 4,
  },
  typeLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#475569',
    textAlign: 'center',
  },
  iconPickerRow: {
    flexDirection: 'row',
    marginBottom: 14,
  },
  iconOption: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  iconOptionSelected: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  iconOptionText: {
    fontSize: 20,
  },
  coordsHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 6,
  },
  useCurrentBtn: {
    paddingVertical: 2,
  },
  useCurrentText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#2563EB',
  },
  coordsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  coordCol: {
    flex: 1,
  },
  radiusPresetsRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  presetBtn: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    paddingVertical: 8,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  presetBtnActive: {
    backgroundColor: '#2563EB',
    borderColor: '#2563EB',
  },
  presetText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
  presetTextActive: {
    color: '#FFFFFF',
    fontWeight: '800',
  },
  activeSwitchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 14,
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    marginVertical: 14,
  },
  switchBox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    backgroundColor: '#FFFFFF',
  },
  switchBoxActive: {
    backgroundColor: '#059669',
    borderColor: '#059669',
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '900',
  },
  switchTextCol: {
    flex: 1,
  },
  switchTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  switchSub: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  formError: {
    color: '#DC2626',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 10,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 10,
  },
  cancelBtn: {
    flex: 1,
  },
  saveBtn: {
    flex: 1.5,
  },
});
