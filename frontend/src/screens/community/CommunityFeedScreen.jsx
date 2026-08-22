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
import CommunityFilter from '../../components/community/CommunityFilter';
import CommunityPost from '../../components/community/CommunityPost';
import ResourceCard from '../../components/community/ResourceCard';

export default function CommunityFeedScreen({ navigation }) {
  const {
    posts,
    resources,
    loading,
    likingPostIds,
    fetchPosts,
    fetchResources,
    toggleLike,
    deleteResource,
    activeCategory,
  } = useCommunityStore();

  const loadData = (category = activeCategory) => {
    fetchPosts(category);
    fetchResources(category);
  };

  useEffect(() => {
    loadData(activeCategory);
  }, []);

  const handleSelectCategory = (category) => {
    loadData(category);
  };

  const isResourceView = activeCategory === 'Resources';

  return (
    <View style={styles.container}>
      {/* Category filter pills */}
      <CommunityFilter activeCategory={activeCategory} onSelectCategory={handleSelectCategory} />

      {/* Posts & Resources List */}
      {loading && posts.length === 0 && resources.length === 0 ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#4F46E5" />
          <Text style={styles.loadingText}>Loading community feed...</Text>
        </View>
      ) : (
        <FlatList
          data={posts}
          keyExtractor={(item) => item.id}
          ListHeaderComponent={
            resources && resources.length > 0 && (activeCategory === 'All' || isResourceView) ? (
              <View style={styles.resourcesHeaderSection}>
                <View style={styles.sectionHeaderRow}>
                  <Text style={styles.sectionTitle}>📚 Caregiver Resources & Tools</Text>
                  <Text style={styles.sectionSubtitle}>{resources.length} verified guides</Text>
                </View>
                {resources.map((res) => (
                  <ResourceCard
                    key={res.id}
                    resource={res}
                    onDelete={(id) => deleteResource(id)}
                  />
                ))}
                {activeCategory === 'All' && posts.length > 0 && (
                  <View style={[styles.sectionHeaderRow, { marginTop: 16 }]}>
                    <Text style={styles.sectionTitle}>💬 Community Feed Discussions</Text>
                  </View>
                )}
              </View>
            ) : null
          }
          renderItem={({ item }) => (
            <CommunityPost
              post={item}
              onPress={() => navigation.navigate('PostDetails', { postId: item.id })}
              onLike={() => toggleLike(item.id)}
              isLiking={Boolean(likingPostIds[item.id])}
              onProfilePress={() => navigation.navigate('CaregiverProfile', { userId: item.author_id })}
            />
          )}
          refreshControl={
            <RefreshControl
              refreshing={loading}
              onRefresh={() => loadData(activeCategory)}
              colors={['#4F46E5']}
            />
          }
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            resources.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyIcon}>🌱</Text>
                <Text style={styles.emptyTitle}>No posts in this category yet</Text>
                <Text style={styles.emptySubtitle}>Be the first caregiver to share a tip, resource, or question!</Text>
              </View>
            ) : null
          }
        />
      )}

      {/* Create Post Floating Action Button */}
      <TouchableOpacity
        style={styles.fab}
        activeOpacity={0.85}
        onPress={() => navigation.navigate('CreatePost')}
      >
        <Text style={styles.fabIcon}>✏️</Text>
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
    backgroundColor: '#F8FAFC',
  },
  loadingText: {
    fontSize: 14,
    color: '#64748B',
    marginTop: 12,
  },
  listContent: {
    padding: 16,
    paddingBottom: 80,
    maxWidth: 760,
    width: '100%',
    alignSelf: 'center',
  },
  resourcesHeaderSection: {
    marginBottom: 8,
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1E293B',
  },
  sectionSubtitle: {
    fontSize: 12,
    color: '#64748B',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 6,
  },
  emptySubtitle: {
    fontSize: 13,
    color: '#64748B',
    textAlign: 'center',
    maxWidth: 280,
    lineHeight: 18,
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
    shadowColor: '#4F46E5',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  fabIcon: {
    fontSize: 24,
  },
});
