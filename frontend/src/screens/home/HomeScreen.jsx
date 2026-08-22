import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Dimensions,
  Platform,
  ActivityIndicator,
  Modal,
} from 'react-native';
import { useAuthStore } from '../../store/authStore';
import { useSafety } from '../../hooks/useSafety';
import { useLocation } from '../../hooks/useLocation';
import { dashboardApi } from '../../services/api/dashboardApi';
import { communityApi } from '../../services/api/communityApi';
import Avatar from '../../components/common/Avatar';
import StatusIndicator from '../../components/common/StatusIndicator';
import AppButton from '../../components/common/AppButton';
import ConfirmModal from '../../components/common/ConfirmModal';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const isDesktop = Platform.OS === 'web' ? SCREEN_WIDTH >= 1024 : SCREEN_WIDTH >= 768;

export default function HomeScreen({ navigation }) {
  const { user } = useAuthStore();
  const {
    childName,
    childAge,
    isSafe,
    currentZone,
    batteryLevel,
    gpsStatus,
    bleConnected,
    separationDistance,
    isEmergencyActive,
    triggerEmergency,
    resolveEmergency,
    safetyEvents,
  } = useSafety();

  const { currentLocation, refreshLocation } = useLocation();

  const [communityPosts, setCommunityPosts] = useState([]);
  const [communityStats, setCommunityStats] = useState({
    my_groups: 3,
    new_messages: 2,
    notifications: 4,
    community_online: 128,
  });
  const [loadingCommunity, setLoadingCommunity] = useState(true);
  const [sosModalVisible, setSosModalVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('HOME'); // 'HOME' | 'COMMUNITY' | 'LOCATION' | 'SAFETY' | 'PROFILE'

  useEffect(() => {
    loadCommunitySummary();
  }, []);

  const loadCommunitySummary = async () => {
    setLoadingCommunity(true);
    try {
      const data = await dashboardApi.getDashboardData();
      if (data && Array.isArray(data.feed)) {
        setCommunityPosts(data.feed.slice(0, 3));
      } else {
        const feedData = await communityApi.getFeed(1, 3);
        if (feedData && Array.isArray(feedData.posts)) {
          setCommunityPosts(feedData.posts.slice(0, 3));
        }
      }
      if (data && data.stats) {
        setCommunityStats(data.stats);
      }
    } catch (e) {
      // Fallback discussions for instant rendering
      setCommunityPosts([
        {
          id: 'post-1',
          author_name: 'Dr. Sarah Mitchell',
          category: 'Sensory Support',
          content: 'Effective de-escalation strategies during auditory sensory overload in public spaces. What visual cues work best for your child?',
          like_count: 24,
          comment_count: 15,
          created_at: '25 mins ago',
        },
        {
          id: 'post-2',
          author_name: 'David Nguyen',
          category: 'Daily Routine',
          content: 'Free printable visual schedule templates for morning transitions before school. Shared in the resource library!',
          like_count: 38,
          comment_count: 9,
          created_at: '1 hour ago',
        },
      ]);
    } finally {
      setLoadingCommunity(false);
    }
  };

  const handleConfirmSOS = async () => {
    setSosModalVisible(false);
    await triggerEmergency({
      location: currentLocation,
      initiatedFrom: 'HomeDashboard',
    });
    navigation.navigate('Emergency');
  };

  const navigateToTab = (tabKey) => {
    setActiveTab(tabKey);
    switch (tabKey) {
      case 'COMMUNITY':
        navigation.navigate('CommunityTab');
        break;
      case 'AAC':
        navigation.navigate('AAC');
        break;
      case 'LEARNING':
        navigation.navigate('LearningTab');
        break;
      case 'SENSORY':
        navigation.navigate('SensoryHome');
        break;
      case 'GAMES':
        navigation.navigate('GamesHome');
        break;
      case 'LOCATION':
        navigation.navigate('LiveLocation');
        break;
      case 'SAFETY':
        navigation.navigate('CaregiverDashboard');
        break;
      case 'PROFILE':
        navigation.navigate('ChildProfile');
        break;
      default:
        break;
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* 1. TOP UNIFIED NAVIGATION BAR */}
      <View style={styles.topBar}>
        <View style={styles.brandRow}>
          <View style={styles.logoSquare}>
            <Text style={styles.logoText}>N</Text>
          </View>
          <View>
            <Text style={styles.brandTitle}>NIVARA</Text>
            <Text style={styles.brandSubtitle}>Unified Autism & Caregiver Support Platform</Text>
          </View>
        </View>

        {/* Desktop / Tablet Nav Links */}
        {isDesktop && (
          <View style={styles.desktopNavTabs}>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'HOME' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('HOME')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'HOME' && styles.desktopTabLabelActive]}>🏠 Home</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'COMMUNITY' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('COMMUNITY')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'COMMUNITY' && styles.desktopTabLabelActive]}>👥 Community</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'AAC' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('AAC')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'AAC' && styles.desktopTabLabelActive]}>🖼️ AAC Board</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'LEARNING' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('LEARNING')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'LEARNING' && styles.desktopTabLabelActive]}>🎓 Learning</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'SENSORY' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('SENSORY')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'SENSORY' && styles.desktopTabLabelActive]}>🎧 Sensory</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'GAMES' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('GAMES')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'GAMES' && styles.desktopTabLabelActive]}>🎮 Games</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'LOCATION' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('LOCATION')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'LOCATION' && styles.desktopTabLabelActive]}>📍 Live GPS</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.desktopTabItem, activeTab === 'SAFETY' && styles.desktopTabItemActive]}
              onPress={() => navigateToTab('SAFETY')}
            >
              <Text style={[styles.desktopTabLabel, activeTab === 'SAFETY' && styles.desktopTabLabelActive]}>🛡️ Safety</Text>
            </TouchableOpacity>
          </View>
        )}

        <View style={styles.topRightActions}>
          <TouchableOpacity
            style={styles.sosTopBtn}
            onPress={() => setSosModalVisible(true)}
            activeOpacity={0.85}
          >
            <Text style={styles.sosTopText}>🚨 SOS</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.userAvatarBtn}
            onPress={() => navigation.navigate('ChildProfile')}
            activeOpacity={0.85}
          >
            <Avatar name={user?.name || 'Jordan Patel'} emoji="👩‍⚕️" size={38} />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Active Emergency Alert Banner if Emergency is Triggered */}
        {isEmergencyActive && (
          <TouchableOpacity
            style={styles.emergencyAlertBanner}
            onPress={() => navigation.navigate('Emergency')}
            activeOpacity={0.85}
          >
            <Text style={styles.emergencyIcon}>🚨</Text>
            <View style={styles.emergencyTextCol}>
              <Text style={styles.emergencyTitle}>EMERGENCY BROADCAST ACTIVE</Text>
              <Text style={styles.emergencySub}>
                Coordinates and alerts broadcasted to caregivers • Tap for Emergency Response
              </Text>
            </View>
            <Text style={styles.emergencyArrow}>›</Text>
          </TouchableOpacity>
        )}

        {/* Caregiver Welcome Greeting */}
        <View style={styles.greetingCard}>
          <View style={styles.greetingTextCol}>
            <Text style={styles.greetingTitle}>
              Good Morning, {user?.name || 'Jordan'} 👋
            </Text>
            <Text style={styles.greetingSubtitle}>
              Here is your unified dashboard for {childName}'s safety and community updates.
            </Text>
          </View>
          <View style={styles.childSafePill}>
            <StatusIndicator
              status={isSafe ? 'safe' : 'danger'}
              label={isSafe ? 'Child Safe' : 'Safety Attention'}
              size={9}
            />
          </View>
        </View>

        {/* 2. DUAL PILLARS GRID: (A) CHILD SAFETY + (B) CAREGIVER COMMUNITY */}
        <View style={[styles.pillarsGrid, isDesktop && styles.pillarsGridDesktop]}>
          {/* ======================================================== */}
          {/* PILLAR 1: CHILD SAFETY & LIVE TRACKING                   */}
          {/* ======================================================== */}
          <View style={[styles.pillarCard, styles.safetyPillarCard]}>
            <View style={styles.pillarHeader}>
              <View style={styles.pillarIconCircleBlue}>
                <Text style={styles.pillarIcon}>🛡️</Text>
              </View>
              <View style={styles.pillarTitleCol}>
                <Text style={styles.pillarTitle}>Child Safety & Live GPS</Text>
                <Text style={styles.pillarSubtitle}>
                  {childName} • Age {childAge}
                </Text>
              </View>
              <View style={styles.statusBadgeGreen}>
                <Text style={styles.statusBadgeTextGreen}>🟢 {isSafe ? 'Safe' : 'Alert'}</Text>
              </View>
            </View>

            {/* Safety Live Telemetry Matrix */}
            <View style={styles.telemetryMatrix}>
              <View style={styles.telemetryItem}>
                <Text style={styles.telemetryLabel}>CURRENT ZONE</Text>
                <Text style={styles.telemetryVal}>{currentZone || 'Home Sanctuary'}</Text>
                <Text style={styles.telemetrySub}>Geofence Active</Text>
              </View>
              <View style={styles.telemetryItem}>
                <Text style={styles.telemetryLabel}>GPS STATUS</Text>
                <Text style={styles.telemetryVal}>✓ {gpsStatus || 'Connected'}</Text>
                <Text style={styles.telemetrySub}>±3.8m Accuracy</Text>
              </View>
              <View style={styles.telemetryItem}>
                <Text style={styles.telemetryLabel}>SMARTBAND</Text>
                <Text style={styles.telemetryVal}>
                  {bleConnected ? `Tethered (${separationDistance}m)` : 'Disconnected'}
                </Text>
                <Text style={styles.telemetrySub}>Battery: {batteryLevel}%</Text>
              </View>
            </View>

            {/* Location Address Strip */}
            <View style={styles.locationStrip}>
              <Text style={styles.pinIcon}>📍</Text>
              <Text style={styles.locationText} numberOfLines={1}>
                {currentLocation?.address || '123 Maple Street, Model Town, Ludhiana'}
              </Text>
            </View>

            {/* Safety Action Buttons */}
            <View style={styles.pillarActionButtons}>
              <TouchableOpacity
                style={styles.primaryPillarBtn}
                onPress={() => navigation.navigate('LiveLocation')}
                activeOpacity={0.85}
              >
                <Text style={styles.primaryPillarBtnText}>🗺️ View Live Location</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.secondaryPillarBtn}
                onPress={() => navigation.navigate('CaregiverDashboard')}
                activeOpacity={0.85}
              >
                <Text style={styles.secondaryPillarBtnText}>Safety Center ›</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* ======================================================== */}
          {/* PILLAR 2: CAREGIVER COMMUNITY PORTAL                     */}
          {/* ======================================================== */}
          <View style={[styles.pillarCard, styles.communityPillarCard]}>
            <View style={styles.pillarHeader}>
              <View style={styles.pillarIconCirclePurple}>
                <Text style={styles.pillarIcon}>👥</Text>
              </View>
              <View style={styles.pillarTitleCol}>
                <Text style={styles.pillarTitle}>Caregiver Community</Text>
                <Text style={styles.pillarSubtitle}>
                  {communityStats.community_online} Caregivers Active Online
                </Text>
              </View>
              <TouchableOpacity
                style={styles.openCommunityLink}
                onPress={() => navigation.navigate('CommunityTab')}
              >
                <Text style={styles.openCommunityLinkText}>Open Portal ›</Text>
              </TouchableOpacity>
            </View>

            {/* Community Feed / Discussion Highlights */}
            {loadingCommunity ? (
              <View style={styles.loadingCommunityBox}>
                <ActivityIndicator size="small" color="#2563EB" />
                <Text style={styles.loadingText}>Loading caregiver discussions...</Text>
              </View>
            ) : (
              <View style={styles.discussionsList}>
                {communityPosts.slice(0, 2).map((post) => (
                  <TouchableOpacity
                    key={post.id}
                    style={styles.discussionCard}
                    onPress={() => navigation.navigate('CommunityTab')}
                    activeOpacity={0.85}
                  >
                    <View style={styles.discussionHeader}>
                      <Text style={styles.discussionAuthor}>👤 {post.author_name || 'Caregiver'}</Text>
                      {post.category && (
                        <View style={styles.categoryPill}>
                          <Text style={styles.categoryText}>{post.category}</Text>
                        </View>
                      )}
                    </View>
                    <Text style={styles.discussionSnippet} numberOfLines={2}>
                      {post.content}
                    </Text>
                    <View style={styles.discussionFooter}>
                      <Text style={styles.discussionMetric}>💬 {post.comment_count || 0} comments</Text>
                      <Text style={styles.discussionMetric}>❤️ {post.like_count || 0} helpful</Text>
                    </View>
                  </TouchableOpacity>
                ))}
              </View>
            )}

            {/* Community Action Buttons */}
            <View style={styles.pillarActionButtons}>
              <TouchableOpacity
                style={[styles.primaryPillarBtn, styles.primaryCommunityBtn]}
                onPress={() => navigation.navigate('CommunityTab')}
                activeOpacity={0.85}
              >
                <Text style={styles.primaryPillarBtnText}>💬 Enter Community Feed</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.secondaryPillarBtn}
                onPress={() => navigation.navigate('SupportCenter')}
                activeOpacity={0.85}
              >
                <Text style={styles.secondaryPillarBtnText}>Caregiver Guides ›</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* 3. QUICK ACTIONS SHORTCUTS */}
        <Text style={styles.sectionHeaderTitle}>QUICK ACTIONS</Text>
        <View style={styles.quickGrid}>
          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => navigation.navigate('AAC')}
            activeOpacity={0.85}
          >
            <View style={[styles.quickIconCircle, { backgroundColor: '#EFF6FF' }]}>
              <Text style={styles.quickActionIcon}>🖼️</Text>
            </View>
            <Text style={styles.quickActionLabel}>AAC Board</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => navigation.navigate('LearningTab')}
            activeOpacity={0.85}
          >
            <View style={[styles.quickIconCircle, { backgroundColor: '#ECFDF5' }]}>
              <Text style={styles.quickActionIcon}>🎓</Text>
            </View>
            <Text style={styles.quickActionLabel}>Routines</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => navigation.navigate('LiveLocation')}
            activeOpacity={0.85}
          >
            <View style={[styles.quickIconCircle, { backgroundColor: '#EFF6FF' }]}>
              <Text style={styles.quickActionIcon}>📍</Text>
            </View>
            <Text style={styles.quickActionLabel}>Live GPS</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => navigation.navigate('CommunityTab')}
            activeOpacity={0.85}
          >
            <View style={[styles.quickIconCircle, { backgroundColor: '#FEF3C7' }]}>
              <Text style={styles.quickActionIcon}>💬</Text>
            </View>
            <Text style={styles.quickActionLabel}>Community</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => navigation.navigate('Tutor')}
            activeOpacity={0.85}
          >
            <View style={[styles.quickIconCircle, { backgroundColor: '#F5F3FF' }]}>
              <Text style={styles.quickActionIcon}>🤖</Text>
            </View>
            <Text style={styles.quickActionLabel}>AI Tutor</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => navigation.navigate('SensoryHome')}
            activeOpacity={0.85}
          >
            <View style={[styles.quickIconCircle, { backgroundColor: '#F0FDF4' }]}>
              <Text style={styles.quickActionIcon}>🎧</Text>
            </View>
            <Text style={styles.quickActionLabel}>Sensory</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => navigation.navigate('EmergencyContacts')}
            activeOpacity={0.85}
          >
            <View style={[styles.quickIconCircle, { backgroundColor: '#FEE2E2' }]}>
              <Text style={styles.quickActionIcon}>📞</Text>
            </View>
            <Text style={styles.quickActionLabel}>Contacts</Text>
          </TouchableOpacity>
        </View>

        {/* 4. UNIFIED RECENT ACTIVITY (SAFETY + COMMUNITY MERGED) */}
        <Text style={styles.sectionHeaderTitle}>RECENT ACTIVITY</Text>
        <View style={styles.activityFeedCard}>
          {safetyEvents.slice(0, 4).map((item, idx) => (
            <View key={item.id || idx} style={styles.activityRow}>
              <View style={[styles.activityDot, item.isSafe ? styles.activityDotGreen : styles.activityDotBlue]} />
              <View style={styles.activityBody}>
                <View style={styles.activityHeader}>
                  <Text style={styles.activityTitle}>{item.title}</Text>
                  <Text style={styles.activityTime}>{item.time}</Text>
                </View>
                <Text style={styles.activityDesc}>{item.desc}</Text>
              </View>
            </View>
          ))}
          <View style={styles.activityRow}>
            <View style={[styles.activityDot, styles.activityDotPurple]} />
            <View style={styles.activityBody}>
              <View style={styles.activityHeader}>
                <Text style={styles.activityTitle}>New Reply in Sensory Support Group</Text>
                <Text style={styles.activityTime}>09:40 AM</Text>
              </View>
              <Text style={styles.activityDesc}>Sarah Mitchell replied to discussion on calming techniques.</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      {/* 5. BOTTOM MOBILE TAB NAVIGATION BAR */}
      {!isDesktop && (
        <View style={styles.bottomTabBar}>
          <TouchableOpacity
            style={styles.tabItem}
            onPress={() => navigateToTab('HOME')}
            activeOpacity={0.85}
          >
            <Text style={[styles.tabIcon, activeTab === 'HOME' && styles.tabIconActive]}>🏠</Text>
            <Text style={[styles.tabLabel, activeTab === 'HOME' && styles.tabLabelActive]}>Home</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.tabItem}
            onPress={() => navigateToTab('COMMUNITY')}
            activeOpacity={0.85}
          >
            <Text style={[styles.tabIcon, activeTab === 'COMMUNITY' && styles.tabIconActive]}>👥</Text>
            <Text style={[styles.tabLabel, activeTab === 'COMMUNITY' && styles.tabLabelActive]}>Community</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.tabItem}
            onPress={() => navigateToTab('LOCATION')}
            activeOpacity={0.85}
          >
            <Text style={[styles.tabIcon, activeTab === 'LOCATION' && styles.tabIconActive]}>📍</Text>
            <Text style={[styles.tabLabel, activeTab === 'LOCATION' && styles.tabLabelActive]}>Live Map</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.tabItem}
            onPress={() => navigateToTab('SAFETY')}
            activeOpacity={0.85}
          >
            <Text style={[styles.tabIcon, activeTab === 'SAFETY' && styles.tabIconActive]}>🛡️</Text>
            <Text style={[styles.tabLabel, activeTab === 'SAFETY' && styles.tabLabelActive]}>Safety</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.tabItem}
            onPress={() => navigateToTab('PROFILE')}
            activeOpacity={0.85}
          >
            <Text style={[styles.tabIcon, activeTab === 'PROFILE' && styles.tabIconActive]}>👤</Text>
            <Text style={[styles.tabLabel, activeTab === 'PROFILE' && styles.tabLabelActive]}>Profile</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* SOS Confirmation Modal */}
      <ConfirmModal
        visible={sosModalVisible}
        onClose={() => setSosModalVisible(false)}
        onConfirm={handleConfirmSOS}
        title="Broadcast Emergency SOS?"
        message={`Are you sure you want to trigger an emergency broadcast for ${childName}? This will immediately notify caregivers and transmit live GPS coordinates.`}
        confirmText="Yes, Send SOS"
        cancelText="Cancel"
        confirmVariant="danger"
        icon="🚨"
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 6,
    elevation: 3,
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  logoSquare: {
    width: 38,
    height: 38,
    borderRadius: 10,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoText: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '900',
  },
  brandTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#0F172A',
    letterSpacing: 1.5,
  },
  brandSubtitle: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  desktopNavTabs: {
    flexDirection: 'row',
    gap: 8,
    backgroundColor: '#F1F5F9',
    padding: 4,
    borderRadius: 12,
  },
  desktopTabItem: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  desktopTabItemActive: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
  },
  desktopTabLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#64748B',
  },
  desktopTabLabelActive: {
    color: '#2563EB',
    fontWeight: '800',
  },
  topRightActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  sosTopBtn: {
    backgroundColor: '#DC2626',
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 999,
  },
  sosTopText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '900',
  },
  userAvatarBtn: {
    borderRadius: 19,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
    paddingBottom: 40,
    maxWidth: 1200,
    alignSelf: 'center',
    width: '100%',
  },
  emergencyAlertBanner: {
    backgroundColor: '#DC2626',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  emergencyIcon: {
    fontSize: 22,
    marginRight: 12,
  },
  emergencyTextCol: {
    flex: 1,
  },
  emergencyTitle: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  emergencySub: {
    color: '#FECACA',
    fontSize: 11,
    marginTop: 2,
  },
  emergencyArrow: {
    color: '#FFFFFF',
    fontSize: 22,
    fontWeight: '800',
  },
  greetingCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 18,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 6,
  },
  greetingTextCol: {
    flex: 1,
  },
  greetingTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#0F172A',
  },
  greetingSubtitle: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  childSafePill: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#A7F3D0',
    marginLeft: 10,
  },
  pillarsGrid: {
    flexDirection: 'column',
    gap: 16,
    marginBottom: 24,
  },
  pillarsGridDesktop: {
    flexDirection: 'row',
  },
  pillarCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
  },
  safetyPillarCard: {
    borderTopWidth: 4,
    borderTopColor: '#2563EB',
  },
  communityPillarCard: {
    borderTopWidth: 4,
    borderTopColor: '#8B5CF6',
  },
  pillarHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  pillarIconCircleBlue: {
    width: 42,
    height: 42,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  pillarIconCirclePurple: {
    width: 42,
    height: 42,
    borderRadius: 12,
    backgroundColor: '#F5F3FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  pillarIcon: {
    fontSize: 20,
  },
  pillarTitleCol: {
    flex: 1,
  },
  pillarTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  pillarSubtitle: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  statusBadgeGreen: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  statusBadgeTextGreen: {
    fontSize: 11,
    fontWeight: '800',
    color: '#059669',
  },
  openCommunityLink: {
    paddingVertical: 4,
  },
  openCommunityLinkText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#8B5CF6',
  },
  telemetryMatrix: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 14,
  },
  telemetryItem: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  telemetryLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#64748B',
    marginBottom: 2,
  },
  telemetryVal: {
    fontSize: 12,
    fontWeight: '800',
    color: '#0F172A',
  },
  telemetrySub: {
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 1,
  },
  locationStrip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    padding: 10,
    borderRadius: 10,
    marginBottom: 16,
    gap: 6,
  },
  pinIcon: {
    fontSize: 14,
  },
  locationText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#1E40AF',
    flex: 1,
  },
  pillarActionButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  primaryPillarBtn: {
    flex: 1.2,
    backgroundColor: '#2563EB',
    paddingVertical: 11,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryCommunityBtn: {
    backgroundColor: '#8B5CF6',
  },
  primaryPillarBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  secondaryPillarBtn: {
    flex: 0.8,
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    paddingVertical: 11,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryPillarBtnText: {
    color: '#334155',
    fontSize: 12,
    fontWeight: '700',
  },
  loadingCommunityBox: {
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 8,
  },
  discussionsList: {
    gap: 8,
    marginBottom: 16,
  },
  discussionCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  discussionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  discussionAuthor: {
    fontSize: 11,
    fontWeight: '700',
    color: '#0F172A',
  },
  categoryPill: {
    backgroundColor: '#EDE9FE',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  categoryText: {
    fontSize: 9,
    fontWeight: '800',
    color: '#7C3AED',
  },
  discussionSnippet: {
    fontSize: 12,
    color: '#475569',
    lineHeight: 16,
    marginBottom: 6,
  },
  discussionFooter: {
    flexDirection: 'row',
    gap: 12,
  },
  discussionMetric: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
  },
  sectionHeaderTitle: {
    fontSize: 12,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 12,
  },
  quickGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  quickItem: {
    flex: 1,
    minWidth: 90,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
  },
  quickIconCircle: {
    width: 44,
    height: 44,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickActionIcon: {
    fontSize: 20,
  },
  quickActionLabel: {
    fontSize: 11,
    fontWeight: '800',
    color: '#0F172A',
    textAlign: 'center',
  },
  activityFeedCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    gap: 14,
  },
  activityRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 5,
  },
  activityDotGreen: {
    backgroundColor: '#059669',
  },
  activityDotBlue: {
    backgroundColor: '#2563EB',
  },
  activityDotPurple: {
    backgroundColor: '#8B5CF6',
  },
  activityBody: {
    flex: 1,
  },
  activityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  activityTitle: {
    fontSize: 12,
    fontWeight: '800',
    color: '#0F172A',
  },
  activityTime: {
    fontSize: 10,
    color: '#94A3B8',
    fontWeight: '600',
  },
  activityDesc: {
    fontSize: 11,
    color: '#64748B',
  },
  bottomTabBar: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingVertical: 8,
    paddingBottom: Platform.OS === 'ios' ? 24 : 8,
    justifyContent: 'space-around',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 8,
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 2,
  },
  tabIcon: {
    fontSize: 20,
    opacity: 0.6,
  },
  tabIconActive: {
    opacity: 1,
    transform: [{ scale: 1.15 }],
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
    marginTop: 2,
  },
  tabLabelActive: {
    color: '#2563EB',
    fontWeight: '900',
  },
});
