import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { useCommunityStore } from '../../store/communityStore';
import CommunityPost from '../../components/community/CommunityPost';
import CommentSection from '../../components/community/CommentSection';

export default function PostDetailsScreen({ route, navigation }) {
  const { postId } = route.params || {};
  const {
    currentPost,
    comments,
    loading,
    commentsLoading,
    submittingComment,
    deletingCommentId,
    commentsError,
    likingPostIds,
    fetchPostDetails,
    fetchComments,
    toggleLike,
    addComment,
    deleteComment,
    deletePost,
  } = useCommunityStore();

  useEffect(() => {
    if (postId) {
      fetchPostDetails(postId);
    }
  }, [postId]);

  const handleRefresh = async () => {
    if (postId) {
      await fetchPostDetails(postId);
    }
  };

  const handleDeletePost = () => {
    Alert.alert('Delete Post', 'Are you sure you want to delete this post?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await deletePost(postId);
            navigation.goBack();
          } catch (err) {
            Alert.alert('Error', err.detail || 'Could not delete post.');
          }
        },
      },
    ]);
  };

  if (loading && !currentPost) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4F46E5" />
        <Text style={styles.loadingText}>Loading post & comments...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => navigation.goBack()}
          activeOpacity={0.7}
        >
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Post & Discussion</Text>
        {currentPost?.is_own ? (
          <TouchableOpacity onPress={handleDeletePost} activeOpacity={0.7}>
            <Text style={styles.deleteText}>Delete</Text>
          </TouchableOpacity>
        ) : (
          <View style={{ width: 50 }} />
        )}
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={handleRefresh} colors={['#4F46E5']} />
        }
      >
        <View style={styles.contentWrapper}>
          {currentPost && (
            <CommunityPost
              post={currentPost}
              onLike={() => toggleLike(currentPost.id)}
              isLiking={Boolean(likingPostIds[currentPost.id])}
              onProfilePress={() =>
                navigation.navigate('CaregiverProfile', { userId: currentPost.author_id })
              }
            />
          )}

          {/* Real-time Connected Comment Section */}
          <CommentSection
            comments={comments}
            loading={commentsLoading}
            submitting={submittingComment}
            deletingId={deletingCommentId}
            error={commentsError}
            onAddComment={(content) => addComment(postId, content)}
            onDeleteComment={(commentId) => deleteComment(postId, commentId)}
            onRetry={() => fetchComments(postId)}
          />
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backBtn: {
    paddingVertical: 4,
    paddingRight: 8,
  },
  backText: {
    fontSize: 15,
    color: '#4F46E5',
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#0F172A',
  },
  deleteText: {
    fontSize: 14,
    color: '#DC2626',
    fontWeight: '600',
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
  scroll: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  contentWrapper: {
    maxWidth: 720,
    width: '100%',
    alignSelf: 'center',
  },
});
