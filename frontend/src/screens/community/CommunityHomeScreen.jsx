import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Dimensions,
  ActivityIndicator,
  Modal,
  Share,
  Platform,
} from 'react-native';
import { useAuthStore } from '../../store/authStore';
import { dashboardApi } from '../../services/api/dashboardApi';
import { communityApi } from '../../services/api/communityApi';
import CommunityFeedScreen from './CommunityFeedScreen';
import ChatListScreen from './ChatListScreen';
import ActiveGroupsScreen from './ActiveGroupsScreen';
import SupportCenterScreen from '../caregiver/SupportCenterScreen';
import chatSocket from '../../services/websocket/chatSocket';
import { useNotificationStore } from '../../store/notificationStore';

const { width } = Dimensions.get('window');
const isDesktop = width >= 1024;
const isTablet = width >= 768 && width < 1024;

export default function CommunityHomeScreen({ navigation }) {
  const { user, isVerified, checkCommunityAccess, loading: authLoading, accessMessage, logout } = useAuthStore();
  const {
    notifications,
    unreadCount,
    loading: loadingNotifs,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    initWebSocket: initNotificationWs,
  } = useNotificationStore();


  const [activeSection, setActiveSection] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const searchDebounceRef = useRef(null);

  // Live Dashboard State
  const [stats, setStats] = useState({ my_groups: 0, new_messages: 0, notifications: 0, community_online: 0 });
  const [posts, setPosts] = useState([]);
  const [events, setEvents] = useState([]);
  const [suggestedGroups, setSuggestedGroups] = useState([]);
  const [spotlights, setSpotlights] = useState([]);
  const [spotlightIndex, setSpotlightIndex] = useState(0);

  // Interactive local states synced with backend
  const [joinedGroups, setJoinedGroups] = useState({});
  const [likedPosts, setLikedPosts] = useState({});
  const [postLikesCount, setPostLikesCount] = useState({});
  const [savedPosts, setSavedPosts] = useState({});

  // Loading & Error states per section
  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [dashboardError, setDashboardError] = useState(null);
  const [eventsError, setEventsError] = useState(null);
  const [groupsError, setGroupsError] = useState(null);

  // Dropdown Panels
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notifMenuOpen, setNotifMenuOpen] = useState(false);

  // Create Post Modal State
  const [createPostVisible, setCreatePostVisible] = useState(false);
  const [newPostContent, setNewPostContent] = useState('');
  const [newPostCategory, setNewPostCategory] = useState('Sensory Support');
  const [submittingPost, setSubmittingPost] = useState(false);
  const [postError, setPostError] = useState('');

  // Comments Modal State
  const [commentModalVisible, setCommentModalVisible] = useState(false);
  const [activePostForComments, setActivePostForComments] = useState(null);
  const [commentsList, setCommentsList] = useState([]);
  const [newCommentText, setNewCommentText] = useState('');
  const [loadingComments, setLoadingComments] = useState(false);
  const [submittingComment, setSubmittingComment] = useState(false);

  useEffect(() => {
    checkCommunityAccess();
    loadDashboardData();

    if (isVerified) {
      fetchUnreadCount();
      fetchNotifications();
      const unsubNotif = initNotificationWs();
      return () => {
        if (unsubNotif) unsubNotif();
      };
    }
  }, [isVerified]);


  const loadDashboardData = async () => {
    setLoadingDashboard(true);
    setDashboardError(null);
    try {
      const data = await dashboardApi.getDashboardData();
      if (data) {
        if (data.stats) {
          setStats(data.stats);
        }
        if (Array.isArray(data.feed)) {
          setPosts(data.feed);
          const likesMap = {};
          const countMap = {};
          data.feed.forEach((p) => {
            likesMap[p.id] = !!p.is_liked;
            countMap[p.id] = p.like_count ?? 0;
          });
          setLikedPosts(likesMap);
          setPostLikesCount(countMap);
        }
        if (Array.isArray(data.events)) {
          setEvents(data.events);
        }
        if (Array.isArray(data.suggested_groups)) {
          setSuggestedGroups(data.suggested_groups);
          const joinMap = {};
          data.suggested_groups.forEach((g) => {
            joinMap[g.id] = !!g.is_joined;
          });
          setJoinedGroups(joinMap);
        }
        if (Array.isArray(data.spotlight)) {
          setSpotlights(data.spotlight);
        }
      }
    } catch (err) {
      console.warn('Aggregated dashboard load failed, loading modular fallbacks:', err);
      setDashboardError(err.message || 'Unable to load dashboard data.');
      // Attempt separate calls
      loadModularStats();
      loadModularFeed();
      loadModularEvents();
      loadModularGroups();
      loadModularSpotlight();
    } finally {
      setLoadingDashboard(false);
    }
  };

  const loadModularStats = async () => {
    try {
      const [g, m, n, c] = await Promise.allSettled([
        dashboardApi.getMyGroupsCount(),
        dashboardApi.getUnreadMessagesCount(),
        dashboardApi.getUnreadNotificationsCount(),
        dashboardApi.getOnlineCommunityCount(),
      ]);
      setStats({
        my_groups: g.status === 'fulfilled' ? g.value.count : 4,
        new_messages: m.status === 'fulfilled' ? m.value.count : 3,
        notifications: n.status === 'fulfilled' ? n.value.count : 3,
        community_online: c.status === 'fulfilled' ? c.value.count : 128,
      });
    } catch (e) {
      console.warn('Modular stats error:', e);
    }
  };

  const loadModularFeed = async () => {
    try {
      const feed = await dashboardApi.getFeedPosts(10);
      if (Array.isArray(feed)) {
        setPosts(feed);
        const likesMap = {};
        const countMap = {};
        feed.forEach((p) => {
          likesMap[p.id] = !!p.is_liked;
          countMap[p.id] = p.like_count ?? 0;
        });
        setLikedPosts(likesMap);
        setPostLikesCount(countMap);
      }
    } catch (e) {
      console.warn('Modular feed error:', e);
    }
  };

  const loadModularEvents = async () => {
    try {
      const evs = await dashboardApi.getUpcomingEvents(5);
      if (Array.isArray(evs)) setEvents(evs);
    } catch (e) {
      setEventsError('Unable to load upcoming events.');
    }
  };

  const loadModularGroups = async () => {
    try {
      const grps = await dashboardApi.getSuggestedGroups(5);
      if (Array.isArray(grps)) {
        setSuggestedGroups(grps);
        const joinMap = {};
        grps.forEach((g) => {
          joinMap[g.id] = !!g.is_joined;
        });
        setJoinedGroups(joinMap);
      }
    } catch (e) {
      setGroupsError('Unable to load suggested groups.');
    }
  };

  const loadModularSpotlight = async () => {
    try {
      const spots = await dashboardApi.getCaregiverSpotlight();
      if (Array.isArray(spots)) setSpotlights(spots);
    } catch (e) {
      console.warn('Spotlight error:', e);
    }
  };

  // Debounced Search Handler
  const handleSearchChange = (text) => {
    setSearchQuery(text);
    if (!text.trim()) {
      setSearchResults(null);
      setSearching(false);
      if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
      return;
    }

    setSearching(true);
    if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);

    searchDebounceRef.current = setTimeout(async () => {
      try {
        const results = await dashboardApi.search(text.trim());
        setSearchResults(results);
      } catch (err) {
        console.warn('Search query error:', err);
      } finally {
        setSearching(false);
      }
    }, 300);
  };

  // Interactive Like Handler
  const handleToggleLike = async (postId) => {
    const isLiked = !!likedPosts[postId];
    const currentCount = postLikesCount[postId] || 0;

    // Optimistic UI update
    setLikedPosts((prev) => ({ ...prev, [postId]: !isLiked }));
    setPostLikesCount((prev) => ({
      ...prev,
      [postId]: isLiked ? Math.max(0, currentCount - 1) : currentCount + 1,
    }));

    try {
      if (isLiked) {
        await dashboardApi.unlikePost(postId);
      } else {
        await dashboardApi.likePost(postId);
      }
    } catch (err) {
      console.warn('Toggle like error:', err);
      // Revert on failure
      setLikedPosts((prev) => ({ ...prev, [postId]: isLiked }));
      setPostLikesCount((prev) => ({ ...prev, [postId]: currentCount }));
    }
  };

  // Interactive Save Handler
  const handleToggleSavePost = async (postId) => {
    const isSaved = !!savedPosts[postId];
    setSavedPosts((prev) => ({ ...prev, [postId]: !isSaved }));

    try {
      if (isSaved) {
        await dashboardApi.unsavePost(postId);
      } else {
        await dashboardApi.savePost(postId);
      }
    } catch (err) {
      console.warn('Toggle save error:', err);
      setSavedPosts((prev) => ({ ...prev, [postId]: isSaved }));
    }
  };

  // Interactive Join Group Handler
  const handleToggleJoinGroup = async (groupId) => {
    const isJoined = !!joinedGroups[groupId];
    setJoinedGroups((prev) => ({ ...prev, [groupId]: !isJoined }));

    try {
      if (isJoined) {
        await dashboardApi.leaveGroup(groupId);
      } else {
        await dashboardApi.joinGroup(groupId);
      }
    } catch (err) {
      console.warn('Toggle group join error:', err);
      setJoinedGroups((prev) => ({ ...prev, [groupId]: isJoined }));
    }
  };

  // Post Share Handler
  const handleSharePost = async (post) => {
    try {
      if (Platform.OS === 'web') {
        if (navigator.share) {
          await navigator.share({
            title: 'NIVARA Caregiver Community',
            text: `${post.author_name}: "${post.content}"`,
            url: window.location.href,
          });
        } else if (navigator.clipboard) {
          await navigator.clipboard.writeText(`${post.author_name}: "${post.content}"`);
          alert('Post text copied to clipboard!');
        }
      } else {
        await Share.share({
          message: `${post.author_name}: "${post.content}" - Shared via NIVARA Caregiver Community`,
        });
      }
    } catch (err) {
      console.warn('Share post error:', err);
    }
  };

  // Open Post Comments Discussion Modal
  const openCommentsForPost = async (post) => {
    setActivePostForComments(post);
    setCommentModalVisible(true);
    setLoadingComments(true);
    try {
      const res = await communityApi.getComments(post.id);
      setCommentsList(Array.isArray(res) ? res : []);
    } catch (err) {
      console.warn('Load comments error:', err);
      setCommentsList([]);
    } finally {
      setLoadingComments(false);
    }
  };

  // Submit New Comment
  const handleAddComment = async () => {
    if (!newCommentText.trim() || !activePostForComments) return;
    setSubmittingComment(true);
    try {
      const res = await communityApi.addComment(activePostForComments.id, newCommentText.trim());
      if (res && res.id) {
        setCommentsList((prev) => [...prev, res]);
      }
      setNewCommentText('');
      setPosts((prev) =>
        prev.map((p) =>
          p.id === activePostForComments.id
            ? { ...p, comment_count: (p.comment_count || 0) + 1 }
            : p
        )
      );
    } catch (err) {
      console.warn('Submit comment error:', err);
      Alert.alert('Comment Failed', err.detail || err.message || 'Could not post comment.');
    } finally {
      setSubmittingComment(false);
    }
  };

  // Delete Comment Handler
  const handleDeleteComment = async (commentId) => {
    if (!activePostForComments) return;
    try {
      await communityApi.deleteComment(activePostForComments.id, commentId);
      setCommentsList((prev) => prev.filter((c) => c.id !== commentId));
      setPosts((prev) =>
        prev.map((p) =>
          p.id === activePostForComments.id
            ? { ...p, comment_count: Math.max(0, (p.comment_count || 0) - 1) }
            : p
        )
      );
    } catch (err) {
      Alert.alert('Delete Failed', err.detail || err.message || 'Could not delete comment.');
    }
  };


  // Create Post Submit Handler
  const handleCreatePostSubmit = async () => {
    if (!newPostContent.trim()) {
      setPostError('Please enter some text for your post.');
      return;
    }
    setSubmittingPost(true);
    setPostError('');
    try {
      const res = await dashboardApi.createPost({
        content: newPostContent.trim(),
        category: newPostCategory,
      });

      const createdItem = {
        id: res?.id || `post-${Date.now()}`,
        author_name: user?.full_name || 'Sarah Mitchell',
        author_avatar: '👩‍🏫',
        is_verified: true,
        time_ago: 'Just now',
        content: newPostContent.trim(),
        category: newPostCategory,
        tags: [newPostCategory, 'Caregiver Community'],
        like_count: 0,
        comment_count: 0,
      };

      setPosts((prev) => [createdItem, ...prev]);
      setNewPostContent('');
      setCreatePostVisible(false);
    } catch (err) {
      console.error('Create post failed:', err);
      setPostError(err.detail || 'Unable to publish post. Please try again.');
    } finally {
      setSubmittingPost(false);
    }
  };

  // Toggle Notification Panel
  const toggleNotificationPanel = async () => {
    const nextState = !notifMenuOpen;
    setNotifMenuOpen(nextState);
    if (nextState) {
      await fetchNotifications();
    }
  };


  // User Logout
  const handleLogout = async () => {
    setUserMenuOpen(false);
    await logout();
  };

  const firstName = user?.full_name ? user.full_name.split(' ')[0] : 'Sarah';

  // Unverified Caregiver Restriction Screen
  if (!isVerified && !authLoading) {
    return (
      <View style={styles.restrictedRoot}>
        <View style={styles.restrictedCard}>
          <View style={styles.shieldCircle}>
            <Text style={styles.shieldEmoji}>🛡️</Text>
          </View>
          <Text style={styles.restrictedHeading}>Verified Caregiver Community</Text>
          <Text style={styles.restrictedMessage}>
            {accessMessage ||
              'Access restricted. To protect caregiver privacy and child safety, only verified caregivers can access private community feeds, chats, and groups.'}
          </Text>
          <TouchableOpacity
            style={styles.verifyActionButton}
            onPress={() => navigation.navigate('VerificationRequest')}
          >
            <Text style={styles.verifyActionText}>Request Caregiver Verification</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.signOutLink} onPress={handleLogout}>
            <Text style={styles.signOutLinkText}>Sign in with another account</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Spotlight fallback
  const activeSpotlightList =
    spotlights.length > 0
      ? spotlights
      : [
          {
            id: 'spot-1',
            name: 'Jessica Miller',
            role: 'Verified Caregiver',
            bio: 'Mom of twin boys on the spectrum. Passionate about sensory play, routine building, and communication tools.',
            avatar: '👩‍👦‍👦',
            bgColor: '#EEF2FF',
          },
          {
            id: 'spot-2',
            name: 'Michael Thompson',
            role: 'Verified Caregiver & Special Ed Educator',
            bio: 'Dad of 8yo on the spectrum. Sharing IEP accommodation tips, visual schedules, and morning strategies.',
            avatar: '👨‍🏫',
            bgColor: '#ECFDF5',
          },
        ];

  const currentSpotlight = activeSpotlightList[spotlightIndex] || activeSpotlightList[0];

  return (
    <View style={styles.pageContainer}>
      {/* 1. LEFT NAVIGATION SIDEBAR */}
      <View style={styles.sidebar}>
        {/* Brand Header */}
        <View style={styles.sidebarBrand}>
          <View style={styles.logoBadge}>
            <Text style={styles.logoIcon}>💙</Text>
          </View>
          <View>
            <Text style={styles.brandName}>NIVARA</Text>
            <Text style={styles.brandSub}>Caregiver Community</Text>
          </View>
        </View>

        {/* Navigation List */}
        <ScrollView style={styles.sidebarNav} showsVerticalScrollIndicator={false}>
          <TouchableOpacity
            style={[styles.navItem, { backgroundColor: '#EFF6FF', marginBottom: 8, borderRadius: 12, borderWidth: 1, borderColor: '#DBEAFE' }]}
            onPress={() => navigation.navigate('Home')}
          >
            <Text style={styles.navIcon}>✨</Text>
            <Text style={[styles.navLabel, { color: '#2563EB', fontWeight: '800' }]}>
              NIVARA Home
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.navItem,
              activeSection === 'dashboard' ? styles.navItemActive : null,
            ]}
            onPress={() => setActiveSection('dashboard')}
          >
            <Text style={styles.navIcon}>🏠</Text>
            <Text
              style={[
                styles.navLabel,
                activeSection === 'dashboard' ? styles.navLabelActive : null,
              ]}
            >
              Community Hub
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.navItem,
              activeSection === 'feed' ? styles.navItemActive : null,
            ]}
            onPress={() => setActiveSection('feed')}
          >
            <Text style={styles.navIcon}>💬</Text>
            <Text
              style={[
                styles.navLabel,
                activeSection === 'feed' ? styles.navLabelActive : null,
              ]}
            >
              Community Feed
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.navItem,
              activeSection === 'chats' ? styles.navItemActive : null,
            ]}
            onPress={() => setActiveSection('chats')}
          >
            <Text style={styles.navIcon}>✉️</Text>
            <Text
              style={[
                styles.navLabel,
                activeSection === 'chats' ? styles.navLabelActive : null,
              ]}
            >
              Messages
            </Text>
            {stats.new_messages > 0 && (
              <View style={styles.counterPill}>
                <Text style={styles.counterText}>{stats.new_messages}</Text>
              </View>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.navItem,
              activeSection === 'groups' ? styles.navItemActive : null,
            ]}
            onPress={() => setActiveSection('groups')}
          >
            <Text style={styles.navIcon}>👥</Text>
            <Text
              style={[
                styles.navLabel,
                activeSection === 'groups' ? styles.navLabelActive : null,
              ]}
            >
              Groups
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => setActiveSection('dashboard')}
          >
            <Text style={styles.navIcon}>📅</Text>
            <Text style={styles.navLabel}>Events</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('CaregiverProfile', { userId: user?.id })}
          >
            <Text style={styles.navIcon}>🧑‍🤝‍🧑</Text>
            <Text style={styles.navLabel}>Caregiver Directory</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('PhoneSupport')}
          >
            <Text style={styles.navIcon}>📚</Text>
            <Text style={styles.navLabel}>Resources</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.navItem} onPress={toggleNotificationPanel}>
            <Text style={styles.navIcon}>🔔</Text>
            <Text style={styles.navLabel}>Notifications</Text>
            {stats.notifications > 0 && (
              <View style={styles.counterPill}>
                <Text style={styles.counterText}>{stats.notifications}</Text>
              </View>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => setActiveSection('dashboard')}
          >
            <Text style={styles.navIcon}>🔖</Text>
            <Text style={styles.navLabel}>Saved</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('LiveLocation')}
          >
            <Text style={styles.navIcon}>📍</Text>
            <Text style={styles.navLabel}>GPS & Live Map</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('SafetyPrivacyCenter')}
          >
            <Text style={styles.navIcon}>🛡️</Text>
            <Text style={styles.navLabel}>Safety Center</Text>
          </TouchableOpacity>

          {/* Account Sub-section */}
          <Text style={styles.accountHeading}>ACCOUNT</Text>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('CaregiverProfile', { userId: user?.id })}
          >
            <Text style={styles.navIcon}>👤</Text>
            <Text style={styles.navLabel}>My Profile</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('SafetyPrivacyCenter')}
          >
            <Text style={styles.navIcon}>⚙️</Text>
            <Text style={styles.navLabel}>Privacy Settings</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('PhoneSupport')}
          >
            <Text style={styles.navIcon}>❓</Text>
            <Text style={styles.navLabel}>Support</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.navItem} onPress={handleLogout}>
            <Text style={styles.navIcon}>🚪</Text>
            <Text style={[styles.navLabel, { color: '#EF4444' }]}>Log Out</Text>
          </TouchableOpacity>

          {/* Bottom Safety Space Card */}
          <View style={styles.sidebarSafetyCard}>
            <View style={styles.sidebarSafetyShield}>
              <Text style={{ fontSize: 22 }}>🛡️</Text>
            </View>
            <Text style={styles.sidebarSafetyTitle}>You're in a safe space</Text>
            <Text style={styles.sidebarSafetySub}>
              This community is here to support you. You are valued, heard, and never alone.
            </Text>
            <TouchableOpacity onPress={() => navigation.navigate('SafetyPrivacyCenter')}>
              <Text style={styles.sidebarSafetyLink}>Learn more →</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </View>

      {/* 2. MAIN CONTENT AREA */}
      <View style={styles.mainContent}>
        {/* Top Header Bar */}
        <View style={styles.topHeader}>
          {/* Debounced Search Bar */}
          <View style={styles.searchBar}>
            <Text style={styles.searchIcon}>🔍</Text>
            <TextInput
              style={styles.searchInput}
              placeholder="Search caregivers, groups, posts..."
              placeholderTextColor="#94A3B8"
              value={searchQuery}
              onChangeText={handleSearchChange}
            />
            {searching ? (
              <ActivityIndicator size="small" color="#2563EB" style={{ paddingHorizontal: 6 }} />
            ) : searchQuery ? (
              <TouchableOpacity onPress={() => handleSearchChange('')}>
                <Text style={styles.clearSearchText}>✕</Text>
              </TouchableOpacity>
            ) : null}
          </View>

          {/* Right User & Alert Actions */}
          <View style={styles.topRightRow}>
            {/* Notification Bell Button */}
            <TouchableOpacity style={styles.bellButton} onPress={toggleNotificationPanel}>
              <Text style={styles.bellIcon}>🔔</Text>
              {unreadCount > 0 && (
                <View style={styles.bellBadge}>
                  <Text style={styles.bellBadgeText}>{unreadCount > 99 ? '99+' : unreadCount}</Text>
                </View>
              )}
            </TouchableOpacity>

            {/* Profile Dropdown Chip */}
            <TouchableOpacity
              style={styles.userProfileChip}
              activeOpacity={0.8}
              onPress={() => setUserMenuOpen(!userMenuOpen)}
            >
              <View style={styles.userAvatar}>
                <Text style={{ fontSize: 18 }}>👩‍🏫</Text>
              </View>
              <View style={styles.userNamesContainer}>
                <Text style={styles.headerUserName}>
                  {user?.full_name || 'Sarah Mitchell'}
                </Text>
                <Text style={styles.headerUserStatus}>✓ Verified Caregiver</Text>
              </View>
              <Text style={styles.dropdownArrow}>{userMenuOpen ? '▴' : '▾'}</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* User Dropdown Menu */}
        {userMenuOpen && (
          <View style={styles.dropdownMenu}>
            <TouchableOpacity
              style={styles.dropdownItem}
              onPress={() => {
                setUserMenuOpen(false);
                navigation.navigate('CaregiverProfile', { userId: user?.id });
              }}
            >
              <Text style={styles.dropdownItemText}>👤 My Profile</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.dropdownItem}
              onPress={() => {
                setUserMenuOpen(false);
                navigation.navigate('SafetyPrivacyCenter');
              }}
            >
              <Text style={styles.dropdownItemText}>⚙️ Settings</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.dropdownItem}
              onPress={() => {
                setUserMenuOpen(false);
                toggleNotificationPanel();
              }}
            >
              <Text style={styles.dropdownItemText}>🔔 Notifications</Text>
            </TouchableOpacity>
            <View style={styles.dropdownDivider} />
            <TouchableOpacity style={styles.dropdownItem} onPress={handleLogout}>
              <Text style={[styles.dropdownItemText, { color: '#EF4444' }]}>🚪 Logout</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Notifications Dropdown Panel */}
        {notifMenuOpen && (
          <View style={styles.notifPanel}>
            <View style={styles.notifPanelHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                <Text style={styles.notifPanelTitle}>Notifications</Text>
                {unreadCount > 0 && (
                  <View style={styles.notifPanelCountBadge}>
                    <Text style={styles.notifPanelCountText}>{unreadCount}</Text>
                  </View>
                )}
              </View>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
                {unreadCount > 0 && (
                  <TouchableOpacity onPress={() => markAllAsRead()}>
                    <Text style={styles.markAllReadText}>Mark all read</Text>
                  </TouchableOpacity>
                )}
                <TouchableOpacity onPress={() => setNotifMenuOpen(false)}>
                  <Text style={styles.notifPanelClose}>✕</Text>
                </TouchableOpacity>
              </View>
            </View>
            <ScrollView style={{ maxHeight: 280 }}>
              {loadingNotifs && notifications.length === 0 ? (
                <ActivityIndicator size="small" color="#2563EB" style={{ padding: 20 }} />
              ) : notifications.length === 0 ? (
                <Text style={styles.emptyNotifText}>You're all caught up! ✨</Text>
              ) : (
                notifications.map((n) => (
                  <TouchableOpacity
                    key={n.id}
                    style={[styles.notifItem, !n.read && styles.notifItemUnread]}
                    activeOpacity={0.7}
                    onPress={() => {
                      if (!n.read) markAsRead(n.id);
                    }}
                  >
                    <View style={styles.notifItemRow}>
                      <View style={styles.notifIconContainer}>
                        <Text style={{ fontSize: 14 }}>
                          {n.type === 'comment' ? '💬' : n.type === 'message' ? '✉️' : n.type === 'group' ? '👥' : '🔔'}
                        </Text>
                      </View>
                      <View style={{ flex: 1 }}>
                        <View style={styles.notifItemHeaderRow}>
                          <Text style={[styles.notifItemTitle, !n.read && styles.notifItemTitleUnread]} numberOfLines={1}>
                            {n.title}
                          </Text>
                          {!n.read && <View style={styles.unreadDot} />}
                        </View>
                        <Text style={styles.notifItemBody} numberOfLines={2}>{n.body}</Text>
                        {n.created_at && (
                          <Text style={styles.notifItemTime}>
                            {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </Text>
                        )}
                      </View>
                    </View>
                  </TouchableOpacity>
                ))
              )}
            </ScrollView>
          </View>
        )}

        {/* Search Results Overlay */}
        {searchResults && (
          <View style={styles.searchOverlay}>
            <Text style={styles.searchResultsTitle}>Search Results for "{searchQuery}"</Text>
            <ScrollView style={{ maxHeight: 300 }}>
              {searchResults.posts?.length > 0 && (
                <View style={styles.searchSection}>
                  <Text style={styles.searchSectionHeading}>Posts</Text>
                  {searchResults.posts.map((p) => (
                    <Text key={p.id} style={styles.searchResultItem}>
                      📝 {p.content}
                    </Text>
                  ))}
                </View>
              )}
              {searchResults.groups?.length > 0 && (
                <View style={styles.searchSection}>
                  <Text style={styles.searchSectionHeading}>Groups</Text>
                  {searchResults.groups.map((g) => (
                    <Text key={g.id} style={styles.searchResultItem}>
                      👥 {g.name}
                    </Text>
                  ))}
                </View>
              )}
              {searchResults.caregivers?.length > 0 && (
                <View style={styles.searchSection}>
                  <Text style={styles.searchSectionHeading}>Caregivers</Text>
                  {searchResults.caregivers.map((c) => (
                    <Text key={c.id} style={styles.searchResultItem}>
                      👤 {c.name}
                    </Text>
                  ))}
                </View>
              )}
              {(!searchResults.posts?.length &&
                !searchResults.groups?.length &&
                !searchResults.caregivers?.length) && (
                <Text style={styles.emptyNotifText}>No results found for "{searchQuery}".</Text>
              )}
            </ScrollView>
          </View>
        )}

        {/* Screen Switcher */}
        {activeSection === 'feed' && (
          <View style={{ flex: 1 }}>
            <CommunityFeedScreen navigation={navigation} />
          </View>
        )}

        {activeSection === 'chats' && (
          <View style={{ flex: 1 }}>
            <ChatListScreen navigation={navigation} />
          </View>
        )}

        {activeSection === 'groups' && (
          <View style={{ flex: 1 }}>
            <ActiveGroupsScreen navigation={navigation} />
          </View>
        )}

        {activeSection === 'dashboard' && (
          <ScrollView
            style={styles.dashboardScroll}
            contentContainerStyle={styles.dashboardScrollContent}
            showsVerticalScrollIndicator={false}
          >
            {/* 1. Welcome Back Banner Card */}
            <View style={styles.welcomeBanner}>
              <View style={styles.welcomeTextColumn}>
                <Text style={styles.welcomeTitle}>
                  Welcome back, {firstName}! 👋
                </Text>
                <Text style={styles.welcomeSubtitle}>
                  Your care journey matters. Connect, share, and grow with your
                  caregiver community.
                </Text>
              </View>
              <View style={styles.welcomeArt}>
                <View style={styles.artBubble}>
                  <Text style={{ fontSize: 42 }}>👩‍👧‍👦</Text>
                </View>
              </View>
            </View>

            {/* 2. Key Metrics Row (4 Cards) */}
            <View style={styles.statsRow}>
              {/* Card 1: Groups */}
              <TouchableOpacity
                style={styles.statCard}
                activeOpacity={0.8}
                onPress={() => setActiveSection('groups')}
              >
                <View style={[styles.statIconBadge, { backgroundColor: '#EEF2FF' }]}>
                  <Text style={{ fontSize: 20 }}>👥</Text>
                </View>
                <View>
                  <Text style={styles.statNumber}>
                    {loadingDashboard ? '...' : stats.my_groups || 0}
                  </Text>
                  <Text style={styles.statLabel}>My Groups</Text>
                  <Text style={styles.statSubText}>Active circles</Text>
                </View>
              </TouchableOpacity>

              {/* Card 2: Messages */}
              <TouchableOpacity
                style={styles.statCard}
                activeOpacity={0.8}
                onPress={() => setActiveSection('chats')}
              >
                <View style={[styles.statIconBadge, { backgroundColor: '#E0F2FE' }]}>
                  <Text style={{ fontSize: 20 }}>💬</Text>
                </View>
                <View>
                  <Text style={styles.statNumber}>
                    {loadingDashboard ? '...' : stats.new_messages || 0}
                  </Text>
                  <Text style={styles.statLabel}>New Messages</Text>
                  <Text style={styles.statSubText}>Unread direct chats</Text>
                </View>
              </TouchableOpacity>

              {/* Card 3: Notifications */}
              <TouchableOpacity
                style={styles.statCard}
                activeOpacity={0.8}
                onPress={toggleNotificationPanel}
              >
                <View style={[styles.statIconBadge, { backgroundColor: '#FEF3C7' }]}>
                  <Text style={{ fontSize: 20 }}>🔔</Text>
                </View>
                <View>
                  <Text style={styles.statNumber}>
                    {loadingNotifs ? '...' : unreadCount}
                  </Text>
                  <Text style={styles.statLabel}>Notifications</Text>
                  <Text style={styles.statSubText}>Recent activity</Text>
                </View>

              </TouchableOpacity>

              {/* Card 4: Community */}
              <TouchableOpacity
                style={styles.statCard}
                activeOpacity={0.8}
                onPress={() => setActiveSection('feed')}
              >
                <View style={[styles.statIconBadge, { backgroundColor: '#F3E8FF' }]}>
                  <Text style={{ fontSize: 20 }}>🧑‍🤝‍🧑</Text>
                </View>
                <View>
                  <Text style={styles.statNumber}>
                    {loadingDashboard ? '...' : stats.community_online || 128}
                  </Text>
                  <Text style={styles.statLabel}>Community</Text>
                  <Text style={styles.statSubText}>Online caregivers</Text>
                </View>
              </TouchableOpacity>
            </View>

            {/* 3. Middle Section: Feed (Left) & Events / Suggestions (Right) */}
            <View style={styles.twoColumnGrid}>
              {/* Left Column: Community Feed */}
              <View style={styles.gridLeft}>
                <View style={styles.feedCard}>
                  <View style={styles.cardHeaderRow}>
                    <Text style={styles.cardSectionTitle}>Community Feed</Text>
                    <TouchableOpacity onPress={() => setActiveSection('feed')}>
                      <Text style={styles.seeAllLink}>See all</Text>
                    </TouchableOpacity>
                  </View>

                  {/* Feed Content */}
                  {loadingDashboard ? (
                    <View style={{ padding: 24, alignItems: 'center' }}>
                      <ActivityIndicator size="small" color="#2563EB" />
                      <Text style={[styles.emptyFeedText, { marginTop: 8 }]}>Loading community feed...</Text>
                    </View>
                  ) : posts.length === 0 ? (
                    <Text style={styles.emptyFeedText}>
                      No community posts yet. Be the first to share something!
                    </Text>
                  ) : (
                    posts.map((post) => {
                      const isLiked = !!likedPosts[post.id];
                      const likeCount = postLikesCount[post.id] ?? post.like_count ?? 0;
                      const isSaved = !!savedPosts[post.id];

                      return (
                        <View key={post.id} style={styles.postItem}>
                          {/* Author Header */}
                          <View style={styles.postAuthorRow}>
                            <View style={styles.postAvatar}>
                              <Text style={{ fontSize: 20 }}>
                                {post.author_avatar || '👩‍🏫'}
                              </Text>
                            </View>
                            <View style={{ flex: 1 }}>
                              <View style={styles.nameBadgeRow}>
                                <Text style={styles.postAuthorName}>
                                  {post.author_name || 'Caregiver Member'}
                                </Text>
                                <View style={styles.verifiedCheckBadge}>
                                  <Text style={styles.verifiedCheckText}>✓ Verified</Text>
                                </View>
                              </View>
                              <Text style={styles.postTime}>
                                {post.time_ago || 'Recent post'}
                              </Text>
                            </View>
                            <TouchableOpacity onPress={() => handleToggleSavePost(post.id)}>
                              <Text style={{ fontSize: 16 }}>{isSaved ? '🔖' : '📑'}</Text>
                            </TouchableOpacity>
                          </View>

                          {/* Content */}
                          <Text style={styles.postContent}>{post.content}</Text>

                          {/* Category Tags */}
                          <View style={styles.tagsRow}>
                            {(post.tags || [post.category || 'Sensory Support', 'Parenting']).map(
                              (tag, idx) => (
                                <View key={idx} style={styles.tagBadge}>
                                  <Text style={styles.tagText}>{tag}</Text>
                                </View>
                              )
                            )}
                          </View>

                          {/* Actions: Likes, Comments, Share */}
                          <View style={styles.postActionsRow}>
                            <TouchableOpacity
                              style={styles.actionBtn}
                              onPress={() => handleToggleLike(post.id)}
                            >
                              <Text style={{ fontSize: 16 }}>
                                {isLiked ? '❤️' : '🤍'}
                              </Text>
                              <Text
                                style={[
                                  styles.actionCount,
                                  isLiked ? { color: '#EF4444' } : null,
                                ]}
                              >
                                {likeCount}
                              </Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                              style={styles.actionBtn}
                              onPress={() => openCommentsForPost(post)}
                            >
                              <Text style={{ fontSize: 16 }}>💬</Text>
                              <Text style={styles.actionCount}>
                                {post.comment_count || 0}
                              </Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                              style={styles.actionBtn}
                              onPress={() => handleSharePost(post)}
                            >
                              <Text style={{ fontSize: 16 }}>↗️</Text>
                              <Text style={styles.actionCount}>Share</Text>
                            </TouchableOpacity>
                          </View>
                        </View>
                      );
                    })
                  )}

                  {/* Create Post Button */}
                  <TouchableOpacity
                    style={styles.createPostBtn}
                    activeOpacity={0.8}
                    onPress={() => setCreatePostVisible(true)}
                  >
                    <Text style={styles.createPostBtnText}>+ Create Post</Text>
                  </TouchableOpacity>
                </View>
              </View>

              {/* Right Column: Events & Suggested Groups */}
              <View style={styles.gridRight}>
                {/* Upcoming Events Card */}
                <View style={styles.eventsCard}>
                  <View style={styles.cardHeaderRow}>
                    <Text style={styles.cardSectionTitle}>Upcoming Events</Text>
                    <TouchableOpacity onPress={() => setActiveSection('dashboard')}>
                      <Text style={styles.seeAllLink}>See all</Text>
                    </TouchableOpacity>
                  </View>

                  {eventsError ? (
                    <View style={styles.widgetErrorContainer}>
                      <Text style={styles.widgetErrorText}>{eventsError}</Text>
                      <TouchableOpacity onPress={loadModularEvents}>
                        <Text style={styles.widgetRetryText}>Retry</Text>
                      </TouchableOpacity>
                    </View>
                  ) : events.length === 0 && !loadingDashboard ? (
                    <Text style={styles.emptyFeedText}>No upcoming events scheduled.</Text>
                  ) : (
                    events.map((e) => (
                      <View key={e.id} style={styles.eventItem}>
                        <View style={styles.eventDateBox}>
                          <Text style={styles.eventMonth}>{e.month || 'MAY'}</Text>
                          <Text style={styles.eventDay}>{e.day || '24'}</Text>
                        </View>
                        <View style={{ flex: 1 }}>
                          <Text style={styles.eventTitle}>{e.title}</Text>
                          <Text style={styles.eventMeta}>
                            {e.time} • {e.location}
                          </Text>
                        </View>
                      </View>
                    ))
                  )}

                  <TouchableOpacity
                    style={styles.calendarBtn}
                    onPress={() => setActiveSection('dashboard')}
                  >
                    <Text style={styles.calendarBtnText}>🗓️ View Calendar</Text>
                  </TouchableOpacity>
                </View>

                {/* Suggested for You Card */}
                <View style={styles.suggestedCard}>
                  <View style={styles.cardHeaderRow}>
                    <Text style={styles.cardSectionTitle}>Suggested for you</Text>
                    <TouchableOpacity onPress={() => setActiveSection('groups')}>
                      <Text style={styles.seeAllLink}>See all</Text>
                    </TouchableOpacity>
                  </View>

                  {groupsError ? (
                    <View style={styles.widgetErrorContainer}>
                      <Text style={styles.widgetErrorText}>{groupsError}</Text>
                      <TouchableOpacity onPress={loadModularGroups}>
                        <Text style={styles.widgetRetryText}>Retry</Text>
                      </TouchableOpacity>
                    </View>
                  ) : suggestedGroups.length === 0 && !loadingDashboard ? (
                    <Text style={styles.emptyFeedText}>No suggested groups right now.</Text>
                  ) : (
                    suggestedGroups.map((g) => {
                      const isJoined = !!joinedGroups[g.id];
                      return (
                        <View key={g.id} style={styles.suggestedRow}>
                          <View style={styles.suggestedIconBadge}>
                            <Text style={{ fontSize: 22 }}>👥</Text>
                          </View>
                          <View style={{ flex: 1 }}>
                            <Text style={styles.suggestedGroupName}>{g.name}</Text>
                            <Text style={styles.suggestedMembers}>
                              {g.member_count || 120} members
                            </Text>
                            <View style={styles.avatarsRow}>
                              <Text style={{ fontSize: 12 }}>👩‍⚕️ 👨‍🏫 👩‍👦‍👦 +28</Text>
                            </View>
                          </View>
                          <TouchableOpacity
                            style={[
                              styles.joinGroupBtn,
                              isJoined ? styles.joinedGroupBtn : null,
                            ]}
                            onPress={() => handleToggleJoinGroup(g.id)}
                          >
                            <Text
                              style={[
                                styles.joinGroupBtnText,
                                isJoined ? styles.joinedGroupBtnText : null,
                              ]}
                            >
                              {isJoined ? 'Joined' : 'Join'}
                            </Text>
                          </TouchableOpacity>
                        </View>
                      );
                    })
                  )}
                </View>
              </View>
            </View>

            {/* 4. Bottom Section: Caregiver Spotlight (Left) & Quick Actions (Right) */}
            <View style={styles.twoColumnGrid}>
              {/* Caregiver Spotlight */}
              <View style={styles.gridLeft}>
                <View style={styles.spotlightCard}>
                  <View style={styles.spotlightHeader}>
                    <Text style={styles.spotlightBadgeTitle}>
                      Caregiver Spotlight
                    </Text>
                  </View>

                  <View style={styles.spotlightBodyRow}>
                    <View
                      style={[
                        styles.spotlightAvatarCircle,
                        { backgroundColor: currentSpotlight.bgColor || '#EEF2FF' },
                      ]}
                    >
                      <Text style={{ fontSize: 44 }}>
                        {currentSpotlight.avatar || '👩‍👦‍👦'}
                      </Text>
                    </View>

                    <View style={{ flex: 1, paddingLeft: 16 }}>
                      <Text style={styles.spotlightName}>
                        {currentSpotlight.name}
                      </Text>
                      <View style={styles.spotlightVerifiedRow}>
                        <Text style={styles.greenCheck}>✓</Text>
                        <Text style={styles.spotlightRole}>
                          {currentSpotlight.role || 'Verified Caregiver'}
                        </Text>
                      </View>
                      <Text style={styles.spotlightBio}>
                        {currentSpotlight.bio}
                      </Text>

                      <View style={styles.spotlightFooterRow}>
                        <TouchableOpacity
                          style={styles.viewProfileBtn}
                          onPress={() =>
                            navigation.navigate('CaregiverProfile', {
                              userId: currentSpotlight.id || 'user-verified-sarah',
                            })
                          }
                        >
                          <Text style={styles.viewProfileBtnText}>View Profile</Text>
                        </TouchableOpacity>

                        <View style={styles.paginationRow}>
                          <Text style={styles.paginationText}>
                            {spotlightIndex + 1}/{activeSpotlightList.length}
                          </Text>
                          <TouchableOpacity
                            style={styles.pageArrow}
                            onPress={() =>
                              setSpotlightIndex((prev) =>
                                prev > 0 ? prev - 1 : activeSpotlightList.length - 1
                              )
                            }
                          >
                            <Text style={styles.pageArrowText}>‹</Text>
                          </TouchableOpacity>
                          <TouchableOpacity
                            style={styles.pageArrow}
                            onPress={() =>
                              setSpotlightIndex((prev) =>
                                prev < activeSpotlightList.length - 1 ? prev + 1 : 0
                              )
                            }
                          >
                            <Text style={styles.pageArrowText}>›</Text>
                          </TouchableOpacity>
                        </View>
                      </View>
                    </View>
                  </View>
                </View>
              </View>

              {/* Quick Actions (2x2 Grid) */}
              <View style={styles.gridRight}>
                <View style={styles.quickActionsCard}>
                  <Text style={styles.cardSectionTitle}>Quick Actions</Text>

                  <View style={styles.actions2x2}>
                    {/* Action 1: Find Caregivers */}
                    <TouchableOpacity
                      style={styles.actionTile}
                      onPress={() =>
                        navigation.navigate('CaregiverProfile', {
                          userId: user?.id,
                        })
                      }
                    >
                      <View
                        style={[
                          styles.actionTileIcon,
                          { backgroundColor: '#EEF2FF' },
                        ]}
                      >
                        <Text style={{ fontSize: 18 }}>👤</Text>
                      </View>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.actionTileTitle}>Find Caregivers</Text>
                        <Text style={styles.actionTileSub}>
                          Connect with verified caregivers
                        </Text>
                      </View>
                    </TouchableOpacity>

                    {/* Action 2: Join Groups */}
                    <TouchableOpacity
                      style={styles.actionTile}
                      onPress={() => setActiveSection('groups')}
                    >
                      <View
                        style={[
                          styles.actionTileIcon,
                          { backgroundColor: '#F3E8FF' },
                        ]}
                      >
                        <Text style={{ fontSize: 18 }}>👥</Text>
                      </View>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.actionTileTitle}>Join Groups</Text>
                        <Text style={styles.actionTileSub}>
                          Explore and join support groups
                        </Text>
                      </View>
                    </TouchableOpacity>

                    {/* Action 3: Ask a Question */}
                    <TouchableOpacity
                      style={styles.actionTile}
                      onPress={() => setCreatePostVisible(true)}
                    >
                      <View
                        style={[
                          styles.actionTileIcon,
                          { backgroundColor: '#ECFDF5' },
                        ]}
                      >
                        <Text style={{ fontSize: 18 }}>❓</Text>
                      </View>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.actionTileTitle}>Ask a Question</Text>
                        <Text style={styles.actionTileSub}>
                          Get advice from the community
                        </Text>
                      </View>
                    </TouchableOpacity>

                    {/* Action 4: Resource Center */}
                    <TouchableOpacity
                      style={styles.actionTile}
                      onPress={() => navigation.navigate('PhoneSupport')}
                    >
                      <View
                        style={[
                          styles.actionTileIcon,
                          { backgroundColor: '#FEF3C7' },
                        ]}
                      >
                        <Text style={{ fontSize: 18 }}>📖</Text>
                      </View>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.actionTileTitle}>Resource Center</Text>
                        <Text style={styles.actionTileSub}>
                          Helpful guides and toolkits
                        </Text>
                      </View>
                    </TouchableOpacity>
                  </View>
                </View>
              </View>
            </View>

            {/* 5. Bottom Community Trust Banner */}
            <View style={styles.bottomCommunityBanner}>
              <View style={styles.bottomBannerLeft}>
                <View style={styles.bottomShieldIcon}>
                  <Text style={{ fontSize: 18 }}>🛡️</Text>
                </View>
                <View>
                  <Text style={styles.bottomBannerTitle}>
                    You are a valued part of our community
                  </Text>
                  <Text style={styles.bottomBannerSub}>
                    Remember: Be kind, be supportive, and take care of yourself too.
                  </Text>
                </View>
              </View>

              <TouchableOpacity
                style={styles.guidelinesBtn}
                onPress={() => navigation.navigate('SafetyPrivacyCenter')}
              >
                <Text style={styles.guidelinesBtnText}>
                  🛡️ Community Guidelines
                </Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        )}
      </View>

      {/* CREATE POST MODAL */}
      <Modal
        visible={createPostVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setCreatePostVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Create Community Post</Text>
              <TouchableOpacity onPress={() => setCreatePostVisible(false)}>
                <Text style={styles.modalClose}>✕</Text>
              </TouchableOpacity>
            </View>

            {postError ? (
              <View style={styles.modalErrorBox}>
                <Text style={styles.modalErrorText}>{postError}</Text>
              </View>
            ) : null}

            <Text style={styles.modalLabel}>Category</Text>
            <View style={styles.categorySelectRow}>
              {['Sensory Support', 'School Life', 'Daily Wins', 'Advice Needed'].map(
                (cat) => (
                  <TouchableOpacity
                    key={cat}
                    style={[
                      styles.categoryOption,
                      newPostCategory === cat ? styles.categoryOptionActive : null,
                    ]}
                    onPress={() => setNewPostCategory(cat)}
                  >
                    <Text
                      style={[
                        styles.categoryOptionText,
                        newPostCategory === cat
                          ? styles.categoryOptionTextActive
                          : null,
                      ]}
                    >
                      {cat}
                    </Text>
                  </TouchableOpacity>
                )
              )}
            </View>

            <Text style={styles.modalLabel}>Your Message</Text>
            <TextInput
              style={styles.modalTextInput}
              placeholder="Share advice, celebrate a win, or ask a question..."
              placeholderTextColor="#94A3B8"
              multiline
              numberOfLines={4}
              value={newPostContent}
              onChangeText={(t) => {
                setNewPostContent(t);
                if (postError) setPostError('');
              }}
            />

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelBtn}
                onPress={() => setCreatePostVisible(false)}
              >
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.publishBtn,
                  submittingPost || !newPostContent.trim()
                    ? styles.publishBtnDisabled
                    : null,
                ]}
                onPress={handleCreatePostSubmit}
                disabled={submittingPost || !newPostContent.trim()}
              >
                {submittingPost ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <Text style={styles.publishBtnText}>Publish Post</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* COMMENTS MODAL */}
      <Modal
        visible={commentModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setCommentModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalCard, { maxHeight: '80%' }]}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Post Discussion</Text>
              <TouchableOpacity onPress={() => setCommentModalVisible(false)}>
                <Text style={styles.modalClose}>✕</Text>
              </TouchableOpacity>
            </View>

            {activePostForComments && (
              <View style={styles.commentHeaderPost}>
                <Text style={styles.commentHeaderAuthor}>
                  {activePostForComments.author_name}
                </Text>
                <Text style={styles.commentHeaderContent} numberOfLines={2}>
                  {activePostForComments.content}
                </Text>
              </View>
            )}

            <ScrollView style={styles.commentsListScroll}>
              {loadingComments ? (
                <ActivityIndicator size="small" color="#2563EB" style={{ padding: 20 }} />
              ) : commentsList.length === 0 ? (
                <Text style={styles.emptyCommentsText}>
                  No comments yet. Start the conversation!
                </Text>
              ) : (
                commentsList.map((c) => (
                  <View key={c.id} style={styles.commentItem}>
                    <View style={styles.commentItemHeader}>
                      <Text style={styles.commentItemAvatar}>
                        {c.author_avatar || '👩‍🏫'}
                      </Text>
                      <Text style={styles.commentItemAuthor}>
                        {c.author_name || 'Caregiver'}
                      </Text>
                    </View>
                    <Text style={styles.commentItemText}>{c.content}</Text>
                  </View>
                ))
              )}
            </ScrollView>

            {/* Add Comment Input */}
            <View style={styles.addCommentRow}>
              <TextInput
                style={styles.commentInput}
                placeholder="Write a supportive reply..."
                placeholderTextColor="#94A3B8"
                value={newCommentText}
                onChangeText={setNewCommentText}
              />
              <TouchableOpacity
                style={[
                  styles.sendCommentBtn,
                  !newCommentText.trim() || submittingComment
                    ? styles.sendCommentBtnDisabled
                    : null,
                ]}
                onPress={handleAddComment}
                disabled={!newCommentText.trim() || submittingComment}
              >
                {submittingComment ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <Text style={styles.sendCommentBtnText}>Post</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  pageContainer: {
    flex: 1,
    flexDirection: isDesktop ? 'row' : 'column',
    backgroundColor: '#FAFBFD',
    height: '100%',
  },

  // SIDEBAR
  sidebar: {
    width: isDesktop ? 260 : '100%',
    backgroundColor: '#FFFFFF',
    borderRightWidth: isDesktop ? 1 : 0,
    borderBottomWidth: isDesktop ? 0 : 1,
    borderColor: '#E2E8F0',
    paddingVertical: 18,
    paddingHorizontal: 16,
    height: isDesktop ? '100%' : 'auto',
  },
  sidebarBrand: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    paddingHorizontal: 8,
  },
  logoBadge: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  logoIcon: {
    fontSize: 20,
  },
  brandName: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
    letterSpacing: 0.5,
  },
  brandSub: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  sidebarNav: {
    flex: 1,
  },
  navItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 14,
    marginBottom: 4,
  },
  navItemActive: {
    backgroundColor: '#EEF2FF',
  },
  navIcon: {
    fontSize: 16,
    marginRight: 12,
  },
  navLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
    flex: 1,
  },
  navLabelActive: {
    color: '#2563EB',
    fontWeight: '700',
  },
  counterPill: {
    backgroundColor: '#2563EB',
    borderRadius: 10,
    paddingHorizontal: 7,
    paddingVertical: 2,
  },
  counterText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '700',
  },
  accountHeading: {
    fontSize: 11,
    fontWeight: '800',
    color: '#94A3B8',
    letterSpacing: 0.8,
    marginTop: 18,
    marginBottom: 8,
    paddingHorizontal: 12,
  },
  sidebarSafetyCard: {
    backgroundColor: '#F0F7FF',
    borderRadius: 18,
    padding: 16,
    marginTop: 18,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#DBEAFE',
  },
  sidebarSafetyShield: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
    shadowColor: '#2563EB',
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 1,
  },
  sidebarSafetyTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 4,
  },
  sidebarSafetySub: {
    fontSize: 11,
    color: '#64748B',
    lineHeight: 16,
    marginBottom: 10,
  },
  sidebarSafetyLink: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },

  // MAIN CONTENT & HEADER
  mainContent: {
    flex: 1,
    height: '100%',
    backgroundColor: '#FAFBFD',
    position: 'relative',
  },
  topHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    gap: 16,
  },
  searchBar: {
    flex: 1,
    maxWidth: 500,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FAFBFD',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderRadius: 24,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  searchIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    color: '#0F172A',
    padding: 0,
  },
  clearSearchText: {
    fontSize: 14,
    color: '#94A3B8',
    paddingHorizontal: 6,
  },
  topRightRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  bellButton: {
    position: 'relative',
    padding: 8,
    backgroundColor: '#F8FAFC',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  bellIcon: {
    fontSize: 16,
  },
  bellDot: {
    position: 'absolute',
    top: 6,
    right: 8,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444',
  },
  bellBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#EF4444',
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 4,
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
  },
  bellBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '800',
  },
  userProfileChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FAFBFD',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderRadius: 24,
    paddingVertical: 4,
    paddingHorizontal: 10,
    gap: 8,
  },
  userAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  userNamesContainer: {
    paddingRight: 4,
  },
  headerUserName: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  headerUserStatus: {
    fontSize: 10,
    color: '#10B981',
    fontWeight: '700',
  },
  dropdownArrow: {
    fontSize: 14,
    color: '#64748B',
  },

  // DROPDOWN MENUS
  dropdownMenu: {
    position: 'absolute',
    top: 65,
    right: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingVertical: 8,
    width: 180,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 8,
    zIndex: 100,
  },
  dropdownItem: {
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  dropdownItemText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#334155',
  },
  dropdownDivider: {
    height: 1,
    backgroundColor: '#F1F5F9',
    marginVertical: 4,
  },
  notifPanel: {
    position: 'absolute',
    top: 65,
    right: 80,
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    width: 320,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOpacity: 0.15,
    shadowRadius: 18,
    elevation: 10,
    zIndex: 100,
  },
  notifPanelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
    paddingBottom: 8,
  },
  notifPanelTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  notifPanelCountBadge: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
  },
  notifPanelCountText: {
    color: '#2563EB',
    fontSize: 11,
    fontWeight: '700',
  },
  markAllReadText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#2563EB',
  },
  notifPanelClose: {
    fontSize: 14,
    color: '#64748B',
    paddingHorizontal: 4,
  },
  notifItem: {
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F8FAFC',
    borderRadius: 10,
  },
  notifItemUnread: {
    backgroundColor: '#F8FAFC',
  },
  notifItemRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
  },
  notifIconContainer: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 2,
  },
  notifItemHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  notifItemTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#334155',
    flex: 1,
  },
  notifItemTitleUnread: {
    fontWeight: '800',
    color: '#0F172A',
  },
  unreadDot: {
    width: 7,
    height: 7,
    borderRadius: 3.5,
    backgroundColor: '#2563EB',
    marginLeft: 6,
  },
  notifItemBody: {
    fontSize: 11,
    color: '#64748B',
    lineHeight: 16,
  },
  notifItemTime: {
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 4,
  },
  emptyNotifText: {
    fontSize: 12,
    color: '#94A3B8',
    textAlign: 'center',
    paddingVertical: 20,
  },


  // SEARCH OVERLAY
  searchOverlay: {
    position: 'absolute',
    top: 65,
    left: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    width: 480,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOpacity: 0.15,
    shadowRadius: 18,
    elevation: 10,
    zIndex: 99,
  },
  searchResultsTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 10,
  },
  searchSection: {
    marginBottom: 10,
  },
  searchSectionHeading: {
    fontSize: 11,
    fontWeight: '800',
    color: '#2563EB',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  searchResultItem: {
    fontSize: 13,
    color: '#334155',
    paddingVertical: 4,
  },

  // DASHBOARD SCROLL & BANNER
  dashboardScroll: {
    flex: 1,
  },
  dashboardScrollContent: {
    padding: 24,
    maxWidth: 1240,
    alignSelf: 'center',
    width: '100%',
  },
  welcomeBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    borderRadius: 22,
    paddingVertical: 24,
    paddingHorizontal: 28,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#DBEAFE',
  },
  welcomeTextColumn: {
    flex: 1,
    paddingRight: 16,
  },
  welcomeTitle: {
    fontSize: 26,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 6,
    letterSpacing: -0.5,
  },
  welcomeSubtitle: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 22,
  },
  welcomeArt: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  artBubble: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#2563EB',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 2,
  },

  // STAT METRIC CARDS ROW
  statsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    minWidth: 150,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    gap: 14,
    shadowColor: '#0F172A',
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 1,
  },
  statIconBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0F172A',
  },
  statLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#334155',
    marginTop: 2,
  },
  statSubText: {
    fontSize: 11,
    color: '#94A3B8',
    fontWeight: '500',
  },

  // 2-COLUMN GRID
  twoColumnGrid: {
    flexDirection: isDesktop ? 'row' : 'column',
    gap: 20,
    marginBottom: 20,
  },
  gridLeft: {
    flex: 1.6,
  },
  gridRight: {
    flex: 1.2,
    gap: 20,
  },

  // CARDS GENERAL
  feedCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardSectionTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  seeAllLink: {
    fontSize: 13,
    fontWeight: '700',
    color: '#2563EB',
  },
  emptyFeedText: {
    fontSize: 13,
    color: '#94A3B8',
    textAlign: 'center',
    paddingVertical: 24,
  },
  widgetErrorContainer: {
    padding: 16,
    alignItems: 'center',
  },
  widgetErrorText: {
    fontSize: 12,
    color: '#EF4444',
    marginBottom: 6,
  },
  widgetRetryText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },

  // POST ITEM
  postItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
    paddingBottom: 16,
    marginBottom: 16,
  },
  postAuthorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  postAvatar: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  nameBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  postAuthorName: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  verifiedCheckBadge: {
    backgroundColor: '#ECFDF5',
    borderRadius: 12,
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderWidth: 1,
    borderColor: '#A7F3D0',
  },
  verifiedCheckText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#059669',
  },
  postTime: {
    fontSize: 11,
    color: '#94A3B8',
    marginTop: 2,
  },
  postContent: {
    fontSize: 14,
    color: '#334155',
    lineHeight: 21,
    marginBottom: 12,
  },
  tagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  tagBadge: {
    backgroundColor: '#F1F5F9',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  tagText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#475569',
  },
  postActionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 20,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  actionCount: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
  },
  createPostBtn: {
    borderWidth: 1.5,
    borderColor: '#2563EB',
    borderRadius: 24,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 6,
  },
  createPostBtnText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
  },

  // EVENTS CARD
  eventsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  eventItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    marginBottom: 14,
  },
  eventDateBox: {
    width: 46,
    height: 46,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  eventMonth: {
    fontSize: 10,
    fontWeight: '800',
    color: '#2563EB',
  },
  eventDay: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  eventTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  eventMeta: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  calendarBtn: {
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 20,
    paddingVertical: 10,
    alignItems: 'center',
    marginTop: 4,
  },
  calendarBtnText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#334155',
  },

  // SUGGESTED GROUP CARD
  suggestedCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  suggestedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 8,
  },
  suggestedIconBadge: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#ECFDF5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  suggestedGroupName: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  suggestedMembers: {
    fontSize: 11,
    color: '#64748B',
  },
  avatarsRow: {
    marginTop: 2,
  },
  joinGroupBtn: {
    backgroundColor: '#EFF6FF',
    borderColor: '#BFDBFE',
    borderWidth: 1,
    borderRadius: 16,
    paddingVertical: 6,
    paddingHorizontal: 16,
  },
  joinedGroupBtn: {
    backgroundColor: '#10B981',
    borderColor: '#10B981',
  },
  joinGroupBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },
  joinedGroupBtnText: {
    color: '#FFFFFF',
  },

  // SPOTLIGHT CARD
  spotlightCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  spotlightHeader: {
    marginBottom: 14,
  },
  spotlightBadgeTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  spotlightBodyRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  spotlightAvatarCircle: {
    width: 86,
    height: 86,
    borderRadius: 43,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E2E8F0',
  },
  spotlightName: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  spotlightVerifiedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginVertical: 2,
  },
  greenCheck: {
    color: '#10B981',
    fontWeight: '900',
    fontSize: 12,
  },
  spotlightRole: {
    fontSize: 11,
    color: '#10B981',
    fontWeight: '700',
  },
  spotlightBio: {
    fontSize: 12,
    color: '#475569',
    lineHeight: 18,
    marginVertical: 6,
  },
  spotlightFooterRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  viewProfileBtn: {
    backgroundColor: '#EFF6FF',
    borderRadius: 14,
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  viewProfileBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },
  paginationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  paginationText: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  pageArrow: {
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  pageArrowText: {
    fontSize: 18,
    color: '#64748B',
    fontWeight: '700',
  },

  // QUICK ACTIONS
  quickActionsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  actions2x2: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 14,
  },
  actionTile: {
    flex: 1,
    minWidth: 140,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FAFBFD',
    borderRadius: 16,
    padding: 12,
    gap: 10,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
  },
  actionTileIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionTileTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
  },
  actionTileSub: {
    fontSize: 10,
    color: '#64748B',
    marginTop: 2,
  },

  // BOTTOM TRUST BANNER
  bottomCommunityBanner: {
    flexDirection: isDesktop ? 'row' : 'column',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    borderRadius: 18,
    padding: 18,
    borderWidth: 1,
    borderColor: '#DBEAFE',
    gap: 14,
  },
  bottomBannerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  bottomShieldIcon: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  bottomBannerTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1E293B',
  },
  bottomBannerSub: {
    fontSize: 11,
    color: '#475569',
    marginTop: 2,
  },
  guidelinesBtn: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  guidelinesBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },

  // MODALS
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    padding: 24,
    width: '100%',
    maxWidth: 520,
    shadowColor: '#0F172A',
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 8,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  modalClose: {
    fontSize: 18,
    color: '#64748B',
    padding: 4,
  },
  modalErrorBox: {
    backgroundColor: '#FEE2E2',
    borderRadius: 12,
    padding: 10,
    marginBottom: 10,
  },
  modalErrorText: {
    fontSize: 12,
    color: '#DC2626',
    fontWeight: '600',
  },
  modalLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#475569',
    marginBottom: 8,
    marginTop: 10,
  },
  categorySelectRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  categoryOption: {
    backgroundColor: '#F1F5F9',
    borderRadius: 14,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  categoryOptionActive: {
    backgroundColor: '#2563EB',
    borderColor: '#2563EB',
  },
  categoryOptionText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#475569',
  },
  categoryOptionTextActive: {
    color: '#FFFFFF',
  },
  modalTextInput: {
    backgroundColor: '#FAFBFD',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderRadius: 16,
    padding: 14,
    fontSize: 14,
    color: '#0F172A',
    minHeight: 110,
    textAlignVertical: 'top',
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
    marginTop: 20,
  },
  cancelBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  cancelBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  publishBtn: {
    backgroundColor: '#2563EB',
    borderRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
  publishBtnDisabled: {
    backgroundColor: '#93C5FD',
  },
  publishBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },

  // COMMENTS MODAL SPECIFIC
  commentHeaderPost: {
    backgroundColor: '#FAFBFD',
    borderRadius: 14,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  commentHeaderAuthor: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
    marginBottom: 2,
  },
  commentHeaderContent: {
    fontSize: 13,
    color: '#475569',
  },
  commentsListScroll: {
    maxHeight: 220,
    marginBottom: 12,
  },
  emptyCommentsText: {
    fontSize: 12,
    color: '#94A3B8',
    textAlign: 'center',
    paddingVertical: 16,
  },
  commentItem: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  commentItemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 2,
  },
  commentItemAvatar: {
    fontSize: 14,
  },
  commentItemAuthor: {
    fontSize: 12,
    fontWeight: '700',
    color: '#0F172A',
  },
  commentItemText: {
    fontSize: 13,
    color: '#334155',
    paddingLeft: 20,
  },
  addCommentRow: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center',
  },
  commentInput: {
    flex: 1,
    backgroundColor: '#FAFBFD',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 8,
    fontSize: 13,
    color: '#0F172A',
  },
  sendCommentBtn: {
    backgroundColor: '#2563EB',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 9,
  },
  sendCommentBtnDisabled: {
    backgroundColor: '#93C5FD',
  },
  sendCommentBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
  },

  // UNVERIFIED RESTRICTED
  restrictedRoot: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FAFBFD',
    padding: 20,
  },
  restrictedCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 32,
    maxWidth: 440,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  shieldCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  shieldEmoji: {
    fontSize: 36,
  },
  restrictedHeading: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 8,
    textAlign: 'center',
  },
  restrictedMessage: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 20,
  },
  verifyActionButton: {
    backgroundColor: '#2563EB',
    borderRadius: 20,
    paddingVertical: 12,
    paddingHorizontal: 24,
    width: '100%',
    alignItems: 'center',
    marginBottom: 12,
  },
  verifyActionText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  signOutLink: {
    paddingVertical: 8,
  },
  signOutLinkText: {
    color: '#64748B',
    fontSize: 13,
    fontWeight: '600',
  },
});
