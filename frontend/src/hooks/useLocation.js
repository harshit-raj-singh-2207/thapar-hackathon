import { useState, useEffect, useCallback } from 'react';
import { locationService } from '../services/location/locationService';
import { backgroundLocationService } from '../services/location/backgroundLocation';
import { useSafetyStore } from '../store/safetyStore';

export function useLocation() {
  const [locationState, setLocationState] = useState(locationService.getState());
  const [isBackgroundTracking, setIsBackgroundTracking] = useState(
    backgroundLocationService.isTracking
  );
  const { currentLocation, fetchLocation, locationLoading, locationError } =
    useSafetyStore();

  useEffect(() => {
    const unsub = locationService.subscribe((s) => setLocationState(s));
    const unsubBg = backgroundLocationService.subscribe(() => {
      setIsBackgroundTracking(backgroundLocationService.isTracking);
    });

    return () => {
      unsub();
      unsubBg();
    };
  }, []);

  const locateNow = useCallback(async () => {
    await fetchLocation();
    return await locationService.locateNow();
  }, [fetchLocation]);

  const toggleBackgroundTracking = useCallback(async () => {
    if (isBackgroundTracking) {
      await backgroundLocationService.stopBackgroundTracking();
      setIsBackgroundTracking(false);
    } else {
      await backgroundLocationService.startBackgroundTracking();
      setIsBackgroundTracking(true);
    }
  }, [isBackgroundTracking]);

  return {
    ...locationState,
    currentLocation: locationState?.childLocation || currentLocation,
    locationLoading,
    locationError,
    isBackgroundTracking,
    locateNow,
    refreshLocation: locateNow,
    toggleBackgroundTracking,
    addSafeZone: (z) => locationService.addSafeZone(z),
    deleteSafeZone: (id) => locationService.deleteSafeZone(id),
    setMode: (m) => locationService.setMode(m),
    setAccuracyMode: (a) => locationService.setAccuracyMode(a),
    setUpdateFrequency: (f) => locationService.setUpdateFrequency(f),
    toggleSharing: () =>
      locationService.setLocationSharing(!locationState?.isLocationSharingOn),
  };
}

export default useLocation;
