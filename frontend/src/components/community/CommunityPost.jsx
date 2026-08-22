import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ActivityIndicator } from 'react-native';
import { playLikeSound } from '../../utils/soundEffects';

export default function CommunityPost({
  post,
  onPress,
  onLike,
  onProfilePress,
  disabled = false,
  isLiking = false,
}) {
  const {
    id,
    author_name,
    author_avatar,
    is_verified_caregiver,
    is_verified,
    content,
    image_url,
    category,
    comment_count = 0,
    like_count = 0,
    is_liked = false,
    created_at,
  } = post;

  const [localLikeLoading, setLocalLikeLoading] = useState(false);

  const author = author_name || 'Caregiver';
  const verified = is_verified_caregiver || is_verified || false;
  const liking = isLiking || localLikeLoading;

  const handleLikePress = async () => {
    if (liking || disabled) return;
    playLikeSound(); // Audio notification sound
    setLocalLikeLoading(true);
    try {
      if (onLike) {
        await onLike();
      }
    } catch (err) {
      console.warn('Like action failed:', err);
    } finally {
      setLocalLikeLoading(false);
    }
  };

  const formatPostTime = (dateString) => {
    if (!dateString) return 'Recent';
    try {
      const d = new Date(dateString);
      if (isNaN(d.getTime())) return dateString;
      const now = new Date();
      const diffMs = now - d;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return dateString;
    }
  };

  return (
    <View style={styles.card}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.authorRow}
          onPress={onProfilePress}
          activeOpacity={0.7}
        >
          <View style={styles.avatar}>
            {author_avatar && author_avatar.startsWith('http') ? (
              <Image source={{ uri: author_avatar }} style={styles.avatarImg} />
            ) : (
              <Text style={styles.avatarText}>{author[0] || 'C'}</Text>
            )}
          </View>
          <View>
            <View style={styles.nameRow}>
              <Text style={styles.authorName}>{author}</Text>
              {verified && (
                <View style={styles.verifiedTag}>
                  <Text style={styles.verifiedText}>✓ Verified</Text>
                </View>
              )}
            </View>
            <Text style={styles.dateText}>{formatPostTime(created_at)}</Text>
          </View>
        </TouchableOpacity>

        {category && (
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>{category}</Text>
          </View>
        )}
      </View>

      {/* Post Content */}
      <TouchableOpacity onPress={onPress} activeOpacity={0.9} style={styles.bodyTouchable}>
        <Text style={styles.content}>{content}</Text>
        {image_url && (
          <Image source={{ uri: image_url }} style={styles.postImage} resizeMode="cover" />
        )}
      </TouchableOpacity>

      {/* Footer Actions (Likes & Comments) */}
      <View style={styles.footer}>
        {/* Like Button */}
        <TouchableOpacity
          style={[styles.actionBtn, is_liked && styles.actionBtnLiked]}
          onPress={handleLikePress}
          disabled={liking}
          activeOpacity={0.7}
        >
          {liking ? (
            <ActivityIndicator size="small" color={is_liked ? '#DC2626' : '#64748B'} />
          ) : (
            <Text style={[styles.actionIcon, is_liked && styles.likedIcon]}>
              {is_liked ? '❤️' : '🤍'}
            </Text>
          )}
          <Text style={[styles.actionLabel, is_liked && styles.likedLabel]}>
            {like_count} {like_count === 1 ? 'Like' : 'Likes'}
          </Text>
        </TouchableOpacity>

        {/* Comment Count Trigger */}
        <TouchableOpacity
          style={styles.actionBtn}
          onPress={onPress}
          activeOpacity={0.7}
        >
          <Text style={styles.actionIcon}>💬</Text>
          <Text style={styles.actionLabel}>
            {comment_count} {comment_count === 1 ? 'Comment' : 'Comments'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
    maxWidth: 720,
    width: '100%',
    alignSelf: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  authorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    flex: 1,
  },
  avatar: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E0E7FF',
  },
  avatarImg: {
    width: 42,
    height: 42,
    borderRadius: 21,
  },
  avatarText: {
    color: '#4F46E5',
    fontSize: 17,
    fontWeight: '700',
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    flexWrap: 'wrap',
  },
  authorName: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  verifiedTag: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 6,
    paddingVertical: 1.5,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#A7F3D0',
  },
  verifiedText: {
    fontSize: 10,
    color: '#059669',
    fontWeight: '700',
  },
  dateText: {
    fontSize: 11,
    color: '#94A3B8',
    marginTop: 1,
  },
  categoryBadge: {
    backgroundColor: '#EEF2FF',
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E0E7FF',
  },
  categoryText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#4F46E5',
  },
  bodyTouchable: {
    marginVertical: 4,
  },
  content: {
    fontSize: 14.5,
    color: '#334155',
    lineHeight: 22,
    marginBottom: 8,
  },
  postImage: {
    width: '100%',
    height: 220,
    borderRadius: 12,
    marginVertical: 8,
  },
  footer: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 12,
    gap: 20,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  actionBtnLiked: {
    backgroundColor: '#FEF2F2',
  },
  actionIcon: {
    fontSize: 16,
  },
  actionLabel: {
    fontSize: 13,
    color: '#64748B',
    fontWeight: '600',
  },
  likedIcon: {
    transform: [{ scale: 1.05 }],
  },
  likedLabel: {
    color: '#DC2626',
    fontWeight: '700',
  },
});
