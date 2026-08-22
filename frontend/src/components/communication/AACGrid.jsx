import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import AACButton from './AACButton';

export default function AACGrid({ cards = [], onSelectCard }) {
  return (
    <View style={styles.gridContainer}>
      <FlatList
        data={cards}
        numColumns={2}
        keyExtractor={(item, index) => item.id || `card-${index}`}
        renderItem={({ item }) => (
          <AACButton
            label={item.label}
            icon={item.icon}
            onPress={() => onSelectCard(item)}
            bgColor={item.bg_color || '#FFFFFF'}
            textColor={item.text_color || '#0F172A'}
          />
        )}
        scrollEnabled={false}
        columnWrapperStyle={styles.row}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  gridContainer: {
    width: '100%',
  },
  row: {
    justifyContent: 'space-between',
    marginBottom: 4,
  },
});
