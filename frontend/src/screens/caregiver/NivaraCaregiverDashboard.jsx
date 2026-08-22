import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
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

export default function NivaraCaregiverDashboard({ navigation }) {
  // Navigation tabs:
  // 'DASHBOARD' | 'LIVE_LOCATION' | 'HISTORY' | 'SAFE_ZONES' | 'WEARABLE' | 'SAFETY_EVENTS' | 'EMERGENCY_CONTACTS' | 'SETTINGS' | 'SUPPORT'
  const [activeNav, setActiveNav] = useState('DASHBOARD');
  const [locationState, setLocationState] = useState(null);
  const [bleState, setBleState] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sosModalVisible, setSosModalVisible] = useState(false);
  const [sosCountdown, setSosCountdown] = useState(5);
  const [settingsModalVisible, setSettingsModalVisible] = useState(false);
  const [addZoneModalVisible, setAddZoneModalVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [selectedZoneId, setSelectedZoneId] = useState('zone-home');
  const [mapZoom, setMapZoom] = useState(1.0);
  const [secondsAgo, setSecondsAgo] = useState(10);

  // Wearable Calibration States (Screenshot 4)
  const [distanceThreshold, setDistanceThreshold] = useState(20);
  const [alertDelay, setAlertDelay] = useState(30);
  const [isBuzzerActive, setIsBuzzerActive] = useState(false);
  const [isLostModeActive, setIsLostModeActive] = useState(false);

  // Safety Events States (Screenshot 5)
  const [eventCategoryFilter, setEventCategoryFilter] = useState('ALL'); // 'ALL', 'ALERTS', 'DEVICE_STATUS', 'GEOFENCES'
  const [isSosAcknowledged, setIsSosAcknowledged] = useState(false);

  // Add Zone Form State (Screenshot 2)
  const [newZoneName, setNewZoneName] = useState('');
  const [newZoneAddress, setNewZoneAddress] = useState('');
  const [newZoneRadius, setNewZoneRadius] = useState(100);
  const [newZoneIcon, setNewZoneIcon] = useState('🏠');

  useEffect(() => {
    const unsubLoc = locationService.subscribe((state) => setLocationState(state));
    const unsubBle = bluetoothService.subscribe((state) => setBleState(state));
    return () => {
      unsubLoc();
      unsubBle();
    };
  }, []);

  // Live seconds ticker
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
    setIsSosAcknowledged(false);
    locationService.addAlert({
      id: `sos-${Date.now()}`,
      type: 'SOS_ALERT',
      title: '🚨 SOS Activated (Critical)',
      message: `Device panic button triggered near Elm Street intersection.`,
      timestamp: new Date(),
    });
    showToast('🚨 SOS distress signal broadcast to all caregivers!');
  };

  const handleAcknowledgeSOS = () => {
    setIsSosAcknowledged(true);
    showToast('✓ SOS alert acknowledged. Protocol updated.');
  };

  const handleFindDevice = async () => {
    setIsBuzzerActive(true);
    playBuzzerSound();
    showToast('🔊 Acoustic buzzer sounding on Nivara GPS Band...');
    setTimeout(() => setIsBuzzerActive(false), 3000);
  };

  const handleRefreshStatus = async () => {
    await bluetoothService.scanAndConnectRealBLE();
    setSecondsAgo(0);
    showToast('Device telemetry and GPS satellite fix refreshed');
  };

  const handleToggleLostMode = () => {
    const nextVal = !isLostModeActive;
    setIsLostModeActive(nextVal);
    if (nextVal) {
      playSeparationAlarmSound();
      showToast('⚠️ Lost Mode ACTIVATED: High-power GPS beacon enabled');
    } else {
      showToast('Lost mode deactivated');
    }
  };

  const handleSaveCalibration = () => {
    bluetoothService.setSeparationThreshold(distanceThreshold);
    showToast(`Safety calibration saved: ${distanceThreshold}m threshold, ${alertDelay}s delay`);
  };

  const handleSaveNewZone = () => {
    if (!newZoneName.trim() || !newZoneAddress.trim()) {
      Alert.alert('Required Fields', 'Please enter a zone name and address.');
      return;
    }
    locationService.addSafeZone({
      name: newZoneName.trim(),
      address: newZoneAddress.trim(),
      radius: Number(newZoneRadius) || 100,
      icon: newZoneIcon,
      active: true,
      color: '#2563EB',
      latitude: 37.7749 + (Math.random() - 0.5) * 0.01,
      longitude: -122.4194 + (Math.random() - 0.5) * 0.01,
    });
    setNewZoneName('');
    setNewZoneAddress('');
    setAddZoneModalVisible(false);
    showToast(`Safe zone "${newZoneName}" created`);
  };

  const handleDeleteZone = (zoneId) => {
    Alert.alert('Delete Safe Zone', 'Are you sure you want to remove this geofence zone?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: () => {
          locationService.deleteSafeZone(zoneId);
          showToast('Safe zone deleted');
        },
      },
    ]);
  };

  const child = {
    name: 'Alex',
    caregiverName: 'Sarah J.',
    battery: locationState?.childLocation?.battery || 82,
    locationName: 'Model Town',
    city: 'Ludhiana',
    accuracy: '±8 meters',
    safeZoneName: 'Home (Model Town)',
    lastSync: '2 mins ago',
  };

  const navItems = [
    { id: 'DASHBOARD', label: 'Dashboard', icon: '⊞' },
    { id: 'LIVE_LOCATION', label: 'Live Location', icon: '📍' },
    { id: 'HISTORY', label: 'History', icon: '🕒' },
    { id: 'SAFE_ZONES', label: 'Safe Zones', icon: '🛡️' },
    { id: 'WEARABLE', label: 'Wearable Device', icon: '⌚' },
    { id: 'SAFETY_EVENTS', label: 'Safety Events', icon: '⚠️' },
    { id: 'EMERGENCY_CONTACTS', label: 'Emergency Contacts', icon: '👥' },
  ];

  const bottomNavItems = [
    { id: 'SETTINGS', label: 'Settings', icon: '⚙️' },
    { id: 'SUPPORT', label: 'Support', icon: '❓' },
  ];

  // Safety Events List (Screenshot 5)
  const safetyEventsList = [
    {
      id: 'ev-sos',
      category: 'ALERTS',
      isCritical: true,
      title: 'SOS Activated',
      badge: 'Critical',
      time: 'Today, 2:45 PM',
      desc: 'Device panic button triggered near Elm Street intersection. Emergency protocol active.',
      icon: '⚠️',
      iconBg: '#FEE2E2',
      iconColor: '#DC2626',
    },
    {
      id: 'ev-exit',
      category: 'GEOFENCES',
      isCritical: false,
      title: 'Safe Zone Exit: Home',
      time: 'Today, 1:15 PM',
      desc: "Subject departed the 'Home' geofence boundary. Heading North-West.",
      icon: '🚶',
      iconBg: '#FEF3C7',
      iconColor: '#D97706',
    },
    {
      id: 'ev-battery',
      category: 'DEVICE_STATUS',
      isCritical: false,
      title: 'Battery Low (15%)',
      time: 'Today, 11:30 AM',
      desc: 'Wearable device battery dropped below warning threshold. Please charge soon.',
      icon: '🔋',
      iconBg: '#F1F5F9',
      iconColor: '#64748B',
    },
    {
      id: 'ev-entry',
      category: 'GEOFENCES',
      isCritical: false,
      title: 'Safe Zone Entry: School',
      time: 'Today, 9:05 AM',
      desc: "Subject safely arrived within the 'School' geofence boundary.",
      icon: '📍',
      iconBg: '#ECFDF5',
      iconColor: '#059669',
    },
  ];

  const filteredEvents = safetyEventsList.filter((ev) => {
    if (eventCategoryFilter === 'ALERTS') return ev.category === 'ALERTS';
    if (eventCategoryFilter === 'DEVICE_STATUS') return ev.category === 'DEVICE_STATUS';
    if (eventCategoryFilter === 'GEOFENCES') return ev.category === 'GEOFENCES';
    return true;
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.mainLayout}>
        {/* ======================================================== */}
        {/* 1. LEFT SIDEBAR NAVIGATION                               */}
        {/* ======================================================== */}
        <View style={styles.sidebar}>
          {/* Logo */}
          <View style={styles.logoRow}>
            <View style={styles.logoSquareBlue}>
              <Text style={styles.logoTextWhite}>N</Text>
            </View>
            <View style={styles.logoTitleCol}>
              <Text style={styles.brandTitle}>Nivara</Text>
              <Text style={styles.brandSubtitle}>Caregiver Dashboard</Text>
            </View>
          </View>

          {/* Navigation Menu */}
          <ScrollView style={styles.navMenu} showsVerticalScrollIndicator={false}>
            {navItems.map((item) => {
              const isActive = activeNav === item.id;
              return (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.navItem, isActive && styles.navItemActive]}
                  onPress={() => setActiveNav(item.id)}
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

          {/* Bottom Sidebar: SOS Button + Settings + Support */}
          <View style={styles.sidebarBottom}>
            <TouchableOpacity
              style={styles.sosSidebarBtnSolid}
              onPress={handleOpenSOS}
              activeOpacity={0.85}
            >
              <Text style={styles.sosAsteriskSolid}>SOS</Text>
              <Text style={styles.sosBtnTextSolid}>SOS Emergency</Text>
            </TouchableOpacity>

            {bottomNavItems.map((item) => {
              const isActive = activeNav === item.id;
              return (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.navItem, isActive && styles.navItemActive]}
                  onPress={() => {
                    if (item.id === 'SETTINGS') setSettingsModalVisible(true);
                    else setActiveNav(item.id);
                  }}
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
          </View>
        </View>

        {/* ======================================================== */}
        {/* 2. MAIN CONTENT VIEWPORT                                */}
        {/* ======================================================== */}
        <View style={styles.contentViewport}>
          {/* Top Header Bar */}
          <View style={styles.topHeader}>
            <View style={styles.headerLeftCol}>
              {activeNav === 'LIVE_LOCATION' ? (
                <Text style={styles.headerLeftTitle}>Live Location</Text>
              ) : activeNav === 'SAFE_ZONES' ? (
                <Text style={styles.headerLeftTitle}>Safe Zones & Geofencing</Text>
              ) : activeNav === 'WEARABLE' ? (
                <Text style={styles.headerLeftTitle}>Wearable Device Management</Text>
              ) : (
                <View style={styles.searchBar}>
                  <Text style={styles.searchIcon}>🔍</Text>
                  <TextInput
                    style={styles.searchInput}
                    placeholder="Search events, locations, or settings..."
                    placeholderTextColor="#94A3B8"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                  />
                </View>
              )}
            </View>

            {/* Center Pill: Live Tracking on Live Location view */}
            {activeNav === 'LIVE_LOCATION' && (
              <View style={styles.liveTrackingPill}>
                <View style={styles.liveRedDot} />
                <Text style={styles.liveTrackingText}>LIVE TRACKING</Text>
              </View>
            )}

            {/* Right Header Actions */}
            <View style={styles.headerRightActions}>
              <TouchableOpacity
                style={styles.emergencySosPillBtn}
                onPress={handleOpenSOS}
                activeOpacity={0.85}
              >
                <Text style={styles.emergencySosIcon}>◎</Text>
                <Text style={styles.emergencySosText}>Emergency SOS</Text>
              </TouchableOpacity>

              <TouchableOpacity onPress={() => showToast('Caregiver Help Center')} activeOpacity={0.8}>
                <Text style={styles.helpIconText}>❓</Text>
              </TouchableOpacity>

              <TouchableOpacity onPress={() => showToast('No unread notifications')} activeOpacity={0.8}>
                <Text style={styles.bellIconText}>🔔</Text>
              </TouchableOpacity>

              <View style={styles.caregiverProfileGroup}>
                <View style={styles.profileAvatar}>
                  <Text style={styles.profileAvatarEmoji}>👩‍⚕️</Text>
                </View>
                <Text style={styles.caregiverNameText}>{child.caregiverName}</Text>
              </View>
            </View>
          </View>

          {/* Toast Notification */}
          {toastMessage && (
            <View style={styles.toastBanner}>
              <Text style={styles.toastText}>{toastMessage}</Text>
            </View>
          )}

          {/* ======================================================== */}
          {/* PAGE 1: DASHBOARD OVERVIEW (SCREENSHOT 1)                */}
          {/* ======================================================== */}
          {activeNav === 'DASHBOARD' && (
            <ScrollView style={styles.scrollArea} contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
              <View style={styles.pageTitleHeader}>
                <Text style={styles.overviewTitle}>Alex's Overview</Text>
                <Text style={styles.overviewSubtitle}>Real-time safety and device status.</Text>
              </View>

              {/* Upper Grid: Profile Card + Live Map Card */}
              <View style={styles.upperRowGrid}>
                {/* Left Profile & Device Card */}
                <View style={styles.profileDeviceCard}>
                  <View style={styles.childProfileHeader}>
                    <View style={styles.childAvatarCircle}>
                      <Text style={styles.childAvatarEmoji}>👦</Text>
                    </View>
                    <View style={styles.childNameCol}>
                      <Text style={styles.childName}>{child.name}</Text>
                      <View style={styles.safeBadge}>
                        <Text style={styles.safeBadgeCheck}>✓</Text>
                        <Text style={styles.safeBadgeText}>Safe</Text>
                      </View>
                    </View>
                  </View>

                  <View style={styles.sensorTile}>
                    <View style={styles.sensorLeft}>
                      <Text style={styles.sensorIcon}>🧬</Text>
                      <Text style={styles.sensorLabel}>GPS Signal</Text>
                    </View>
                    <View style={styles.sensorRight}>
                      <Text style={styles.sensorConnectedText}>Connected</Text>
                      <Text style={styles.sensorBarIcon}>📶</Text>
                    </View>
                  </View>

                  <View style={styles.sensorTile}>
                    <View style={styles.sensorLeft}>
                      <Text style={styles.sensorIcon}>⌚</Text>
                      <Text style={styles.sensorLabel}>Wearable Band</Text>
                    </View>
                    <View style={styles.sensorRight}>
                      <Text style={styles.sensorConnectedText}>Connected</Text>
                      <Text style={styles.sensorBtIcon}>ᛒ</Text>
                    </View>
                  </View>

                  <View style={styles.sensorTile}>
                    <View style={styles.sensorLeft}>
                      <Text style={styles.sensorIcon}>🔋</Text>
                      <Text style={styles.sensorLabel}>Battery Level</Text>
                    </View>
                    <View style={styles.sensorRight}>
                      <Text style={styles.batteryPercentText}>{child.battery}%</Text>
                    </View>
                  </View>

                  <TouchableOpacity
                    style={styles.deviceSettingsBtn}
                    onPress={() => setActiveNav('WEARABLE')}
                  >
                    <Text style={styles.gearBtnIcon}>⚙️</Text>
                    <Text style={styles.deviceSettingsText}>Device Settings</Text>
                  </TouchableOpacity>
                </View>

                {/* Right Interactive Map Card */}
                <View style={styles.overviewMapCard}>
                  <View style={styles.mapFloatingHeader}>
                    <View style={styles.mapLocationPill}>
                      <View style={styles.blueLocationDot} />
                      <Text style={styles.mapLocationTitle}>Current Location: Home</Text>
                    </View>
                    <Text style={styles.mapUpdatedSub}>Updated {child.lastSync}</Text>
                  </View>

                  <View style={styles.mapCanvas}>
                    <View style={styles.roadDiagonal1} />
                    <View style={styles.roadDiagonal2} />
                    <View style={styles.roadStraight} />
                    <Text style={[styles.mapPlaceLabel, { top: 38, left: 180 }]}>Meadowbrook Estates</Text>
                    <Text style={[styles.mapPlaceLabel, { top: 90, right: 30 }]}>Meadowbrook Community Park</Text>
                    <Text style={[styles.streetNameLabel, { top: 120, left: 70, transform: [{ rotate: '-35deg' }] }]}>Maplewood Dr</Text>
                    <Text style={[styles.streetNameLabel, { top: 175, left: 130, transform: [{ rotate: '-35deg' }] }]}>14 Maplewood Dr</Text>

                    <View style={styles.homeZonePin}>
                      <Text style={styles.homeZoneIcon}>🏠</Text>
                      <Text style={styles.homeZoneText}>Home</Text>
                    </View>

                    <View style={styles.childMapMarker}>
                      <View style={styles.childMarkerRing} />
                      <View style={styles.childMarkerBubble}>
                        <Text style={styles.childMarkerIcon}>👤</Text>
                      </View>
                    </View>

                    <View style={styles.mapFloatingControls}>
                      <TouchableOpacity style={styles.mapControlBtn} onPress={() => setMapZoom((z) => Math.min(2, z + 0.2))}>
                        <Text style={styles.mapControlPlus}>＋</Text>
                      </TouchableOpacity>
                      <TouchableOpacity style={styles.mapControlBtn} onPress={() => setMapZoom((z) => Math.max(0.6, z - 0.2))}>
                        <Text style={styles.mapControlMinus}>－</Text>
                      </TouchableOpacity>
                      <TouchableOpacity style={styles.mapControlBtn} onPress={() => showToast('Centered on Alex')}>
                        <Text style={styles.mapControlTarget}>🎯</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                </View>
              </View>

              {/* Lower 3-Column Widgets */}
              <View style={styles.lowerRowGrid}>
                {/* 1. Recent Events */}
                <View style={styles.widgetCard}>
                  <View style={styles.widgetHeaderRow}>
                    <Text style={styles.widgetHeaderIcon}>🕒</Text>
                    <Text style={styles.widgetTitle}>Recent Events</Text>
                  </View>
                  <View style={styles.timelineList}>
                    <View style={styles.timelineRow}>
                      <View style={styles.timelineDotCol}>
                        <View style={[styles.timelineDot, styles.dotGreen]} />
                        <View style={styles.timelineLine} />
                      </View>
                      <View style={styles.timelineBody}>
                        <Text style={styles.eventTimeText}>9:15 AM</Text>
                        <Text style={styles.eventDescText}>Entered <Text style={styles.boldEventTarget}>School</Text> Safe Zone</Text>
                      </View>
                    </View>
                    <View style={styles.timelineRow}>
                      <View style={styles.timelineDotCol}>
                        <View style={[styles.timelineDot, styles.dotGray]} />
                      </View>
                      <View style={styles.timelineBody}>
                        <Text style={styles.eventTimeText}>8:30 AM</Text>
                        <Text style={styles.eventDescText}>Left <Text style={styles.boldEventTarget}>Home</Text> Safe Zone</Text>
                      </View>
                    </View>
                  </View>
                  <TouchableOpacity style={styles.viewFullHistoryBtn} onPress={() => setActiveNav('HISTORY')}>
                    <Text style={styles.viewFullHistoryText}>View full history</Text>
                  </TouchableOpacity>
                </View>

                {/* 2. Active Safe Zones */}
                <View style={styles.widgetCard}>
                  <View style={styles.widgetHeaderRow}>
                    <Text style={styles.widgetHeaderIcon}>🛡️</Text>
                    <Text style={styles.widgetTitle}>Active Safe Zones</Text>
                  </View>
                  <View style={styles.zonesList}>
                    <View style={styles.safeZoneItem}>
                      <View style={styles.safeZoneIconBox}><Text style={styles.safeZoneIcon}>🏠</Text></View>
                      <View style={styles.safeZoneInfo}>
                        <Text style={styles.safeZoneName}>Home</Text>
                        <Text style={styles.safeZoneActiveText}>Active</Text>
                      </View>
                    </View>
                    <View style={styles.safeZoneItem}>
                      <View style={styles.safeZoneIconBox}><Text style={styles.safeZoneIcon}>🎓</Text></View>
                      <View style={styles.safeZoneInfo}>
                        <Text style={styles.safeZoneName}>School</Text>
                        <Text style={styles.safeZonePresentText}>Alex is here</Text>
                      </View>
                    </View>
                  </View>
                  <TouchableOpacity style={styles.addZoneDashedBtn} onPress={() => setAddZoneModalVisible(true)}>
                    <Text style={styles.addZoneDashedText}>＋ Add Zone</Text>
                  </TouchableOpacity>
                </View>

                {/* 3. Wearable Health */}
                <View style={styles.widgetCard}>
                  <View style={styles.widgetHeaderRow}>
                    <Text style={styles.widgetHeaderIcon}>📊</Text>
                    <Text style={styles.widgetTitle}>Wearable Health</Text>
                  </View>
                  <View style={styles.circularGaugeContainer}>
                    <View style={styles.circularGaugeOuter}>
                      <View style={styles.circularGaugeInner}>
                        <Text style={styles.gaugePercentText}>{child.battery}%</Text>
                      </View>
                    </View>
                  </View>
                  <Text style={styles.batteryHealthyText}>Battery is healthy. Last synced {child.lastSync}.</Text>
                  <View style={styles.healthInfoBox}>
                    <Text style={styles.healthInfoIcon}>ℹ️</Text>
                    <Text style={styles.healthInfoText}>Device is reporting strong GPS and Cellular signals. No immediate action needed.</Text>
                  </View>
                </View>
              </View>
            </ScrollView>
          )}

          {/* ======================================================== */}
          {/* PAGE 2: LIVE LOCATION FULL MAP (SCREENSHOT 3)            */}
          {/* ======================================================== */}
          {activeNav === 'LIVE_LOCATION' && (
            <View style={styles.liveMapContainer}>
              <View style={styles.fullVectorMap}>
                <View style={styles.highwayYellow44} />
                <View style={styles.highwayYellow5} />
                <View style={styles.highwayDiagonal} />
                <View style={styles.streetLine1} />
                <View style={styles.streetLine2} />
                <View style={styles.streetLine3} />
                <View style={styles.streetLine4} />

                <View style={[styles.highwayBadge, { top: '19%', left: '45%' }]}><Text style={styles.highwayBadgeText}>44</Text></View>
                <View style={[styles.highwayBadge, { top: '34%', left: '58%' }]}><Text style={styles.highwayBadgeText}>44</Text></View>
                <View style={[styles.highwayBadge, { top: '61%', left: '50%' }]}><Text style={styles.highwayBadgeText}>5</Text></View>
                <View style={[styles.highwayBadge, { bottom: '6%', right: '23%' }]}><Text style={styles.highwayBadgeText}>5</Text></View>
                <View style={[styles.highwayBadge, { bottom: '15%', left: '62%' }]}><Text style={styles.highwayBadgeText}>11</Text></View>
                <View style={[styles.highwayBadgeGreen, { top: '42%', left: '40%' }]}><Text style={styles.highwayBadgeGreenText}>20</Text></View>

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

                <View style={[styles.poiBadge, { top: '10%', left: '28%' }]}><Text style={styles.poiPurpleIcon}>🎡</Text><Text style={styles.poiPurpleText}>Hardy's World</Text></View>
                <View style={[styles.poiBadge, { top: '57%', left: '23%' }]}><Text style={styles.poiBlueIcon}>🛍️</Text><Text style={styles.poiBlueText}>Nexus MBD Neopolis Mall</Text></View>
                <View style={[styles.poiBadge, { bottom: '20%', right: '16%' }]}><Text style={styles.poiPurpleIcon}>🌊</Text><Text style={styles.poiPurpleText}>Water Dreams</Text></View>
                <View style={[styles.poiHospital, { top: '44%', left: '62%' }]}><Text style={styles.poiHospitalText}>H</Text></View>

                {/* Geofence Ring & Marker */}
                <View style={styles.alexGeofenceCircle} />
                <View style={styles.alexMarkerContainer}>
                  <View style={styles.alexMarkerAvatarRing}>
                    <Text style={styles.alexAvatarFace}>👦</Text>
                    <View style={styles.alexLiveStatusDot} />
                  </View>
                  <View style={styles.alexNamePill}><Text style={styles.alexNamePillText}>Alex</Text></View>
                </View>

                {/* Top Left Controls */}
                <View style={styles.topLeftMapControls}>
                  <TouchableOpacity style={styles.mapControlBtn} onPress={() => setMapZoom((z) => Math.min(2.2, z + 0.25))}><Text style={styles.mapBtnSymbol}>＋</Text></TouchableOpacity>
                  <TouchableOpacity style={styles.mapControlBtn} onPress={() => setMapZoom((z) => Math.max(0.5, z - 0.25))}><Text style={styles.mapBtnSymbol}>－</Text></TouchableOpacity>
                  <TouchableOpacity style={styles.mapControlBtn} onPress={() => showToast('Map centered on Alex')}><Text style={styles.mapBtnIcon}>🎯</Text></TouchableOpacity>
                  <TouchableOpacity style={styles.mapControlBtn} onPress={handleRefreshStatus}><Text style={styles.mapBtnIcon}>🔄</Text></TouchableOpacity>
                </View>

                {/* Top Right Floating Card Stack */}
                <View style={styles.topRightCardStack}>
                  <View style={styles.liveLocationCard}>
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
                    <View style={styles.updatedRow}>
                      <Text style={styles.updatedClockIcon}>🕒</Text>
                      <Text style={styles.updatedText}>Updated {secondsAgo === 0 ? 'just now' : `${secondsAgo} seconds ago`}</Text>
                    </View>
                    <View style={styles.cardInternalDivider} />
                    <View style={styles.telemetryGrid}>
                      <View style={styles.telemetryCol}>
                        <Text style={styles.telemetryLabel}>Current Location</Text>
                        <View style={styles.telemetryValRow}>
                          <Text style={styles.pinBlueIcon}>📍</Text>
                          <Text style={styles.telemetryValAddress}>{child.locationName},{'\n'}{child.city}</Text>
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
                    <View style={styles.cardFooterDivider} />
                    <View style={styles.cardFooterRow}>
                      <TouchableOpacity style={styles.viewRouteBtn} onPress={() => setActiveNav('HISTORY')}>
                        <Text style={styles.routeHistoryIcon}>⮂</Text>
                        <Text style={styles.viewRouteText}>View Route History</Text>
                      </TouchableOpacity>
                      <TouchableOpacity style={styles.moreOptionsBtn} onPress={() => setSettingsModalVisible(true)}>
                        <Text style={styles.moreOptionsText}>⋮</Text>
                      </TouchableOpacity>
                    </View>
                  </View>

                  <View style={styles.insideSafeZoneCard}>
                    <View style={styles.safeZoneHomeIconBox}><Text style={styles.safeZoneHomeEmoji}>🏠</Text></View>
                    <View style={styles.safeZoneTextCol}>
                      <Text style={styles.insideSafeZoneTitle}>Inside Safe Zone</Text>
                      <Text style={styles.insideSafeZoneSub}>{child.safeZoneName}</Text>
                    </View>
                  </View>
                </View>
              </View>
            </View>
          )}

          {/* ======================================================== */}
          {/* PAGE 3: SAFE ZONES & GEOFENCING (SCREENSHOT 2)           */}
          {/* ======================================================== */}
          {activeNav === 'SAFE_ZONES' && (
            <View style={styles.safeZoneSplitLayout}>
              <View style={styles.geofenceMapFrame}>
                <View style={styles.vectorMapCanvas}>
                  <View style={styles.mapParkGreen1} />
                  <View style={styles.mapParkGreen2} />
                  <View style={styles.mapStreetGridH1} />
                  <View style={styles.mapStreetGridH2} />
                  <View style={styles.mapStreetGridH3} />
                  <View style={styles.mapStreetGridV1} />
                  <View style={styles.mapStreetGridV2} />

                  <Text style={[styles.mapLabelTiny, { top: 30, left: 40 }]}>Oak Avenue</Text>
                  <Text style={[styles.mapLabelTiny, { top: 70, left: 40 }]}>Elm Street</Text>
                  <Text style={[styles.mapLabelTiny, { top: 110, left: 40 }]}>Willow Drive</Text>
                  <Text style={[styles.mapLabelTiny, { top: 120, right: 80 }]}>Cedar Lane</Text>

                  <View style={styles.ambientGeofenceTop} />

                  <TouchableOpacity
                    style={[styles.homeGeofenceCircle, selectedZoneId === 'zone-home' && styles.geofenceCircleSelected]}
                    onPress={() => setSelectedZoneId('zone-home')}
                  >
                    <View style={styles.zoneCenterBadge}>
                      <Text style={styles.zoneCenterIcon}>🏠</Text>
                      <Text style={styles.zoneCenterText}>Home (100m)</Text>
                    </View>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.schoolGeofenceCircle, selectedZoneId === 'zone-school' && styles.geofenceCircleSelected]}
                    onPress={() => setSelectedZoneId('zone-school')}
                  >
                    <View style={styles.zoneCenterBadge}>
                      <Text style={styles.zoneCenterIcon}>🎓</Text>
                      <Text style={styles.zoneCenterText}>School (150m)</Text>
                    </View>
                  </TouchableOpacity>

                  <View style={styles.floatingMapControls}>
                    <TouchableOpacity style={styles.mapActionBtn} onPress={() => setMapZoom((z) => Math.min(2.0, z + 0.25))}><Text style={styles.mapActionPlus}>＋</Text></TouchableOpacity>
                    <TouchableOpacity style={styles.mapActionBtn} onPress={() => setMapZoom((z) => Math.max(0.6, z - 0.25))}><Text style={styles.mapActionMinus}>－</Text></TouchableOpacity>
                    <TouchableOpacity style={styles.mapActionBtn} onPress={() => showToast('Centered on zones')}><Text style={styles.mapActionTarget}>🎯</Text></TouchableOpacity>
                  </View>
                </View>
              </View>

              <View style={styles.activeZonesSidebarPanel}>
                <View style={styles.activeZonesHeaderRow}>
                  <Text style={styles.activeZonesHeaderTitle}>Active Zones</Text>
                  <TouchableOpacity style={styles.addZonePillBtn} onPress={() => setAddZoneModalVisible(true)}>
                    <Text style={styles.addZonePillText}>＋ Add Zone</Text>
                  </TouchableOpacity>
                </View>

                <ScrollView style={styles.zonesScrollList} showsVerticalScrollIndicator={false}>
                  <TouchableOpacity
                    style={[styles.zoneItemCard, selectedZoneId === 'zone-home' && styles.zoneItemCardSelected]}
                    onPress={() => setSelectedZoneId('zone-home')}
                  >
                    <View style={styles.zoneItemTopRow}>
                      <View style={styles.zoneItemLeft}>
                        <View style={styles.homeBlueIconCircle}><Text style={styles.zoneHomeIcon}>🏠</Text></View>
                        <View style={styles.zoneItemNameCol}>
                          <Text style={styles.zoneItemName}>Home</Text>
                          <Text style={styles.zoneItemAddress}>123 Maple Street</Text>
                        </View>
                      </View>
                      <View style={styles.safePillBadge}><Text style={styles.safePillCheck}>✓</Text><Text style={styles.safePillText}>Safe</Text></View>
                    </View>
                    <View style={styles.zoneItemDivider} />
                    <View style={styles.zoneItemBottomRow}>
                      <Text style={styles.radiusValText}>🎯 Radius: 100m</Text>
                      <View style={styles.zoneActionIcons}>
                        <TouchableOpacity onPress={() => showToast('Editing Home Safe Zone...')}><Text style={styles.editPenIcon}>✏️</Text></TouchableOpacity>
                        <TouchableOpacity onPress={() => handleDeleteZone('zone-home')}><Text style={styles.trashIcon}>🗑️</Text></TouchableOpacity>
                      </View>
                    </View>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.zoneItemCard, selectedZoneId === 'zone-school' && styles.zoneItemCardSelected]}
                    onPress={() => setSelectedZoneId('zone-school')}
                  >
                    <View style={styles.zoneItemTopRow}>
                      <View style={styles.zoneItemLeft}>
                        <View style={styles.schoolGrayIconCircle}><Text style={styles.zoneSchoolIcon}>🎓</Text></View>
                        <View style={styles.zoneItemNameCol}>
                          <Text style={styles.zoneItemName}>Oakridge School</Text>
                          <Text style={styles.zoneItemAddress}>456 Oak Avenue</Text>
                        </View>
                      </View>
                      <View style={styles.inactivePillBadge}><Text style={styles.inactivePillText}>Inactive</Text></View>
                    </View>
                    <View style={styles.zoneItemDivider} />
                    <View style={styles.zoneItemBottomRow}>
                      <Text style={styles.radiusValText}>🎯 Radius: 150m</Text>
                      <View style={styles.zoneActionIcons}>
                        <TouchableOpacity onPress={() => showToast('Editing Oakridge School...')}><Text style={styles.editPenIcon}>✏️</Text></TouchableOpacity>
                        <TouchableOpacity onPress={() => handleDeleteZone('zone-school')}><Text style={styles.trashIcon}>🗑️</Text></TouchableOpacity>
                      </View>
                    </View>
                  </TouchableOpacity>
                </ScrollView>
              </View>
            </View>
          )}

          {/* ======================================================== */}
          {/* PAGE 4: WEARABLE DEVICE MANAGEMENT (SCREENSHOT 4)        */}
          {/* ======================================================== */}
          {activeNav === 'WEARABLE' && (
            <ScrollView style={styles.scrollArea} contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
              <View style={styles.wearableGrid}>
                {/* Left Column: Hero & Actions */}
                <View style={styles.wearableLeftCol}>
                  <View style={styles.deviceHeroCard}>
                    <View style={styles.deviceImageContainer}>
                      <View style={styles.imageConnectedBadge}>
                        <View style={styles.connectedGreenDot} />
                        <Text style={styles.connectedBadgeText}>Connected</Text>
                      </View>
                      <View style={styles.smartWatchVisual}>
                        <View style={styles.watchBezel}>
                          <View style={styles.watchScreen}>
                            <Text style={styles.watchTimeText}>09:41</Text>
                            <Text style={styles.watchHeartText}>❤️ 78 bpm</Text>
                            <Text style={styles.watchStepsText}>🚶 4,120 steps</Text>
                          </View>
                        </View>
                        <View style={styles.watchStrapTop} />
                        <View style={styles.watchStrapBottom} />
                      </View>
                    </View>

                    <View style={styles.deviceInfoBody}>
                      <Text style={styles.deviceHeroTitle}>Nivara GPS Band</Text>
                      <Text style={styles.deviceAssignedText}>Assigned to: <Text style={styles.assignedNameBold}>Sarah Jennings</Text></Text>
                      <View style={styles.metaTilesRow}>
                        <View style={styles.metaTile}>
                          <Text style={styles.metaTileLabel}>DEVICE ID</Text>
                          <Text style={styles.metaTileValue}>NV - BAND - 1024</Text>
                        </View>
                        <View style={styles.metaTile}>
                          <Text style={styles.metaTileLabel}>FIRMWARE</Text>
                          <Text style={styles.metaTileValue}>v2.4.1</Text>
                        </View>
                      </View>
                    </View>
                  </View>

                  <View style={styles.deviceActionsCard}>
                    <Text style={styles.deviceActionsSectionLabel}>DEVICE ACTIONS</Text>
                    <TouchableOpacity style={[styles.deviceActionItem, isBuzzerActive && styles.deviceActionItemActive]} onPress={handleFindDevice}>
                      <View style={styles.actionItemLeft}>
                        <Text style={styles.actionItemIcon}>🔍</Text>
                        <Text style={styles.actionItemLabel}>{isBuzzerActive ? 'Sounding Buzzer on Band...' : 'Find Device'}</Text>
                      </View>
                      <Text style={styles.actionItemChevron}>›</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.deviceActionItem} onPress={handleRefreshStatus}>
                      <View style={styles.actionItemLeft}>
                        <Text style={styles.actionItemIcon}>🔄</Text>
                        <Text style={styles.actionItemLabel}>Refresh Status</Text>
                      </View>
                      <Text style={styles.actionItemChevron}>›</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={[styles.deviceActionItem, isLostModeActive ? styles.lostModeActiveItem : styles.lostModeItem]} onPress={handleToggleLostMode}>
                      <View style={styles.actionItemLeft}>
                        <Text style={styles.lostModeIcon}>⚠️</Text>
                        <Text style={styles.lostModeLabel}>{isLostModeActive ? 'Lost Mode (ACTIVE)' : 'Lost Mode'}</Text>
                      </View>
                      <Text style={styles.lostModeChevron}>›</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Right Column: Telemetry & Calibration */}
                <View style={styles.wearableRightCol}>
                  <View style={styles.metricsTopRow}>
                    <View style={styles.metricHeroCard}>
                      <View style={styles.metricCardHeader}>
                        <Text style={styles.metricCardLabel}>Battery</Text>
                        <Text style={styles.batteryPlugIcon}>🔌</Text>
                      </View>
                      <Text style={styles.metricHeroVal}>82%</Text>
                      <Text style={styles.batteryChargingSub}>Charging</Text>
                    </View>
                    <View style={styles.metricHeroCard}>
                      <View style={styles.metricCardHeader}>
                        <Text style={styles.metricCardLabel}>GPS Connection</Text>
                        <Text style={styles.satelliteIcon}>🛰️</Text>
                      </View>
                      <Text style={styles.metricHeroVal}>Active</Text>
                      <Text style={styles.metricSubInfo}>Accuracy: High (3m)</Text>
                    </View>
                    <View style={styles.metricHeroCard}>
                      <View style={styles.metricCardHeader}>
                        <Text style={styles.metricCardLabel}>Bluetooth</Text>
                        <Text style={styles.bleIcon}>ᛒ</Text>
                      </View>
                      <Text style={styles.metricHeroVal}>Connected</Text>
                      <Text style={styles.bluetoothSignalGreen}>Signal: Strong</Text>
                    </View>
                  </View>

                  <View style={styles.safetyCalibrationCard}>
                    <View style={styles.calibrationHeaderRow}>
                      <View>
                        <Text style={styles.calibrationTitle}>Safety Calibration</Text>
                        <Text style={styles.calibrationSubtitle}>Configure Separation Detection parameters.</Text>
                      </View>
                      <TouchableOpacity style={styles.saveChangesBtn} onPress={handleSaveCalibration}>
                        <Text style={styles.saveChangesText}>Save Changes</Text>
                      </TouchableOpacity>
                    </View>

                    <View style={styles.detectionStatesSection}>
                      <Text style={styles.detectionStatesLabel}>DETECTION STATES</Text>
                      <View style={styles.statesRow}>
                        <View style={styles.stateItem}>
                          <View style={styles.connectedCircleIcon}><Text style={styles.stateCircleIconText}>🔗</Text></View>
                          <Text style={styles.stateConnectedTitle}>Connected</Text>
                          <Text style={styles.stateDistanceRange}>&lt; 15m</Text>
                        </View>
                        <View style={styles.stateItem}>
                          <View style={styles.warningCircleIcon}><Text style={styles.stateCircleIconText}>⚠️</Text></View>
                          <Text style={styles.stateWarningTitle}>Warning</Text>
                          <Text style={styles.stateDistanceRange}>15m - 20m</Text>
                        </View>
                        <View style={styles.stateItem}>
                          <View style={styles.separatedCircleIcon}><Text style={styles.stateCircleIconText}>🚫</Text></View>
                          <Text style={styles.stateSeparatedTitle}>Separated</Text>
                          <Text style={styles.stateDistanceRange}>&gt; 20m</Text>
                        </View>
                      </View>
                    </View>

                    <View style={styles.sliderGroup}>
                      <View style={styles.sliderHeaderRow}>
                        <Text style={styles.sliderTitle}>Distance Threshold</Text>
                        <View style={styles.sliderValueBadge}><Text style={styles.sliderValueText}>{distanceThreshold}m</Text></View>
                      </View>
                      <Text style={styles.sliderDesc}>Alert triggers if distance exceeds this limit.</Text>
                      <View style={styles.sliderTrackContainer}>
                        <View style={styles.sliderTrackBg}>
                          <View style={[styles.sliderTrackFill, { width: `${((distanceThreshold - 5) / 45) * 100}%` }]} />
                        </View>
                        <View style={styles.sliderStepsRow}>
                          {[5, 10, 15, 20, 30, 40, 50].map((val) => (
                            <TouchableOpacity key={val} style={[styles.stepTick, distanceThreshold === val && styles.stepTickActive]} onPress={() => setDistanceThreshold(val)} />
                          ))}
                        </View>
                      </View>
                      <View style={styles.sliderAxisRow}><Text style={styles.sliderAxisText}>5m</Text><Text style={styles.sliderAxisText}>50m</Text></View>
                    </View>

                    <View style={styles.sliderGroup}>
                      <View style={styles.sliderHeaderRow}>
                        <Text style={styles.sliderTitle}>Alert Delay</Text>
                        <View style={styles.sliderValueBadge}><Text style={styles.sliderValueText}>{alertDelay}s</Text></View>
                      </View>
                      <Text style={styles.sliderDesc}>Grace period before triggering full alarm.</Text>
                      <View style={styles.sliderTrackContainer}>
                        <View style={styles.sliderTrackBg}>
                          <View style={[styles.sliderTrackFill, { width: `${(alertDelay / 120) * 100}%` }]} />
                        </View>
                        <View style={styles.sliderStepsRow}>
                          {[0, 15, 30, 60, 90, 120].map((val) => (
                            <TouchableOpacity key={val} style={[styles.stepTick, alertDelay === val && styles.stepTickActive]} onPress={() => setAlertDelay(val)} />
                          ))}
                        </View>
                      </View>
                      <View style={styles.sliderAxisRow}><Text style={styles.sliderAxisText}>Instant</Text><Text style={styles.sliderAxisText}>120s</Text></View>
                    </View>
                  </View>
                </View>
              </View>
            </ScrollView>
          )}

          {/* ======================================================== */}
          {/* PAGE 5: SAFETY EVENTS & SOS CENTER (SCREENSHOT 5)        */}
          {/* ======================================================== */}
          {activeNav === 'SAFETY_EVENTS' && (
            <ScrollView style={styles.scrollArea} contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
              <View style={styles.safetyEventsPageTitleGroup}>
                <Text style={styles.safetyEventsHeading}>Safety Events & SOS Center</Text>
                <Text style={styles.safetyEventsSubheading}>
                  Review real-time alerts and historical safety transitions.
                </Text>
              </View>

              <View style={styles.safetyEventsMainGrid}>
                {/* Left Column: Filter Pills + Vertical Timeline (65%) */}
                <View style={styles.timelineLeftColumn}>
                  <View style={styles.filterPillsContainer}>
                    {[
                      { id: 'ALL', label: 'All Events' },
                      { id: 'ALERTS', label: 'Alerts' },
                      { id: 'DEVICE_STATUS', label: 'Device Status' },
                      { id: 'GEOFENCES', label: 'Geofences' },
                    ].map((tab) => {
                      const isSelected = eventCategoryFilter === tab.id;
                      return (
                        <TouchableOpacity
                          key={tab.id}
                          style={[styles.filterPillItem, isSelected && styles.filterPillItemActive]}
                          onPress={() => setEventCategoryFilter(tab.id)}
                          activeOpacity={0.8}
                        >
                          <Text style={[styles.filterPillItemText, isSelected && styles.filterPillItemTextActive]}>
                            {tab.label}
                          </Text>
                        </TouchableOpacity>
                      );
                    })}
                  </View>

                  <View style={styles.verticalTimelineList}>
                    {filteredEvents.map((ev, idx) => (
                      <View key={ev.id} style={styles.timelineRowWrapper}>
                        <View style={styles.timelineIconCol}>
                          <View style={[styles.timelineRoundIconBox, { backgroundColor: ev.iconBg }]}>
                            <Text style={styles.timelineRoundEmoji}>{ev.icon}</Text>
                          </View>
                          {idx < filteredEvents.length - 1 && <View style={styles.timelineVerticalLine} />}
                        </View>

                        <View style={[styles.eventCardBox, ev.isCritical && styles.criticalEventCardBox]}>
                          <View style={styles.eventCardHeaderRow}>
                            <View style={styles.eventCardTitleGroup}>
                              <Text style={[styles.eventCardTitle, ev.isCritical && styles.criticalEventTitle]}>
                                {ev.title}
                              </Text>
                              {ev.badge && (
                                <View style={styles.criticalBadgePill}>
                                  <Text style={styles.criticalBadgeText}>{ev.badge}</Text>
                                </View>
                              )}
                            </View>
                            <Text style={styles.eventCardTime}>{ev.time}</Text>
                          </View>

                          <Text style={styles.eventCardDesc}>{ev.desc}</Text>

                          {ev.isCritical && (
                            <View style={styles.criticalCardActionsRow}>
                              <TouchableOpacity
                                style={[styles.acknowledgeSolidBtn, isSosAcknowledged && styles.acknowledgeSolidBtnDone]}
                                onPress={handleAcknowledgeSOS}
                                activeOpacity={0.85}
                              >
                                <Text style={styles.acknowledgeBtnCheck}>✓</Text>
                                <Text style={styles.acknowledgeSolidBtnText}>
                                  {isSosAcknowledged ? 'Acknowledged' : 'Acknowledge'}
                                </Text>
                              </TouchableOpacity>

                              <TouchableOpacity
                                style={styles.viewLocationOutlineBtn}
                                onPress={() => setActiveNav('LIVE_LOCATION')}
                                activeOpacity={0.85}
                              >
                                <Text style={styles.mapPinOutlineIcon}>🗺️</Text>
                                <Text style={styles.viewLocationOutlineText}>View Location</Text>
                              </TouchableOpacity>
                            </View>
                          )}
                        </View>
                      </View>
                    ))}

                    <TouchableOpacity style={styles.loadMoreEventsRow} onPress={() => showToast('All events loaded.')}>
                      <Text style={styles.loadMoreEventsText}>Load More Events...</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Right Column: Device Health & Quick Help (35%) */}
                <View style={styles.sideCardsRightColumn}>
                  <View style={styles.sideHealthCard}>
                    <View style={styles.sideCardHeaderRow}>
                      <View style={styles.sideCardIconBoxBlue}>
                        <Text style={styles.sideCardEmoji}>⌚</Text>
                      </View>
                      <Text style={styles.sideCardTitle}>Current Device Health</Text>
                    </View>

                    <View style={styles.healthMetricTile}>
                      <View style={styles.healthMetricLeft}>
                        <Text style={styles.healthMetricIcon}>🔋</Text>
                        <Text style={styles.healthMetricLabel}>Battery Level</Text>
                      </View>
                      <View style={styles.greenBatteryPill}>
                        <Text style={styles.greenBatteryPillText}>{child.battery}%</Text>
                      </View>
                    </View>

                    <View style={styles.healthMetricTile}>
                      <View style={styles.healthMetricLeft}>
                        <Text style={styles.healthMetricIcon}>📶</Text>
                        <Text style={styles.healthMetricLabel}>LTE Signal</Text>
                      </View>
                      <Text style={styles.healthMetricBoldVal}>Strong</Text>
                    </View>

                    <View style={styles.healthMetricTile}>
                      <View style={styles.healthMetricLeft}>
                        <Text style={styles.healthMetricIcon}>🎯</Text>
                        <Text style={styles.healthMetricLabel}>GPS Accuracy</Text>
                      </View>
                      <View style={styles.healthMetricRightCol}>
                        <Text style={styles.healthMetricBoldVal}>High</Text>
                        <Text style={styles.healthMetricAccuracySub}>(±5m)</Text>
                      </View>
                    </View>
                  </View>

                  <View style={styles.sideHealthCard}>
                    <View style={styles.sideCardHeaderRow}>
                      <View style={styles.sideCardIconBoxRed}>
                        <Text style={styles.sideCardEmoji}>🛟</Text>
                      </View>
                      <Text style={styles.sideCardTitle}>Quick Help</Text>
                    </View>

                    <TouchableOpacity
                      style={styles.emergencyServicesBox}
                      onPress={() => showToast('Calling 911 Emergency Services...')}
                      activeOpacity={0.85}
                    >
                      <View style={styles.helpTextCol}>
                        <Text style={styles.emergencyServicesTitle}>Emergency Services</Text>
                        <Text style={styles.emergencyServicesSub}>Call 911 immediately</Text>
                      </View>
                      <Text style={styles.phoneRedIcon}>📞</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.primaryCaregiverBox}
                      onPress={() => showToast('Calling Michael J...')}
                      activeOpacity={0.85}
                    >
                      <View style={styles.helpTextCol}>
                        <Text style={styles.primaryCaregiverTitle}>Primary Caregiver</Text>
                        <Text style={styles.primaryCaregiverSub}>Call Michael J.</Text>
                      </View>
                      <Text style={styles.phoneGrayIcon}>📱</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              </View>
            </ScrollView>
          )}

          {/* ======================================================== */}
          {/* PAGE 6: HISTORY                                          */}
          {/* ======================================================== */}
          {activeNav === 'HISTORY' && (
            <ScrollView style={styles.scrollArea} contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
              <View style={styles.pageTitleHeader}>
                <Text style={styles.overviewTitle}>Location History & Timeline</Text>
                <Text style={styles.overviewSubtitle}>Detailed logs of all recorded GPS coordinates and geofence events.</Text>
              </View>
              <View style={styles.sideHealthCard}>
                <Text style={styles.sideCardTitle}>Today's Route Points</Text>
                <View style={styles.healthMetricTile}>
                  <Text style={styles.healthMetricLabel}>📍 Model Town, Ludhiana</Text>
                  <Text style={styles.healthMetricBoldVal}>2:45 PM</Text>
                </View>
                <View style={styles.healthMetricTile}>
                  <Text style={styles.healthMetricLabel}>📍 Civil Lines, Ludhiana</Text>
                  <Text style={styles.healthMetricBoldVal}>1:15 PM</Text>
                </View>
                <View style={styles.healthMetricTile}>
                  <Text style={styles.healthMetricLabel}>📍 Haibowal Kalan, Ludhiana</Text>
                  <Text style={styles.healthMetricBoldVal}>9:05 AM</Text>
                </View>
              </View>
            </ScrollView>
          )}

          {/* ======================================================== */}
          {/* PAGE 7: EMERGENCY CONTACTS                               */}
          {/* ======================================================== */}
          {activeNav === 'EMERGENCY_CONTACTS' && (
            <ScrollView style={styles.scrollArea} contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
              <View style={styles.pageTitleHeader}>
                <Text style={styles.overviewTitle}>Emergency Contacts Network</Text>
                <Text style={styles.overviewSubtitle}>Designated first responders and priority guardians.</Text>
              </View>
              <View style={styles.sideHealthCard}>
                <TouchableOpacity style={styles.emergencyServicesBox} onPress={() => showToast('Calling 911...')}>
                  <View style={styles.helpTextCol}>
                    <Text style={styles.emergencyServicesTitle}>Call Emergency Services (911)</Text>
                    <Text style={styles.emergencyServicesSub}>Immediate Police & Ambulance Dispatch</Text>
                  </View>
                  <Text style={styles.phoneRedIcon}>📞</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.primaryCaregiverBox} onPress={() => showToast('Calling Sarah (Mom)...')}>
                  <View style={styles.helpTextCol}>
                    <Text style={styles.primaryCaregiverTitle}>Sarah Miller (Mom)</Text>
                    <Text style={styles.primaryCaregiverSub}>Primary Guardian • +1 (555) 234-5678</Text>
                  </View>
                  <Text style={styles.phoneGrayIcon}>📞</Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          )}

          {/* ======================================================== */}
          {/* PAGE 8: SUPPORT & CARE CENTER                            */}
          {/* ======================================================== */}
          {activeNav === 'SUPPORT' && (
            <ScrollView style={styles.scrollArea} contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
              <View style={styles.pageTitleHeader}>
                <Text style={styles.overviewTitle}>Nivara Support & Help Center</Text>
                <Text style={styles.overviewSubtitle}>24/7 dedicated caregiver assistance and wearable hardware support.</Text>
              </View>
              <View style={styles.sideHealthCard}>
                <TouchableOpacity style={styles.healthMetricTile} onPress={() => showToast('Opening Live Chat...')}>
                  <Text style={styles.healthMetricLabel}>💬 Live Caregiver Chat Support</Text>
                  <Text style={styles.healthMetricBoldVal}>›</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.healthMetricTile} onPress={() => showToast('Calling Caregiver Hotline...')}>
                  <Text style={styles.healthMetricLabel}>📞 24/7 Crisis & Support Hotline</Text>
                  <Text style={styles.healthMetricBoldVal}>›</Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          )}
        </View>
      </View>

      {/* Add Safe Zone Modal */}
      <Modal visible={addZoneModalVisible} transparent animationType="slide">
        <View style={styles.modalBackdrop}>
          <View style={styles.addZoneModalCard}>
            <View style={styles.modalHeaderRow}>
              <Text style={styles.modalTitleText}>Add New Safe Zone</Text>
              <TouchableOpacity onPress={() => setAddZoneModalVisible(false)}><Text style={styles.modalCloseText}>✕</Text></TouchableOpacity>
            </View>
            <View style={styles.modalFormBody}>
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>Zone Name *</Text>
                <TextInput style={styles.modalInput} placeholder="e.g. Grandma's House, Therapy Center" placeholderTextColor="#94A3B8" value={newZoneName} onChangeText={setNewZoneName} />
              </View>
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>Address or Landmark *</Text>
                <TextInput style={styles.modalInput} placeholder="e.g. 789 Pinecrest Blvd" placeholderTextColor="#94A3B8" value={newZoneAddress} onChangeText={setNewZoneAddress} />
              </View>
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>Geofence Radius: {newZoneRadius} meters</Text>
                <View style={styles.radiusPillsRow}>
                  {[50, 100, 150, 200, 300].map((rad) => (
                    <TouchableOpacity key={rad} style={[styles.modalRadiusPill, newZoneRadius === rad && styles.modalRadiusPillActive]} onPress={() => setNewZoneRadius(rad)}>
                      <Text style={[styles.modalRadiusPillText, newZoneRadius === rad && styles.modalRadiusPillTextActive]}>{rad}m</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
              <TouchableOpacity style={styles.createZoneSubmitBtn} onPress={handleSaveNewZone}>
                <Text style={styles.createZoneSubmitText}>Create Safe Zone</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* SOS Emergency Modal */}
      <Modal visible={sosModalVisible} transparent animationType="fade">
        <View style={styles.modalBackdrop}>
          <View style={styles.sosModalCard}>
            <View style={styles.sosSirenCircle}><Text style={styles.sosModalIcon}>🚨</Text></View>
            <Text style={styles.sosModalTitle}>EMERGENCY SOS</Text>
            <Text style={styles.sosModalSubtitle}>Broadcasting high-priority distress signal and live GPS coordinates to emergency contacts.</Text>
            <View style={styles.countdownBox}>
              <Text style={styles.countdownNum}>{sosCountdown}</Text>
              <Text style={styles.countdownSub}>Auto-activating in seconds</Text>
            </View>
            <View style={styles.sosModalActions}>
              <TouchableOpacity style={styles.sosConfirmBtn} onPress={handleConfirmSOS}><Text style={styles.sosConfirmText}>🚨 SEND SOS NOW</Text></TouchableOpacity>
              <TouchableOpacity style={styles.sosCancelBtn} onPress={handleCancelSOS}><Text style={styles.sosCancelText}>Cancel Emergency</Text></TouchableOpacity>
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
        onToggleSharing={() => locationService.setLocationSharing(!locationState?.isLocationSharingOn)}
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
    marginBottom: 24,
    paddingHorizontal: 6,
  },
  logoSquareBlue: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#1E40AF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  logoTextWhite: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '900',
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
  sosSidebarBtnSolid: {
    backgroundColor: '#B91C1C',
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 11,
    marginBottom: 12,
    gap: 6,
  },
  sosAsteriskSolid: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '900',
  },
  sosBtnTextSolid: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
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
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 999,
    paddingHorizontal: 14,
    width: 320,
    height: 38,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  searchIcon: {
    fontSize: 13,
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 12,
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
    gap: 16,
  },
  emergencySosPillBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 6,
    gap: 6,
  },
  emergencySosIcon: {
    fontSize: 12,
    color: '#DC2626',
    fontWeight: '900',
  },
  emergencySosText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#DC2626',
  },
  helpIconText: {
    fontSize: 16,
    color: '#64748B',
  },
  bellIconText: {
    fontSize: 16,
    color: '#64748B',
  },
  caregiverProfileGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginLeft: 4,
  },
  profileAvatar: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileAvatarEmoji: {
    fontSize: 16,
  },
  caregiverNameText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
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

  // SCROLL CONTAINER
  scrollArea: {
    flex: 1,
  },
  scrollContainer: {
    padding: 24,
    paddingBottom: 50,
  },

  // PAGE 1: DASHBOARD STYLES
  pageTitleHeader: {
    marginBottom: 20,
  },
  overviewTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  overviewSubtitle: {
    fontSize: 13,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '500',
  },
  upperRowGrid: {
    flexDirection: isDesktop ? 'row' : 'column',
    gap: 20,
    marginBottom: 20,
  },
  profileDeviceCard: {
    flex: 3,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  childProfileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  childAvatarCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FEF3C7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  childAvatarEmoji: {
    fontSize: 24,
  },
  childNameCol: {},
  childName: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  safeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 999,
    alignSelf: 'flex-start',
  },
  safeBadgeCheck: {
    color: '#059669',
    fontSize: 10,
    fontWeight: '900',
    marginRight: 4,
  },
  safeBadgeText: {
    color: '#059669',
    fontSize: 11,
    fontWeight: '700',
  },
  sensorTile: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  sensorLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sensorIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  sensorLabel: {
    fontSize: 12,
    color: '#334155',
    fontWeight: '600',
  },
  sensorRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sensorConnectedText: {
    fontSize: 12,
    color: '#059669',
    fontWeight: '700',
    marginRight: 4,
  },
  sensorBarIcon: {
    fontSize: 12,
  },
  sensorBtIcon: {
    fontSize: 12,
    color: '#059669',
    fontWeight: '800',
  },
  batteryPercentText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#0F172A',
  },
  deviceSettingsBtn: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 12,
    paddingVertical: 10,
    marginTop: 8,
    backgroundColor: '#FFFFFF',
  },
  gearBtnIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  deviceSettingsText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#1E293B',
  },
  overviewMapCard: {
    flex: 7,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
  },
  mapFloatingHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
  },
  mapLocationPill: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
  },
  blueLocationDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#2563EB',
    marginRight: 6,
  },
  mapLocationTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  mapUpdatedSub: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '500',
  },
  mapCanvas: {
    height: 240,
    backgroundColor: '#E8EFE9',
    position: 'relative',
    overflow: 'hidden',
  },
  roadDiagonal1: {
    position: 'absolute',
    top: -40,
    left: 40,
    width: 300,
    height: 28,
    backgroundColor: '#FFFFFF',
    transform: [{ rotate: '-35deg' }],
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#CBD5E1',
  },
  roadDiagonal2: {
    position: 'absolute',
    top: 40,
    left: 140,
    width: 320,
    height: 24,
    backgroundColor: '#FFFFFF',
    transform: [{ rotate: '-35deg' }],
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#CBD5E1',
  },
  roadStraight: {
    position: 'absolute',
    top: 130,
    left: 0,
    right: 0,
    height: 20,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#CBD5E1',
  },
  mapPlaceLabel: {
    position: 'absolute',
    fontSize: 9,
    fontWeight: '800',
    color: '#64748B',
  },
  streetNameLabel: {
    position: 'absolute',
    fontSize: 8,
    color: '#94A3B8',
    fontWeight: '700',
  },
  homeZonePin: {
    position: 'absolute',
    top: 135,
    left: 200,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    zIndex: 10,
  },
  homeZoneIcon: {
    fontSize: 10,
    marginRight: 3,
  },
  homeZoneText: {
    fontSize: 9,
    fontWeight: '800',
    color: '#0F172A',
  },
  childMapMarker: {
    position: 'absolute',
    top: 140,
    left: 240,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 15,
  },
  childMarkerRing: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(37, 99, 235, 0.25)',
    position: 'absolute',
  },
  childMarkerBubble: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#1E3A8A',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  childMarkerIcon: {
    fontSize: 11,
  },
  mapFloatingControls: {
    position: 'absolute',
    right: 12,
    bottom: 12,
    gap: 4,
    zIndex: 20,
  },
  mapControlBtn: {
    width: 28,
    height: 28,
    borderRadius: 6,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mapControlPlus: {
    fontSize: 14,
    fontWeight: '800',
    color: '#334155',
  },
  mapControlMinus: {
    fontSize: 14,
    fontWeight: '800',
    color: '#334155',
  },
  mapControlTarget: {
    fontSize: 11,
  },
  lowerRowGrid: {
    flexDirection: isDesktop ? 'row' : 'column',
    gap: 20,
  },
  widgetCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  widgetHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  widgetHeaderIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  widgetTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  timelineList: {
    marginBottom: 14,
  },
  timelineRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  timelineDotCol: {
    alignItems: 'center',
    width: 16,
    marginRight: 8,
  },
  timelineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 3,
  },
  dotGreen: {
    backgroundColor: '#059669',
  },
  dotGray: {
    backgroundColor: '#CBD5E1',
  },
  timelineLine: {
    width: 1.5,
    flex: 1,
    backgroundColor: '#E2E8F0',
    marginTop: 2,
  },
  timelineBody: {
    flex: 1,
  },
  eventTimeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#0F172A',
  },
  eventDescText: {
    fontSize: 12,
    color: '#475569',
    marginTop: 1,
  },
  boldEventTarget: {
    fontWeight: '800',
    color: '#1E40AF',
  },
  viewFullHistoryBtn: {
    marginTop: 6,
  },
  viewFullHistoryText: {
    fontSize: 12,
    color: '#2563EB',
    fontWeight: '700',
  },
  zonesList: {
    gap: 10,
    marginBottom: 14,
  },
  safeZoneItem: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    padding: 10,
  },
  safeZoneIconBox: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  safeZoneIcon: {
    fontSize: 16,
  },
  safeZoneInfo: {
    flex: 1,
  },
  safeZoneName: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  safeZoneActiveText: {
    fontSize: 11,
    color: '#059669',
    fontWeight: '600',
  },
  safeZonePresentText: {
    fontSize: 11,
    color: '#059669',
    fontWeight: '700',
  },
  addZoneDashedBtn: {
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderStyle: 'dashed',
    borderRadius: 12,
    paddingVertical: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addZoneDashedText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
  },
  circularGaugeContainer: {
    alignItems: 'center',
    marginVertical: 10,
  },
  circularGaugeOuter: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 6,
    borderColor: '#059669',
    justifyContent: 'center',
    alignItems: 'center',
  },
  circularGaugeInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  gaugePercentText: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0F172A',
  },
  batteryHealthyText: {
    fontSize: 12,
    color: '#475569',
    textAlign: 'center',
    marginBottom: 12,
    fontWeight: '500',
  },
  healthInfoBox: {
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 10,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  healthInfoIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  healthInfoText: {
    flex: 1,
    fontSize: 11,
    color: '#475569',
    lineHeight: 16,
    fontWeight: '500',
  },

  // PAGE 2: LIVE LOCATION STYLES
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

  // PAGE 3: SAFE ZONES STYLES
  safeZoneSplitLayout: {
    flex: 1,
    flexDirection: isDesktop ? 'row' : 'column',
    backgroundColor: '#FFFFFF',
  },
  geofenceMapFrame: {
    flex: 6.5,
    backgroundColor: '#E4EDE5',
    position: 'relative',
    overflow: 'hidden',
    borderRightWidth: 1,
    borderRightColor: '#EEF2F6',
  },
  vectorMapCanvas: {
    flex: 1,
    position: 'relative',
  },
  mapParkGreen1: {
    position: 'absolute',
    top: 20,
    left: 30,
    width: 180,
    height: 140,
    backgroundColor: '#D1E7D5',
    borderRadius: 18,
  },
  mapParkGreen2: {
    position: 'absolute',
    bottom: 40,
    left: 40,
    width: 190,
    height: 150,
    backgroundColor: '#D1E7D5',
    borderRadius: 18,
  },
  mapStreetGridH1: {
    position: 'absolute',
    top: 50,
    left: 0,
    right: 0,
    height: 14,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#D4DEC8',
  },
  mapStreetGridH2: {
    position: 'absolute',
    top: 180,
    left: 0,
    right: 0,
    height: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#D4DEC8',
  },
  mapStreetGridH3: {
    position: 'absolute',
    bottom: 120,
    left: 0,
    right: 0,
    height: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#D4DEC8',
  },
  mapStreetGridV1: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 230,
    width: 16,
    backgroundColor: '#FFFFFF',
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderColor: '#D4DEC8',
  },
  mapStreetGridV2: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    right: 140,
    width: 16,
    backgroundColor: '#FFFFFF',
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderColor: '#D4DEC8',
  },
  mapLabelTiny: {
    position: 'absolute',
    fontSize: 8,
    color: '#82957C',
    fontWeight: '700',
  },
  ambientGeofenceTop: {
    position: 'absolute',
    top: 30,
    left: '35%',
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: 'rgba(37, 99, 235, 0.12)',
    borderWidth: 1,
    borderColor: 'rgba(37, 99, 235, 0.25)',
  },
  homeGeofenceCircle: {
    position: 'absolute',
    top: '32%',
    left: '30%',
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: 'rgba(59, 130, 246, 0.18)',
    borderWidth: 2,
    borderColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  schoolGeofenceCircle: {
    position: 'absolute',
    bottom: '12%',
    right: '18%',
    width: 220,
    height: 220,
    borderRadius: 110,
    backgroundColor: 'rgba(100, 116, 139, 0.16)',
    borderWidth: 1.5,
    borderColor: '#475569',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  geofenceCircleSelected: {
    borderWidth: 3,
  },
  zoneCenterBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  zoneCenterIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  zoneCenterText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#0F172A',
  },
  floatingMapControls: {
    position: 'absolute',
    right: 16,
    bottom: 24,
    gap: 6,
    zIndex: 30,
  },
  mapActionBtn: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mapActionPlus: {
    fontSize: 16,
    fontWeight: '800',
    color: '#334155',
  },
  mapActionMinus: {
    fontSize: 16,
    fontWeight: '800',
    color: '#334155',
  },
  mapActionTarget: {
    fontSize: 13,
  },
  activeZonesSidebarPanel: {
    flex: 3.5,
    backgroundColor: '#FFFFFF',
    padding: 24,
  },
  activeZonesHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  activeZonesHeaderTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  addZonePillBtn: {
    backgroundColor: '#0F3D87',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 999,
  },
  addZonePillText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  zonesScrollList: {
    flex: 1,
  },
  zoneItemCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
  },
  zoneItemCardSelected: {
    borderColor: '#2563EB',
    backgroundColor: '#F8FAFC',
  },
  zoneItemTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  zoneItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  homeBlueIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#1D4ED8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  zoneHomeIcon: {
    fontSize: 16,
  },
  schoolGrayIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  zoneSchoolIcon: {
    fontSize: 16,
  },
  zoneItemNameCol: {
    flex: 1,
  },
  zoneItemName: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  zoneItemAddress: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  safePillBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
  },
  safePillCheck: {
    color: '#059669',
    fontSize: 10,
    fontWeight: '900',
    marginRight: 4,
  },
  safePillText: {
    color: '#059669',
    fontSize: 11,
    fontWeight: '700',
  },
  inactivePillBadge: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
  },
  inactivePillText: {
    color: '#64748B',
    fontSize: 11,
    fontWeight: '700',
  },
  zoneItemDivider: {
    height: 1,
    backgroundColor: '#EEF2F6',
    marginBottom: 10,
  },
  zoneItemBottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  radiusValText: {
    fontSize: 11,
    color: '#334155',
    fontWeight: '600',
  },
  zoneActionIcons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  editPenIcon: {
    fontSize: 14,
  },
  trashIcon: {
    fontSize: 14,
  },

  // PAGE 4: WEARABLE STYLES
  wearableGrid: {
    flexDirection: isDesktop ? 'row' : 'column',
    gap: 24,
  },
  wearableLeftCol: {
    flex: 4,
    gap: 20,
  },
  deviceHeroCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
  },
  deviceImageContainer: {
    height: 160,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  imageConnectedBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: '#064E3B',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
  },
  connectedGreenDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#34D399',
    marginRight: 5,
  },
  connectedBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '800',
  },
  smartWatchVisual: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  watchStrapTop: {
    position: 'absolute',
    top: -24,
    width: 32,
    height: 24,
    backgroundColor: '#334155',
    borderRadius: 4,
  },
  watchBezel: {
    width: 80,
    height: 80,
    borderRadius: 18,
    backgroundColor: '#0F172A',
    borderWidth: 3,
    borderColor: '#475569',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  watchScreen: {
    alignItems: 'center',
  },
  watchTimeText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '900',
  },
  watchHeartText: {
    color: '#F87171',
    fontSize: 8,
    fontWeight: '700',
    marginTop: 2,
  },
  watchStepsText: {
    color: '#60A5FA',
    fontSize: 7,
    fontWeight: '700',
  },
  watchStrapBottom: {
    position: 'absolute',
    bottom: -24,
    width: 32,
    height: 24,
    backgroundColor: '#334155',
    borderRadius: 4,
  },
  deviceInfoBody: {
    padding: 18,
  },
  deviceHeroTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  deviceAssignedText: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 16,
  },
  assignedNameBold: {
    color: '#1E40AF',
    fontWeight: '800',
  },
  metaTilesRow: {
    flexDirection: 'row',
    gap: 10,
  },
  metaTile: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    borderRadius: 12,
    padding: 10,
  },
  metaTileLabel: {
    fontSize: 8,
    fontWeight: '800',
    color: '#64748B',
    marginBottom: 4,
  },
  metaTileValue: {
    fontSize: 12,
    fontWeight: '800',
    color: '#0F172A',
  },
  deviceActionsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  deviceActionsSectionLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 12,
  },
  deviceActionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 14,
    marginBottom: 10,
    backgroundColor: '#FFFFFF',
  },
  deviceActionItemActive: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  actionItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionItemIcon: {
    fontSize: 14,
    marginRight: 10,
  },
  actionItemLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  actionItemChevron: {
    fontSize: 16,
    color: '#94A3B8',
    fontWeight: '800',
  },
  lostModeItem: {
    borderColor: '#FECACA',
    backgroundColor: '#FEF2F2',
  },
  lostModeActiveItem: {
    borderColor: '#DC2626',
    backgroundColor: '#FEE2E2',
  },
  lostModeIcon: {
    fontSize: 14,
    marginRight: 10,
  },
  lostModeLabel: {
    fontSize: 13,
    fontWeight: '800',
    color: '#DC2626',
  },
  lostModeChevron: {
    fontSize: 16,
    color: '#DC2626',
    fontWeight: '800',
  },
  wearableRightCol: {
    flex: 6,
    gap: 20,
  },
  metricsTopRow: {
    flexDirection: 'row',
    gap: 12,
  },
  metricHeroCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  metricCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  metricCardLabel: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  batteryPlugIcon: {
    fontSize: 14,
  },
  satelliteIcon: {
    fontSize: 14,
  },
  bleIcon: {
    fontSize: 14,
    fontWeight: '800',
    color: '#1E40AF',
  },
  metricHeroVal: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0F172A',
    marginBottom: 2,
  },
  batteryChargingSub: {
    fontSize: 11,
    color: '#059669',
    fontWeight: '700',
  },
  metricSubInfo: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '500',
  },
  bluetoothSignalGreen: {
    fontSize: 11,
    color: '#059669',
    fontWeight: '700',
  },
  safetyCalibrationCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 22,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  calibrationHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 22,
  },
  calibrationTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#0F172A',
  },
  calibrationSubtitle: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  saveChangesBtn: {
    backgroundColor: '#0F3D87',
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 8,
  },
  saveChangesText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  detectionStatesSection: {
    marginBottom: 24,
  },
  detectionStatesLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 14,
  },
  statesRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 10,
  },
  stateItem: {
    alignItems: 'center',
    flex: 1,
  },
  connectedCircleIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#065F46',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  warningCircleIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  separatedCircleIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  stateCircleIconText: {
    fontSize: 18,
  },
  stateConnectedTitle: {
    fontSize: 12,
    fontWeight: '800',
    color: '#059669',
  },
  stateWarningTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
  },
  stateSeparatedTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
  },
  stateDistanceRange: {
    fontSize: 10,
    color: '#94A3B8',
    fontWeight: '600',
    marginTop: 2,
  },
  sliderGroup: {
    marginTop: 18,
  },
  sliderHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sliderTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  sliderValueBadge: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  sliderValueText: {
    fontSize: 12,
    fontWeight: '900',
    color: '#1E40AF',
  },
  sliderDesc: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
    marginBottom: 10,
  },
  sliderTrackContainer: {
    position: 'relative',
    height: 24,
    justifyContent: 'center',
  },
  sliderTrackBg: {
    height: 6,
    backgroundColor: '#E2E8F0',
    borderRadius: 3,
    overflow: 'hidden',
  },
  sliderTrackFill: {
    height: '100%',
    backgroundColor: '#2563EB',
  },
  sliderStepsRow: {
    position: 'absolute',
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stepTick: {
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#94A3B8',
  },
  stepTickActive: {
    borderColor: '#2563EB',
    backgroundColor: '#2563EB',
    transform: [{ scale: 1.2 }],
  },
  sliderAxisRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  sliderAxisText: {
    fontSize: 10,
    color: '#94A3B8',
    fontWeight: '600',
  },

  // PAGE 5: SAFETY EVENTS & SOS CENTER STYLES
  safetyEventsPageTitleGroup: {
    marginBottom: 20,
  },
  safetyEventsHeading: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0F172A',
  },
  safetyEventsSubheading: {
    fontSize: 13,
    color: '#64748B',
    marginTop: 3,
    fontWeight: '500',
  },
  safetyEventsMainGrid: {
    flexDirection: isDesktop ? 'row' : 'column',
    gap: 24,
    alignItems: 'flex-start',
  },
  timelineLeftColumn: {
    flex: 6.5,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  filterPillsContainer: {
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    padding: 4,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 24,
  },
  filterPillItem: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 8,
  },
  filterPillItemActive: {
    backgroundColor: '#E0E7FF',
  },
  filterPillItemText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748B',
  },
  filterPillItemTextActive: {
    color: '#1E40AF',
    fontWeight: '800',
  },
  verticalTimelineList: {},
  timelineRowWrapper: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  timelineIconCol: {
    alignItems: 'center',
    width: 36,
    marginRight: 14,
  },
  timelineRoundIconBox: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  timelineRoundEmoji: {
    fontSize: 14,
  },
  timelineVerticalLine: {
    width: 1.5,
    flex: 1,
    backgroundColor: '#E2E8F0',
    marginVertical: 4,
  },
  eventCardBox: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 16,
  },
  criticalEventCardBox: {
    borderColor: '#FECACA',
    borderLeftWidth: 4,
    borderLeftColor: '#DC2626',
  },
  eventCardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  eventCardTitleGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  eventCardTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  criticalEventTitle: {
    color: '#991B1B',
    fontSize: 15,
    fontWeight: '900',
  },
  criticalBadgePill: {
    backgroundColor: '#DC2626',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  criticalBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '900',
  },
  eventCardTime: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
  },
  eventCardDesc: {
    fontSize: 12,
    color: '#475569',
    lineHeight: 18,
  },
  criticalCardActionsRow: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 14,
  },
  acknowledgeSolidBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#B91C1C',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 9,
    gap: 6,
  },
  acknowledgeSolidBtnDone: {
    backgroundColor: '#059669',
  },
  acknowledgeBtnCheck: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '900',
  },
  acknowledgeSolidBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  viewLocationOutlineBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 9,
    gap: 6,
  },
  mapPinOutlineIcon: {
    fontSize: 12,
  },
  viewLocationOutlineText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#0F172A',
  },
  loadMoreEventsRow: {
    alignItems: 'center',
    paddingVertical: 14,
  },
  loadMoreEventsText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },
  sideCardsRightColumn: {
    flex: 3.5,
    gap: 20,
  },
  sideHealthCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  sideCardHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 10,
  },
  sideCardIconBoxBlue: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sideCardIconBoxRed: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#FEF2F2',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sideCardEmoji: {
    fontSize: 16,
  },
  sideCardTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  healthMetricTile: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    marginBottom: 10,
  },
  healthMetricLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  healthMetricIcon: {
    fontSize: 14,
  },
  healthMetricLabel: {
    fontSize: 12,
    color: '#475569',
    fontWeight: '600',
  },
  greenBatteryPill: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  greenBatteryPillText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#059669',
  },
  healthMetricBoldVal: {
    fontSize: 12,
    fontWeight: '800',
    color: '#0F172A',
  },
  healthMetricRightCol: {
    alignItems: 'flex-end',
  },
  healthMetricAccuracySub: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
  },
  emergencyServicesBox: {
    backgroundColor: '#FEE2E2',
    borderRadius: 14,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  helpTextCol: {
    flex: 1,
  },
  emergencyServicesTitle: {
    color: '#991B1B',
    fontSize: 13,
    fontWeight: '800',
  },
  emergencyServicesSub: {
    color: '#B91C1C',
    fontSize: 11,
    fontWeight: '600',
    marginTop: 1,
  },
  phoneRedIcon: {
    fontSize: 16,
    color: '#B91C1C',
  },
  primaryCaregiverBox: {
    backgroundColor: '#F8FAFC',
    borderRadius: 14,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  primaryCaregiverTitle: {
    color: '#0F172A',
    fontSize: 13,
    fontWeight: '800',
  },
  primaryCaregiverSub: {
    color: '#64748B',
    fontSize: 11,
    fontWeight: '500',
    marginTop: 1,
  },
  phoneGrayIcon: {
    fontSize: 16,
    color: '#475569',
  },

  // MODALS
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  addZoneModalCard: {
    width: '100%',
    maxWidth: 500,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
  },
  modalHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 18,
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
    paddingBottom: 12,
  },
  modalTitleText: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  modalCloseText: {
    fontSize: 16,
    color: '#64748B',
    fontWeight: '700',
  },
  modalFormBody: {
    gap: 14,
  },
  formGroup: {
    gap: 6,
  },
  formLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  modalInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 13,
    color: '#0F172A',
  },
  radiusPillsRow: {
    flexDirection: 'row',
    gap: 8,
  },
  modalRadiusPill: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 999,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  modalRadiusPillActive: {
    backgroundColor: '#0F3D87',
    borderColor: '#0F3D87',
  },
  modalRadiusPillText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#475569',
  },
  modalRadiusPillTextActive: {
    color: '#FFFFFF',
  },
  createZoneSubmitBtn: {
    backgroundColor: '#0F3D87',
    paddingVertical: 14,
    borderRadius: 999,
    alignItems: 'center',
    marginTop: 8,
  },
  createZoneSubmitText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '800',
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
});
