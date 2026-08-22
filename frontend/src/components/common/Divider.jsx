import React from 'react';
import { View, StyleSheet } from 'react-native';

export default function Divider({ style, color = '#EEF2F6', marginVertical = 12 }) {
  return (
    <View
      style={[
        styles.divider,
        { backgroundColor: color, marginVertical },
        style,
      ]}
    />
  );
}

const styles = StyleSheet.create({
  divider: {
    height: 1,
    width: '100%',
  },
});
