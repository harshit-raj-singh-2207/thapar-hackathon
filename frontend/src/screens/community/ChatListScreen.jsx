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
import { useChatStore } from '../../store/chatStore';
import ChatListItem from '../../components/community/ChatListItem';

export default function ChatListScreen({ navigation }) {
  const { chats, loading, fetchChats, initWebSocket } = useChatStore();

  useEffect(() => {
    fetchChats();
    const cleanupWs = initWebSocket();
    return () => cleanupWs && cleanupWs();
  }, []);

  return (
    <View style={styles.container}>
      {loading && chats.length === 0 ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#4F46E5" />
        </View>
      ) : (
        <FlatList
          data={chats}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <ChatListItem
              chat={item}
              onPress={() =>
                navigation.navigate('DirectMessage', {
                  chatId: item.id,
                  recipientId: item.recipient_id,
                  name: item.name,
                })
              }
            />
          )}
          refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchChats} />}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyTitle}>No direct messages yet</Text>
              <Text style={styles.emptySubtitle}>Start a private conversation with a verified caregiver!</Text>
            </View>
          }
        />
      )}

      {/* New Chat FAB */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => navigation.navigate('NewChat')}
      >
        <Text style={styles.fabIcon}>💬</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    paddingVertical: 8,
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
  fab: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
  },
  fabIcon: {
    fontSize: 24,
  },
});
