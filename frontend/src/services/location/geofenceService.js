import { locationService } from './locationService';
import { isPointInsideSafeZone, calculateDistance } from '../../utils/locationUtils';

class GeofenceService {
  constructor() {
    this.activeZones = [];
    this.currentInsideZoneIds = new Set();
    this.listeners = new Set();
  }

  setZones(zones = []) {
    this.activeZones = zones;
  }

  evaluateLocation(currentCoord, zones = this.activeZones) {
    if (!currentCoord || !zones.length) return null;

    let insideZone = null;
    const currentInside = new Set();

    for (const zone of zones) {
      if (zone.active && isPointInsideSafeZone(currentCoord, zone)) {
        insideZone = zone;
        currentInside.add(zone.id);

        if (!this.currentInsideZoneIds.has(zone.id)) {
          this.onGeofenceTransition('ENTER', zone, currentCoord);
        }
      }
    }

    this.currentInsideZoneIds.forEach((prevId) => {
      if (!currentInside.has(prevId)) {
        const exitedZone = zones.find((z) => z.id === prevId);
        if (exitedZone) {
          this.onGeofenceTransition('EXIT', exitedZone, currentCoord);
        }
      }
    });

    this.currentInsideZoneIds = currentInside;
    return insideZone;
  }

  onGeofenceTransition(transitionType, zone, coord) {
    const isEnter = transitionType === 'ENTER';
    const event = {
      id: `gf-${Date.now()}`,
      type: isEnter ? 'SAFE_ZONE_ENTRY' : 'SAFE_ZONE_EXIT',
      title: isEnter ? `Entered ${zone.name}` : `Exited ${zone.name}`,
      desc: isEnter
        ? `Child safely arrived inside '${zone.name}' (${zone.address || 'Safe Area'}).`
        : `Child departed '${zone.name}' boundary.`,
      zoneId: zone.id,
      zoneName: zone.name,
      location: zone.address || `${coord?.latitude?.toFixed(4)}, ${coord?.longitude?.toFixed(4)}`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      timestamp: new Date().toISOString(),
      isSafe: isEnter,
      battery: '84%',
      gpsAccuracy: '±3m',
    };

    locationService.addAlert(event);
    this.notifyListeners(event);
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notifyListeners(event) {
    this.listeners.forEach((fn) => {
      try {
        fn(event);
      } catch (e) {}
    });
  }

  getDistanceToZone(point, zone) {
    if (!point || !zone) return null;
    return calculateDistance(point.latitude, point.longitude, zone.latitude, zone.longitude);
  }
}

export const geofenceService = new GeofenceService();
export default geofenceService;
