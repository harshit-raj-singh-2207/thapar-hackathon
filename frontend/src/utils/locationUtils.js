/**
 * Haversine formula to calculate the distance between two GPS coordinates in meters.
 */
export function calculateDistance(lat1, lon1, lat2, lon2) {
  if (!lat1 || !lon1 || !lat2 || !lon2) return 0;
  const R = 6371e3; // Earth radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return Math.round(R * c);
}

/**
 * Checks whether a given coordinate point is inside a circular safe zone.
 */
export function isPointInsideSafeZone(point, zone) {
  if (!point || !zone) return false;
  const dist = calculateDistance(
    point.latitude,
    point.longitude,
    zone.latitude,
    zone.longitude
  );
  return dist <= (zone.radius || 100);
}

/**
 * Formats seconds into human-readable relative string.
 */
export function formatRelativeSeconds(seconds) {
  if (!seconds || seconds <= 5) return 'Just now';
  if (seconds < 60) return `${seconds} seconds ago`;
  const mins = Math.floor(seconds / 60);
  return `${mins} min${mins > 1 ? 's' : ''} ago`;
}

/**
 * Calculates log-distance path loss distance from RSSI (BLE Proximity).
 */
export function calculateBLEProximity(rssi, txPower = -59, n = 2.0) {
  if (!rssi || rssi === 0) return 999;
  const ratio = (txPower - rssi) / (10 * n);
  const dist = Math.pow(10, ratio);
  return parseFloat(dist.toFixed(1));
}
