import { useEffect, useCallback } from 'react';
import { useSafetyStore } from '../store/safetyStore';
import { locationService } from '../services/location/locationService';
import { bluetoothService } from '../services/bluetooth/bluetoothService';

export function useSafety() {
  const store = useSafetyStore();

  useEffect(() => {
    store.fetchSafetyStatus();
    store.fetchSafeZones();
    store.fetchEmergencyContacts();
    store.fetchSafetyEvents();

    const unsubLoc = locationService.subscribe((locState) => {
      if (locState?.childLocation) {
        store.setBatteryLevel(locState.childLocation.battery || 84);
        store.setGpsStatus(locState.gpsStatus || 'ACTIVE');
      }
    });

    const unsubBle = bluetoothService.subscribe((bleState) => {
      store.setBleConnected(bleState?.status === 'CONNECTED');
      if (bleState?.device?.distanceMeters) {
        store.setSeparationDistance(bleState.device.distanceMeters);
      }
    });

    return () => {
      unsubLoc();
      unsubBle();
    };
  }, []);

  const triggerEmergency = useCallback(
    async (payload) => {
      return await store.triggerSOS(payload);
    },
    [store]
  );

  const resolveEmergency = useCallback(
    async (emergencyId) => {
      return await store.resolveEmergency(emergencyId);
    },
    [store]
  );

  return {
    ...store,
    triggerEmergency,
    resolveEmergency,
  };
}

export default useSafety;
