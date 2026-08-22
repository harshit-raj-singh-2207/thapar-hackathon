import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { useAuthStore } from '../store/authStore';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';

export default function AppNavigator() {
  const { token, initialAuthChecked, loadStoredAuth } = useAuthStore();

  useEffect(() => {
    loadStoredAuth();
  }, []);

  if (!initialAuthChecked) {
    return (
      <View style={styles.splashContainer}>
        <View style={styles.brandRow}>
          <Text style={styles.sparkleIcon}>✦</Text>
          <Text style={styles.brandTitle}>NIVARA</Text>
        </View>
        <ActivityIndicator size="large" color="#2563EB" style={styles.loader} />
        <Text style={styles.splashSubtitle}>Loading secure session...</Text>
      </View>
    );
  }

  return (
    <NavigationContainer>
      {token ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  splashContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FAFBFD',
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sparkleIcon: {
    fontSize: 24,
    color: '#2563EB',
    marginRight: 8,
    fontWeight: '900',
  },
  brandTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0F172A',
    letterSpacing: 2,
  },
  loader: {
    marginVertical: 12,
  },
  splashSubtitle: {
    fontSize: 14,
    color: '#64748B',
  },
});
