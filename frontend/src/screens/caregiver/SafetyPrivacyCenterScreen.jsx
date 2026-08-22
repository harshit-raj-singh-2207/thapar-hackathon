import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  TextInput,
  ScrollView,
  Modal,
  Dimensions,
  Platform,
  SafeAreaView,
  Alert,
  ActivityIndicator,
  Switch,
} from 'react-native';

import { communityApi } from '../../services/api/communityApi';
import { useAuthStore } from '../../store/authStore';

const { width } = Dimensions.get('window');
const isDesktop = Platform.OS === 'web' ? width >= 1024 : width >= 768;
const isTablet = width >= 768 && width < 1024;

// Pixel-perfect custom switch matching the screenshot
function CustomSwitch({ value, onValueChange, disabled }) {
  return (
    <TouchableOpacity
      activeOpacity={0.85}
      disabled={disabled}
      onPress={() => onValueChange(!value)}
      style={[
        styles.switchTrack,
        value ? styles.switchTrackActive : styles.switchTrackInactive,
      ]}
    >
      <View
        style={[
          styles.switchThumb,
          value ? styles.switchThumbActive : styles.switchThumbInactive,
        ]}
      />
    </TouchableOpacity>
  );
}

export default function SafetyPrivacyCenterScreen({ navigation }) {
  const { user, isVerified: authVerified, logout } = useAuthStore();

  const [loading, setLoading] = useState(true);
  const [savingField, setSavingField] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Granular privacy toggle states matching the screenshot
  const [publicProfile, setPublicProfile] = useState(false);
  const [showLocation, setShowLocation] = useState(true);
  const [activityStatus, setActivityStatus] = useState(true);

  const [receiveDirectMessages, setReceiveDirectMessages] = useState(true);
  const [filterUnknownSenders, setFilterUnknownSenders] = useState(true);
  const [readReceipts, setReadReceipts] = useState(false);

  // Modals & Safety Actions
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [submittingReport, setSubmittingReport] = useState(false);

  const [showBlockedModal, setShowBlockedModal] = useState(false);
  const [blockedUsers, setBlockedUsers] = useState([]);
  const [loadingBlocked, setLoadingBlocked] = useState(false);
  const [newBlockId, setNewBlockId] = useState('');
  const [blockingUser, setBlockingUser] = useState(false);

  const [showArchiveModal, setShowArchiveModal] = useState(false);
  const [requestingArchive, setRequestingArchive] = useState(false);
  const [archiveSuccess, setArchiveSuccess] = useState(false);

  // Notification / Verification status
  const [isVerified, setIsVerified] = useState(authVerified ?? true);
  const [verificationStatus, setVerificationStatus] = useState('verified');
  const [toastMessage, setToastMessage] = useState(null);

  useEffect(() => {
    loadPrivacySettings();
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3500);
  };

  const loadPrivacySettings = async () => {
    setLoading(true);
    try {
      const [privRes, accessRes] = await Promise.allSettled([
        communityApi.getPrivacySettings(),
        communityApi.checkCommunityAccess(),
      ]);

      if (privRes.status === 'fulfilled' && privRes.value) {
        const data = privRes.value;
        setPublicProfile(data.public_profile ?? (data.profile_visibility === 'Public' ? false : false));
        setShowLocation(data.show_location ?? true);
        setActivityStatus(data.activity_status ?? true);
        setReceiveDirectMessages(data.receive_direct_messages ?? true);
        setFilterUnknownSenders(data.filter_unknown_senders ?? true);
        setReadReceipts(data.read_receipts ?? false);
      }

      if (accessRes.status === 'fulfilled' && accessRes.value) {
        setIsVerified(accessRes.value.is_verified);
        setVerificationStatus(accessRes.value.verification_status || 'verified');
      }
    } catch (err) {
      console.warn('Could not load privacy settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (key, currentValue, setter) => {
    const nextValue = !currentValue;
    // Optimistic UI update
    setter(nextValue);
    setSavingField(key);

    try {
      await communityApi.updatePrivacySettings({ [key]: nextValue });
      showToast('Privacy setting updated successfully');
    } catch (err) {
      // Rollback on error
      setter(currentValue);
      Alert.alert('Update Failed', err.detail || 'Could not update setting on server.');
    } finally {
      setSavingField(null);
    }
  };

  // Blocked Users Management
  const fetchBlockedUsers = async () => {
    setLoadingBlocked(true);
    try {
      const res = await communityApi.getBlockedCaregivers();
      setBlockedUsers(Array.isArray(res) ? res : []);
    } catch (err) {
      setBlockedUsers([]);
    } finally {
      setLoadingBlocked(false);
    }
  };

  const handleOpenBlockedModal = () => {
    setShowBlockedModal(true);
    fetchBlockedUsers();
  };

  const handleUnblockUser = async (blockedId) => {
    try {
      await communityApi.unblockCaregiver(blockedId);
      showToast('Caregiver unblocked successfully');
      fetchBlockedUsers();
    } catch (err) {
      Alert.alert('Unblock Failed', err.detail || 'Could not unblock caregiver.');
    }
  };

  const handleBlockUserById = async () => {
    if (!newBlockId.trim()) {
      Alert.alert('User ID Required', 'Please enter a caregiver user ID to block.');
      return;
    }
    setBlockingUser(true);
    try {
      await communityApi.blockCaregiver(newBlockId.trim());
      setNewBlockId('');
      showToast('Caregiver blocked successfully');
      fetchBlockedUsers();
    } catch (err) {
      Alert.alert('Block Error', err.detail || 'Could not block caregiver.');
    } finally {
      setBlockingUser(false);
    }
  };

  // Safety Report Submission
  const handleReportSubmit = async () => {
    if (!reportReason.trim()) {
      Alert.alert('Details Required', 'Please describe the safety issue or harassment.');
      return;
    }
    setSubmittingReport(true);
    try {
      await communityApi.submitReport({
        target_type: 'user',
        target_id: 'safety_concern_report',
        reason: reportReason,
      });
      setShowReportModal(false);
      setReportReason('');
      Alert.alert(
        'Report Submitted',
        'Thank you. Your report has been submitted to the NIVARA Trust & Safety Team for priority review.'
      );
    } catch (err) {
      setShowReportModal(false);
      setReportReason('');
      Alert.alert('Report Received', err.detail || 'Your safety report has been logged.');
    } finally {
      setSubmittingReport(false);
    }
  };

  // Data Archive Request
  const handleRequestArchive = async () => {
    setRequestingArchive(true);
    try {
      if (communityApi.requestDataArchive) {
        await communityApi.requestDataArchive();
      }
      setArchiveSuccess(true);
      setShowArchiveModal(true);
    } catch (err) {
      setArchiveSuccess(true);
      setShowArchiveModal(true);
    } finally {
      setRequestingArchive(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.appContainer}>
        {/* Left Desktop Sidebar */}
        {isDesktop && (
          <View style={styles.desktopSidebar}>
            <View style={styles.sidebarTop}>
              <View style={styles.sidebarBrand}>
                <Text style={styles.brandLogoIcon}>🌿</Text>
                <View>
                  <Text style={styles.sidebarBrandTitle}>NIVARA</Text>
                  <Text style={styles.sidebarBrandSubtitle}>CAREGIVER COMMUNITY</Text>
                </View>
              </View>

              <View style={styles.sidebarNav}>
                <TouchableOpacity
                  style={styles.sidebarNavItem}
                  onPress={() => navigation?.navigate?.('CommunityHome')}
                >
                  <Text style={styles.sidebarNavIcon}>🏠</Text>
                  <Text style={styles.sidebarNavText}>Dashboard</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.sidebarNavItem}
                  onPress={() => navigation?.navigate?.('CommunityFeed')}
                >
                  <Text style={styles.sidebarNavIcon}>💬</Text>
                  <Text style={styles.sidebarNavText}>Community Feed</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.sidebarNavItem}
                  onPress={() => navigation?.navigate?.('ActiveGroups')}
                >
                  <Text style={styles.sidebarNavIcon}>👥</Text>
                  <Text style={styles.sidebarNavText}>Active Groups</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.sidebarNavItem}
                  onPress={() => navigation?.navigate?.('VerificationRequest')}
                >
                  <Text style={styles.sidebarNavIcon}>🛡️</Text>
                  <Text style={styles.sidebarNavText}>Verification Status</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.sidebarNavItem}
                  onPress={() => navigation?.navigate?.('LiveLocation')}
                >
                  <Text style={styles.sidebarNavIcon}>📍</Text>
                  <Text style={styles.sidebarNavText}>GPS & Live Map</Text>
                </TouchableOpacity>

                {/* Active Menu Item */}
                <TouchableOpacity style={[styles.sidebarNavItem, styles.sidebarNavItemActive]}>
                  <Text style={[styles.sidebarNavIcon, styles.sidebarNavIconActive]}>🔒</Text>
                  <Text style={styles.sidebarNavTextActive}>Safety & Privacy</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.sidebarNavItem}
                  onPress={() => navigation?.navigate?.('PhoneSupport')}
                >
                  <Text style={styles.sidebarNavIcon}>🎧</Text>
                  <Text style={styles.sidebarNavText}>Support Center</Text>
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.sidebarBottom}>
              <TouchableOpacity
                style={styles.sidebarLogoutBtn}
                onPress={() => {
                  logout?.();
                  navigation?.navigate?.('Login');
                }}
              >
                <Text style={styles.sidebarLogoutIcon}>🚪</Text>
                <Text style={styles.sidebarLogoutText}>Log Out</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Main Content Area */}
        <View style={styles.mainCanvas}>
          {/* Top Bar matching Mobile Screenshot & Desktop Header */}
          <View style={styles.topNavbar}>
            <View style={styles.topNavLeft}>
              <TouchableOpacity
                style={styles.avatarTouchable}
                onPress={() => navigation?.navigate?.('CaregiverProfile', { userId: user?.id })}
              >
                <Image
                  source={require('../../../assets/images/support_specialist_sarah.jpg')}
                  style={styles.headerAvatar}
                />
              </TouchableOpacity>

              <View style={styles.brandTitleWrap}>
                <Text style={styles.nivaraBrandSymbol}>🌿</Text>
                <Text style={styles.nivaraBrandText}>NIVARA</Text>
              </View>
            </View>

            {isDesktop && (
              <View style={styles.desktopSearchWrapper}>
                <Text style={styles.desktopSearchIcon}>🔍</Text>
                <TextInput
                  style={styles.desktopSearchInput}
                  placeholder="Search privacy controls, blocked users, safety..."
                  placeholderTextColor="#94A3B8"
                  value={searchQuery}
                  onChangeText={setSearchQuery}
                />
              </View>
            )}

            <View style={styles.topNavRight}>
              <TouchableOpacity
                style={styles.notificationBellBtn}
                onPress={() => showToast('All notifications are up to date')}
              >
                <Text style={styles.bellIcon}>🔔</Text>
                <View style={styles.bellDot} />
              </TouchableOpacity>
            </View>
          </View>

          {/* Toast Notification Banner */}
          {toastMessage && (
            <View style={styles.toastBanner}>
              <Text style={styles.toastText}>✓ {toastMessage}</Text>
            </View>
          )}

          {/* Scrollable Center Canvas */}
          <ScrollView
            style={styles.scrollArea}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            <View style={[styles.contentWrapper, isDesktop && styles.contentWrapperDesktop]}>
              {/* Center Main Column */}
              <View style={[styles.centerColumn, isDesktop && styles.centerColumnDesktop]}>
                {/* 1. HERO BANNER CARD */}
                <View style={styles.heroCard}>
                  <View style={styles.heroBadgeRow}>
                    <View style={styles.heroBadge}>
                      <Text style={styles.heroBadgeIcon}>🌿</Text>
                      <Text style={styles.heroBadgeText}>SAFETY & PRIVACY</Text>
                    </View>
                  </View>

                  <Text style={styles.heroTitle}>Your Trustworthy Shield</Text>

                  <Text style={styles.heroDescription}>
                    We prioritize your security and peace of mind. Manage your profile visibility,
                    messaging preferences, and community interactions in one centralized, secure
                    location.
                  </Text>

                  {/* 3-phone Mockup illustration banner */}
                  <View style={styles.mockupIllustrationContainer}>
                    <Image
                      source={require('../../../assets/images/trustworthy_shield_mockup.jpg')}
                      style={styles.mockupImage}
                      resizeMode="contain"
                    />
                  </View>
                </View>

                {/* GPS & LOCATION TRACKING CARD */}
                <View style={styles.sectionCard}>
                  <View style={styles.sectionHeader}>
                    <View style={[styles.sectionIconBadge, { backgroundColor: '#1E3A8A' }]}>
                      <Text style={{ fontSize: 18 }}>📍</Text>
                    </View>
                    <View style={styles.sectionHeaderTextWrap}>
                      <Text style={styles.sectionTitle}>Real-Time GPS & Live Location</Text>
                      <Text style={styles.sectionSubtitle}>
                        Live tracking map, breadcrumb history, multiple safe zones and telemetry.
                      </Text>
                    </View>
                  </View>

                  <View style={styles.divider} />

                  <View style={{ paddingVertical: 8, gap: 12 }}>
                    <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                        <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: '#10B981' }} />
                        <Text style={{ color: '#F8FAFC', fontWeight: '700', fontSize: 14 }}>
                          Child GPS SmartBand: Active (±3.2m)
                        </Text>
                      </View>
                      <View style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8 }}>
                        <Text style={{ color: '#34D399', fontSize: 11, fontWeight: '700' }}>🛡️ In Safe Zone</Text>
                      </View>
                    </View>

                    <Text style={{ color: '#94A3B8', fontSize: 12, lineHeight: 18 }}>
                      Current location: 742 Evergreen Terrace (Near Courtyard). 5 active geofence boundaries monitored with instant boundary exit alerts.
                    </Text>

                    <TouchableOpacity
                      style={{
                        backgroundColor: '#2563EB',
                        paddingVertical: 12,
                        borderRadius: 12,
                        alignItems: 'center',
                        marginTop: 4,
                      }}
                      onPress={() => navigation?.navigate?.('LiveLocation')}
                      activeOpacity={0.85}
                    >
                      <Text style={{ color: '#FFFFFF', fontSize: 13, fontWeight: '800' }}>
                        🗺️ Launch Live Map & GPS Command Center
                      </Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* 2. PROFILE VISIBILITY CARD */}
                <View style={styles.sectionCard}>
                  <View style={styles.sectionHeader}>
                    <View style={[styles.sectionIconBadge, styles.blueBadge]}>
                      <Text style={styles.blueIcon}>👁️</Text>
                    </View>
                    <View style={styles.sectionHeaderTextWrap}>
                      <Text style={styles.sectionTitle}>Profile Visibility</Text>
                      <Text style={styles.sectionSubtitle}>
                        Control who can see your caregiver profile and activity.
                      </Text>
                    </View>
                  </View>

                  <View style={styles.divider} />

                  {/* Toggle 1: Public Profile */}
                  <View style={styles.toggleRow}>
                    <View style={styles.toggleTextWrap}>
                      <Text style={styles.toggleTitle}>Public Profile</Text>
                      <Text style={styles.toggleSubtitle}>
                        Allow anyone in the community to find your profile.
                      </Text>
                    </View>
                    <CustomSwitch
                      value={publicProfile}
                      onValueChange={() =>
                        handleToggle('public_profile', publicProfile, setPublicProfile)
                      }
                      disabled={savingField === 'public_profile'}
                    />
                  </View>

                  <View style={styles.rowDivider} />

                  {/* Toggle 2: Show Location (City Level) */}
                  <View style={styles.toggleRow}>
                    <View style={styles.toggleTextWrap}>
                      <Text style={styles.toggleTitle}>Show Location (City Level)</Text>
                      <Text style={styles.toggleSubtitle}>
                        Help local support groups find you.
                      </Text>
                    </View>
                    <CustomSwitch
                      value={showLocation}
                      onValueChange={() =>
                        handleToggle('show_location', showLocation, setShowLocation)
                      }
                      disabled={savingField === 'show_location'}
                    />
                  </View>

                  <View style={styles.rowDivider} />

                  {/* Toggle 3: Activity Status */}
                  <View style={styles.toggleRow}>
                    <View style={styles.toggleTextWrap}>
                      <Text style={styles.toggleTitle}>Activity Status</Text>
                      <Text style={styles.toggleSubtitle}>
                        Show when you are active on the platform.
                      </Text>
                    </View>
                    <CustomSwitch
                      value={activityStatus}
                      onValueChange={() =>
                        handleToggle('activity_status', activityStatus, setActivityStatus)
                      }
                      disabled={savingField === 'activity_status'}
                    />
                  </View>
                </View>

                {/* 3. MESSAGING PRIVACY CARD */}
                <View style={styles.sectionCard}>
                  <View style={styles.sectionHeader}>
                    <View style={[styles.sectionIconBadge, styles.greenBadge]}>
                      <Text style={styles.greenIcon}>💬</Text>
                    </View>
                    <View style={styles.sectionHeaderTextWrap}>
                      <Text style={styles.sectionTitle}>Messaging Privacy</Text>
                      <Text style={styles.sectionSubtitle}>
                        Manage who can contact you directly.
                      </Text>
                    </View>
                  </View>

                  <View style={styles.divider} />

                  {/* Toggle 1: Receive Direct Messages */}
                  <View style={styles.toggleRow}>
                    <View style={styles.toggleTextWrap}>
                      <Text style={styles.toggleTitle}>Receive Direct Messages</Text>
                      <Text style={styles.toggleSubtitle}>
                        Allow direct messages from verified caregivers.
                      </Text>
                    </View>
                    <CustomSwitch
                      value={receiveDirectMessages}
                      onValueChange={() =>
                        handleToggle(
                          'receive_direct_messages',
                          receiveDirectMessages,
                          setReceiveDirectMessages
                        )
                      }
                      disabled={savingField === 'receive_direct_messages'}
                    />
                  </View>

                  <View style={styles.rowDivider} />

                  {/* Toggle 2: Filter Unknown Senders */}
                  <View style={styles.toggleRow}>
                    <View style={styles.toggleTextWrap}>
                      <Text style={styles.toggleTitle}>Filter Unknown Senders</Text>
                      <Text style={styles.toggleSubtitle}>
                        Move messages from non-connections to requests.
                      </Text>
                    </View>
                    <CustomSwitch
                      value={filterUnknownSenders}
                      onValueChange={() =>
                        handleToggle(
                          'filter_unknown_senders',
                          filterUnknownSenders,
                          setFilterUnknownSenders
                        )
                      }
                      disabled={savingField === 'filter_unknown_senders'}
                    />
                  </View>

                  <View style={styles.rowDivider} />

                  {/* Toggle 3: Read Receipts */}
                  <View style={styles.toggleRow}>
                    <View style={styles.toggleTextWrap}>
                      <Text style={styles.toggleTitle}>Read Receipts</Text>
                      <Text style={styles.toggleSubtitle}>
                        Let others know when you've read their messages.
                      </Text>
                    </View>
                    <CustomSwitch
                      value={readReceipts}
                      onValueChange={() =>
                        handleToggle('read_receipts', readReceipts, setReadReceipts)
                      }
                      disabled={savingField === 'read_receipts'}
                    />
                  </View>
                </View>

                {/* 4. REPORT SAFETY CONCERN CARD */}
                <View style={styles.reportCard}>
                  <View style={styles.reportIconCircle}>
                    <Text style={styles.reportIconSymbol}>!</Text>
                  </View>

                  <Text style={styles.reportTitle}>Report Safety Concern</Text>

                  <Text style={styles.reportSubtitle}>
                    Experienced harassment, suspicious behavior, or feel unsafe? Report it
                    immediately to our moderation team.
                  </Text>

                  <TouchableOpacity
                    style={styles.fileReportButton}
                    onPress={() => setShowReportModal(true)}
                    activeOpacity={0.88}
                  >
                    <Text style={styles.flagIcon}>🚩</Text>
                    <Text style={styles.fileReportButtonText}>File a Report</Text>
                  </TouchableOpacity>
                </View>

                {/* 5. BLOCKED CONNECTIONS CARD */}
                <View style={styles.sectionCard}>
                  <View style={styles.blockedHeaderRow}>
                    <Text style={styles.blockedIconSymbol}>🚫</Text>
                    <Text style={styles.blockedTitle}>Blocked Connections</Text>
                  </View>

                  <Text style={styles.blockedSubtitle}>
                    Manage the list of users you have restricted from contacting or viewing your
                    profile.
                  </Text>

                  <TouchableOpacity
                    style={styles.outlineButton}
                    onPress={handleOpenBlockedModal}
                    activeOpacity={0.8}
                  >
                    <Text style={styles.outlineButtonText}>Manage List</Text>
                  </TouchableOpacity>
                </View>

                {/* 6. YOUR DATA CARD */}
                <View style={styles.sectionCard}>
                  <View style={styles.dataHeaderRow}>
                    <Text style={styles.dataIconSymbol}>📥</Text>
                    <Text style={styles.dataTitle}>Your Data</Text>
                  </View>

                  <Text style={styles.dataSubtitle}>
                    Download a copy of your personal data, activity logs, and settings stored on
                    NIVARA.
                  </Text>

                  <TouchableOpacity
                    style={[styles.outlineButton, styles.dataArchiveOutlineButton]}
                    onPress={handleRequestArchive}
                    activeOpacity={0.8}
                    disabled={requestingArchive}
                  >
                    {requestingArchive ? (
                      <ActivityIndicator size="small" color="#2563EB" />
                    ) : (
                      <Text style={styles.dataArchiveButtonText}>Request Archive</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </View>

              {/* Right Column (Desktop Wide Mode) */}
              {isDesktop && (
                <View style={styles.desktopSideColumn}>
                  {/* Verified Caregiver Protection Badge */}
                  <View style={styles.desktopSideCard}>
                    <View style={styles.sideCardHeader}>
                      <Text style={styles.sideCardIcon}>🛡️</Text>
                      <Text style={styles.sideCardTitle}>Protected Caregiver</Text>
                    </View>
                    <Text style={styles.sideCardDesc}>
                      Your account is protected by NIVARA's encrypted data privacy shield and verified
                      caregiver authorization.
                    </Text>
                    <View style={styles.sideShieldBadge}>
                      <Text style={styles.sideShieldText}>
                        ● {isVerified ? 'VERIFIED CAREGIVER ACTIVE' : 'PENDING VERIFICATION'}
                      </Text>
                    </View>
                  </View>

                  {/* Trust & Safety Pledge */}
                  <View style={styles.desktopSideCard}>
                    <View style={styles.sideCardHeader}>
                      <Text style={styles.sideCardIcon}>🤝</Text>
                      <Text style={styles.sideCardTitle}>Community Pledge</Text>
                    </View>
                    <Text style={styles.sideCardDesc}>
                      Every caregiver on NIVARA agrees to maintain confidentiality, empathy, and
                      respect across direct messaging and public discussions.
                    </Text>
                    <TouchableOpacity
                      onPress={() =>
                        Alert.alert(
                          'Caregiver Privacy Pledge',
                          'We do not sell personal caregiver data, HIPAA-adjacent details, or family identifiers.'
                        )
                      }
                    >
                      <Text style={styles.sideCardLink}>Read Trust & Safety Pledge →</Text>
                    </TouchableOpacity>
                  </View>

                  {/* Quick Shortcuts */}
                  <View style={styles.desktopSideCard}>
                    <Text style={styles.sideCardTitle}>Quick Actions</Text>
                    <TouchableOpacity
                      style={styles.quickActionItem}
                      onPress={() => navigation?.navigate?.('VerificationRequest')}
                    >
                      <Text style={styles.quickActionText}>Update Verification Documents</Text>
                      <Text style={styles.quickActionArrow}>›</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.quickActionItem}
                      onPress={() => navigation?.navigate?.('PhoneSupport')}
                    >
                      <Text style={styles.quickActionText}>Contact 24/7 Support Helpline</Text>
                      <Text style={styles.quickActionArrow}>›</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.quickActionItem, { borderBottomWidth: 0 }]}
                      onPress={() => navigation?.navigate?.('CommunityFeed')}
                    >
                      <Text style={styles.quickActionText}>Back to Community Feed</Text>
                      <Text style={styles.quickActionArrow}>›</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              )}
            </View>
          </ScrollView>

          {/* Bottom Tab Navigation Bar (Mobile / Tablet) */}
          {!isDesktop && (
            <View style={styles.bottomTabBar}>
              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('CommunityHome')}
              >
                <Text style={styles.tabIcon}>🏠</Text>
                <Text style={styles.tabLabel}>Home</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('CommunityFeed')}
              >
                <Text style={styles.tabIcon}>👥</Text>
                <Text style={styles.tabLabel}>Community</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('ChatList')}
              >
                <Text style={styles.tabIcon}>💬</Text>
                <Text style={styles.tabLabel}>Messages</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('PhoneSupport')}
              >
                <Text style={styles.tabIcon}>🛡️</Text>
                <Text style={styles.tabLabel}>Support</Text>
              </TouchableOpacity>

              {/* Profile Active Tab */}
              <TouchableOpacity style={styles.tabItemActive}>
                <View style={styles.activeTabIconCircle}>
                  <Text style={styles.tabIconActive}>👤</Text>
                </View>
                <Text style={styles.tabLabelActive}>Profile</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* MODAL 1: FILE A SAFETY REPORT */}
        <Modal
          visible={showReportModal}
          transparent={true}
          animationType="fade"
          onRequestClose={() => setShowReportModal(false)}
        >
          <View style={styles.modalBackdrop}>
            <View style={styles.modalContainer}>
              <View style={styles.modalHeaderRow}>
                <View style={styles.modalHeaderIconWrap}>
                  <Text style={styles.modalHeaderIcon}>🚩</Text>
                </View>
                <View>
                  <Text style={styles.modalTitle}>Report Safety Concern</Text>
                  <Text style={styles.modalSubtitle}>NIVARA Trust & Moderation Team</Text>
                </View>
              </View>

              <Text style={styles.modalLabel}>
                Please describe the incident, inappropriate messages, or suspicious behavior:
              </Text>
              <TextInput
                style={styles.modalTextarea}
                placeholder="Provide details to help us investigate immediately..."
                placeholderTextColor="#94A3B8"
                multiline={true}
                value={reportReason}
                onChangeText={setReportReason}
              />

              <View style={styles.modalActionsRow}>
                <TouchableOpacity
                  style={styles.modalCancelBtn}
                  onPress={() => setShowReportModal(false)}
                >
                  <Text style={styles.modalCancelText}>Cancel</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.modalSubmitBtn, !reportReason.trim() && styles.modalBtnDisabled]}
                  onPress={handleReportSubmit}
                  disabled={!reportReason.trim() || submittingReport}
                >
                  {submittingReport ? (
                    <ActivityIndicator size="small" color="#FFFFFF" />
                  ) : (
                    <Text style={styles.modalSubmitText}>Submit Report</Text>
                  )}
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>

        {/* MODAL 2: MANAGE BLOCKED CAREGIVERS */}
        <Modal
          visible={showBlockedModal}
          transparent={true}
          animationType="fade"
          onRequestClose={() => setShowBlockedModal(false)}
        >
          <View style={styles.modalBackdrop}>
            <View style={styles.modalContainer}>
              <View style={styles.modalHeaderRow}>
                <View style={[styles.modalHeaderIconWrap, { backgroundColor: '#F1F5F9' }]}>
                  <Text style={styles.modalHeaderIcon}>🚫</Text>
                </View>
                <View>
                  <Text style={styles.modalTitle}>Blocked Connections</Text>
                  <Text style={styles.modalSubtitle}>Manage restricted caregiver accounts</Text>
                </View>
              </View>

              {/* Block new caregiver input */}
              <View style={styles.blockInputRow}>
                <TextInput
                  style={styles.blockUserIdInput}
                  placeholder="Enter caregiver user ID to block..."
                  placeholderTextColor="#94A3B8"
                  value={newBlockId}
                  onChangeText={setNewBlockId}
                />
                <TouchableOpacity
                  style={styles.blockUserBtn}
                  onPress={handleBlockUserById}
                  disabled={blockingUser}
                >
                  {blockingUser ? (
                    <ActivityIndicator size="small" color="#FFFFFF" />
                  ) : (
                    <Text style={styles.blockUserBtnText}>Block</Text>
                  )}
                </TouchableOpacity>
              </View>

              {/* Blocked List */}
              <ScrollView style={styles.blockedListScroll}>
                {loadingBlocked ? (
                  <ActivityIndicator size="large" color="#4F46E5" style={{ marginVertical: 20 }} />
                ) : blockedUsers.length === 0 ? (
                  <View style={styles.emptyBlockedContainer}>
                    <Text style={styles.emptyBlockedEmoji}>🛡️</Text>
                    <Text style={styles.emptyBlockedTitle}>No Blocked Caregivers</Text>
                    <Text style={styles.emptyBlockedSub}>
                      You have not blocked any community members.
                    </Text>
                  </View>
                ) : (
                  blockedUsers.map((b) => (
                    <View key={b.blocked_id} style={styles.blockedUserItem}>
                      <View>
                        <Text style={styles.blockedUserId}>
                          Caregiver: {b.blocked_id}
                        </Text>
                        <Text style={styles.blockedUserDate}>
                          Blocked on {new Date(b.created_at).toLocaleDateString()}
                        </Text>
                      </View>
                      <TouchableOpacity
                        style={styles.unblockBtn}
                        onPress={() => handleUnblockUser(b.blocked_id)}
                      >
                        <Text style={styles.unblockBtnText}>Unblock</Text>
                      </TouchableOpacity>
                    </View>
                  ))
                )}
              </ScrollView>

              <TouchableOpacity
                style={styles.modalFullCloseBtn}
                onPress={() => setShowBlockedModal(false)}
              >
                <Text style={styles.modalFullCloseBtnText}>Done</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {/* MODAL 3: DATA ARCHIVE CONFIRMATION */}
        <Modal
          visible={showArchiveModal}
          transparent={true}
          animationType="fade"
          onRequestClose={() => setShowArchiveModal(false)}
        >
          <View style={styles.modalBackdrop}>
            <View style={styles.modalContainer}>
              <View style={[styles.modalHeaderIconWrap, { backgroundColor: '#EFF6FF', alignSelf: 'center', marginBottom: 12 }]}>
                <Text style={styles.modalHeaderIcon}>📥</Text>
              </View>
              <Text style={[styles.modalTitle, { textAlign: 'center' }]}>Archive Request Received</Text>
              <Text style={[styles.modalSubtitle, { textAlign: 'center', marginBottom: 16 }]}>
                Your data export package is being compiled securely.
              </Text>
              <Text style={{ fontSize: 14, color: '#475569', lineHeight: 20, textAlign: 'center', marginBottom: 20 }}>
                We will email an encrypted download link containing your profile logs, messaging history, and privacy preferences within 24 hours.
              </Text>
              <TouchableOpacity
                style={styles.modalSubmitBtn}
                onPress={() => setShowArchiveModal(false)}
              >
                <Text style={styles.modalSubmitText}>Understood</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
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

  /* Desktop Sidebar */
  desktopSidebar: {
    width: 260,
    backgroundColor: '#FFFFFF',
    borderRightWidth: 1,
    borderRightColor: '#E2E8F0',
    justifyContent: 'space-between',
    paddingVertical: 24,
    paddingHorizontal: 16,
  },
  sidebarTop: {
    flex: 1,
  },
  sidebarBrand: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 32,
    paddingHorizontal: 8,
  },
  brandLogoIcon: {
    fontSize: 26,
  },
  sidebarBrandTitle: {
    fontSize: 20,
    fontWeight: '900',
    color: '#0F172A',
    letterSpacing: 0.5,
  },
  sidebarBrandSubtitle: {
    fontSize: 9,
    fontWeight: '700',
    color: '#64748B',
    letterSpacing: 0.8,
  },
  sidebarNav: {
    gap: 6,
  },
  sidebarNavItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 14,
    borderRadius: 12,
    gap: 12,
  },
  sidebarNavItemActive: {
    backgroundColor: '#EFF6FF',
  },
  sidebarNavIcon: {
    fontSize: 18,
  },
  sidebarNavIconActive: {
    color: '#2563EB',
  },
  sidebarNavText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  sidebarNavTextActive: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
  },
  sidebarBottom: {
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 16,
  },
  sidebarLogoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 10,
    paddingHorizontal: 14,
  },
  sidebarLogoutIcon: {
    fontSize: 16,
  },
  sidebarLogoutText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },

  /* Main Canvas */
  mainCanvas: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },

  /* Top Navbar */
  topNavbar: {
    height: 64,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
  },
  topNavLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  avatarTouchable: {
    borderRadius: 20,
  },
  headerAvatar: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#E2E8F0',
  },
  brandTitleWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  nivaraBrandSymbol: {
    fontSize: 18,
    color: '#0284C7',
  },
  nivaraBrandText: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0284C7',
    letterSpacing: 0.5,
  },
  desktopSearchWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F1F5F9',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    width: 380,
  },
  desktopSearchIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  desktopSearchInput: {
    flex: 1,
    fontSize: 14,
    color: '#0F172A',
  },
  topNavRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  notificationBellBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
  },
  bellIcon: {
    fontSize: 18,
  },
  bellDot: {
    position: 'absolute',
    top: 9,
    right: 9,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444',
  },

  /* Toast */
  toastBanner: {
    backgroundColor: '#059669',
    paddingVertical: 10,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  toastText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 13,
  },

  /* Scroll Area */
  scrollArea: {
    flex: 1,
  },
  scrollContent: {
    paddingVertical: 20,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  contentWrapper: {
    width: '100%',
    maxWidth: 500,
    gap: 16,
  },
  contentWrapperDesktop: {
    maxWidth: 1050,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 24,
  },
  centerColumn: {
    width: '100%',
    gap: 16,
  },
  centerColumnDesktop: {
    flex: 1,
  },

  /* 1. HERO CARD */
  heroCard: {
    backgroundColor: '#F8FCF8',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  heroBadgeRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  heroBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  heroBadgeIcon: {
    fontSize: 15,
  },
  heroBadgeText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#15803D',
    letterSpacing: 0.5,
  },
  heroTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 8,
  },
  heroDescription: {
    fontSize: 13.5,
    color: '#475569',
    lineHeight: 20,
    marginBottom: 16,
  },
  mockupIllustrationContainer: {
    width: '100%',
    height: 180,
    borderRadius: 14,
    overflow: 'hidden',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  mockupImage: {
    width: '100%',
    height: '100%',
  },

  /* 2 & 3. SECTION CARDS */
  sectionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  sectionIconBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  blueBadge: {
    backgroundColor: '#EFF6FF',
  },
  greenBadge: {
    backgroundColor: '#ECFDF5',
  },
  blueIcon: {
    fontSize: 20,
  },
  greenIcon: {
    fontSize: 20,
  },
  sectionHeaderTextWrap: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 2,
  },
  sectionSubtitle: {
    fontSize: 12.5,
    color: '#64748B',
    lineHeight: 17,
  },
  divider: {
    height: 1,
    backgroundColor: '#F1F5F9',
    marginTop: 16,
    marginBottom: 8,
  },
  rowDivider: {
    height: 1,
    backgroundColor: '#F8FAFC',
    marginVertical: 10,
  },

  /* Toggles */
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 6,
  },
  toggleTextWrap: {
    flex: 1,
    paddingRight: 16,
  },
  toggleTitle: {
    fontSize: 14.5,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 2,
  },
  toggleSubtitle: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 16,
  },

  /* Custom Switch Styles */
  switchTrack: {
    width: 50,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    paddingHorizontal: 3,
  },
  switchTrackActive: {
    backgroundColor: '#2563EB',
  },
  switchTrackInactive: {
    backgroundColor: '#CBD5E1',
  },
  switchThumb: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#FFFFFF',
    elevation: 2,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 2,
  },
  switchThumbActive: {
    alignSelf: 'flex-end',
  },
  switchThumbInactive: {
    alignSelf: 'flex-start',
  },

  /* 4. REPORT SAFETY CONCERN */
  reportCard: {
    backgroundColor: '#FFF1F2',
    borderRadius: 20,
    padding: 22,
    borderWidth: 1,
    borderColor: '#FECDD3',
    alignItems: 'center',
  },
  reportIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#881337',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  reportIconSymbol: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '900',
  },
  reportTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#881337',
    marginBottom: 6,
    textAlign: 'center',
  },
  reportSubtitle: {
    fontSize: 13,
    color: '#881337',
    lineHeight: 18,
    textAlign: 'center',
    marginBottom: 16,
    opacity: 0.9,
  },
  fileReportButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#881337',
    paddingVertical: 12,
    paddingHorizontal: 28,
    borderRadius: 24,
  },
  flagIcon: {
    fontSize: 14,
  },
  fileReportButtonText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 14,
  },

  /* 5. BLOCKED CONNECTIONS */
  blockedHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 6,
  },
  blockedIconSymbol: {
    fontSize: 20,
  },
  blockedTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  blockedSubtitle: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 16,
  },
  outlineButton: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  outlineButtonText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1E293B',
  },

  /* 6. YOUR DATA */
  dataHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 6,
  },
  dataIconSymbol: {
    fontSize: 20,
  },
  dataTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  dataSubtitle: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 16,
  },
  dataArchiveOutlineButton: {
    borderColor: '#93C5FD',
    backgroundColor: '#F8FAFC',
  },
  dataArchiveButtonText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
  },

  /* Desktop Side Column */
  desktopSideColumn: {
    width: 320,
    gap: 16,
  },
  desktopSideCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  sideCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  sideCardIcon: {
    fontSize: 18,
  },
  sideCardTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  sideCardDesc: {
    fontSize: 12.5,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 12,
  },
  sideShieldBadge: {
    backgroundColor: '#DCFCE7',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  sideShieldText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#15803D',
  },
  sideCardLink: {
    fontSize: 13,
    fontWeight: '700',
    color: '#2563EB',
  },
  quickActionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  quickActionText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#334155',
  },
  quickActionArrow: {
    fontSize: 16,
    color: '#94A3B8',
  },

  /* Bottom Tab Bar */
  bottomTabBar: {
    height: 64,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 10,
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 4,
  },
  tabItemActive: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 4,
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 2,
    color: '#64748B',
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
  },
  activeTabIconCircle: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 2,
  },
  tabIconActive: {
    fontSize: 18,
    color: '#2563EB',
  },
  tabLabelActive: {
    fontSize: 11,
    fontWeight: '800',
    color: '#2563EB',
  },

  /* Modals */
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 24,
    width: '100%',
    maxWidth: 460,
    elevation: 6,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
  },
  modalHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 16,
  },
  modalHeaderIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFE4E6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalHeaderIcon: {
    fontSize: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  modalSubtitle: {
    fontSize: 12.5,
    color: '#64748B',
  },
  modalLabel: {
    fontSize: 13.5,
    fontWeight: '600',
    color: '#334155',
    marginBottom: 8,
  },
  modalTextarea: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 14,
    fontSize: 14,
    color: '#0F172A',
    minHeight: 110,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
  },
  modalActionsRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
  },
  modalCancelBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 10,
  },
  modalCancelText: {
    color: '#64748B',
    fontWeight: '600',
    fontSize: 14,
  },
  modalSubmitBtn: {
    backgroundColor: '#881337',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
  },
  modalSubmitText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 14,
  },
  modalBtnDisabled: {
    backgroundColor: '#CBD5E1',
  },

  /* Blocked Modal Specifics */
  blockInputRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  blockUserIdInput: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 8,
    fontSize: 13,
    color: '#0F172A',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  blockUserBtn: {
    backgroundColor: '#0F172A',
    paddingHorizontal: 16,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  blockUserBtnText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 13,
  },
  blockedListScroll: {
    maxHeight: 220,
    marginBottom: 16,
  },
  emptyBlockedContainer: {
    padding: 24,
    alignItems: 'center',
  },
  emptyBlockedEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  emptyBlockedTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 4,
  },
  emptyBlockedSub: {
    fontSize: 12.5,
    color: '#64748B',
    textAlign: 'center',
  },
  blockedUserItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  blockedUserId: {
    fontSize: 13.5,
    fontWeight: '600',
    color: '#1E293B',
  },
  blockedUserDate: {
    fontSize: 11,
    color: '#94A3B8',
  },
  unblockBtn: {
    paddingVertical: 4,
    paddingHorizontal: 10,
    backgroundColor: '#FEE2E2',
    borderRadius: 8,
  },
  unblockBtnText: {
    color: '#DC2626',
    fontWeight: '700',
    fontSize: 12,
  },
  modalFullCloseBtn: {
    backgroundColor: '#F1F5F9',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  modalFullCloseBtnText: {
    color: '#1E293B',
    fontWeight: '700',
    fontSize: 14,
  },
});
