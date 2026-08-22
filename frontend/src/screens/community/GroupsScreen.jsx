import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useCommunityStore } from '../../store/communityStore';
import GroupListItem from '../../components/community/GroupListItem';

export default function GroupsScreen({ navigation }) {
  const { groups, loading, fetchGroups, joinGroup, leaveGroup } = useCommunityStore();

  useEffect(() => {
    fetchGroups();
  }, []);

  return (
    <View style={styles.container}>
      {/* Top Controls */}
      <View style={styles.topBar}>
        <TouchableOpacity
          style={styles.actionBtn}
          onPress={() => navigation.navigate('DiscoverGroups')}
        >
          <Text style={styles.actionBtnText}>🔍 Discover Groups</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionBtn, styles.primaryBtn]}
          onPress={() => navigation.navigate('CreateGroup')}
        >
          <Text style={styles.primaryBtnText}>➕ Create Group</Text>
        </TouchableOpacity>
      </View>

      {/* Groups List */}
      {loading && groups.length === 0 ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#4F46E5" />
        </View>
      ) : (
        <FlatList
          data={groups}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <GroupListItem
              group={item}
              onPress={() =>
                item.is_joined
                  ? navigation.navigate('GroupChat', { groupId: item.id, name: item.name })
                  : navigation.navigate('GroupDetails', { groupId: item.id })
              }
              onJoinToggle={() => (item.is_joined ? leaveGroup(item.id) : joinGroup(item.id))}
            />
          )}
          refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchGroups} />}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyTitle}>No groups created yet</Text>
              <Text style={styles.emptySubtitle}>Create a group to discuss sensory, IEP, or visual schedules!</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  topBar: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  actionBtn: {
    flex: 1,
    paddingVertical: 10,
    backgroundColor: '#F1F5F9',
    borderRadius: 8,
    alignItems: 'center',
  },
  actionBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
  },
  primaryBtn: {
    backgroundColor: '#4F46E5',
  },
  primaryBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: 16,
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  emptyTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: '#334155',
    marginBottom: 6,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
  },
});
