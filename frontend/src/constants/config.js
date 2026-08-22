import Constants from 'expo-constants';
import { Platform } from 'react-native';

export const getApiBaseUrl = () => {
  // If EXPO_PUBLIC_API_URL is explicitly set to a non-localhost address, use it
  if (process.env.EXPO_PUBLIC_API_URL && !process.env.EXPO_PUBLIC_API_URL.includes('localhost') && !process.env.EXPO_PUBLIC_API_URL.includes('127.0.0.1')) {
    return process.env.EXPO_PUBLIC_API_URL;
  }

  // Detect Expo Metro host IP for physical devices and emulators
  const hostUri =
    Constants.expoConfig?.hostUri ||
    Constants.manifest?.debuggerHost ||
    Constants.manifest2?.extra?.expoGo?.developer?.manifest?.debuggerHost;

  if (hostUri) {
    const host = hostUri.split(':')[0];
    if (host && host !== 'localhost' && host !== '127.0.0.1') {
      return `http://${host}:8000/api/v1`;
    }
  }

  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000/api/v1';
  }

  return process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
};

export const getWsBaseUrl = () => {
  const httpUrl = getApiBaseUrl();
  return httpUrl.replace(/^http/, 'ws');
};

export const BASE_URL = getApiBaseUrl();
export const WS_URL = getWsBaseUrl();

export default {
  BASE_URL,
  WS_URL,
  getApiBaseUrl,
  getWsBaseUrl,
};
