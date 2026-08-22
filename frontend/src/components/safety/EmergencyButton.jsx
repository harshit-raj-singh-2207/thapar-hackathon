import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, View } from 'react-native';

export default function EmergencyButton({
  onPress,
  label = 'SOS EMERGENCY',
  icon = '🚨',
  loading = false,
  disabled = false,
  isActive = false,
  size = 'large', // 'normal' | 'large'
  style,
}) {
  const isLarge = size === 'large';

  return (
    <TouchableOpacity
      style={[
        styles.button,
        isLarge ? styles.largeButton : styles.normalButton,
        isActive && styles.activeButton,
        disabled && styles.disabledButton,
        style,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.85}
      accessibilityRole="button"
      accessibilityLabel={label}
    >
      {loading ? (
        <ActivityIndicator size="small" color="#FFFFFF" />
      ) : (
        <View style={styles.content}>
          <Text style={[styles.icon, isLarge && styles.largeIcon]}>{icon}</Text>
          <Text style={[styles.text, isLarge && styles.largeText]}>
            {isActive ? 'EMERGENCY BROADCAST ACTIVE' : label}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#DC2626',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 16,
    shadowColor: '#DC2626',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 10,
    elevation: 6,
  },
  normalButton: {
    paddingVertical: 14,
    paddingHorizontal: 20,
  },
  largeButton: {
    paddingVertical: 18,
    paddingHorizontal: 28,
  },
  activeButton: {
    backgroundColor: '#991B1B',
    borderWidth: 2,
    borderColor: '#FECACA',
  },
  disabledButton: {
    opacity: 0.6,
    shadowOpacity: 0,
    elevation: 0,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  icon: {
    fontSize: 18,
  },
  largeIcon: {
    fontSize: 24,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: 0.8,
  },
  largeText: {
    fontSize: 16,
  },
});
