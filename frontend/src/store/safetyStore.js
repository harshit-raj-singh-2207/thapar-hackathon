import { create } from 'zustand';
import { DEFAULT_SAFE_ZONES, DEFAULT_EMERGENCY_CONTACTS } from '../constants/safetyConstants';
import { safetyApi } from '../services/api/safetyApi';

export const useSafetyStore = create((set, get) => ({
  // Child & Safety Status
  childId: 'child-leo-1',
  childName: 'Leo Mitchell',
  childAge: 8,
  childStatus: 'Safe — Inside Home Sanctuary',
  isSafe: true,
  currentZone: 'Home Safe Zone',
  batteryLevel: 88,
  gpsStatus: 'ACTIVE',
  bleConnected: true,
  separationDistance: 1.4,
  isLocationSharingOn: true,
  accuracyMode: 'HIGH',

  // Real-time location
  currentLocation: {
    latitude: 37.7749,
    longitude: -122.4194,
    accuracy: 3.5,
    address: '742 Evergreen Terrace, Springfield',
    timestamp: new Date().toISOString(),
  },
  locationLoading: false,
  locationError: null,

  // Geofences / Safe Zones
  safeZones: DEFAULT_SAFE_ZONES,
  safeZonesLoading: false,

  // Emergency Contacts
  emergencyContacts: DEFAULT_EMERGENCY_CONTACTS,
  contactsLoading: false,

  // Active Alerts & Emergency State
  activeAlerts: [],
  activeEmergency: null,
  isEmergencyActive: false,
  emergencyLoading: false,

  // Safety Events Log
  safetyEvents: [],
  eventsLoading: false,

  // Device & Overview
  safetyOverview: null,
  overviewLoading: false,

  // Actions
  setChildId: (id) => set({ childId: id }),

  fetchSafetyStatus: async () => {
    try {
      const childId = get().childId;
      const data = await safetyApi.getSafetyStatus(childId);
      if (data) {
        set({
          isSafe: data.isSafe ?? true,
          childName: data.childName || get().childName,
          childAge: data.age || get().childAge,
          childStatus: data.status || get().childStatus,
          batteryLevel: data.batteryLevel || data.battery || get().batteryLevel,
          gpsStatus: data.gpsStatus || get().gpsStatus,
          bleConnected: data.bleConnected ?? get().bleConnected,
          currentZone: data.currentZone || get().currentZone,
          separationDistance: data.separationDistance || get().separationDistance,
        });
      }
    } catch (e) {}
  },

  fetchLocation: async () => {
    set({ locationLoading: true, locationError: null });
    try {
      const childId = get().childId;
      const loc = await safetyApi.getCurrentLocation(childId);
      set({ currentLocation: loc, locationLoading: false });
    } catch (err) {
      set({ locationLoading: false, locationError: err.message });
    }
  },

  fetchSafeZones: async () => {
    set({ safeZonesLoading: true });
    try {
      const childId = get().childId;
      const zones = await safetyApi.getSafeZones(childId);
      set({ safeZones: zones || DEFAULT_SAFE_ZONES, safeZonesLoading: false });
    } catch (e) {
      set({ safeZonesLoading: false });
    }
  },

  addSafeZone: async (zoneData) => {
    const created = await safetyApi.createSafeZone({
      child_id: get().childId,
      ...zoneData,
    });
    set((state) => ({ safeZones: [created, ...state.safeZones] }));
    return created;
  },

  updateSafeZone: async (zoneId, zoneData) => {
    const updated = await safetyApi.updateSafeZone(zoneId, zoneData);
    set((state) => ({
      safeZones: state.safeZones.map((z) => (z.id === zoneId ? { ...z, ...updated } : z)),
    }));
    return updated;
  },

  removeSafeZone: async (zoneId) => {
    await safetyApi.deleteSafeZone(zoneId);
    set((state) => ({ safeZones: state.safeZones.filter((z) => z.id !== zoneId) }));
  },

  toggleSafeZoneActive: (zoneId) => {
    set((state) => ({
      safeZones: state.safeZones.map((z) =>
        z.id === zoneId ? { ...z, active: !z.active } : z
      ),
    }));
  },

  fetchEmergencyContacts: async () => {
    set({ contactsLoading: true });
    try {
      const childId = get().childId;
      const contacts = await safetyApi.getEmergencyContacts(childId);
      set({ emergencyContacts: contacts || DEFAULT_EMERGENCY_CONTACTS, contactsLoading: false });
    } catch (e) {
      set({ contactsLoading: false });
    }
  },

  addEmergencyContact: async (contactData) => {
    const created = await safetyApi.addEmergencyContact({
      child_id: get().childId,
      ...contactData,
    });
    set((state) => ({ emergencyContacts: [...state.emergencyContacts, created] }));
    return created;
  },

  updateEmergencyContact: async (contactId, contactData) => {
    const updated = await safetyApi.updateEmergencyContact(contactId, contactData);
    set((state) => ({
      emergencyContacts: state.emergencyContacts.map((c) =>
        c.id === contactId ? { ...c, ...updated } : c
      ),
    }));
  },

  removeEmergencyContact: async (contactId) => {
    await safetyApi.deleteEmergencyContact(contactId);
    set((state) => ({
      emergencyContacts: state.emergencyContacts.filter((c) => c.id !== contactId),
    }));
  },

  setPrimaryContact: (contactId) => {
    set((state) => ({
      emergencyContacts: state.emergencyContacts.map((c) => ({
        ...c,
        isPrimary: c.id === contactId,
      })),
    }));
  },

  triggerSOS: async (customPayload = {}) => {
    set({ emergencyLoading: true });
    const payload = {
      child_id: get().childId,
      type: 'SOS_PANIC',
      childName: get().childName,
      location: get().currentLocation,
      timestamp: new Date().toISOString(),
      ...customPayload,
    };
    try {
      const res = await safetyApi.triggerEmergency(payload);
      set({
        isEmergencyActive: true,
        activeEmergency: res,
        isSafe: false,
        emergencyLoading: false,
      });
      get().addAlert({
        id: `sos-${Date.now()}`,
        type: 'SOS_TRIGGERED',
        title: 'CRITICAL ALERT: SOS Emergency Triggered',
        message: `Panic alert broadcasted with live location at ${get().currentLocation?.address || 'Current Coordinates'}.`,
        timestamp: new Date().toISOString(),
        acknowledged: false,
      });
      return res;
    } catch (e) {
      set({ isEmergencyActive: true, isSafe: false, emergencyLoading: false });
    }
  },

  resolveEmergency: async (emergencyId, notes = 'Emergency resolved by caregiver.') => {
    set({ emergencyLoading: true });
    try {
      await safetyApi.resolveEmergency(emergencyId || get().activeEmergency?.id, notes);
    } catch (e) {}
    set({
      isEmergencyActive: false,
      activeEmergency: null,
      isSafe: true,
      emergencyLoading: false,
    });
  },

  fetchSafetyEvents: async (params = {}) => {
    set({ eventsLoading: true });
    try {
      const childId = get().childId;
      const events = await safetyApi.getSafetyEvents({ child_id: childId, ...params });
      set({ safetyEvents: events || [], eventsLoading: false });
    } catch (e) {
      set({ eventsLoading: false });
    }
  },

  fetchSafetyOverview: async () => {
    set({ overviewLoading: true });
    try {
      const childId = get().childId;
      const overview = await safetyApi.getSafetyOverview(childId);
      set({ safetyOverview: overview, overviewLoading: false });
      return overview;
    } catch (e) {
      set({ overviewLoading: false });
    }
  },

  addAlert: (alert) =>
    set((state) => ({
      activeAlerts: [
        { id: `alert-${Date.now()}`, timestamp: new Date().toISOString(), acknowledged: false, ...alert },
        ...state.activeAlerts,
      ],
    })),

  acknowledgeAlert: (alertId) =>
    set((state) => ({
      activeAlerts: state.activeAlerts.map((a) =>
        a.id === alertId ? { ...a, acknowledged: true } : a
      ),
    })),

  clearAlerts: () => set({ activeAlerts: [] }),

  setBatteryLevel: (level) => set({ batteryLevel: level }),
  setGpsStatus: (status) => set({ gpsStatus: status }),
  setBleConnected: (connected) => set({ bleConnected: connected }),
  setSeparationDistance: (dist) => set({ separationDistance: dist }),
  toggleLocationSharing: () =>
    set((state) => ({ isLocationSharingOn: !state.isLocationSharingOn })),
}));

export default useSafetyStore;
