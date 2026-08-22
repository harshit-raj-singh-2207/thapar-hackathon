import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function Badge({
  label,
  variant = 'primary', // 'primary' | 'safe' | 'danger' | 'warning' | 'neutral'
  icon,
  size = 'md', // 'sm' | 'md'
  style,
  textStyle,
}) {
  const getBadgeStyle = () => {
    switch (variant) {
      case 'safe':
        return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
      case 'danger':
        return { bg: '#FEF2F2', text: '#DC2626', border: '#FECACA' };
      case 'warning':
        return { bg: '#FEF3C7', text: '#D97706', border: '#FDE68A' };
      case 'neutral':
        return { bg: '#F1F5F9', text: '#475569', border: '#E2E8F0' };
      case 'primary':
      default:
        return { bg: '#EFF6FF', text: '#2563EB', border: '#BFDBFE' };
    }
  };

  const current = getBadgeStyle();

  return (
    <View
      style={[
        styles.badge,
        size === 'sm' ? styles.badgeSm : styles.badgeMd,
        { backgroundColor: current.bg, borderColor: current.border },
        style,
      ]}
    >
      {icon && <Text style={styles.icon}>{icon}</Text>}
      <Text
        style={[
          styles.text,
          size === 'sm' ? styles.textSm : styles.textMd,
          { color: current.text },
          textStyle,
        ]}
      >
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 999,
    borderWidth: 1,
    alignSelf: 'flex-start',
  },
  badgeSm: {
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  badgeMd: {
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  icon: {
    fontSize: 11,
    marginRight: 4,
  },
  text: {
    fontWeight: '800',
    letterSpacing: 0.2,
  },
  textSm: {
    fontSize: 10,
  },
  textMd: {
    fontSize: 11,
  },
});
