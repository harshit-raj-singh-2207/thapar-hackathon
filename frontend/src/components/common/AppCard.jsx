import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';

export default function AppCard({
  children,
  style,
  onPress,
  variant = 'default', // 'default' | 'outlined' | 'elevated' | 'danger' | 'safe'
  padding = 18,
}) {
  const getCardStyles = () => {
    const arr = [styles.base, { padding }];

    switch (variant) {
      case 'outlined':
        arr.push(styles.outlined);
        break;
      case 'elevated':
        arr.push(styles.elevated);
        break;
      case 'danger':
        arr.push(styles.danger);
        break;
      case 'safe':
        arr.push(styles.safe);
        break;
      case 'default':
      default:
        arr.push(styles.defaultCard);
        break;
    }

    if (style) arr.push(style);
    return arr;
  };

  if (onPress) {
    return (
      <TouchableOpacity
        style={getCardStyles()}
        onPress={onPress}
        activeOpacity={0.88}
      >
        {children}
      </TouchableOpacity>
    );
  }

  return <View style={getCardStyles()}>{children}</View>;
}

const styles = StyleSheet.create({
  base: {
    borderRadius: 18,
    marginBottom: 14,
  },
  defaultCard: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  outlined: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#CBD5E1',
  },
  elevated: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.08,
    shadowRadius: 14,
    elevation: 4,
  },
  danger: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
    borderLeftWidth: 5,
    borderLeftColor: '#DC2626',
  },
  safe: {
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#A7F3D0',
    borderLeftWidth: 5,
    borderLeftColor: '#059669',
  },
});
