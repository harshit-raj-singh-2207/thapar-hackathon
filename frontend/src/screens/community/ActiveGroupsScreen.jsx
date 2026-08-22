import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  TextInput,
  ScrollView,
  Dimensions,
  Platform,
  SafeAreaView,
  Alert,
} from 'react-native';

const { width } = Dimensions.get('window');
const isDesktop = Platform.OS === 'web' ? width > 768 : width > 600;

export default function ActiveGroupsScreen({ navigation }) {
  const [postText, setPostText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isJoined, setIsJoined] = useState(true);
  const [posts, setPosts] = useState([
    {
      id: '1',
      authorInitials: 'SJ',
      authorName: 'Sarah Jenkins',
      timestamp: '2 hours ago',
      content:
        'Hi everyone, we just received our diagnosis last week. It feels overwhelming to process all the medical paperwork and sensory schedules, but reading your posts has given us so much hope.',
      likes: 12,
      comments: 5,
    },
    {
      id: '2',
      authorInitials: 'MR',
      authorName: 'Marcus Reed',
      timestamp: '5 hours ago',
      content:
        'Does anyone have recommendations for noise-canceling headphones or quiet spaces for kids aged 4-6? We are planning our first family park trip after speech therapy.',
      likes: 24,
      comments: 9,
    },
  ]);

  const handleCreatePost = () => {
    if (!postText.trim()) return;
    const newPost = {
      id: Date.now().toString(),
      authorInitials: 'U',
      authorName: 'You',
      timestamp: 'Just now',
      content: postText,
      likes: 0,
      comments: 0,
    };
    setPosts([newPost, ...posts]);
    setPostText('');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.appContainer}>
        {/* Left Navigation Sidebar */}
        {isDesktop && (
          <View style={styles.sidebar}>
            <View style={styles.sidebarTopContent}>
              {/* Caregiver Portal Brand Header */}
              <View style={styles.brandContainer}>
                <View style={styles.brandLogoBox}>
                  <Text style={styles.brandLogoIcon}>🛡️</Text>
                </View>
                <View style={styles.brandTextWrapper}>
                  <Text style={styles.brandTitle}>Caregiver Portal</Text>
                  <View style={styles.verificationBadge}>
                    <Text style={styles.verificationBadgeText}>Verification In Progress</Text>
                  </View>
                </View>
              </View>

              {/* Sidebar Menu Items */}
              <View style={styles.menuContainer}>
                <TouchableOpacity
                  style={styles.navItem}
                  onPress={() => navigation?.navigate?.('CommunityHome')}
                >
                  <Text style={styles.navIcon}>🎛️</Text>
                  <Text style={styles.navText}>Dashboard</Text>
                </TouchableOpacity>

                {/* Active Highlighted Item */}
                <TouchableOpacity style={[styles.navItem, styles.navItemActive]}>
                  <Text style={[styles.navIcon, styles.navIconActive]}>👥</Text>
                  <Text style={styles.navTextActive}>Active Groups</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.navItem}
                  onPress={() => navigation?.navigate?.('VerificationRequest')}
                >
                  <Text style={styles.navIcon}>🛡️</Text>
                  <Text style={styles.navText}>Verification Status</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.navItem}
                  onPress={() => navigation?.navigate?.('SafetyPrivacyCenter')}
                >
                  <Text style={styles.navIcon}>📖</Text>
                  <Text style={styles.navText}>Community Guidelines</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.navItem}
                  onPress={() => navigation?.navigate?.('PhoneSupport')}
                >
                  <Text style={styles.navIcon}>🎧</Text>
                  <Text style={styles.navText}>Support Center</Text>
                </TouchableOpacity>
              </View>

              {/* Settings & Sign Out */}
              <View style={styles.sidebarBottomNav}>
                <TouchableOpacity style={styles.navItem}>
                  <Text style={styles.navIcon}>⚙️</Text>
                  <Text style={styles.navText}>Settings</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.navItem}>
                  <Text style={styles.navIcon}>🚪</Text>
                  <Text style={styles.navText}>Sign Out</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Sidebar Bottom Faded Background Image Graphic */}
            <View style={styles.sidebarBgGraphicWrapper}>
              <Image
                source={require('../../../assets/images/sidebar_bottom_bg.jpg')}
                style={styles.sidebarBgImage}
                resizeMode="cover"
              />
            </View>
          </View>
        )}

        {/* Main Content Workspace */}
        <View style={styles.mainContent}>
          {/* Main Top Header */}
          <View style={styles.topHeader}>
            <Text style={styles.topPageTitle}>Support Center</Text>

            <View style={styles.topHeaderRight}>
              <TouchableOpacity style={styles.headerIconButton}>
                <Text style={styles.headerIconText}>🔔</Text>
                <View style={styles.notificationDot} />
              </TouchableOpacity>

              <TouchableOpacity style={styles.headerIconButton}>
                <Text style={styles.headerIconText}>❓</Text>
              </TouchableOpacity>

              <View style={styles.userProfileAvatar}>
                <Text style={styles.userAvatarText}>👤</Text>
              </View>
            </View>
          </View>

          {/* Scrollable Canvas */}
          <ScrollView
            style={styles.scrollCanvas}
            contentContainerStyle={styles.scrollCanvasContent}
            showsVerticalScrollIndicator={false}
          >
            {/* Page Header Title */}
            <Text style={styles.pageMainTitle}>Active Groups</Text>

            {/* Two-Column Grid Layout */}
            <View style={[styles.gridContainer, isDesktop && styles.gridContainerDesktop]}>
              {/* Left Column: Group Banner, Composer, Search, Posts */}
              <View style={styles.leftColumn}>
                {/* Group Details Hero Card */}
                <View style={styles.groupCard}>
                  {/* Header Banner Image */}
                  <View style={styles.bannerImageContainer}>
                    <Image
                      source={require('../../../assets/images/active_groups_banner.jpg')}
                      style={styles.bannerImage}
                      resizeMode="cover"
                    />
                  </View>

                  {/* Group Info Header Row */}
                  <View style={styles.groupInfoHeader}>
                    {/* Overlapping Badge */}
                    <View style={styles.badgeCircle}>
                      <Text style={styles.badgeCircleIcon}>👥</Text>
                    </View>

                    {/* Joined Status Button */}
                    <TouchableOpacity
                      style={[styles.joinedButton, !isJoined && styles.joinButton]}
                      onPress={() => setIsJoined(!isJoined)}
                      activeOpacity={0.8}
                    >
                      <Text style={[styles.joinedButtonText, !isJoined && styles.joinButtonText]}>
                        {isJoined ? '✓ Joined' : '+ Join Group'}
                      </Text>
                    </TouchableOpacity>
                  </View>

                  {/* Group Title & Details */}
                  <View style={styles.groupBody}>
                    <Text style={styles.groupTitle}>Parents of Newly Diagnosed</Text>
                    <Text style={styles.groupDescription}>
                      A supportive space for parents and guardians navigating recent diagnoses. Share experiences, resources, and find comfort in a community that understands your journey.
                    </Text>

                    {/* Stats Row */}
                    <View style={styles.statsRow}>
                      <View style={styles.statItem}>
                        <Text style={styles.statIcon}>👥</Text>
                        <Text style={styles.statText}>1.2k Members</Text>
                      </View>
                      <View style={styles.statItem}>
                        <Text style={styles.statIcon}>💬</Text>
                        <Text style={styles.statText}>14 posts today</Text>
                      </View>
                    </View>
                  </View>
                </View>

                {/* Post Composer Card */}
                <View style={styles.composerCard}>
                  <View style={styles.composerInputRow}>
                    <View style={styles.composerAvatarCircle}>
                      <Text style={styles.composerAvatarText}>U</Text>
                    </View>
                    <TextInput
                      style={styles.composerTextInput}
                      placeholder="Share an update, ask a question, or introduce yourself..."
                      placeholderTextColor="#94A3B8"
                      multiline={true}
                      value={postText}
                      onChangeText={setPostText}
                    />
                  </View>

                  <View style={styles.composerActionRow}>
                    <View style={styles.composerIconsGroup}>
                      <TouchableOpacity style={styles.composerIconBtn}>
                        <Text style={styles.composerIconText}>🖼️</Text>
                      </TouchableOpacity>
                      <TouchableOpacity style={styles.composerIconBtn}>
                        <Text style={styles.composerIconText}>😊</Text>
                      </TouchableOpacity>
                      <TouchableOpacity style={styles.composerIconBtn}>
                        <Text style={styles.composerIconText}>📎</Text>
                      </TouchableOpacity>
                    </View>

                    <TouchableOpacity
                      style={[styles.postButton, !postText.trim() && styles.postButtonDisabled]}
                      onPress={handleCreatePost}
                      disabled={!postText.trim()}
                      activeOpacity={0.8}
                    >
                      <Text style={styles.postButtonText}>Post</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Search Bar Input */}
                <View style={styles.searchBarWrapper}>
                  <Text style={styles.searchIcon}>🔍</Text>
                  <TextInput
                    style={styles.searchInput}
                    placeholder="Search posts in this group..."
                    placeholderTextColor="#94A3B8"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                  />
                </View>

                {/* Feed Posts */}
                {posts
                  .filter((p) => p.content.toLowerCase().includes(searchQuery.toLowerCase()))
                  .map((post) => (
                    <View key={post.id} style={styles.postCard}>
                      <View style={styles.postHeader}>
                        <View style={styles.authorRow}>
                          <View style={styles.authorAvatarCircle}>
                            <Text style={styles.authorAvatarText}>{post.authorInitials}</Text>
                          </View>
                          <View>
                            <Text style={styles.authorName}>{post.authorName}</Text>
                            <Text style={styles.postTimestamp}>{post.timestamp}</Text>
                          </View>
                        </View>
                        <TouchableOpacity style={styles.moreOptionsBtn}>
                          <Text style={styles.moreOptionsText}>•••</Text>
                        </TouchableOpacity>
                      </View>

                      <Text style={styles.postBodyText}>{post.content}</Text>

                      <View style={styles.postFooter}>
                        <TouchableOpacity style={styles.postActionBtn}>
                          <Text style={styles.postActionIcon}>👍</Text>
                          <Text style={styles.postActionText}>{post.likes} Likes</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.postActionBtn}>
                          <Text style={styles.postActionIcon}>💬</Text>
                          <Text style={styles.postActionText}>{post.comments} Comments</Text>
                        </TouchableOpacity>
                      </View>
                    </View>
                  ))}
              </View>

              {/* Right Column: About Card & Group Rules */}
              <View style={styles.rightColumn}>
                {/* About Card */}
                <View style={styles.sideCard}>
                  <View style={styles.sideCardHeader}>
                    <Text style={styles.sideCardIcon}>ℹ️</Text>
                    <Text style={styles.sideCardTitle}>About</Text>
                  </View>

                  <Text style={styles.aboutDescription}>
                    A safe, private space designed for parents and guardians who are at the beginning of their caregiving journey following a new medical or developmental diagnosis.
                  </Text>

                  <View style={styles.aboutMetaRow}>
                    <Text style={styles.aboutMetaIcon}>🌐</Text>
                    <Text style={styles.aboutMetaText}>Public Group (Visible in Directory)</Text>
                  </View>

                  <View style={styles.aboutMetaRow}>
                    <Text style={styles.aboutMetaIcon}>📅</Text>
                    <Text style={styles.aboutMetaText}>Created March 2023</Text>
                  </View>
                </View>

                {/* Group Rules Card */}
                <View style={styles.sideCard}>
                  <View style={styles.sideCardHeader}>
                    <Text style={styles.sideCardIcon}>📜</Text>
                    <Text style={styles.sideCardTitle}>Group Rules</Text>
                  </View>

                  <View style={styles.ruleItem}>
                    <Text style={styles.ruleTitle}>1. Be Kind and Courteous</Text>
                    <Text style={styles.ruleDesc}>
                      We're all in this together to create a welcoming environment. Let's treat everyone with respect.
                    </Text>
                  </View>

                  <View style={styles.ruleItem}>
                    <Text style={styles.ruleTitle}>2. No Hate Speech or Bullying</Text>
                    <Text style={styles.ruleDesc}>
                      Make sure everyone feels safe. Bullying of any kind isn't allowed, and degrading comments will be removed.
                    </Text>
                  </View>

                  <View style={[styles.ruleItem, { marginBottom: 0 }]}>
                    <Text style={styles.ruleTitle}>3. Respect Privacy</Text>
                    <Text style={styles.ruleDesc}>
                      Being part of this group requires mutual trust. What's shared in the group should stay in the group.
                    </Text>
                  </View>
                </View>
              </View>
            </View>
          </ScrollView>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  appContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
  },

  /* Sidebar Styles */
  sidebar: {
    width: 250,
    backgroundColor: '#FFFFFF',
    borderRightWidth: 1,
    borderRightColor: '#E2E8F0',
    justifyContent: 'space-between',
    position: 'relative',
    overflow: 'hidden',
  },
  sidebarTopContent: {
    paddingVertical: 24,
    paddingHorizontal: 16,
    zIndex: 2,
  },
  brandContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  brandLogoBox: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  brandLogoIcon: {
    fontSize: 20,
    color: '#FFFFFF',
  },
  brandTextWrapper: {
    flex: 1,
  },
  brandTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  verificationBadge: {
    backgroundColor: '#FEF3C7',
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: 10,
    alignSelf: 'flex-start',
    marginTop: 4,
  },
  verificationBadgeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#D97706',
  },
  menuContainer: {
    marginTop: 8,
  },
  navItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 11,
    paddingHorizontal: 14,
    borderRadius: 10,
    marginBottom: 4,
  },
  navItemActive: {
    backgroundColor: '#4F46E5',
  },
  navIcon: {
    fontSize: 16,
    marginRight: 12,
    color: '#64748B',
  },
  navIconActive: {
    color: '#FFFFFF',
  },
  navText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  navTextActive: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  sidebarBottomNav: {
    marginTop: 24,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 16,
  },
  sidebarBgGraphicWrapper: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 180,
    opacity: 0.18,
    pointerEvents: 'none',
  },
  sidebarBgImage: {
    width: '100%',
    height: '100%',
  },

  /* Main Content Area */
  mainContent: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  topHeader: {
    height: 64,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 28,
  },
  topPageTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0F172A',
  },
  topHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  headerIconButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  headerIconText: {
    fontSize: 16,
  },
  notificationDot: {
    position: 'absolute',
    top: 6,
    right: 6,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444',
  },
  userProfileAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 4,
  },
  userAvatarText: {
    fontSize: 18,
  },

  /* Scroll Canvas */
  scrollCanvas: {
    flex: 1,
  },
  scrollCanvasContent: {
    padding: 28,
  },
  pageMainTitle: {
    fontSize: 32,
    fontWeight: '900',
    color: '#0F172A',
    marginBottom: 24,
  },

  /* Two Column Grid */
  gridContainer: {
    flexDirection: 'column',
    gap: 24,
  },
  gridContainerDesktop: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  leftColumn: {
    flex: 1.6,
  },
  rightColumn: {
    flex: 1,
  },

  /* Group Hero Banner Card */
  groupCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 10,
    elevation: 2,
  },
  bannerImageContainer: {
    width: '100%',
    height: 180,
    backgroundColor: '#EEF2FF',
  },
  bannerImage: {
    width: '100%',
    height: '100%',
  },
  groupInfoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    paddingHorizontal: 24,
    marginTop: -30,
    marginBottom: 12,
  },
  badgeCircle: {
    width: 68,
    height: 68,
    borderRadius: 34,
    backgroundColor: '#4F46E5',
    borderWidth: 4,
    borderColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeCircleIcon: {
    fontSize: 30,
    color: '#FFFFFF',
  },
  joinedButton: {
    backgroundColor: '#4F46E5',
    paddingVertical: 9,
    paddingHorizontal: 20,
    borderRadius: 20,
  },
  joinedButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  joinButton: {
    backgroundColor: '#EEF2FF',
    borderWidth: 1,
    borderColor: '#4F46E5',
  },
  joinButtonText: {
    color: '#4F46E5',
  },
  groupBody: {
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
  groupTitle: {
    fontSize: 24,
    fontWeight: '900',
    color: '#0F172A',
    marginBottom: 8,
  },
  groupDescription: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 22,
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 20,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statIcon: {
    fontSize: 15,
    marginRight: 6,
    color: '#64748B',
  },
  statText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
  },

  /* Composer Card */
  composerCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 10,
    elevation: 2,
  },
  composerInputRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  composerAvatarCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  composerAvatarText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#475569',
  },
  composerTextInput: {
    flex: 1,
    fontSize: 15,
    color: '#0F172A',
    minHeight: 48,
    paddingTop: 8,
  },
  composerActionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  composerIconsGroup: {
    flexDirection: 'row',
    gap: 12,
  },
  composerIconBtn: {
    width: 34,
    height: 34,
    borderRadius: 8,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  composerIconText: {
    fontSize: 16,
  },
  postButton: {
    backgroundColor: '#4F46E5',
    paddingVertical: 8,
    paddingHorizontal: 24,
    borderRadius: 20,
  },
  postButtonDisabled: {
    backgroundColor: '#CBD5E1',
  },
  postButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },

  /* Search Input Wrapper */
  searchBarWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
  },
  searchIcon: {
    fontSize: 16,
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    color: '#0F172A',
  },

  /* Post Cards */
  postCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 10,
    elevation: 2,
  },
  postHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  authorRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  authorAvatarCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#B45309',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  authorAvatarText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 15,
  },
  authorName: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  postTimestamp: {
    fontSize: 12,
    color: '#94A3B8',
    marginTop: 2,
  },
  moreOptionsBtn: {
    padding: 4,
  },
  moreOptionsText: {
    fontSize: 16,
    color: '#94A3B8',
  },
  postBodyText: {
    fontSize: 14,
    color: '#334155',
    lineHeight: 22,
    marginBottom: 16,
  },
  postFooter: {
    flexDirection: 'row',
    gap: 20,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  postActionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  postActionIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  postActionText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
  },

  /* Right Side Cards */
  sideCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 24,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 10,
    elevation: 2,
  },
  sideCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sideCardIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  sideCardTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  aboutDescription: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 22,
    marginBottom: 20,
  },
  aboutMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  aboutMetaIcon: {
    fontSize: 15,
    marginRight: 10,
    color: '#64748B',
  },
  aboutMetaText: {
    fontSize: 13,
    color: '#64748B',
    fontWeight: '500',
  },
  ruleItem: {
    marginBottom: 18,
  },
  ruleTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  ruleDesc: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 19,
  },
});
