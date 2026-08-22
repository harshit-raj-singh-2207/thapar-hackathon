export const GPS_ACCURACY_MODES = {
  HIGH: 'HIGH',
  BALANCED: 'BALANCED',
  BATTERY_SAVER: 'BATTERY_SAVER',
};

export const GPS_STATUS_TYPES = {
  ACTIVE: 'ACTIVE',
  WEAK: 'WEAK',
  UNAVAILABLE: 'UNAVAILABLE',
  OFFLINE: 'OFFLINE',
};

export const BLE_CONNECTION_STATUS = {
  CONNECTED: 'CONNECTED',
  CONNECTING: 'CONNECTING',
  DISCONNECTED: 'DISCONNECTED',
  ERROR: 'ERROR',
};

export const SAFETY_EVENT_TYPES = {
  SOS_TRIGGERED: 'SOS_TRIGGERED',
  SAFE_ZONE_ENTRY: 'SAFE_ZONE_ENTRY',
  SAFE_ZONE_EXIT: 'SAFE_ZONE_EXIT',
  BAND_CONNECTED: 'BAND_CONNECTED',
  BAND_DISCONNECTED: 'BAND_DISCONNECTED',
  SEPARATION_DETECTED: 'SEPARATION_DETECTED',
  GPS_UNAVAILABLE: 'GPS_UNAVAILABLE',
  LOW_BATTERY: 'LOW_BATTERY',
  LOCATION_UPDATED: 'LOCATION_UPDATED',
};

export const ZONE_TYPES = [
  { key: 'Home', label: 'Home', icon: '🏠', color: '#2563EB' },
  { key: 'School', label: 'School', icon: '🎓', color: '#8B5CF6' },
  { key: 'Therapy', label: 'Therapy Center', icon: '🏥', color: '#059669' },
  { key: 'Family', label: "Grandparents' / Family", icon: '🏡', color: '#D97706' },
  { key: 'Park', label: 'Park / Play Area', icon: '🌳', color: '#10B981' },
  { key: 'Other', label: 'Other Safe Zone', icon: '📍', color: '#64748B' },
];

export const UPDATE_FREQUENCIES = [
  { label: 'Real-time (10s)', value: 10000, description: 'High precision active tracking' },
  { label: 'Standard (30s)', value: 30000, description: 'Balanced battery & accuracy' },
  { label: 'Eco (1 min)', value: 60000, description: 'Battery saving for long days' },
  { label: 'Periodic (5 min)', value: 300000, description: 'Low power background tracking' },
];

export const PROXIMITY_ZONES = {
  IMMEDIATE: { key: 'IMMEDIATE', label: 'Immediate (< 2m)', color: '#10B981' },
  NEAR: { key: 'NEAR', label: 'Near (2m - 5m)', color: '#3B82F6' },
  FAR: { key: 'FAR', label: 'Far (5m - 12m)', color: '#F59E0B' },
  OUT_OF_RANGE: { key: 'OUT_OF_RANGE', label: 'Separated (> 12m)', color: '#EF4444' },
};

export const SEPARATION_DEFAULTS = {
  THRESHOLD_METERS: 12,
  ALERT_DELAY_SECONDS: 30,
  AUTO_RECONNECT: true,
  BUZZER_DURATION_MS: 3000,
};

export const SAFE_ZONE_ICONS = ['🏠', '🎓', '🏥', '🏡', '🌳', '⚽', '🎨', '🛒', '🏢', '🛡️'];

export const DEFAULT_SAFE_ZONES = [
  {
    id: 'zone-home',
    name: 'Home Sanctuary',
    address: '123 Maple Street, Model Town, Ludhiana',
    radius: 100,
    icon: '🏠',
    zoneType: 'Home',
    active: true,
    color: '#2563EB',
    latitude: 30.9010,
    longitude: 75.8573,
    isOccupied: true,
  },
  {
    id: 'zone-school',
    name: 'Oakridge School',
    address: '456 Oak Avenue, Civil Lines, Ludhiana',
    radius: 150,
    icon: '🎓',
    zoneType: 'School',
    active: true,
    color: '#8B5CF6',
    latitude: 30.9120,
    longitude: 75.8450,
    isOccupied: false,
  },
  {
    id: 'zone-therapy',
    name: 'Sensory Steps Therapy Center',
    address: '78 Mall Road, Ludhiana',
    radius: 120,
    icon: '🏥',
    zoneType: 'Therapy',
    active: true,
    color: '#059669',
    latitude: 30.8950,
    longitude: 75.8320,
    isOccupied: false,
  },
  {
    id: 'zone-grandparents',
    name: "Grandparents' Home",
    address: '12 Park View Colony, Ludhiana',
    radius: 80,
    icon: '🏡',
    zoneType: 'Family',
    active: true,
    color: '#D97706',
    latitude: 30.8870,
    longitude: 75.8610,
    isOccupied: false,
  },
];

export const DEFAULT_EMERGENCY_CONTACTS = [
  {
    id: 'ec-1',
    name: 'Dr. Jordan Patel (Caregiver)',
    relationship: 'Mother / Primary Caregiver',
    phone: '+91 98765 43210',
    isPrimary: true,
    priority: 1,
    avatar: '👩‍⚕️',
  },
  {
    id: 'ec-2',
    name: 'Sarah Mitchell',
    relationship: 'Aunt / Co-Caregiver',
    phone: '+91 98123 45678',
    isPrimary: false,
    priority: 2,
    avatar: '👩',
  },
  {
    id: 'ec-3',
    name: 'David Jennings (School Coordinator)',
    relationship: 'Special Education Liaison',
    phone: '+91 98234 56789',
    isPrimary: false,
    priority: 3,
    avatar: '👨‍🏫',
  },
];
