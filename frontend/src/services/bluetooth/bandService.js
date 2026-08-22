import { bluetoothService, BLE_STATUS } from './bluetoothService';
import { safetyApi } from '../api/safetyApi';

export const bandService = {
  getBandInfo: () => {
    const bleState = bluetoothService.getState();
    return {
      deviceId: bleState?.device?.id || 'NV-BAND-8821',
      name: bleState?.device?.name || 'Nivara GPS SmartBand v2',
      model: bleState?.device?.model || 'CoreBand Pro v2.4',
      mac: bleState?.device?.mac || 'E4:95:6E:41:88:21',
      firmware: bleState?.device?.firmware || 'v2.4.12-secure',
      assignedTo: 'Alex Jennings',
      battery: bleState?.device?.battery || 84,
      isCharging: bleState?.device?.isCharging || false,
      rssi: bleState?.device?.rssi || -58,
      distanceMeters: bleState?.device?.distanceMeters || 3.8,
      proximityZone: bleState?.device?.proximityZone || 'NEAR',
      lastSync: bleState?.device?.lastSync || new Date(),
      gpsStatus: bleState?.device?.gpsStatus || 'ACTIVE',
      connectionState: bleState?.status || BLE_STATUS.CONNECTED,
    };
  },

  connectBand: async (deviceId) => {
    await safetyApi.connectBand(deviceId);
    return await bluetoothService.connectDevice();
  },

  disconnectBand: async (deviceId) => {
    await safetyApi.disconnectBand(deviceId);
    return await bluetoothService.disconnectDevice();
  },

  reconnect: async () => {
    return await bluetoothService.scanAndConnectRealBLE();
  },

  triggerBuzzer: async () => {
    return await bluetoothService.triggerBuzzerBeacon();
  },

  refreshStatus: async () => {
    return await bluetoothService.scanAndConnectRealBLE();
  },

  setTetherAlarm: (enabled) => {
    bluetoothService.setTetherAlarm(enabled);
  },

  setSeparationThreshold: (meters) => {
    bluetoothService.setSeparationThreshold(meters);
  },
};

export default bandService;
