// NIVARA GPS & Location Service
// Supports Real-Time Browser Geolocation & Realistic Caregiver/Child Simulation

import AsyncStorage from '@react-native-async-storage/async-storage';

export const GPS_STATUS = {
  ACTIVE: 'ACTIVE',
  WEAK: 'WEAK',
  UNAVAILABLE: 'UNAVAILABLE',
  OFFLINE: 'OFFLINE',
};

export const EVENT_TYPES = {
  ZONE_ENTRY: 'ZONE_ENTRY',
  ZONE_EXIT: 'ZONE_EXIT',
  BREADCRUMB: 'BREADCRUMB',
  LOCATE_NOW: 'LOCATE_NOW',
  SOS_ALERT: 'SOS_ALERT',
  STATUS_CHANGE: 'STATUS_CHANGE',
  SHARING_TOGGLED: 'SHARING_TOGGLED',
};

// Default Safe Zones (Pre-configured for Caregiver / Child)
export const DEFAULT_SAFE_ZONES = [
  {
    id: 'zone-home',
    name: 'Home Safe Zone',
    category: 'Home',
    address: '742 Evergreen Terrace, Springfield',
    latitude: 37.7749,
    longitude: -122.4194,
    radius: 150, // in meters
    color: '#10B981', // emerald
    icon: '🏠',
    active: true,
    notifyOnEntry: true,
    notifyOnExit: true,
    schedule: 'Always Active',
  },
  {
    id: 'zone-school',
    name: 'Oakwood Elementary School',
    category: 'School',
    address: '1040 Willow Creek Rd, Springfield',
    latitude: 37.7785,
    longitude: -122.4140,
    radius: 200,
    color: '#3B82F6', // blue
    icon: '🏫',
    active: true,
    notifyOnEntry: true,
    notifyOnExit: true,
    schedule: 'Mon - Fri, 8:00 AM - 3:30 PM',
  },
  {
    id: 'zone-therapy',
    name: 'Sensory Bloom Therapy Clinic',
    category: 'Medical',
    address: '520 Healing Path Suite 3B, Springfield',
    latitude: 37.7710,
    longitude: -122.4250,
    radius: 120,
    color: '#8B5CF6', // purple
    icon: '🧩',
    active: true,
    notifyOnEntry: true,
    notifyOnExit: true,
    schedule: 'Tue & Thu, 2:00 PM - 5:00 PM',
  },
  {
    id: 'zone-park',
    name: 'Sunset Sensory Play Park',
    category: 'Recreation',
    address: '300 Meadow Green Blvd, Springfield',
    latitude: 37.7802,
    longitude: -122.4280,
    radius: 180,
    color: '#F59E0B', // amber
    icon: '🌳',
    active: true,
    notifyOnEntry: true,
    notifyOnExit: true,
    schedule: 'Weekends, 9:00 AM - 6:00 PM',
  },
  {
    id: 'zone-grandparents',
    name: "Grandparent's Residence",
    category: 'Family',
    address: '118 Magnolia Lane, Springfield',
    latitude: 37.7690,
    longitude: -122.4120,
    radius: 100,
    color: '#EC4899', // pink
    icon: '👵',
    active: true,
    notifyOnEntry: true,
    notifyOnExit: true,
    schedule: 'On Request',
  },
];

// Initial mock route history
export const INITIAL_LOCATION_HISTORY = [
  {
    id: 'loc-hist-1',
    date: 'Today',
    time: '4:15 PM',
    isoTime: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    latitude: 37.7752,
    longitude: -122.4190,
    address: '742 Evergreen Terrace (Near Courtyard)',
    accuracy: 3.2,
    speed: 0.4,
    eventType: EVENT_TYPES.BREADCRUMB,
    zoneName: 'Home Safe Zone',
    inSafeZone: true,
    battery: 88,
  },
  {
    id: 'loc-hist-2',
    date: 'Today',
    time: '3:45 PM',
    isoTime: new Date(Date.now() - 32 * 60 * 1000).toISOString(),
    latitude: 37.7749,
    longitude: -122.4194,
    address: '742 Evergreen Terrace, Springfield',
    accuracy: 2.8,
    speed: 0.0,
    eventType: EVENT_TYPES.ZONE_ENTRY,
    zoneName: 'Home Safe Zone',
    inSafeZone: true,
    battery: 90,
  },
  {
    id: 'loc-hist-3',
    date: 'Today',
    time: '3:20 PM',
    isoTime: new Date(Date.now() - 57 * 60 * 1000).toISOString(),
    latitude: 37.7760,
    longitude: -122.4165,
    address: 'Willow Creek Way (In Transit with School Bus)',
    accuracy: 6.5,
    speed: 18.2,
    eventType: EVENT_TYPES.BREADCRUMB,
    zoneName: null,
    inSafeZone: false,
    battery: 91,
  },
  {
    id: 'loc-hist-4',
    date: 'Today',
    time: '3:05 PM',
    isoTime: new Date(Date.now() - 72 * 60 * 1000).toISOString(),
    latitude: 37.7785,
    longitude: -122.4140,
    address: 'Oakwood Elementary School Gates',
    accuracy: 4.1,
    speed: 1.2,
    eventType: EVENT_TYPES.ZONE_EXIT,
    zoneName: 'Oakwood Elementary School',
    inSafeZone: true,
    battery: 92,
  },
  {
    id: 'loc-hist-5',
    date: 'Today',
    time: '1:30 PM',
    isoTime: new Date(Date.now() - 167 * 60 * 1000).toISOString(),
    latitude: 37.7783,
    longitude: -122.4142,
    address: 'Oakwood Elementary Sensory Room',
    accuracy: 3.5,
    speed: 0.1,
    eventType: EVENT_TYPES.BREADCRUMB,
    zoneName: 'Oakwood Elementary School',
    inSafeZone: true,
    battery: 94,
  },
  {
    id: 'loc-hist-6',
    date: 'Today',
    time: '8:30 AM',
    isoTime: new Date(Date.now() - 467 * 60 * 1000).toISOString(),
    latitude: 37.7785,
    longitude: -122.4140,
    address: 'Oakwood Elementary School Front Office',
    accuracy: 3.0,
    speed: 0.0,
    eventType: EVENT_TYPES.ZONE_ENTRY,
    zoneName: 'Oakwood Elementary School',
    inSafeZone: true,
    battery: 98,
  },
  {
    id: 'loc-hist-7',
    date: 'Today',
    time: '8:05 AM',
    isoTime: new Date(Date.now() - 492 * 60 * 1000).toISOString(),
    latitude: 37.7749,
    longitude: -122.4194,
    address: '742 Evergreen Terrace, Springfield',
    accuracy: 2.5,
    speed: 1.1,
    eventType: EVENT_TYPES.ZONE_EXIT,
    zoneName: 'Home Safe Zone',
    inSafeZone: true,
    battery: 100,
  },
];

// Helper: Haversine distance formula in meters
export function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // Earth's radius in meters
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

// Helper: Calculate compass bearing between two points
export function calculateBearing(lat1, lon1, lat2, lon2) {
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

  const y = Math.sin(deltaLambda) * Math.cos(phi2);
  const x =
    Math.cos(phi1) * Math.sin(phi2) -
    Math.sin(phi1) * Math.cos(phi2) * Math.cos(deltaLambda);
  const theta = Math.atan2(y, x);
  const brng = ((theta * 180) / Math.PI + 360) % 360;

  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'];
  const index = Math.round(brng / 45) % 8;
  return { degrees: Math.round(brng), cardinal: directions[index] };
}

class LocationService {
  constructor() {
    this.listeners = new Set();
    this.timer = null;
    this.simStep = 0;

    // Default Caregiver location (e.g. Work/Mobile)
    this.caregiverLocation = {
      name: 'Sarah Mitchell (Caregiver)',
      role: 'Caregiver Device',
      latitude: 37.7762,
      longitude: -122.4225,
      accuracy: 4.5,
      address: 'Downtown Medical Center Plaza',
      lastUpdated: new Date(),
    };

    // Default Child / Wearable location
    this.childLocation = {
      name: 'Leo Mitchell',
      device: 'NIVARA SmartBand #NV-8821',
      latitude: 37.7752,
      longitude: -122.4190,
      accuracy: 3.2,
      speed: 0.4,
      altitude: 42,
      heading: 45,
      address: '742 Evergreen Terrace (Near Courtyard)',
      zoneName: 'Home Safe Zone',
      currentZoneId: 'zone-home',
      isInSafeZone: true,
      battery: 88,
      isCharging: false,
      satellites: 14,
      signalDbm: -68,
      lastUpdated: new Date(),
    };

    // Last known location (cached fallback)
    this.lastKnownLocation = { ...this.childLocation };

    // Service State
    this.gpsStatus = GPS_STATUS.ACTIVE;
    this.isTracking = true;
    this.isLocationSharingOn = true;
    this.updateFrequency = 15; // in seconds
    this.accuracyMode = 'HIGH'; // 'HIGH', 'BALANCED', 'BATTERY_SAVER'
    this.activeMode = 'SIMULATION'; // 'SIMULATION' or 'REAL_GPS'
    this.safeZones = [...DEFAULT_SAFE_ZONES];
    this.locationHistory = [...INITIAL_LOCATION_HISTORY];
    this.notifications = [];
    this.alerts = [];

    // Simulation Waypoints for Demo Patrol
    this.simWaypoints = [
      { lat: 37.7752, lon: -122.4190, address: '742 Evergreen Terrace (Living Room & Yard)', speed: 0.3 },
      { lat: 37.7756, lon: -122.4185, address: 'Evergreen Terrace Walkway', speed: 1.1 },
      { lat: 37.7764, lon: -122.4172, address: 'Pinecrest Ave intersection', speed: 1.4 },
      { lat: 37.7775, lon: -122.4153, address: 'Approaching Willow Creek Rd', speed: 2.8 },
      { lat: 37.7785, lon: -122.4140, address: 'Oakwood Elementary School Gates', speed: 0.8 },
      { lat: 37.7783, lon: -122.4142, address: 'Oakwood Elementary Play Area', speed: 0.2 },
      { lat: 37.7770, lon: -122.4160, address: 'Willow Creek Way Walk', speed: 1.2 },
      { lat: 37.7750, lon: -122.4192, address: '742 Evergreen Terrace (Home Patio)', speed: 0.0 },
    ];

    this.initFromStorage();
  }

  async initFromStorage() {
    try {
      const storedZones = await AsyncStorage.getItem('nivara_safe_zones');
      if (storedZones) {
        this.safeZones = JSON.parse(storedZones);
      }
      const storedSharing = await AsyncStorage.getItem('nivara_loc_sharing');
      if (storedSharing !== null) {
        this.isLocationSharingOn = JSON.parse(storedSharing);
      }
      const storedFreq = await AsyncStorage.getItem('nivara_loc_frequency');
      if (storedFreq) {
        this.updateFrequency = parseInt(storedFreq, 10);
      }
    } catch (e) {
      console.log('[LocationService] storage init error:', e);
    }
    this.startTracking();
  }

  // Subscribe UI components to location changes
  subscribe(callback) {
    this.listeners.add(callback);
    // Send immediate initial snapshot
    callback(this.getState());
    return () => this.listeners.delete(callback);
  }

  notifyListeners() {
    const snapshot = this.getState();
    this.listeners.forEach((cb) => {
      try {
        cb(snapshot);
      } catch (err) {
        console.error('[LocationService] listener error:', err);
      }
    });
  }

  getState() {
    const distanceToCaregiver = calculateDistance(
      this.childLocation.latitude,
      this.childLocation.longitude,
      this.caregiverLocation.latitude,
      this.caregiverLocation.longitude
    );

    const bearingToChild = calculateBearing(
      this.caregiverLocation.latitude,
      this.caregiverLocation.longitude,
      this.childLocation.latitude,
      this.childLocation.longitude
    );

    return {
      childLocation: { ...this.childLocation },
      caregiverLocation: { ...this.caregiverLocation },
      lastKnownLocation: { ...this.lastKnownLocation },
      gpsStatus: this.gpsStatus,
      isTracking: this.isTracking,
      isLocationSharingOn: this.isLocationSharingOn,
      updateFrequency: this.updateFrequency,
      accuracyMode: this.accuracyMode,
      activeMode: this.activeMode,
      safeZones: [...this.safeZones],
      locationHistory: [...this.locationHistory],
      distanceToCaregiver: Math.round(distanceToCaregiver),
      bearingToChild,
      alerts: [...this.alerts],
      timestamp: new Date(),
    };
  }

  // Start periodic tracking loop
  startTracking() {
    if (this.timer) clearInterval(this.timer);
    this.isTracking = true;
    this.timer = setInterval(() => {
      this.tick();
    }, this.updateFrequency * 1000);
    this.notifyListeners();
  }

  stopTracking() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.isTracking = false;
    this.notifyListeners();
  }

  // Handle location update tick
  tick() {
    if (!this.isLocationSharingOn || this.gpsStatus === GPS_STATUS.OFFLINE) {
      return;
    }

    if (this.activeMode === 'REAL_GPS' && typeof navigator !== 'undefined' && navigator.geolocation) {
      this.fetchRealBrowserLocation();
      return;
    }

    // Otherwise run realistic simulated patrol step
    this.advanceSimulationStep();
  }

  advanceSimulationStep() {
    this.simStep = (this.simStep + 1) % this.simWaypoints.length;
    const wp = this.simWaypoints[this.simStep];

    // Add tiny realistic jitter (±0.00015 deg ~ 15m)
    const jitterLat = (Math.random() - 0.5) * 0.0001;
    const jitterLon = (Math.random() - 0.5) * 0.0001;

    const newLat = wp.lat + jitterLat;
    const newLon = wp.lon + jitterLon;

    this.updateChildPosition(newLat, newLon, wp.address, wp.speed, EVENT_TYPES.BREADCRUMB);
  }

  // Update child position and check geofence boundary transitions
  updateChildPosition(lat, lon, address, speed = 0, eventType = EVENT_TYPES.BREADCRUMB) {
    const prevZone = this.childLocation.currentZoneId;

    // Check which safe zone child is currently inside
    let currentActiveZone = null;
    for (const zone of this.safeZones) {
      if (!zone.active) continue;
      const dist = calculateDistance(lat, lon, zone.latitude, zone.longitude);
      if (dist <= zone.radius) {
        currentActiveZone = zone;
        break;
      }
    }

    const isInSafeZone = currentActiveZone !== null;
    const zoneName = currentActiveZone ? currentActiveZone.name : 'Outside Safe Zones';
    const currentZoneId = currentActiveZone ? currentActiveZone.id : null;

    // Detect zone entry / exit transition
    let detectedEvent = eventType;
    if (prevZone !== currentZoneId) {
      if (currentZoneId && !prevZone) {
        detectedEvent = EVENT_TYPES.ZONE_ENTRY;
        this.addAlert({
          id: `alert-${Date.now()}`,
          type: 'SAFE_ZONE_ENTRY',
          title: `Entered Safe Zone`,
          message: `Leo Mitchell safely arrived at ${currentActiveZone.name}.`,
          timestamp: new Date(),
          zoneId: currentZoneId,
        });
      } else if (!currentZoneId && prevZone) {
        detectedEvent = EVENT_TYPES.ZONE_EXIT;
        const previousZoneObj = this.safeZones.find((z) => z.id === prevZone);
        this.addAlert({
          id: `alert-${Date.now()}`,
          type: 'SAFE_ZONE_EXIT',
          title: `⚠️ Exited Safe Zone`,
          message: `Leo Mitchell left ${previousZoneObj?.name || 'Safe Zone'}. Live GPS tracking active.`,
          timestamp: new Date(),
          zoneId: prevZone,
        });
      }
    }

    // Battery simulation (subtle slow drain)
    const newBattery = Math.max(15, this.childLocation.battery - (Math.random() < 0.1 ? 1 : 0));

    // Dynamic accuracy based on GPS Status
    let accuracy = 3.0 + Math.random() * 1.5;
    if (this.gpsStatus === GPS_STATUS.WEAK) accuracy = 18.0 + Math.random() * 12.0;
    if (this.gpsStatus === GPS_STATUS.UNAVAILABLE) accuracy = 75.0;

    const newLocation = {
      name: 'Leo Mitchell',
      device: 'NIVARA SmartBand #NV-8821',
      latitude: parseFloat(lat.toFixed(6)),
      longitude: parseFloat(lon.toFixed(6)),
      accuracy: parseFloat(accuracy.toFixed(1)),
      speed: parseFloat(speed.toFixed(1)),
      altitude: 40 + Math.floor(Math.random() * 8),
      heading: (this.childLocation.heading + 25) % 360,
      address: address || `${lat.toFixed(4)}°N, ${Math.abs(lon).toFixed(4)}°W`,
      zoneName,
      currentZoneId,
      isInSafeZone,
      battery: newBattery,
      isCharging: false,
      satellites: this.gpsStatus === GPS_STATUS.ACTIVE ? 14 : this.gpsStatus === GPS_STATUS.WEAK ? 5 : 0,
      signalDbm: this.gpsStatus === GPS_STATUS.ACTIVE ? -65 : -95,
      lastUpdated: new Date(),
    };

    this.childLocation = newLocation;
    this.lastKnownLocation = { ...newLocation };

    // Record to history
    const now = new Date();
    const historyItem = {
      id: `hist-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      date: 'Today',
      time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      isoTime: now.toISOString(),
      latitude: newLocation.latitude,
      longitude: newLocation.longitude,
      address: newLocation.address,
      accuracy: newLocation.accuracy,
      speed: newLocation.speed,
      eventType: detectedEvent,
      zoneName: newLocation.zoneName,
      inSafeZone: newLocation.isInSafeZone,
      battery: newLocation.battery,
    };

    this.locationHistory = [historyItem, ...this.locationHistory.slice(0, 49)];
    this.notifyListeners();
  }

  addAlert(alertObj) {
    this.alerts = [alertObj, ...this.alerts.slice(0, 19)];
  }

  dismissAlert(alertId) {
    this.alerts = this.alerts.filter((a) => a.id !== alertId);
    this.notifyListeners();
  }

  clearAllAlerts() {
    this.alerts = [];
    this.notifyListeners();
  }

  // "Locate Now" action: triggers instant high-priority ping
  async locateNow() {
    this.gpsStatus = GPS_STATUS.ACTIVE;
    if (this.activeMode === 'REAL_GPS' && typeof navigator !== 'undefined' && navigator.geolocation) {
      await this.fetchRealBrowserLocation();
    } else {
      // Simulate rapid ping
      await new Promise((resolve) => setTimeout(resolve, 800));
      this.advanceSimulationStep();
      const current = this.childLocation;
      this.addAlert({
        id: `ping-${Date.now()}`,
        type: 'LOCATE_NOW',
        title: '📍 Live Location Ping Received',
        message: `High-precision fix locked at ${current.address} (±${current.accuracy}m).`,
        timestamp: new Date(),
      });
    }
    return this.getState();
  }

  // Switch between Real GPS and Simulation
  setMode(mode) {
    this.activeMode = mode; // 'REAL_GPS' or 'SIMULATION'
    if (mode === 'REAL_GPS') {
      this.fetchRealBrowserLocation();
    }
    this.notifyListeners();
  }

  // Real Web Geolocation API Integration
  fetchRealBrowserLocation() {
    return new Promise((resolve, reject) => {
      if (typeof navigator === 'undefined' || !navigator.geolocation) {
        this.gpsStatus = GPS_STATUS.UNAVAILABLE;
        this.notifyListeners();
        reject(new Error('Geolocation not supported on this device/browser'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          this.gpsStatus = GPS_STATUS.ACTIVE;
          const { latitude, longitude, accuracy, speed } = pos.coords;
          const addr = `Live Browser Coordinates: ${latitude.toFixed(5)}°, ${longitude.toFixed(5)}°`;
          this.updateChildPosition(latitude, longitude, addr, speed || 0, EVENT_TYPES.LOCATE_NOW);
          resolve(this.getState());
        },
        (err) => {
          console.warn('[LocationService] Geolocation error:', err);
          if (err.code === 1) {
            // Permission denied
            this.gpsStatus = GPS_STATUS.UNAVAILABLE;
          } else if (err.code === 2) {
            // Position unavailable
            this.gpsStatus = GPS_STATUS.WEAK;
          } else {
            this.gpsStatus = GPS_STATUS.OFFLINE;
          }
          this.notifyListeners();
          resolve(this.getState());
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 5000 }
      );
    });
  }

  // GPS State Switcher (for diagnostics / demo edge case testing)
  setGpsStatus(status) {
    this.gpsStatus = status;
    if (status === GPS_STATUS.OFFLINE) {
      this.addAlert({
        id: `status-${Date.now()}`,
        type: 'STATUS_OFFLINE',
        title: '🔴 GPS Signal Lost',
        message: 'Child SmartBand is offline. Showing last known location.',
        timestamp: new Date(),
      });
    } else if (status === GPS_STATUS.WEAK) {
      this.addAlert({
        id: `status-${Date.now()}`,
        type: 'STATUS_WEAK',
        title: '🟡 Weak Satellite Signal',
        message: 'GPS precision reduced to ±25m due to indoor obstruction.',
        timestamp: new Date(),
      });
    }
    this.notifyListeners();
  }

  // Location Sharing Toggle
  async setLocationSharing(enabled) {
    this.isLocationSharingOn = enabled;
    try {
      await AsyncStorage.setItem('nivara_loc_sharing', JSON.stringify(enabled));
    } catch (e) {}

    this.addAlert({
      id: `share-${Date.now()}`,
      type: 'SHARING_TOGGLED',
      title: enabled ? '🟢 Location Sharing Enabled' : '⏸️ Location Sharing Paused',
      message: enabled
        ? 'Real-time location is being broadcast to verified caregivers.'
        : 'Live location broadcast paused. Safe-zone entry/exit alerts remain active.',
      timestamp: new Date(),
    });

    this.notifyListeners();
  }

  // Update Frequency Selector
  async setUpdateFrequency(seconds) {
    this.updateFrequency = seconds;
    try {
      await AsyncStorage.setItem('nivara_loc_frequency', seconds.toString());
    } catch (e) {}
    this.startTracking();
  }

  // Accuracy Mode
  setAccuracyMode(mode) {
    this.accuracyMode = mode;
    this.notifyListeners();
  }

  // Safe Zone CRUD Operations
  async addSafeZone(zoneData) {
    const newZone = {
      id: `zone-${Date.now()}`,
      active: true,
      notifyOnEntry: true,
      notifyOnExit: true,
      schedule: 'Always Active',
      color: '#3B82F6',
      icon: '🛡️',
      radius: 150,
      ...zoneData,
    };
    this.safeZones = [newZone, ...this.safeZones];
    await this.persistSafeZones();
    this.tick(); // Re-evaluate geofence
    return newZone;
  }

  async updateSafeZone(zoneId, updates) {
    this.safeZones = this.safeZones.map((z) => (z.id === zoneId ? { ...z, ...updates } : z));
    await this.persistSafeZones();
    this.tick();
  }

  async deleteSafeZone(zoneId) {
    this.safeZones = this.safeZones.filter((z) => z.id !== zoneId);
    await this.persistSafeZones();
    this.tick();
  }

  async toggleSafeZoneActive(zoneId) {
    this.safeZones = this.safeZones.map((z) =>
      z.id === zoneId ? { ...z, active: !z.active } : z
    );
    await this.persistSafeZones();
    this.tick();
  }

  async persistSafeZones() {
    try {
      await AsyncStorage.setItem('nivara_safe_zones', JSON.stringify(this.safeZones));
    } catch (e) {}
    this.notifyListeners();
  }

  // Clear location history
  clearLocationHistory() {
    this.locationHistory = [];
    this.notifyListeners();
  }
}

export const locationService = new LocationService();
export default locationService;
