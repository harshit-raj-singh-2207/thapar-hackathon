import { useState, useEffect, useCallback } from 'react';
import { bluetoothService, BLE_STATUS, PROXIMITY_ZONE } from '../services/bluetooth/bluetoothService';
import { bandService } from '../services/bluetooth/bandService';

export function useBluetooth() {
  const [bleState, setBleState] = useState(bluetoothService.getState());
  const [isScanning, setIsScanning] = useState(false);
  const [isBuzzerActive, setIsBuzzerActive] = useState(false);

  useEffect(() => {
    const unsub = bluetoothService.subscribe((s) => setBleState(s));
    return () => unsub();
  }, []);

  const scanAndConnect = useCallback(async () => {
    setIsScanning(true);
    const res = await bluetoothService.scanAndConnectRealBLE();
    setIsScanning(false);
    return res;
  }, []);

  const disconnectDevice = useCallback(async () => {
    return await bluetoothService.disconnectDevice();
  }, []);

  const triggerBuzzer = useCallback(async () => {
    setIsBuzzerActive(true);
    await bandService.triggerBuzzer();
    setTimeout(() => setIsBuzzerActive(false), 3000);
  }, []);

  const setSeparationThreshold = useCallback((meters) => {
    bluetoothService.setSeparationThreshold(meters);
  }, []);

  const setTetherAlarm = useCallback((enabled) => {
    bluetoothService.setTetherAlarm(enabled);
  }, []);

  return {
    ...bleState,
    isScanning,
    isBuzzerActive,
    BLE_STATUS,
    PROXIMITY_ZONE,
    scanAndConnect,
    disconnectDevice,
    triggerBuzzer,
    setSeparationThreshold,
    setTetherAlarm,
  };
}

export default useBluetooth;
