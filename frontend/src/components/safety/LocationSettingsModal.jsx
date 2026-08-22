import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  TextInput,
  Switch,
  Alert,
} from 'react-native';

export default function LocationSettingsModal({
  visible,
  onClose,
  isLocationSharingOn,
  updateFrequency = 15,
  accuracyMode = 'HIGH',
  activeMode = 'SIMULATION',
  onToggleSharing,
  onChangeFrequency,
  onChangeAccuracyMode,
  onChangeActiveMode,
  onAddSafeZone,
}) {
  const [activeTab, setActiveTab] = useState('PREFERENCES'); // 'PREFERENCES' or 'ADD_ZONE'

  const [zoneName, setZoneName] = useState('');
  const [zoneAddress, setZoneAddress] = useState('');
  const [zoneCategory, setZoneCategory] = useState('Home');
  const [zoneRadius, setZoneRadius] = useState(150);
  const [zoneColor, setZoneColor] = useState('#10B981');
  const [zoneIcon, setZoneIcon] = useState('🏠');
  const [zoneNotifyEntry, setZoneNotifyEntry] = useState(true);
  const [zoneNotifyExit, setZoneNotifyExit] = useState(true);
  const [submittingZone, setSubmittingZone] = useState(false);

  const frequencyOptions = [
    { value: 5, label: 'Real-Time (5s)', desc: 'High battery usage, fastest updates' },
    { value: 15, label: 'Standard (15s)', desc: 'Recommended balance' },
    { value: 30, label: 'Balanced (30s)', desc: 'Optimized for all-day tracking' },
    { value: 60, label: 'Eco (1m)', desc: 'Low battery consumption' },
    { value: 120, label: 'Battery Saver (2m)', desc: 'Minimum power mode' },
  ];

  const accuracyOptions = [
    { value: 'HIGH', label: 'High Precision (GNSS + WiFi + Cellular)', icon: '🎯' },
    { value: 'BALANCED', label: 'Balanced (Cellular + WiFi)', icon: '⚖️' },
    { value: 'BATTERY_SAVER', label: 'Battery Saver (Cellular Only)', icon: '🔋' },
  ];

  const iconOptions = ['🏠', '🏫', '🧩', '🌳', '👵', '🏥', '⚽', '🎨'];
  const colorOptions = ['#10B981', '#2563EB', '#8B5CF6', '#F59E0B', '#EC4899', '#06B6D4'];

  const handleSaveZone = async () => {
    if (!zoneName.trim()) {
      Alert.alert('Zone Name Required', 'Please enter a name for the safe zone.');
      return;
    }
    if (!zoneAddress.trim()) {
      Alert.alert('Address Required', 'Please enter a street address or location name.');
      return;
    }

    setSubmittingZone(true);
    try {
      if (onAddSafeZone) {
        await onAddSafeZone({
          name: zoneName.trim(),
          address: zoneAddress.trim(),
          category: zoneCategory,
          radius: Number(zoneRadius) || 150,
          color: zoneColor,
          icon: zoneIcon,
          notifyOnEntry: zoneNotifyEntry,
          notifyOnExit: zoneNotifyExit,
          latitude: 37.7749 + (Math.random() - 0.5) * 0.01,
          longitude: -122.4194 + (Math.random() - 0.5) * 0.01,
        });
      }
      setZoneName('');
      setZoneAddress('');
      setActiveTab('PREFERENCES');
      Alert.alert('Success', 'Safe Zone created successfully.');
    } finally {
      setSubmittingZone(false);
    }
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.modalBackdrop}>
        <View style={styles.modalCard}>
          {/* Header */}
          <View style={styles.modalHeader}>
            <View style={styles.titleRow}>
              <View style={styles.headerIconCircle}>
                <Text style={styles.headerIcon}>⚙️</Text>
              </View>
              <Text style={styles.modalTitle}>Location & GPS Settings</Text>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Text style={styles.closeBtnText}>✕</Text>
            </TouchableOpacity>
          </View>

          {/* Tab Switcher */}
          <View style={styles.tabsRow}>
            <TouchableOpacity
              style={[styles.tabBtn, activeTab === 'PREFERENCES' && styles.tabBtnActive]}
              onPress={() => setActiveTab('PREFERENCES')}
            >
              <Text
                style={[
                  styles.tabText,
                  activeTab === 'PREFERENCES' && styles.tabTextActive,
                ]}
              >
                Tracking Preferences
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.tabBtn, activeTab === 'ADD_ZONE' && styles.tabBtnActive]}
              onPress={() => setActiveTab('ADD_ZONE')}
            >
              <Text
                style={[
                  styles.tabText,
                  activeTab === 'ADD_ZONE' && styles.tabTextActive,
                ]}
              >
                ＋ Add Safe Zone
              </Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.scrollBody} showsVerticalScrollIndicator={false}>
            {activeTab === 'PREFERENCES' ? (
              <View style={styles.tabContent}>
                {/* 1. Location Sharing Master Switch */}
                <View style={styles.settingCard}>
                  <View style={styles.settingHeader}>
                    <View style={styles.settingInfo}>
                      <Text style={styles.settingTitle}>Broadcast Live Location</Text>
                      <Text style={styles.settingDesc}>
                        Share child real-time GPS stream with authorized caregivers.
                      </Text>
                    </View>
                    <Switch
                      value={isLocationSharingOn}
                      onValueChange={onToggleSharing}
                      trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
                      thumbColor={isLocationSharingOn ? '#2563EB' : '#94A3B8'}
                    />
                  </View>
                </View>

                {/* 2. GPS Engine Mode */}
                <View style={styles.settingCard}>
                  <Text style={styles.settingTitle}>GPS Provider Engine</Text>
                  <Text style={styles.settingDesc}>
                    Choose between live browser device GPS or realistic simulation for testing.
                  </Text>
                  <View style={styles.providerRow}>
                    <TouchableOpacity
                      style={[
                        styles.providerBtn,
                        activeMode === 'SIMULATION' && styles.providerBtnActive,
                      ]}
                      onPress={() => onChangeActiveMode && onChangeActiveMode('SIMULATION')}
                    >
                      <Text style={styles.providerIcon}>🤖</Text>
                      <Text
                        style={[
                          styles.providerLabel,
                          activeMode === 'SIMULATION' && styles.providerLabelActive,
                        ]}
                      >
                        Simulation (Demo)
                      </Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={[
                        styles.providerBtn,
                        activeMode === 'REAL_GPS' && styles.providerBtnActive,
                      ]}
                      onPress={() => onChangeActiveMode && onChangeActiveMode('REAL_GPS')}
                    >
                      <Text style={styles.providerIcon}>🛰️</Text>
                      <Text
                        style={[
                          styles.providerLabel,
                          activeMode === 'REAL_GPS' && styles.providerLabelActive,
                        ]}
                      >
                        Browser Geolocation
                      </Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* 3. Update Frequency Selector */}
                <View style={styles.settingCard}>
                  <Text style={styles.settingTitle}>Location Update Frequency</Text>
                  <Text style={styles.settingDesc}>
                    Controls how frequently the wearable broadcasts location fixes.
                  </Text>
                  <View style={styles.optionsList}>
                    {frequencyOptions.map((opt) => {
                      const isSelected = updateFrequency === opt.value;
                      return (
                        <TouchableOpacity
                          key={opt.value}
                          style={[
                            styles.optionItem,
                            isSelected && styles.optionItemActive,
                          ]}
                          onPress={() => onChangeFrequency && onChangeFrequency(opt.value)}
                        >
                          <View
                            style={[
                              styles.radioDotOuter,
                              isSelected && styles.radioDotOuterActive,
                            ]}
                          >
                            {isSelected && <View style={styles.radioDotInner} />}
                          </View>
                          <View style={styles.optionTextCol}>
                            <Text
                              style={[
                                styles.optionLabel,
                                isSelected && styles.optionLabelActive,
                              ]}
                            >
                              {opt.label}
                            </Text>
                            <Text style={styles.optionDesc}>{opt.desc}</Text>
                          </View>
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                </View>

                {/* 4. Accuracy Mode */}
                <View style={styles.settingCard}>
                  <Text style={styles.settingTitle}>Precision & Power Profile</Text>
                  <View style={styles.optionsList}>
                    {accuracyOptions.map((opt) => {
                      const isSelected = accuracyMode === opt.value;
                      return (
                        <TouchableOpacity
                          key={opt.value}
                          style={[
                            styles.optionItem,
                            isSelected && styles.optionItemActive,
                          ]}
                          onPress={() => onChangeAccuracyMode && onChangeAccuracyMode(opt.value)}
                        >
                          <Text style={styles.optIcon}>{opt.icon}</Text>
                          <Text
                            style={[
                              styles.optionLabel,
                              isSelected && styles.optionLabelActive,
                            ]}
                          >
                            {opt.label}
                          </Text>
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                </View>
              </View>
            ) : (
              /* Add Safe Zone Form */
              <View style={styles.tabContent}>
                <View style={styles.formGroup}>
                  <Text style={styles.formLabel}>Zone Name *</Text>
                  <TextInput
                    style={styles.formInput}
                    placeholder="e.g. Grandma's House, Karate Club"
                    placeholderTextColor="#94A3B8"
                    value={zoneName}
                    onChangeText={setZoneName}
                  />
                </View>

                <View style={styles.formGroup}>
                  <Text style={styles.formLabel}>Street Address / Location *</Text>
                  <TextInput
                    style={styles.formInput}
                    placeholder="e.g. 500 Park Avenue, Springfield"
                    placeholderTextColor="#94A3B8"
                    value={zoneAddress}
                    onChangeText={setZoneAddress}
                  />
                </View>

                <View style={styles.formGroup}>
                  <Text style={styles.formLabel}>Radius: {zoneRadius} meters</Text>
                  <View style={styles.radiusPillsRow}>
                    {[100, 150, 200, 300, 500].map((rad) => (
                      <TouchableOpacity
                        key={rad}
                        style={[
                          styles.radiusPill,
                          zoneRadius === rad && styles.radiusPillActive,
                        ]}
                        onPress={() => setZoneRadius(rad)}
                      >
                        <Text
                          style={[
                            styles.radiusPillText,
                            zoneRadius === rad && styles.radiusPillTextActive,
                          ]}
                        >
                          {rad}m
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>

                <View style={styles.formGroup}>
                  <Text style={styles.formLabel}>Icon & Theme Color</Text>
                  <View style={styles.iconsRow}>
                    {iconOptions.map((ic) => (
                      <TouchableOpacity
                        key={ic}
                        style={[
                          styles.iconSelectBtn,
                          zoneIcon === ic && styles.iconSelectBtnActive,
                        ]}
                        onPress={() => setZoneIcon(ic)}
                      >
                        <Text style={styles.pickerIcon}>{ic}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>

                  <View style={styles.colorsRow}>
                    {colorOptions.map((c) => (
                      <TouchableOpacity
                        key={c}
                        style={[
                          styles.colorCircle,
                          { backgroundColor: c },
                          zoneColor === c && styles.colorCircleActive,
                        ]}
                        onPress={() => setZoneColor(c)}
                      />
                    ))}
                  </View>
                </View>

                <View style={styles.settingCard}>
                  <View style={styles.switchRow}>
                    <Text style={styles.switchLabel}>Notify on Safe-Zone Entry</Text>
                    <Switch
                      value={zoneNotifyEntry}
                      onValueChange={setZoneNotifyEntry}
                      trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
                      thumbColor={zoneNotifyEntry ? '#2563EB' : '#94A3B8'}
                    />
                  </View>
                  <View style={[styles.switchRow, { marginTop: 10 }]}>
                    <Text style={styles.switchLabel}>Notify on Safe-Zone Exit</Text>
                    <Switch
                      value={zoneNotifyExit}
                      onValueChange={setZoneNotifyExit}
                      trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
                      thumbColor={zoneNotifyExit ? '#2563EB' : '#94A3B8'}
                    />
                  </View>
                </View>

                <TouchableOpacity
                  style={[styles.submitZoneBtn, submittingZone && { opacity: 0.6 }]}
                  onPress={handleSaveZone}
                  disabled={submittingZone}
                >
                  <Text style={styles.submitZoneBtnText}>
                    {submittingZone ? 'Creating...' : '💾 Save Safe Zone'}
                  </Text>
                </TouchableOpacity>
              </View>
            )}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.45)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  modalCard: {
    width: '100%',
    maxWidth: 600,
    maxHeight: '90%',
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 24,
    elevation: 8,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerIconCircle: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  headerIcon: {
    fontSize: 18,
  },
  modalTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#0F172A',
  },
  closeBtn: {
    padding: 6,
  },
  closeBtnText: {
    fontSize: 16,
    color: '#64748B',
    fontWeight: '700',
  },
  tabsRow: {
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
  },
  tabBtn: {
    flex: 1,
    paddingVertical: 14,
    alignItems: 'center',
  },
  tabBtnActive: {
    borderBottomWidth: 2,
    borderBottomColor: '#2563EB',
    backgroundColor: '#FFFFFF',
  },
  tabText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#64748B',
  },
  tabTextActive: {
    color: '#2563EB',
    fontWeight: '800',
  },
  scrollBody: {
    padding: 20,
  },
  tabContent: {
    gap: 16,
    paddingBottom: 24,
  },
  settingCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  settingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flex: 1,
    marginRight: 12,
  },
  settingTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  settingDesc: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 17,
    marginBottom: 10,
    fontWeight: '500',
  },
  providerRow: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 6,
  },
  providerBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    gap: 8,
  },
  providerBtnActive: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  providerIcon: {
    fontSize: 16,
  },
  providerLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#475569',
    flex: 1,
  },
  providerLabelActive: {
    color: '#2563EB',
  },
  optionsList: {
    gap: 8,
  },
  optionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  optionItemActive: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  radioDotOuter: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  radioDotOuterActive: {
    borderColor: '#2563EB',
  },
  radioDotInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#2563EB',
  },
  optionTextCol: {
    flex: 1,
  },
  optionLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  optionLabelActive: {
    color: '#2563EB',
  },
  optionDesc: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '500',
  },
  optIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  formGroup: {
    gap: 6,
  },
  formLabel: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  formInput: {
    backgroundColor: '#F8FAFC',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 12,
    color: '#0F172A',
    fontSize: 13,
    fontWeight: '500',
  },
  radiusPillsRow: {
    flexDirection: 'row',
    gap: 8,
  },
  radiusPill: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  radiusPillActive: {
    backgroundColor: '#2563EB',
    borderColor: '#1D4ED8',
  },
  radiusPillText: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '700',
  },
  radiusPillTextActive: {
    color: '#FFFFFF',
  },
  iconsRow: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  iconSelectBtn: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  iconSelectBtnActive: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  pickerIcon: {
    fontSize: 18,
  },
  colorsRow: {
    flexDirection: 'row',
    gap: 10,
  },
  colorCircle: {
    width: 30,
    height: 30,
    borderRadius: 15,
  },
  colorCircleActive: {
    borderWidth: 3,
    borderColor: '#0F172A',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  switchLabel: {
    fontSize: 13,
    color: '#0F172A',
    fontWeight: '700',
  },
  submitZoneBtn: {
    backgroundColor: '#2563EB',
    paddingVertical: 14,
    borderRadius: 999,
    alignItems: 'center',
    marginTop: 10,
  },
  submitZoneBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '800',
  },
});
