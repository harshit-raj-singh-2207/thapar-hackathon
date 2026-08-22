// NIVARA Phone ↔ SmartBand Bluetooth BLE & Separation Detection Service

import AsyncStorage from '@react-native-async-storage/async-storage';
import { playSeparationAlarmSound, playRadarPingSound, playBuzzerSound } from '../../utils/soundEffects';

export const BLE_STATUS = {
  CONNECTED: 'CONNECTED',
  PAIRING: 'PAIRING',
  DISCONNECTED: 'DISCONNECTED',
  SCANNING: 'SCANNING',
  ERROR: 'ERROR',
};

export const PROXIMITY_ZONE = {
  IMMEDIATE: 'IMMEDIATE', // < 2 meters (Beside Caregiver)
  NEAR: 'NEAR',           // 2 - 5 meters (Safe Proximity)
  FAR: 'FAR',             // 5 - 12 meters (Boundary Warning)
  OUT_OF_RANGE: 'OUT_OF_RANGE', // > 12 meters (Separation Alert)
};

// Estimate distance from RSSI using standard Log-Distance Path Loss model
export function rssiToDistance(rssi, txPower = -59, n = 2.4) {
  if (!rssi || rssi >= 0) return 0.5;
  const ratio = (txPower - rssi) / (10 * n);
  const distance = Math.pow(10, ratio);
  return Math.min(50, Math.max(0.2, parseFloat(distance.toFixed(1))));
}

// Convert distance to proximity zone category
export function getProximityZone(distanceMeters) {
  if (distanceMeters <= 2.0) return PROXIMITY_ZONE.IMMEDIATE;
  if (distanceMeters <= 5.0) return PROXIMITY_ZONE.NEAR;
  if (distanceMeters <= 12.0) return PROXIMITY_ZONE.FAR;
  return PROXIMITY_ZONE.OUT_OF_RANGE;
}

class BluetoothService {
  constructor() {
    this.listeners = new Set();
    this.radarTimer = null;
    this.separationTimer = null;
    this.breachDuration = 0;

    // Connected Band Hardware Profile
    this.device = {
      id: 'NV-BAND-8821-BLE',
      name: 'Leo Mitchell SmartBand',
      model: 'NIVARA CoreBand v2.4',
      mac: 'E4:95:6E:41:88:21',
      firmware: 'v2.4.12-secure',
      battery: 88,
      isCharging: false,
      rssi: -58, // in dBm
      txPower: -59,
      distanceMeters: 1.4,
      proximityZone: PROXIMITY_ZONE.IMMEDIATE,
      lastSync: new Date(),
      lastSeenLocation: '742 Evergreen Terrace (Living Room)',
    };

    // Bluetooth Connection & Tether State
    this.status = BLE_STATUS.CONNECTED;
    this.tetherAlarmEnabled = true;
    this.separationThreshold = 10; // in meters (alert triggers if distance > threshold)
    this.autoReconnect = true;
    this.alertSoundEnabled = true;
    this.vibrateEnabled = true;
    this.isBuzzerActive = false;
    this.separationBreachActive = false;

    // Simulation Walk Waypoints for Proximity Radar Demo
    this.radarSimIndex = 0;
    this.radarSimSteps = [
      { rssi: -48, desc: 'Beside Caregiver (Arm Reach)' },
      { rssi: -54, desc: 'In Living Room (2m)' },
      { rssi: -62, desc: 'Walking towards hallway (4m)' },
      { rssi: -72, desc: 'In Kitchen area (7m)' },
      { rssi: -84, desc: 'Near backyard patio door (11m - Warning)' },
      { rssi: -95, desc: 'Stepped into backyard (16m - SEPARATION BREACH)' },
      { rssi: -82, desc: 'Returning towards house (10m)' },
      { rssi: -60, desc: 'Back in hallway (3.5m)' },
    ];

    this.initStorage();
  }

  async initStorage() {
    try {
      const storedTether = await AsyncStorage.getItem('nivara_tether_enabled');
      if (storedTether !== null) {
        this.tetherAlarmEnabled = JSON.parse(storedTether);
      }
      const storedThresh = await AsyncStorage.getItem('nivara_separation_threshold');
      if (storedThresh) {
        this.separationThreshold = parseInt(storedThresh, 10);
      }
    } catch (e) {}

    this.startRadarLoop();
  }

  subscribe(callback) {
    this.listeners.add(callback);
    callback(this.getState());
    return () => this.listeners.delete(callback);
  }

  notifyListeners() {
    const snapshot = this.getState();
    this.listeners.forEach((cb) => {
      try {
        cb(snapshot);
      } catch (e) {
        console.error('[BluetoothService] listener error:', e);
      }
    });
  }

  getState() {
    return {
      status: this.status,
      device: { ...this.device },
      tetherAlarmEnabled: this.tetherAlarmEnabled,
      separationThreshold: this.separationThreshold,
      autoReconnect: this.autoReconnect,
      alertSoundEnabled: this.alertSoundEnabled,
      vibrateEnabled: this.vibrateEnabled,
      isBuzzerActive: this.isBuzzerActive,
      separationBreachActive: this.separationBreachActive,
      breachDuration: this.breachDuration,
      timestamp: new Date(),
    };
  }

  // Periodic Radar Ping & Proximity Assessment
  startRadarLoop() {
    if (this.radarTimer) clearInterval(this.radarTimer);
    this.radarTimer = setInterval(() => {
      this.tickRadar();
    }, 2500);
  }

  stopRadarLoop() {
    if (this.radarTimer) {
      clearInterval(this.radarTimer);
      this.radarTimer = null;
    }
  }

  tickRadar() {
    if (this.status !== BLE_STATUS.CONNECTED) return;

    // Simulate RSSI subtle jitter or patrol
    const step = this.radarSimSteps[this.radarSimIndex];
    const jitter = Math.floor((Math.random() - 0.5) * 4);
    const newRssi = Math.min(-35, Math.max(-105, step.rssi + jitter));
    const dist = rssiToDistance(newRssi, this.device.txPower);
    const zone = getProximityZone(dist);

    this.device = {
      ...this.device,
      rssi: newRssi,
      distanceMeters: dist,
      proximityZone: zone,
      lastSync: new Date(),
    };

    // Check Separation Tether Threshold
    if (this.tetherAlarmEnabled) {
      if (dist > this.separationThreshold || zone === PROXIMITY_ZONE.OUT_OF_RANGE) {
        this.breachDuration += 2.5;
        if (!this.separationBreachActive) {
          this.triggerSeparationBreach();
        }
      } else {
        if (this.separationBreachActive) {
          this.clearSeparationBreach();
        }
        this.breachDuration = 0;
      }
    }

    this.notifyListeners();
  }

  // Advance simulation manually or via slider
  setSimulatedDistance(distMeters) {
    const calculatedRssi = Math.round(this.device.txPower - 10 * 2.4 * Math.log10(distMeters));
    const zone = getProximityZone(distMeters);

    this.device = {
      ...this.device,
      distanceMeters: distMeters,
      rssi: calculatedRssi,
      proximityZone: zone,
      lastSync: new Date(),
    };

    if (this.tetherAlarmEnabled && distMeters > this.separationThreshold) {
      this.triggerSeparationBreach();
    } else if (this.separationBreachActive) {
      this.clearSeparationBreach();
    }

    this.notifyListeners();
  }

  // Trigger Out-of-Range Separation Breach
  triggerSeparationBreach() {
    this.separationBreachActive = true;
    if (this.alertSoundEnabled) {
      playSeparationAlarmSound();
    }
    this.notifyListeners();
  }

  clearSeparationBreach() {
    this.separationBreachActive = false;
    this.breachDuration = 0;
    this.notifyListeners();
  }

  // "Buzzer / Find My Band" Action
  async triggerFindMyBand() {
    this.isBuzzerActive = true;
    playBuzzerSound();
    this.notifyListeners();

    setTimeout(() => {
      this.isBuzzerActive = false;
      this.notifyListeners();
    }, 3000);
  }

  // Web Bluetooth API Integration (Real Device Connection)
  async scanAndConnectRealBLE() {
    this.status = BLE_STATUS.SCANNING;
    this.notifyListeners();

    if (typeof navigator !== 'undefined' && navigator.bluetooth) {
      try {
        const bleDevice = await navigator.bluetooth.requestDevice({
          filters: [{ namePrefix: 'NV-BAND' }, { namePrefix: 'NIVARA' }],
          optionalServices: ['battery_service', 'heart_rate'],
        });

        this.status = BLE_STATUS.PAIRING;
        this.notifyListeners();

        const server = await bleDevice.gatt.connect();
        this.device.id = bleDevice.id || 'NV-BAND-8821-REAL';
        this.device.name = bleDevice.name || 'NIVARA SmartBand';
        this.status = BLE_STATUS.CONNECTED;
        this.notifyListeners();
        return true;
      } catch (err) {
        console.warn('[BluetoothService] Real BLE connect failed, falling back to simulated band:', err);
        // Graceful fallback to simulated BLE band
        this.simulateConnect();
        return false;
      }
    } else {
      // Simulate BLE connection flow
      this.simulateConnect();
      return true;
    }
  }

  simulateConnect() {
    this.status = BLE_STATUS.PAIRING;
    this.notifyListeners();

    setTimeout(() => {
      this.status = BLE_STATUS.CONNECTED;
      this.device.rssi = -55;
      this.device.distanceMeters = 1.2;
      this.device.proximityZone = PROXIMITY_ZONE.IMMEDIATE;
      this.notifyListeners();
    }, 1200);
  }

  disconnectBand() {
    this.status = BLE_STATUS.DISCONNECTED;
    this.separationBreachActive = false;
    this.notifyListeners();
  }

  // Configuration Toggles
  async setTetherAlarm(enabled) {
    this.tetherAlarmEnabled = enabled;
    if (!enabled) {
      this.clearSeparationBreach();
    }
    try {
      await AsyncStorage.setItem('nivara_tether_enabled', JSON.stringify(enabled));
    } catch (e) {}
    this.notifyListeners();
  }

  async setSeparationThreshold(meters) {
    this.separationThreshold = meters;
    try {
      await AsyncStorage.setItem('nivara_separation_threshold', meters.toString());
    } catch (e) {}
    this.notifyListeners();
  }

  setAlertSound(enabled) {
    this.alertSoundEnabled = enabled;
    this.notifyListeners();
  }

  setAutoReconnect(enabled) {
    this.autoReconnect = enabled;
    this.notifyListeners();
  }
}

export const bluetoothService = new BluetoothService();
export default bluetoothService;
