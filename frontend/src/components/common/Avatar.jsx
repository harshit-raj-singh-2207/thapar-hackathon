import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';

export default function Avatar({
  uri,
  name = 'User',
  emoji = '👤',
  size = 44,
  style,
  borderColor,
}) {
  const getInitials = () => {
    if (!name) return 'N';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();
  };

  const dynamicStyles = {
    width: size,
    height: size,
    borderRadius: size / 2,
    ...(borderColor ? { borderWidth: 2, borderColor } : {}),
  };

  if (uri) {
    return (
      <Image
        source={{ uri }}
        style={[styles.avatarImg, dynamicStyles, style]}
      />
    );
  }

  return (
    <View style={[styles.avatarCircle, dynamicStyles, style]}>
      {emoji ? (
        <Text style={[styles.emoji, { fontSize: size * 0.45 }]}>{emoji}</Text>
      ) : (
        <Text style={[styles.initials, { fontSize: size * 0.38 }]}>
          {getInitials()}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  avatarImg: {
    backgroundColor: '#E2E8F0',
  },
  avatarCircle: {
    backgroundColor: '#EFF6FF',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#BFDBFE',
  },
  initials: {
    fontWeight: '800',
    color: '#2563EB',
  },
  emoji: {
    textAlign: 'center',
  },
});
