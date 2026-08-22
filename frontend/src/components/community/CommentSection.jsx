import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Image,
} from 'react-native';
import { playCommentSound } from '../../utils/soundEffects';

export default function CommentSection({
  comments = [],
  loading = false,
  submitting = false,
  deletingId = null,
  error = null,
  onAddComment,
  onDeleteComment,
  onRetry,
}) {
  const [text, setText] = useState('');
  const [localSubmitting, setLocalSubmitting] = useState(false);
  const [actionError, setActionError] = useState(null);

  const isPosting = submitting || localSubmitting;

  const handleSubmit = async () => {
    if (!text.trim() || isPosting) return;
    playCommentSound(); // Audio notification sound
    setActionError(null);
    setLocalSubmitting(true);
    try {
      if (onAddComment) {
        await onAddComment(text.trim());
      }
      setText('');
    } catch (err) {
      const msg = err.detail || err.message || 'Could not post comment. Please try again.';
      setActionError(msg);
      Alert.alert('Comment Failed', msg);
    } finally {
      setLocalSubmitting(false);
    }
  };

  const handleDelete = (commentId) => {
    Alert.alert(
      'Delete Comment',
      'Are you sure you want to remove this comment?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            setActionError(null);
            try {
              if (onDeleteComment) {
                await onDeleteComment(commentId);
              }
            } catch (err) {
              const msg = err.detail || err.message || 'Could not delete comment.';
              setActionError(msg);
              Alert.alert('Delete Failed', msg);
            }
          },
        },
      ]
    );
  };

  const formatCommentTime = (dateString) => {
    if (!dateString) return 'Just now';
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
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.headerRow}>
        <Text style={styles.title}>
          💬 Comments {comments.length > 0 ? `(${comments.length})` : ''}
        </Text>
        {loading && <ActivityIndicator size="small" color="#4F46E5" />}
      </View>

      {/* Action Error Banner */}
      {actionError && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>⚠️ {actionError}</Text>
          <TouchableOpacity onPress={() => setActionError(null)}>
            <Text style={styles.errorDismiss}>✕</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Input Box */}
      <View style={styles.inputCard}>
        <TextInput
          style={styles.input}
          placeholder="Share your caregiver insight, encouragement, or question..."
          placeholderTextColor="#94A3B8"
          value={text}
          onChangeText={setText}
          multiline
          maxLength={1000}
          editable={!isPosting}
        />
        <View style={styles.inputFooter}>
          <Text style={styles.charCount}>{text.length}/1000</Text>
          <TouchableOpacity
            style={[styles.sendBtn, (!text.trim() || isPosting) && styles.sendBtnDisabled]}
            onPress={handleSubmit}
            disabled={!text.trim() || isPosting}
            activeOpacity={0.8}
          >
            {isPosting ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.sendBtnText}>Post Comment</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>

      {/* Loading State */}
      {loading && comments.length === 0 ? (
        <View style={styles.stateContainer}>
          <ActivityIndicator size="small" color="#4F46E5" />
          <Text style={styles.loadingText}>Loading comments...</Text>
        </View>
      ) : error && comments.length === 0 ? (
        /* Error State */
        <View style={styles.stateContainer}>
          <Text style={styles.errorTitle}>Could not load comments</Text>
          <Text style={styles.errorSubtitle}>{error}</Text>
          {onRetry && (
            <TouchableOpacity style={styles.retryBtn} onPress={onRetry}>
              <Text style={styles.retryBtnText}>↻ Retry</Text>
            </TouchableOpacity>
          )}
        </View>
      ) : comments.length === 0 ? (
        /* Empty State */
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyIcon}>🗨️</Text>
          <Text style={styles.emptyTitle}>No comments yet</Text>
          <Text style={styles.emptySubtitle}>
            Be the first caregiver to reply and share your perspective!
          </Text>
        </View>
      ) : (
        /* Comment List */
        <View style={styles.commentsList}>
          {comments.map((item, idx) => {
            const isDeleting = deletingId === item.id;
            const author = item.author_name || item.author || 'Caregiver';
            const isVerified = item.is_verified_caregiver || item.is_verified || false;

            return (
              <View key={item.id || idx} style={styles.commentCard}>
                {/* Avatar */}
                <View style={styles.avatar}>
                  {item.author_avatar && item.author_avatar.startsWith('http') ? (
                    <Image source={{ uri: item.author_avatar }} style={styles.avatarImg} />
                  ) : (
                    <Text style={styles.avatarText}>{author[0] || 'C'}</Text>
                  )}
                </View>

                {/* Content */}
                <View style={styles.commentContent}>
                  <View style={styles.commentTopRow}>
                    <View style={styles.authorMeta}>
                      <Text style={styles.authorName}>{author}</Text>
                      {isVerified && (
                        <View style={styles.verifiedChip}>
                          <Text style={styles.verifiedChipText}>✓ Verified</Text>
                        </View>
                      )}
                    </View>
                    <Text style={styles.timestamp}>
                      {formatCommentTime(item.created_at)}
                    </Text>
                  </View>

                  <Text style={styles.commentText}>{item.content}</Text>

                  {/* Actions (Delete only where item.is_own is supported) */}
                  {item.is_own && (
                    <View style={styles.commentActions}>
                      <TouchableOpacity
                        style={styles.deleteAction}
                        onPress={() => handleDelete(item.id)}
                        disabled={isDeleting}
                      >
                        {isDeleting ? (
                          <ActivityIndicator size="small" color="#DC2626" />
                        ) : (
                          <Text style={styles.deleteActionText}>🗑️ Delete</Text>
                        )}
                      </TouchableOpacity>
                    </View>
                  )}
                </View>
              </View>
            );
          })}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    marginBottom: 12,
  },
  errorText: {
    fontSize: 12,
    color: '#DC2626',
    fontWeight: '500',
    flex: 1,
  },
  errorDismiss: {
    fontSize: 14,
    color: '#DC2626',
    fontWeight: '700',
    marginLeft: 8,
  },
  inputCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 10,
    marginBottom: 16,
  },
  input: {
    fontSize: 14,
    color: '#0F172A',
    minHeight: 56,
    textAlignVertical: 'top',
    padding: 4,
  },
  inputFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 8,
  },
  charCount: {
    fontSize: 11,
    color: '#94A3B8',
  },
  sendBtn: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    minHeight: 34,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendBtnDisabled: {
    backgroundColor: '#CBD5E1',
  },
  sendBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
  stateContainer: {
    paddingVertical: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: 13,
    color: '#64748B',
    marginTop: 8,
  },
  errorTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#DC2626',
    marginBottom: 4,
  },
  errorSubtitle: {
    fontSize: 12,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 12,
  },
  retryBtn: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 6,
  },
  retryBtnText: {
    fontSize: 12,
    color: '#4F46E5',
    fontWeight: '600',
  },
  emptyContainer: {
    paddingVertical: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  emptyTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 4,
  },
  emptySubtitle: {
    fontSize: 13,
    color: '#64748B',
    textAlign: 'center',
    maxWidth: 280,
    lineHeight: 18,
  },
  commentsList: {
    gap: 12,
  },
  commentCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
    gap: 12,
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E0E7FF',
  },
  avatarImg: {
    width: 36,
    height: 36,
    borderRadius: 18,
  },
  avatarText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#4F46E5',
  },
  commentContent: {
    flex: 1,
  },
  commentTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  authorMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    flexWrap: 'wrap',
  },
  authorName: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  verifiedChip: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 6,
    paddingVertical: 1.5,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#A7F3D0',
  },
  verifiedChipText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#059669',
  },
  timestamp: {
    fontSize: 11,
    color: '#94A3B8',
  },
  commentText: {
    fontSize: 13,
    color: '#334155',
    lineHeight: 19,
  },
  commentActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 6,
  },
  deleteAction: {
    paddingVertical: 2,
    paddingHorizontal: 6,
  },
  deleteActionText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#DC2626',
  },
});
