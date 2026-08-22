import { locationService } from './locationService';

class BackgroundLocationService {
  constructor() {
    this.isTracking = false;
    this.trackingInterval = null;
    this.updateIntervalMs = 30000;
    this.listeners = new Set();
    this.lastLocation = null;
    this.permissionGranted = true;
  }

  async requestPermissions() {
    try {
      // In web/expo environment, verify permissions
      if (typeof navigator !== 'undefined' && navigator.permissions) {
        try {
          const result = await navigator.permissions.query({ name: 'geolocation' });
          this.permissionGranted = result.state === 'granted' || result.state === 'prompt';
        } catch (e) {
          this.permissionGranted = true;
        }
      }
      return this.permissionGranted;
    } catch (err) {
      return false;
    }
  }

  async startBackgroundTracking(intervalMs = 30000) {
    this.updateIntervalMs = intervalMs;
    const hasPerm = await this.requestPermissions();
    if (!hasPerm) {
      return { success: false, error: 'PERMISSION_DENIED' };
    }

    this.isTracking = true;
    locationService.setMode('REALTIME');

    if (this.trackingInterval) clearInterval(this.trackingInterval);
    this.trackingInterval = setInterval(() => {
      if (this.isTracking) {
        const state = locationService.getState();
        this.lastLocation = state?.childLocation;
        this.notifyListeners({
          location: this.lastLocation,
          timestamp: new Date().toISOString(),
          isBackground: true,
        });
      }
    }, this.updateIntervalMs);

    return { success: true, tracking: true };
  }

  async stopBackgroundTracking() {
    this.isTracking = false;
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
      this.trackingInterval = null;
    }
    locationService.setMode('BALANCED');
    return { success: true, tracking: false };
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notifyListeners(data) {
    this.listeners.forEach((fn) => {
      try {
        fn(data);
      } catch (e) {}
    });
  }

  getStatus() {
    return {
      isTracking: this.isTracking,
      provider: 'GPS_SATELLITE_HYBRID',
      updateIntervalMs: this.updateIntervalMs,
      permissionGranted: this.permissionGranted,
      lastLocation: this.lastLocation,
    };
  }
}

export const backgroundLocationService = new BackgroundLocationService();
export default backgroundLocationService;
