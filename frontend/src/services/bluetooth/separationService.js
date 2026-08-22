import { bluetoothService, PROXIMITY_ZONE } from './bluetoothService';
import { playSeparationAlarmSound } from '../../utils/soundEffects';
import { locationService } from '../location/locationService';

export const separationService = {
  setSeparationThreshold: (meters) => {
    bluetoothService.setSeparationThreshold(meters);
  },

  handleSeparationBreach: (distance) => {
    playSeparationAlarmSound();
    locationService.addAlert({
      id: `sep-${Date.now()}`,
      type: 'SEPARATION_DETECTED',
      title: 'Separation Warning: Child Distance Exceeded',
      message: `Band proximity breach detected. Estimated distance: ${distance}m (Safe limit: ${bluetoothService.getState().separationThreshold}m).`,
      timestamp: new Date().toISOString(),
    });
  },

  getSeparationParameters: () => {
    const state = bluetoothService.getState();
    return {
      thresholdMeters: state.separationThreshold || 12,
      currentDistance: state.device?.distanceMeters || 3.8,
      proximityZone: state.device?.proximityZone || PROXIMITY_ZONE.NEAR,
      isTetherActive: state.tetherAlarmEnabled !== false,
      isBreachActive: state.separationBreachActive || false,
    };
  },
};

export default separationService;
