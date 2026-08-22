import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Platform,
  SafeAreaView,
  Alert,
  Modal,
  Animated,
} from 'react-native';

import { locationService } from '../../services/location/locationService';
import { bluetoothService } from '../../services/bluetooth/bluetoothService';
import { playSeparationAlarmSound, playBuzzerSound } from '../../utils/soundEffects';
import LocationSettingsModal from '../../components/safety/LocationSettingsModal';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const isDesktop = Platform.OS === 'web' ? SCREEN_WIDTH >= 1024 : SCREEN_WIDTH >= 768;

export default function LiveLocationScreen({ navigation }) {
  const [locationState, setLocationState] = useState(null);
  const [bleState, setBleState] = useState(null);
  const [activeNav, setActiveNav] = useState('LIVE_LOCATION');
  const [secondsAgo, setSecondsAgo] = useState(10);
  const [mapZoom, setMapZoom] = useState(1.0);
  const [toastMessage, setToastMessage] = useState(null);
  const [sosModalVisible, setSosModalVisible] = useState(false);
  const [sosCountdown, setSosCountdown] = useState(5);
  const [settingsModalVisible, setSettingsModalVisible] = useState(false);

  // Pulse animation for live marker
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.25,
          duration: 1100,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1.0,
          duration: 1100,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  useEffect(() => {
    const unsubLoc = locationService.subscribe((state) => setLocationState(state));
    const unsubBle = bluetoothService.subscribe((state) => setBleState(state));
    return () => {
      unsubLoc();
      unsubBle();
    };
  }, []);

  // Update ticker
  useEffect(() => {
    const interval = setInterval(() => {
      setSecondsAgo((s) => (s >= 59 ? 5 : s + 1));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleRefreshFix = async () => {
    await locationService.locateNow();
    setSecondsAgo(0);
    showToast('Satellite fix refreshed');
  };

  const handleOpenSOS = () => {
    setSosCountdown(5);
    setSosModalVisible(true);
    playSeparationAlarmSound();
  };

  useEffect(() => {
    let timer;
    if (sosModalVisible && sosCountdown > 0) {
      timer = setTimeout(() => setSosCountdown((c) => c - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [sosModalVisible, sosCountdown]);

  const handleCancelSOS = () => {
    setSosModalVisible(false);
    showToast('SOS cancelled.');
  };

  const handleConfirmSOS = () => {
    setSosModalVisible(false);
    locationService.addAlert({
      id: `sos-${Date.now()}`,
      type: 'SOS_ALERT',
      title: '🚨 EMERGENCY SOS ACTIVE',
      message: `Distress alert broadcast from Model Town, Ludhiana.`,
      timestamp: new Date(),
    });
    showToast('🚨 Emergency alert sent to all emergency contacts!');
  };

  const child = {
    name: 'Alex',
    battery: locationState?.childLocation?.battery || 82,
    locationName: 'Model Town',
    city: 'Ludhiana',
    accuracy: '±8 meters',
    safeZoneName: 'Home (Model Town)',
  };

  const navItems = [
    { id: 'HOME', label: 'NIVARA Home', icon: '🏠' },
    { id: 'COMMUNITY', label: 'Community Portal', icon: '👥' },
    { id: 'LIVE_LOCATION', label: 'Live Location GPS', icon: '📍' },
    { id: 'SAFE_ZONES', label: 'Safe Zones', icon: '🛡️' },
    { id: 'WEARABLE', label: 'GPS Smartband', icon: '⌚' },
    { id: 'EMERGENCY_CONTACTS', label: 'Emergency Contacts', icon: '📞' },
    { id: 'DASHBOARD', label: 'Safety Overview', icon: '⊞' },
  ];

  const bottomNavItems = [
    { id: 'SETTINGS', label: 'Settings', icon: '⚙️' },
    { id: 'SUPPORT', label: 'Support', icon: '❓' },
  ];

  const handleNavClick = (itemId) => {
    if (itemId === 'HOME') {
      navigation.navigate('Home');
    } else if (itemId === 'COMMUNITY') {
      navigation.navigate('CommunityTab');
    } else if (itemId === 'LIVE_LOCATION') {
      setActiveNav('LIVE_LOCATION');
    } else if (itemId === 'SAFE_ZONES') {
      navigation.navigate('SafeZones');
    } else if (itemId === 'WEARABLE') {
      navigation.navigate('GPSBand');
    } else if (itemId === 'EMERGENCY_CONTACTS') {
      navigation.navigate('EmergencyContacts');
    } else {
      navigation.navigate('CaregiverDashboard');
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.mainLayout}>
        {/* ======================================================== */}
        {/* 1. LEFT SIDEBAR NAVIGATION                               */}
        {/* ======================================================== */}
        <View style={styles.sidebar}>
          {/* Logo */}
          <View style={styles.logoRow}>
            <View style={styles.shieldLogo}>
              <Text style={styles.shieldIcon}>🛡️</Text>
            </View>
            <View style={styles.logoTitleCol}>
              <Text style={styles.brandTitle}>Nivara</Text>
              <Text style={styles.brandSubtitle}>Caregiver Dashboard</Text>
            </View>
          </View>

          {/* Solid Red SOS Emergency Button */}
          <TouchableOpacity
            style={styles.sosSidebarBtnSolid}
            onPress={handleOpenSOS}
            activeOpacity={0.85}
          >
            <Text style={styles.sosAsteriskSolid}>✱</Text>
            <Text style={styles.sosBtnTextSolid}>SOS Emergency</Text>
          </TouchableOpacity>

          {/* Navigation Menu */}
          <ScrollView style={styles.navMenu} showsVerticalScrollIndicator={false}>
            {navItems.map((item) => {
              const isActive = item.id === 'LIVE_LOCATION';
              return (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.navItem, isActive && styles.navItemActive]}
                  onPress={() => handleNavClick(item.id)}
                  activeOpacity={0.75}
                >
                  <Text style={[styles.navIcon, isActive && styles.navIconActive]}>
                    {item.icon}
                  </Text>
                  <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>
                    {item.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          {/* Bottom Sidebar Links */}
          <View style={styles.sidebarBottom}>
            {bottomNavItems.map((item) => (
              <TouchableOpacity
                key={item.id}
                style={styles.navItem}
                onPress={() => {
                  if (item.id === 'SETTINGS') setSettingsModalVisible(true);
                  else showToast('Support Center');
                }}
                activeOpacity={0.75}
              >
                <Text style={styles.navIcon}>{item.icon}</Text>
                <Text style={styles.navLabel}>{item.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* ======================================================== */}
        {/* 2. MAIN CONTENT VIEWPORT (LIVE LOCATION FULL MAP)       */}
        {/* ======================================================== */}
        <View style={styles.contentViewport}>
          {/* Top Header Bar */}
          <View style={styles.topHeader}>
            <View style={styles.headerLeftCol}>
              <TouchableOpacity
                style={styles.backHomeBtn}
                onPress={() => navigation.navigate('Home')}
                activeOpacity={0.85}
              >
                <Text style={styles.backHomeBtnText}>← 🏠 Home</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.communityJumpBtn}
                onPress={() => navigation.navigate('CommunityTab')}
                activeOpacity={0.85}
              >
                <Text style={styles.communityJumpBtnText}>👥 Community</Text>
              </TouchableOpacity>
            </View>

            {/* Center: Live Tracking Red Pulsing Pill */}
            <View style={styles.liveTrackingPill}>
              <View style={styles.liveRedDot} />
              <Text style={styles.liveTrackingText}>LIVE TRACKING</Text>
            </View>

            {/* Right Action Icons & Profile */}
            <View style={styles.headerRightActions}>
              <TouchableOpacity style={styles.iconBtn} onPress={() => showToast('No unread notifications')}>
                <Text style={styles.actionIcon}>🔔</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.iconBtn} onPress={() => showToast('Caregiver Help Center')}>
                <Text style={styles.actionIcon}>❓</Text>
              </TouchableOpacity>

              {/* Profile Avatar */}
              <View style={styles.profileAvatarWrapper}>
                <View style={styles.profileAvatar}>
                  <Text style={styles.profileAvatarEmoji}>👩‍⚕️</Text>
                </View>
                <View style={styles.onlineBadgeDot} />
              </View>
            </View>
          </View>

          {/* Toast Notification */}
          {toastMessage && (
            <View style={styles.toastBanner}>
              <Text style={styles.toastText}>{toastMessage}</Text>
            </View>
          )}

          {/* Full Interactive Live Vector Map Canvas */}
          <View style={styles.liveMapContainer}>
            <View style={styles.fullVectorMap}>
              {/* Highways & Arteries */}
              <View style={styles.highwayYellow44} />
              <View style={styles.highwayYellow5} />
              <View style={styles.highwayDiagonal} />
              <View style={styles.streetLine1} />
              <View style={styles.streetLine2} />
              <View style={styles.streetLine3} />
              <View style={styles.streetLine4} />

              {/* Highway Badges */}
              <View style={[styles.highwayBadge, { top: '19%', left: '45%' }]}>
                <Text style={styles.highwayBadgeText}>44</Text>
              </View>
              <View style={[styles.highwayBadge, { top: '34%', left: '58%' }]}>
                <Text style={styles.highwayBadgeText}>44</Text>
              </View>
              <View style={[styles.highwayBadge, { top: '61%', left: '50%' }]}>
                <Text style={styles.highwayBadgeText}>5</Text>
              </View>
              <View style={[styles.highwayBadge, { bottom: '6%', right: '23%' }]}>
                <Text style={styles.highwayBadgeText}>5</Text>
              </View>
              <View style={[styles.highwayBadge, { bottom: '15%', left: '62%' }]}>
                <Text style={styles.highwayBadgeText}>11</Text>
              </View>
              <View style={[styles.highwayBadgeGreen, { top: '42%', left: '40%' }]}>
                <Text style={styles.highwayBadgeGreenText}>20</Text>
              </View>

              {/* City & Area Labels */}
              <Text style={styles.cityLudhianaText}>Ludhiana</Text>
              <Text style={styles.cityLudhianaPunjabi}>ਲੁਧਿਆਣਾ</Text>
              <Text style={[styles.areaLabel, { top: '31%', left: '42%' }]}>HAIBOWAL KALAN</Text>
              <Text style={[styles.areaLabel, { top: '42%', left: '46%' }]}>CIVIL LINES</Text>
              <Text style={[styles.areaLabel, { top: '37%', left: '57%' }]}>SUNDER NAGAR</Text>
              <Text style={[styles.areaLabel, { top: '56%', left: '36%' }]}>BHAI RANDHIR SINGH NAGAR</Text>
              <Text style={[styles.areaLabel, { bottom: '26%', left: '54%' }]}>DUGGRI</Text>
              <Text style={[styles.areaLabel, { bottom: '30%', right: '30%' }]}>SHIMLAPURI</Text>
              <Text style={[styles.areaLabel, { bottom: '28%', right: '14%' }]}>DHANDARI KALAN</Text>
              <Text style={[styles.areaLabel, { bottom: '28%', right: '2%' }]}>GOBINDGARH</Text>
              <Text style={[styles.areaLabel, { bottom: '12%', left: '30%' }]}>Lalton Kalan</Text>
              <Text style={[styles.areaLabel, { bottom: '8%', left: '60%' }]}>Gill</Text>

              {/* Points of Interest */}
              <View style={[styles.poiBadge, { top: '10%', left: '28%' }]}>
                <Text style={styles.poiPurpleIcon}>🎡</Text>
                <Text style={styles.poiPurpleText}>Hardy's World</Text>
              </View>

              <View style={[styles.poiBadge, { top: '57%', left: '23%' }]}>
                <Text style={styles.poiBlueIcon}>🛍️</Text>
                <Text style={styles.poiBlueText}>Nexus MBD Neopolis Mall</Text>
              </View>

              <View style={[styles.poiBadge, { bottom: '20%', right: '16%' }]}>
                <Text style={styles.poiPurpleIcon}>🌊</Text>
                <Text style={styles.poiPurpleText}>Water Dreams</Text>
              </View>

              <View style={[styles.poiHospital, { top: '44%', left: '62%' }]}>
                <Text style={styles.poiHospitalText}>H</Text>
              </View>

              {/* Safe Zone Geofence Circle around Alex */}
              <View style={styles.alexGeofenceCircle} />

              {/* Alex Live Position Pin Marker */}
              <View style={styles.alexMarkerContainer}>
                <View style={styles.alexMarkerAvatarRing}>
                  <Text style={styles.alexAvatarFace}>👦</Text>
                  <View style={styles.alexLiveStatusDot} />
                </View>
                <View style={styles.alexNamePill}>
                  <Text style={styles.alexNamePillText}>Alex</Text>
                </View>
              </View>

              {/* Top-Left Floating Controls (+ / - / Center / Refresh) */}
              <View style={styles.topLeftMapControls}>
                <TouchableOpacity
                  style={styles.mapControlBtn}
                  onPress={() => setMapZoom((z) => Math.min(2.2, z + 0.25))}
                >
                  <Text style={styles.mapBtnSymbol}>＋</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.mapControlBtn}
                  onPress={() => setMapZoom((z) => Math.max(0.5, z - 0.25))}
                >
                  <Text style={styles.mapBtnSymbol}>－</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.mapControlBtn}
                  onPress={() => {
                    setMapZoom(1.0);
                    showToast('Map centered on Alex');
                  }}
                >
                  <Text style={styles.mapBtnIcon}>🎯</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.mapControlBtn}
                  onPress={handleRefreshFix}
                >
                  <Text style={styles.mapBtnIcon}>🔄</Text>
                </TouchableOpacity>
              </View>

              {/* Top-Right Floating Status Card & Safe Zone Card */}
              <View style={styles.topRightCardStack}>
                {/* Main Status Overview Card */}
                <View style={styles.liveLocationCard}>
                  {/* Header Row */}
                  <View style={styles.cardHeaderRow}>
                    <View style={styles.cardHeaderLeft}>
                      <Text style={styles.checkCircleGreen}>✓</Text>
                      <Text style={styles.currentlyHereTitle}>Alex is currently here</Text>
                    </View>
                    <View style={styles.batteryPill}>
                      <Text style={styles.batteryPillIcon}>🔋</Text>
                      <Text style={styles.batteryPillText}>{child.battery}%</Text>
                    </View>
                  </View>

                  {/* Updated Timestamp Subtitle */}
                  <View style={styles.updatedRow}>
                    <Text style={styles.updatedClockIcon}>🕒</Text>
                    <Text style={styles.updatedText}>
                      Updated {secondsAgo === 0 ? 'just now' : `${secondsAgo} seconds ago`}
                    </Text>
                  </View>

                  {/* Divider */}
                  <View style={styles.cardInternalDivider} />

                  {/* 2-Column Telemetry Metrics Grid */}
                  <View style={styles.telemetryGrid}>
                    <View style={styles.telemetryCol}>
                      <Text style={styles.telemetryLabel}>Current Location</Text>
                      <View style={styles.telemetryValRow}>
                        <Text style={styles.pinBlueIcon}>📍</Text>
                        <Text style={styles.telemetryValAddress}>
                          {child.locationName},{'\n'}{child.city}
                        </Text>
                      </View>
                    </View>

                    <View style={styles.telemetryCol}>
                      <Text style={styles.telemetryLabel}>GPS Accuracy</Text>
                      <View style={styles.telemetryValRow}>
                        <Text style={styles.radarBlueIcon}>🎯</Text>
                        <Text style={styles.telemetryValAccuracy}>{child.accuracy}</Text>
                      </View>
                    </View>
                  </View>

                  {/* Bottom Action: View Route History */}
                  <View style={styles.cardFooterDivider} />
                  <View style={styles.cardFooterRow}>
                    <TouchableOpacity
                      style={styles.viewRouteBtn}
                      onPress={() => showToast('Opening Route History...')}
                    >
                      <Text style={styles.routeHistoryIcon}>⮂</Text>
                      <Text style={styles.viewRouteText}>View Route History</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.moreOptionsBtn}
                      onPress={() => setSettingsModalVisible(true)}
                    >
                      <Text style={styles.moreOptionsText}>⋮</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Secondary Banner: Inside Safe Zone */}
                <View style={styles.insideSafeZoneCard}>
                  <View style={styles.safeZoneHomeIconBox}>
                    <Text style={styles.safeZoneHomeEmoji}>🏠</Text>
                  </View>
                  <View style={styles.safeZoneTextCol}>
                    <Text style={styles.insideSafeZoneTitle}>Inside Safe Zone</Text>
                    <Text style={styles.insideSafeZoneSub}>{child.safeZoneName}</Text>
                  </View>
                </View>
              </View>
            </View>
          </View>
        </View>
      </View>

      {/* SOS Emergency Modal */}
      <Modal visible={sosModalVisible} transparent animationType="fade">
        <View style={styles.modalBackdrop}>
          <View style={styles.sosModalCard}>
            <View style={styles.sosSirenCircle}>
              <Text style={styles.sosModalIcon}>🚨</Text>
            </View>
            <Text style={styles.sosModalTitle}>EMERGENCY SOS</Text>
            <Text style={styles.sosModalSubtitle}>
              Broadcasting high-priority distress signal and live GPS coordinates to emergency contacts.
            </Text>
            <View style={styles.countdownBox}>
              <Text style={styles.countdownNum}>{sosCountdown}</Text>
              <Text style={styles.countdownSub}>Auto-activating in seconds</Text>
            </View>
            <View style={styles.sosModalActions}>
              <TouchableOpacity
                style={styles.sosConfirmBtn}
                onPress={handleConfirmSOS}
                activeOpacity={0.85}
              >
                <Text style={styles.sosConfirmText}>🚨 SEND SOS NOW</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.sosCancelBtn}
                onPress={handleCancelSOS}
                activeOpacity={0.85}
              >
                <Text style={styles.sosCancelText}>Cancel Emergency</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Location Settings Modal */}
      <LocationSettingsModal
        visible={settingsModalVisible}
        onClose={() => setSettingsModalVisible(false)}
        isLocationSharingOn={locationState?.isLocationSharingOn}
        updateFrequency={locationState?.updateFrequency}
        accuracyMode={locationState?.accuracyMode}
        activeMode={locationState?.activeMode}
        onToggleSharing={() =>
          locationService.setLocationSharing(!locationState?.isLocationSharingOn)
        }
        onChangeFrequency={(f) => locationService.setUpdateFrequency(f)}
        onChangeAccuracyMode={(m) => locationService.setAccuracyMode(m)}
        onChangeActiveMode={(m) => locationService.setMode(m)}
        onAddSafeZone={(z) => locationService.addSafeZone(z)}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  mainLayout: {
    flex: 1,
    flexDirection: 'row',
  },

  // SIDEBAR
  sidebar: {
    width: 230,
    backgroundColor: '#FFFFFF',
    borderRightWidth: 1,
    borderRightColor: '#EEF2F6',
    paddingVertical: 20,
    paddingHorizontal: 14,
    display: isDesktop ? 'flex' : 'none',
  },
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    paddingHorizontal: 6,
  },
  shieldLogo: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: '#1E40AF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  shieldIcon: {
    fontSize: 16,
  },
  logoTitleCol: {
    flex: 1,
  },
  brandTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  brandSubtitle: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '500',
  },
  sosSidebarBtnSolid: {
    backgroundColor: '#B91C1C',
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    marginBottom: 20,
    shadowColor: '#B91C1C',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 6,
  },
  sosAsteriskSolid: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '900',
    marginRight: 6,
  },
  sosBtnTextSolid: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
    letterSpacing: 0.2,
  },
  navMenu: {
    flex: 1,
  },
  navItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 10,
    marginBottom: 4,
  },
  navItemActive: {
    backgroundColor: '#E0E7FF',
  },
  navIcon: {
    fontSize: 16,
    color: '#64748B',
    marginRight: 12,
    width: 20,
    textAlign: 'center',
  },
  navIconActive: {
    color: '#1E40AF',
  },
  navLabel: {
    fontSize: 13,
    color: '#475569',
    fontWeight: '600',
  },
  navLabelActive: {
    color: '#1E40AF',
    fontWeight: '800',
  },
  sidebarBottom: {
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 12,
  },

  // TOP HEADER
  contentViewport: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    display: 'flex',
    flexDirection: 'column',
  },
  topHeader: {
    height: 64,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
  },
  headerLeftCol: {},
  headerLeftTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  liveTrackingPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEE2E2',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  liveRedDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#DC2626',
    marginRight: 6,
  },
  liveTrackingText: {
    color: '#B91C1C',
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 0.8,
  },
  headerRightActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  iconBtn: {
    padding: 6,
  },
  actionIcon: {
    fontSize: 16,
  },
  profileAvatarWrapper: {
    position: 'relative',
    marginLeft: 4,
  },
  profileAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileAvatarEmoji: {
    fontSize: 18,
  },
  onlineBadgeDot: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#10B981',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  toastBanner: {
    backgroundColor: '#2563EB',
    paddingVertical: 8,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  toastText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
  },

  // LIVE LOCATION MAP
  liveMapContainer: {
    flex: 1,
    position: 'relative',
    backgroundColor: '#E8EFE9',
    overflow: 'hidden',
  },
  fullVectorMap: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#E6ECE5',
  },
  highwayYellow44: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: '48%',
    width: 22,
    backgroundColor: '#FEF08A',
    borderLeftWidth: 1.5,
    borderRightWidth: 1.5,
    borderColor: '#FACC15',
    transform: [{ rotate: '12deg' }],
  },
  highwayYellow5: {
    position: 'absolute',
    top: '30%',
    bottom: 0,
    left: '52%',
    width: 18,
    backgroundColor: '#FEF08A',
    borderLeftWidth: 1.5,
    borderRightWidth: 1.5,
    borderColor: '#FACC15',
    transform: [{ rotate: '-18deg' }],
  },
  highwayDiagonal: {
    position: 'absolute',
    top: '35%',
    bottom: 0,
    left: '25%',
    width: 16,
    backgroundColor: '#FFFFFF',
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderColor: '#CBD5E1',
    transform: [{ rotate: '42deg' }],
  },
  streetLine1: {
    position: 'absolute',
    top: '25%',
    left: 0,
    right: 0,
    height: 12,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#CBD5E1',
  },
  streetLine2: {
    position: 'absolute',
    top: '52%',
    left: 0,
    right: 0,
    height: 14,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#CBD5E1',
  },
  streetLine3: {
    position: 'absolute',
    bottom: '22%',
    left: 0,
    right: 0,
    height: 12,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#CBD5E1',
  },
  streetLine4: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: '28%',
    width: 14,
    backgroundColor: '#FFFFFF',
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderColor: '#CBD5E1',
  },
  highwayBadge: {
    position: 'absolute',
    backgroundColor: '#FBBF24',
    paddingHorizontal: 5,
    paddingVertical: 2,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#D97706',
    zIndex: 10,
  },
  highwayBadgeText: {
    fontSize: 9,
    fontWeight: '900',
    color: '#000000',
  },
  highwayBadgeGreen: {
    position: 'absolute',
    backgroundColor: '#10B981',
    paddingHorizontal: 5,
    paddingVertical: 2,
    borderRadius: 4,
    zIndex: 10,
  },
  highwayBadgeGreenText: {
    fontSize: 8,
    fontWeight: '900',
    color: '#FFFFFF',
  },
  cityLudhianaText: {
    position: 'absolute',
    top: '46%',
    left: '52%',
    fontSize: 22,
    fontWeight: '900',
    color: '#1E293B',
    zIndex: 5,
    letterSpacing: -0.5,
  },
  cityLudhianaPunjabi: {
    position: 'absolute',
    top: '52%',
    left: '52%',
    fontSize: 16,
    fontWeight: '800',
    color: '#334155',
    zIndex: 5,
  },
  areaLabel: {
    position: 'absolute',
    fontSize: 9,
    fontWeight: '800',
    color: '#475569',
    letterSpacing: 0.5,
    zIndex: 5,
  },
  poiBadge: {
    position: 'absolute',
    flexDirection: 'row',
    alignItems: 'center',
    zIndex: 8,
  },
  poiPurpleIcon: {
    fontSize: 14,
    marginRight: 4,
  },
  poiPurpleText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#7C3AED',
  },
  poiBlueIcon: {
    fontSize: 14,
    marginRight: 4,
  },
  poiBlueText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#2563EB',
  },
  poiHospital: {
    position: 'absolute',
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#DC2626',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
    zIndex: 8,
  },
  poiHospitalText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '900',
  },
  alexGeofenceCircle: {
    position: 'absolute',
    top: '38%',
    left: '38%',
    width: 170,
    height: 170,
    borderRadius: 85,
    backgroundColor: 'rgba(37, 99, 235, 0.14)',
    borderWidth: 1.5,
    borderColor: 'rgba(37, 99, 235, 0.4)',
    zIndex: 15,
  },
  alexMarkerContainer: {
    position: 'absolute',
    top: '47%',
    left: '46%',
    alignItems: 'center',
    zIndex: 25,
  },
  alexMarkerAvatarRing: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    borderWidth: 3,
    borderColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 6,
  },
  alexAvatarFace: {
    fontSize: 22,
  },
  alexLiveStatusDot: {
    position: 'absolute',
    bottom: -1,
    right: -1,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#10B981',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  alexNamePill: {
    backgroundColor: '#0F172A',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    marginTop: 3,
  },
  alexNamePillText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '800',
  },
  topLeftMapControls: {
    position: 'absolute',
    top: 20,
    left: 20,
    gap: 8,
    zIndex: 30,
  },
  mapControlBtn: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#0F172A',
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
  },
  mapBtnSymbol: {
    fontSize: 18,
    fontWeight: '800',
    color: '#334155',
  },
  mapBtnIcon: {
    fontSize: 14,
  },
  topRightCardStack: {
    position: 'absolute',
    top: 20,
    right: 20,
    width: 340,
    gap: 12,
    zIndex: 30,
  },
  liveLocationCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 5,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  checkCircleGreen: {
    color: '#059669',
    fontSize: 16,
    fontWeight: '900',
    marginRight: 8,
  },
  currentlyHereTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  batteryPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  batteryPillIcon: {
    fontSize: 10,
    marginRight: 3,
  },
  batteryPillText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#1E40AF',
  },
  updatedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
  },
  updatedClockIcon: {
    fontSize: 11,
    marginRight: 4,
  },
  updatedText: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '500',
  },
  cardInternalDivider: {
    height: 1,
    backgroundColor: '#EEF2F6',
    marginVertical: 14,
  },
  telemetryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  telemetryCol: {
    flex: 1,
  },
  telemetryLabel: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
    marginBottom: 4,
  },
  telemetryValRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  pinBlueIcon: {
    fontSize: 13,
    marginRight: 4,
    marginTop: 1,
  },
  radarBlueIcon: {
    fontSize: 13,
    marginRight: 4,
    marginTop: 1,
  },
  telemetryValAddress: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
    lineHeight: 18,
  },
  telemetryValAccuracy: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
    lineHeight: 18,
  },
  cardFooterDivider: {
    height: 1,
    backgroundColor: '#EEF2F6',
    marginTop: 14,
    marginBottom: 10,
  },
  cardFooterRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  viewRouteBtn: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  routeHistoryIcon: {
    fontSize: 14,
    color: '#2563EB',
    fontWeight: '800',
    marginRight: 6,
  },
  viewRouteText: {
    fontSize: 13,
    color: '#2563EB',
    fontWeight: '800',
  },
  moreOptionsBtn: {
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  moreOptionsText: {
    fontSize: 16,
    fontWeight: '800',
    color: '#64748B',
  },
  insideSafeZoneCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 10,
    elevation: 4,
  },
  safeZoneHomeIconBox: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: '#ECFDF5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    borderWidth: 1,
    borderColor: '#A7F3D0',
  },
  safeZoneHomeEmoji: {
    fontSize: 18,
  },
  safeZoneTextCol: {
    flex: 1,
  },
  insideSafeZoneTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  insideSafeZoneSub: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
    fontWeight: '500',
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  sosModalCard: {
    width: '100%',
    maxWidth: 480,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#DC2626',
  },
  sosSirenCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#FEE2E2',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
  },
  sosModalIcon: {
    fontSize: 28,
  },
  sosModalTitle: {
    fontSize: 20,
    fontWeight: '900',
    color: '#991B1B',
    marginBottom: 6,
  },
  sosModalSubtitle: {
    fontSize: 13,
    color: '#475569',
    textAlign: 'center',
    lineHeight: 18,
    marginBottom: 16,
  },
  countdownBox: {
    backgroundColor: '#FEF2F2',
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 14,
    alignItems: 'center',
    marginBottom: 18,
  },
  countdownNum: {
    fontSize: 32,
    fontWeight: '900',
    color: '#DC2626',
  },
  countdownSub: {
    fontSize: 11,
    color: '#991B1B',
    fontWeight: '700',
  },
  sosModalActions: {
    width: '100%',
    gap: 10,
  },
  sosConfirmBtn: {
    backgroundColor: '#DC2626',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  sosConfirmText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '800',
  },
  sosCancelBtn: {
    backgroundColor: '#F1F5F9',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  sosCancelText: {
    color: '#475569',
    fontSize: 13,
    fontWeight: '700',
  },
  headerLeftCol: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  backHomeBtn: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  backHomeBtnText: {
    color: '#1E40AF',
    fontSize: 12,
    fontWeight: '800',
  },
  communityJumpBtn: {
    backgroundColor: '#F5F3FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#DDD6FE',
  },
  communityJumpBtnText: {
    color: '#6D28D9',
    fontSize: 12,
    fontWeight: '800',
  },
});
