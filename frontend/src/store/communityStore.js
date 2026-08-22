import { create } from 'zustand';
import { communityApi } from '../services/api/communityApi';
import chatSocket from '../services/websocket/chatSocket';
import { playLikeSound, playCommentSound, playNotificationSound } from '../utils/soundEffects';

export const useCommunityStore = create((set, get) => ({
  posts: [],
  currentPost: null,
  comments: [],
  groups: [],
  myGroups: [],
  resources: [],
  currentResource: null,
  activeCategory: 'All',
  loading: false,
  commentsLoading: false,
  submittingComment: false,
  deletingCommentId: null,
  likingPostIds: {},
  error: null,
  commentsError: null,

  fetchPosts: async (category = 'All') => {
    set({ loading: true, activeCategory: category, error: null });
    try {
      const posts = await communityApi.getPosts(category);
      set({ posts: Array.isArray(posts) ? posts : [], loading: false });
    } catch (err) {
      set({ error: err.detail || err.message, loading: false });
    }
  },

  createPost: async ({ content, image_url, category }) => {
    try {
      const newPost = await communityApi.createPost({ content, image_url, category });
      set((state) => ({ posts: [newPost, ...state.posts] }));
      return newPost;
    } catch (err) {
      throw err;
    }
  },

  fetchPostDetails: async (postId) => {
    set({ loading: true, commentsLoading: true, error: null, commentsError: null });
    try {
      const [currentPost, comments] = await Promise.all([
        communityApi.getPostDetails(postId),
        communityApi.getComments(postId).catch((e) => {
          console.warn('Comments fetch error:', e);
          return [];
        }),
      ]);
      set({
        currentPost,
        comments: Array.isArray(comments) ? comments : [],
        loading: false,
        commentsLoading: false,
      });
    } catch (err) {
      set({ error: err.detail || err.message, loading: false, commentsLoading: false });
    }
  },

  fetchComments: async (postId) => {
    set({ commentsLoading: true, commentsError: null });
    try {
      const comments = await communityApi.getComments(postId);
      set({ comments: Array.isArray(comments) ? comments : [], commentsLoading: false });
    } catch (err) {
      set({ commentsError: err.detail || err.message, commentsLoading: false });
    }
  },

  toggleLike: async (postId) => {
    const state = get();
    if (state.likingPostIds[postId]) return; // prevent duplicate clicks

    playLikeSound(); // Audio notification sound
    set((s) => ({ likingPostIds: { ...s.likingPostIds, [postId]: true } }));
    try {
      const result = await communityApi.toggleLikePost(postId);
      const newLikeCount = typeof result?.like_count === 'number' ? result.like_count : 0;
      const isLiked = Boolean(result?.is_liked);

      set((s) => ({
        posts: s.posts.map((p) =>
          p.id === postId ? { ...p, like_count: newLikeCount, is_liked: isLiked } : p
        ),
        currentPost:
          s.currentPost?.id === postId
            ? { ...s.currentPost, like_count: newLikeCount, is_liked: isLiked }
            : s.currentPost,
        likingPostIds: { ...s.likingPostIds, [postId]: false },
      }));
    } catch (err) {
      console.error('Error toggling like:', err);
      set((s) => ({ likingPostIds: { ...s.likingPostIds, [postId]: false } }));
      throw err;
    }
  },

  addComment: async (postId, content) => {
    set({ submittingComment: true });
    try {
      playCommentSound(); // Audio notification sound
      const comment = await communityApi.addComment(postId, content);
      set((state) => ({
        comments: [...state.comments, comment],
        posts: state.posts.map((p) => (p.id === postId ? { ...p, comment_count: (p.comment_count || 0) + 1 } : p)),
        currentPost:
          state.currentPost?.id === postId
            ? { ...state.currentPost, comment_count: (state.currentPost.comment_count || 0) + 1 }
            : state.currentPost,
        submittingComment: false,
      }));
      return comment;
    } catch (err) {
      set({ submittingComment: false });
      throw err;
    }
  },

  deleteComment: async (postId, commentId) => {
    set({ deletingCommentId: commentId });
    try {
      await communityApi.deleteComment(postId, commentId);
      set((state) => ({
        comments: state.comments.filter((c) => c.id !== commentId),
        posts: state.posts.map((p) =>
          p.id === postId ? { ...p, comment_count: Math.max(0, (p.comment_count || 0) - 1) } : p
        ),
        currentPost:
          state.currentPost?.id === postId
            ? { ...state.currentPost, comment_count: Math.max(0, (state.currentPost.comment_count || 0) - 1) }
            : state.currentPost,
        deletingCommentId: null,
      }));
    } catch (err) {
      set({ deletingCommentId: null });
      throw err;
    }
  },


  deletePost: async (postId) => {
    try {
      await communityApi.deletePost(postId);
      set((state) => ({
        posts: state.posts.filter((p) => p.id !== postId),
        currentPost: state.currentPost?.id === postId ? null : state.currentPost,
      }));
    } catch (err) {
      throw err;
    }
  },

  fetchResources: async (category = 'All') => {
    set({ loading: true, error: null });
    try {
      const resources = await communityApi.getResources(category);
      set({ resources, loading: false });
    } catch (err) {
      set({ error: err.detail || err.message, loading: false });
    }
  },

  createResource: async ({ title, description, category, url, file_type }) => {
    try {
      const newRes = await communityApi.createResource({ title, description, category, url, file_type });
      set((state) => ({ resources: [newRes, ...state.resources] }));
      return newRes;
    } catch (err) {
      throw err;
    }
  },

  deleteResource: async (resourceId) => {
    try {
      await communityApi.deleteResource(resourceId);
      set((state) => ({ resources: state.resources.filter((r) => r.id !== resourceId) }));
    } catch (err) {
      throw err;
    }
  },

  fetchGroups: async (search = '') => {
    set({ loading: true, error: null });
    try {
      const groups = await communityApi.discoverGroups(search);
      const myGroups = groups.filter((g) => g.is_joined);
      set({ groups, myGroups, loading: false });
    } catch (err) {
      set({ error: err.detail || err.message, loading: false });
    }
  },

  joinGroup: async (groupId) => {
    try {
      const res = await communityApi.joinGroup(groupId);
      set((state) => ({
        groups: state.groups.map((g) =>
          g.id === groupId ? { ...g, is_joined: true, member_count: res.member_count } : g
        ),
      }));
    } catch (err) {
      throw err;
    }
  },

  leaveGroup: async (groupId) => {
    try {
      const res = await communityApi.leaveGroup(groupId);
      set((state) => ({
        groups: state.groups.map((g) =>
          g.id === groupId ? { ...g, is_joined: false, member_count: res.member_count } : g
        ),
      }));
    } catch (err) {
      throw err;
    }
  },

  initWebSocket: () => {
    chatSocket.connect();
    return chatSocket.addListener((data) => {
      if (data && data.type === 'new_comment') {
        const { post_id, comment } = data;
        if (!post_id || !comment) return;

        set((state) => {
          const isCurrentPost = state.currentPost?.id === post_id;
          const commentExists = state.comments.some((c) => c.id === comment.id);

          const updatedComments = isCurrentPost && !commentExists
            ? [...state.comments, comment]
            : state.comments;

          const updatedPosts = state.posts.map((p) =>
            p.id === post_id ? { ...p, comment_count: (p.comment_count || 0) + (commentExists ? 0 : 1) } : p
          );

          const updatedCurrentPost = isCurrentPost
            ? { ...state.currentPost, comment_count: (state.currentPost.comment_count || 0) + (commentExists ? 0 : 1) }
            : state.currentPost;

          return {
            comments: updatedComments,
            posts: updatedPosts,
            currentPost: updatedCurrentPost,
          };
        });
      }
    });
  },
}));
