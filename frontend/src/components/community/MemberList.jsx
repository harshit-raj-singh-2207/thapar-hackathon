import React from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import MemberItem from './MemberItem';

export default function MemberList({ members = [], onMemberPress }) {
  return (
    <View style={styles.container}>
      <FlatList
        data={members}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <MemberItem member={item} onPress={() => onMemberPress && onMemberPress(item.id)} />
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
