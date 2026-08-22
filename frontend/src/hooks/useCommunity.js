import { useEffect } from 'react';
import { useCommunityStore } from '../store/communityStore';

export function useCommunity(category = 'All') {
  const {
    posts,
    currentPost,
    comments,
    groups,
    myGroups,
    activeCategory,
    loading,
    commentsLoading,
    submittingComment,
    deletingCommentId,
    commentsError,
    likingPostIds,
    error,
    fetchPosts,
    createPost,
    fetchPostDetails,
    fetchComments,
    toggleLike,
    addComment,
    deleteComment,
    deletePost,
    fetchGroups,
    joinGroup,
    leaveGroup,
  } = useCommunityStore();

  useEffect(() => {
    fetchPosts(category);
    fetchGroups();
  }, [category]);

  return {
    posts,
    currentPost,
    comments,
    groups,
    myGroups,
    activeCategory,
    loading,
    commentsLoading,
    submittingComment,
    deletingCommentId,
    commentsError,
    likingPostIds,
    error,
    refetchPosts: () => fetchPosts(category),
    createPost,
    fetchPostDetails,
    fetchComments,
    toggleLike,
    addComment,
    deleteComment,
    deletePost,
    refetchGroups: fetchGroups,
    joinGroup,
    leaveGroup,
  };
}

export default useCommunity;
