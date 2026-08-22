import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Modal,
  Dimensions,
  Platform,
  SafeAreaView,
  Linking,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { supportApi } from '../../services/api/supportApi';
import { communityApi } from '../../services/api/communityApi';
import { useAuthStore } from '../../store/authStore';

const { width } = Dimensions.get('window');

// Responsive breakpoints
const isDesktopWidth = (w) => (Platform.OS === 'web' ? w > 1024 : w > 900);
const isTabletWidth = (w) => (Platform.OS === 'web' ? w > 640 && w <= 1024 : w > 600 && w <= 900);

export default function SupportCenterScreen({ navigation }) {
  const [windowWidth, setWindowWidth] = useState(Dimensions.get('window').width);
  const isDesktop = isDesktopWidth(windowWidth);
  const isTablet = isTabletWidth(windowWidth);

  const { user, logout, token } = useAuthStore();

  // Search & Navigation States
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTopTab, setActiveTopTab] = useState('support');
  const [activeSideNav, setActiveSideNav] = useState('support');
  const [copiedToast, setCopiedToast] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Showcase Carousel state
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [showShowcaseModal, setShowShowcaseModal] = useState(false);

  // Callback Modal & Interactive States
  const [showCallbackModal, setShowCallbackModal] = useState(false);
  const [callbackDate, setCallbackDate] = useState('Today');
  const [callbackTime, setCallbackTime] = useState('2:30 PM');
  const [callbackPhone, setCallbackPhone] = useState('');
  const [bookingCallback, setBookingCallback] = useState(false);
  const [callbackSuccessMsg, setCallbackSuccessMsg] = useState('');
  const [callbackErrorMsg, setCallbackErrorMsg] = useState('');

  // Guide Reader Modal
  const [showGuideModal, setShowGuideModal] = useState(false);
  const [selectedGuide, setSelectedGuide] = useState(null);

  // Support Ticket Modal
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [ticketSubject, setTicketSubject] = useState('');
  const [ticketCategory, setTicketCategory] = useState('Caregiver Support');
  const [ticketDesc, setTicketDesc] = useState('');
  const [submittingTicket, setSubmittingTicket] = useState(false);
  const [ticketSuccessMsg, setTicketSuccessMsg] = useState('');
  const [ticketErrorMsg, setTicketErrorMsg] = useState('');

  // Voice Call Simulator States
  const [callState, setCallState] = useState('idle'); // 'idle' | 'calling' | 'connected' | 'ended'
  const [callDuration, setCallDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeaker, setIsSpeaker] = useState(false);
  const [activeCallContact, setActiveCallContact] = useState(null);

  // Backend API Data States
  const [hotlinesData, setHotlinesData] = useState(null);
  const [loadingHotlines, setLoadingHotlines] = useState(true);
  const [hotlinesError, setHotlinesError] = useState(null);

  const [backendResources, setBackendResources] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);

  const [myTickets, setMyTickets] = useState([]);
  const [myCalls, setMyCalls] = useState([]);
  const [loadingRequests, setLoadingRequests] = useState(true);
  const [requestsError, setRequestsError] = useState(null);

  const supportPin = '4829';

  // Responsive dimension listener
  useEffect(() => {
    const handleResize = ({ window }) => {
      setWindowWidth(window.width);
    };
    const subscription = Dimensions.addEventListener('change', handleResize);
    return () => subscription?.remove?.();
  }, []);

  // Voice call duration timer
  useEffect(() => {
    let timer;
    if (callState === 'connected') {
      timer = setInterval(() => {
        setCallDuration((prev) => prev + 1);
      }, 1000);
    } else {
      setCallDuration(0);
    }
    return () => clearInterval(timer);
  }, [callState]);

  // Load API Data on mount & token change
  useEffect(() => {
    loadSupportCenterData();
  }, [token]);

  const loadSupportCenterData = async () => {
    setLoadingHotlines(true);
    setLoadingRequests(true);
    setHotlinesError(null);
    setRequestsError(null);

    // 1. Fetch Hotlines from /api/v1/support/hotlines (Public)
    try {
      const hData = await supportApi.getHotlines();
      if (hData) {
        setHotlinesData(hData);
      }
    } catch (err) {
      console.warn('Failed to load hotlines from backend:', err);
      setHotlinesError('Unable to load hotline directory from backend.');
    } finally {
      setLoadingHotlines(false);
    }

    // 2. Fetch Resources from /api/v1/community/resources (Community resources)
    try {
      setLoadingResources(true);
      const resData = await communityApi.getResources();
      if (Array.isArray(resData)) {
        setBackendResources(resData);
      }
    } catch (err) {
      // Unverified or network fallback
      console.warn('Resources fetch notice:', err?.message || err);
    } finally {
      setLoadingResources(false);
    }

    // 3. Fetch User's Tickets & Calls from backend
    if (token) {
      try {
        const [tRes, cRes] = await Promise.allSettled([
          supportApi.getMyTickets(),
          supportApi.getMyCalls(),
        ]);

        if (tRes.status === 'fulfilled' && Array.isArray(tRes.value)) {
          setMyTickets(tRes.value);
        } else if (tRes.status === 'rejected') {
          console.warn('Tickets fetch failed:', tRes.reason);
          setRequestsError(tRes.reason?.detail || 'Unable to sync support requests.');
        }

        if (cRes.status === 'fulfilled' && Array.isArray(cRes.value)) {
          setMyCalls(cRes.value);
        }
      } catch (err) {
        console.warn('Error fetching support requests:', err);
        setRequestsError('Failed to load support requests.');
      } finally {
        setLoadingRequests(false);
      }
    } else {
      setLoadingRequests(false);
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadSupportCenterData();
    setRefreshing(false);
  }, [token]);

  // Callback Scheduling Flow -> POST /api/v1/support/calls/schedule
  const handleConfirmCallback = async () => {
    setCallbackErrorMsg('');
    setCallbackSuccessMsg('');

    const formattedSlot = `${callbackDate}, ${callbackTime}`;
    if (!formattedSlot.trim()) {
      setCallbackErrorMsg('Please select a preferred date and time slot.');
      return;
    }

    setBookingCallback(true);
    try {
      const res = await supportApi.scheduleCall({
        time_slot: formattedSlot,
        phone_number: callbackPhone.trim() || undefined,
      });

      const specialist = res.specialist_name || 'Sarah J.';
      const scheduledTime = res.scheduled_time || formattedSlot;
      setCallbackSuccessMsg(
        `Your callback has been scheduled successfully with ${specialist} for ${scheduledTime}.`
      );

      // Refresh calls and tickets list
      const updatedCalls = await supportApi.getMyCalls().catch(() => []);
      if (Array.isArray(updatedCalls)) {
        setMyCalls(updatedCalls);
      }

      // Close modal after brief success presentation
      setTimeout(() => {
        setShowCallbackModal(false);
        setCallbackSuccessMsg('');
        setCallbackPhone('');
      }, 2000);
    } catch (err) {
      console.error('Schedule callback error:', err);
      const detail = err.detail || err.message || 'Unable to schedule your callback. Please try again.';
      setCallbackErrorMsg(detail === 'Missing or invalid token in Authorization header.'
        ? 'Please log in to schedule a support callback.'
        : 'Unable to schedule your callback. Please try again.');
    } finally {
      setBookingCallback(false);
    }
  };

  // Support Ticket Submission Flow -> POST /api/v1/support/tickets
  const handleCreateTicket = async () => {
    setTicketErrorMsg('');
    setTicketSuccessMsg('');

    if (!ticketSubject.trim()) {
      setTicketErrorMsg('Subject is required for your inquiry.');
      return;
    }
    if (!ticketDesc.trim()) {
      setTicketErrorMsg('Please provide a description of the assistance you need.');
      return;
    }

    setSubmittingTicket(true);
    try {
      const res = await supportApi.createTicket({
        subject: ticketSubject.trim(),
        category: ticketCategory,
        description: ticketDesc.trim(),
      });

      setTicketSuccessMsg(`Inquiry ${res.ticket_number || ''} submitted successfully. Our team will follow up within 2 hours.`);

      // Refresh tickets list
      const updatedTickets = await supportApi.getMyTickets().catch(() => []);
      if (Array.isArray(updatedTickets)) {
        setMyTickets(updatedTickets);
      }

      setTimeout(() => {
        setShowTicketModal(false);
        setTicketSuccessMsg('');
        setTicketSubject('');
        setTicketDesc('');
      }, 2000);
    } catch (err) {
      console.error('Submit ticket error:', err);
      const detail = err.detail || err.message || 'Unable to submit your support inquiry. Please try again.';
      setTicketErrorMsg(detail);
    } finally {
      setSubmittingTicket(false);
    }
  };

  // Call Handlers
  const handleStartCall = (contactInfo = null) => {
    setActiveCallContact(contactInfo);
    setCallState('calling');
    setTimeout(() => {
      setCallState('connected');
    }, 2000);
  };

  const handleEndCall = () => {
    setCallState('ended');
    setTimeout(() => {
      setCallState('idle');
      setActiveCallContact(null);
    }, 1500);
  };

  const handlePhoneDial = (phoneNumber) => {
    if (!phoneNumber) return;
    const cleanNum = phoneNumber.replace(/[^0-9+]/g, '');
    const telUrl = `tel:${cleanNum}`;
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      window.location.href = telUrl;
    } else {
      Linking.openURL(telUrl).catch(() => {
        copyPinToClipboard();
      });
    }
  };

  const copyPinToClipboard = () => {
    try {
      if (Platform.OS === 'web' && typeof navigator !== 'undefined' && navigator.clipboard) {
        navigator.clipboard.writeText(supportPin);
      }
    } catch (e) {
      // fallback
    }
    setCopiedToast(true);
    setTimeout(() => {
      setCopiedToast(false);
    }, 2500);
  };

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Core Caregiver Guides data with optional backend community resources integration
  const staticCaregiverGuides = [
    {
      id: 'sensory',
      title: 'Sensory Overload Help',
      badge: 'High Priority',
      description: 'Quick-response environmental adjustments and calming techniques during sensory flooding.',
      tips: [
        'Dim ambient lighting and eliminate high-frequency acoustic triggers.',
        'Offer deep pressure compression or weighted vests if comfortable.',
        'Use quiet verbal cues or visual PECS symbols rather than complex questions.',
        'Create an immediate quiet decompression zone with minimal stimuli.',
      ],
    },
    {
      id: 'routine',
      title: 'Daily Visual Routines',
      badge: 'Step-by-step',
      description: 'Structuring morning, school, and bedtime transitions to prevent anxiety.',
      tips: [
        'Keep visual timers visible 5 minutes before scheduled task changes.',
        'Celebrate completed daily milestones with predictable positive reinforcement.',
        'Use sequence cards (First -> Then) for transitions between preferred and non-preferred tasks.',
      ],
    },
    {
      id: 'meltdown',
      title: 'Meltdown vs Tantrum De-escalation',
      badge: 'Safety Strategy',
      description: 'Identifying neurodiversity-affirming safety protocols during emotional dysregulation.',
      tips: [
        'Recognize that sensory meltdowns are involuntary responses, not behavioral defiance.',
        'Maintain calm body language, reduce verbal input to 1-2 words.',
        'Protect physical safety and give time for adrenaline levels to normalize.',
      ],
    },
    {
      id: 'school',
      title: 'IEP & School Accommodations',
      badge: 'Advocacy Guide',
      description: 'Navigating customized learning plans and communication logs with educators.',
      tips: [
        'Document sensory triggers and preferred soothing methods in writing.',
        'Request scheduled sensory diet breaks throughout classroom hours.',
      ],
    },
  ];

  // Merge static curated guides with backend resources if available
  const allGuides = [
    ...staticCaregiverGuides,
    ...backendResources.map((r) => ({
      id: r.id,
      title: r.title,
      badge: r.category || 'Community Resource',
      description: r.description,
      tips: [
        `Category: ${r.category || 'General'}`,
        `Contributed by verified caregiver: ${r.author_name || 'Caregiver'}`,
        r.url ? `External Link: ${r.url}` : 'Available in NIVARA community knowledge base',
      ],
    })),
  ];

  // Dynamic filter based on search query
  const queryTrimmed = searchQuery.trim().toLowerCase();
  const filteredGuides = queryTrimmed
    ? allGuides.filter(
        (g) =>
          g.title.toLowerCase().includes(queryTrimmed) ||
          g.description.toLowerCase().includes(queryTrimmed) ||
          (g.badge && g.badge.toLowerCase().includes(queryTrimmed))
      )
    : allGuides;

  // Mockup carousel slides
  const showcaseSlides = [
    {
      id: 0,
      title: 'Discover & Learn',
      tagline: 'Personalized Caregiver Modules',
      sub: 'Step-by-step video courses and interactive guides for every milestone.',
      illustration: '👩‍🏫',
    },
    {
      id: 1,
      title: 'Instant Support & Calls',
      tagline: 'Direct Specialist Access',
      sub: 'Connect with certified specialists and crisis professionals 24/7.',
      illustration: '🎧',
    },
    {
      id: 2,
      title: 'Community & Peer Groups',
      tagline: 'Safe Moderated Spaces',
      sub: 'Exchange strategies with verified caregivers in supportive group chats.',
      illustration: '🤝',
    },
  ];

  // Combine Active Support Requests (Tickets + Scheduled Calls)
  const combinedSupportRequests = [
    ...myCalls.map((c) => ({
      id: c.id,
      type: '1-on-1 Call',
      icon: '📞',
      title: `Callback with ${c.specialist_name || 'Sarah J.'}`,
      status: c.status || 'scheduled',
      scheduled_time: c.scheduled_time,
      created_at: c.created_at,
      details: `Scheduled callback slot: ${c.scheduled_time}`,
    })),
    ...myTickets.map((t) => ({
      id: t.id,
      type: 'Inquiry Ticket',
      icon: '📋',
      title: t.subject || 'Support Inquiry',
      status: t.status || 'open',
      ticket_number: t.ticket_number,
      created_at: t.created_at,
      details: `${t.category || 'General'} • ${t.description || ''}`,
    })),
  ].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));

  // Extract Emergency Hotlines from backend hotlinesData
  const backendHotlines = hotlinesData?.hotlines || [];
  const crisisHotlines = backendHotlines.filter(
    (h) =>
      h.label?.toLowerCase().includes('crisis') ||
      h.label?.toLowerCase().includes('local') ||
      h.region?.toLowerCase().includes('crisis') ||
      h.region?.toLowerCase().includes('local')
  );
  const tollFreeHotlines = backendHotlines.filter(
    (h) => !crisisHotlines.includes(h)
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Top Banner Navigation Bar (Tablet / Desktop Breadcrumb) */}
      {(isDesktop || isTablet) && (
        <View style={styles.topBannerBar}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation?.goBack?.() || navigation?.navigate?.('CommunityHome')}
            activeOpacity={0.7}
          >
            <Text style={styles.backArrow}>←</Text>
            <Text style={styles.backTitle}>NIVARA Portal</Text>
          </TouchableOpacity>

          {/* Top Navbar Pill Tabs */}
          <View style={styles.topNavbarTabs}>
            <TouchableOpacity
              style={[styles.topTabPill, activeTopTab === 'dashboard' && styles.topTabPillActive]}
              onPress={() => {
                setActiveTopTab('dashboard');
                navigation?.navigate?.('CommunityHome');
              }}
            >
              <Text style={styles.topTabIcon}>🎛️</Text>
              <Text style={[styles.topTabText, activeTopTab === 'dashboard' && styles.topTabTextActive]}>
                Dashboard
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.topTabPill, activeTopTab === 'groups' && styles.topTabPillActive]}
              onPress={() => {
                setActiveTopTab('groups');
                navigation?.navigate?.('ActiveGroups');
              }}
            >
              <Text style={styles.topTabIcon}>👥</Text>
              <Text style={[styles.topTabText, activeTopTab === 'groups' && styles.topTabTextActive]}>
                Active Groups
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.topTabPill, activeTopTab === 'verification' && styles.topTabPillActive]}
              onPress={() => {
                setActiveTopTab('verification');
                navigation?.navigate?.('VerificationRequest');
              }}
            >
              <Text style={styles.topTabIcon}>🛡️</Text>
              <Text style={[styles.topTabText, activeTopTab === 'verification' && styles.topTabTextActive]}>
                Verification Status
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.topTabPill, activeTopTab === 'guidelines' && styles.topTabPillActive]}
              onPress={() => {
                setActiveTopTab('guidelines');
                navigation?.navigate?.('SafetyPrivacyCenter');
              }}
            >
              <Text style={styles.topTabIcon}>📖</Text>
              <Text style={[styles.topTabText, activeTopTab === 'guidelines' && styles.topTabTextActive]}>
                Guidelines
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.topTabPill, activeTopTab === 'support' && styles.topTabPillActivePrimary]}
              onPress={() => setActiveTopTab('support')}
            >
              <Text style={styles.topTabIconPrimary}>🎧</Text>
              <Text style={styles.topTabTextActivePrimary}>Support Center</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Main Layout Container */}
      <View style={styles.appContainer}>
        {/* Left Navigation Sidebar (Desktop 1280x800 & 1440x900) */}
        {isDesktop && (
          <View style={styles.sidebar}>
            <View style={styles.sidebarTopContent}>
              {/* Brand Header */}
              <View style={styles.brandContainer}>
                <View style={styles.brandLogoBox}>
                  <Text style={styles.brandLogoIcon}>✦</Text>
                </View>
                <View style={styles.brandTextWrapper}>
                  <Text style={styles.brandTitle}>NIVARA</Text>
                  <View style={styles.verificationBadge}>
                    <Text style={styles.verificationBadgeText}>Caregiver Portal</Text>
                  </View>
                </View>
              </View>

              {/* Sidebar Menu Items */}
              <View style={styles.menuContainer}>
                <TouchableOpacity
                  style={[styles.navItem, activeSideNav === 'dashboard' && styles.navItemActive]}
                  onPress={() => {
                    setActiveSideNav('dashboard');
                    navigation?.navigate?.('CommunityHome');
                  }}
                >
                  <Text style={styles.navIcon}>🎛️</Text>
                  <Text style={styles.navText}>Dashboard</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.navItem, activeSideNav === 'groups' && styles.navItemActive]}
                  onPress={() => {
                    setActiveSideNav('groups');
                    navigation?.navigate?.('ActiveGroups');
                  }}
                >
                  <Text style={styles.navIcon}>👥</Text>
                  <Text style={styles.navText}>Active Groups</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.navItem, activeSideNav === 'verification' && styles.navItemActive]}
                  onPress={() => {
                    setActiveSideNav('verification');
                    navigation?.navigate?.('VerificationRequest');
                  }}
                >
                  <Text style={styles.navIcon}>🛡️</Text>
                  <Text style={styles.navText}>Verification Status</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.navItem, activeSideNav === 'guidelines' && styles.navItemActive]}
                  onPress={() => {
                    setActiveSideNav('guidelines');
                    navigation?.navigate?.('SafetyPrivacyCenter');
                  }}
                >
                  <Text style={styles.navIcon}>📖</Text>
                  <Text style={styles.navText}>Community Guidelines</Text>
                </TouchableOpacity>

                {/* HIGHLIGHTED SUPPORT ITEM */}
                <TouchableOpacity
                  style={[styles.navItem, styles.navItemActivePrimary]}
                  onPress={() => setActiveSideNav('support')}
                >
                  <Text style={styles.navIconPrimary}>🎧</Text>
                  <Text style={styles.navTextActivePrimary}>Support Center</Text>
                </TouchableOpacity>
              </View>

              {/* Settings & Sign Out */}
              <View style={styles.sidebarBottomNav}>
                <TouchableOpacity
                  style={styles.navItem}
                  onPress={() => navigation?.navigate?.('SafetyPrivacyCenter')}
                >
                  <Text style={styles.navIcon}>⚙️</Text>
                  <Text style={styles.navText}>Settings</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.navItem}
                  onPress={async () => {
                    await logout();
                  }}
                >
                  <Text style={styles.navIcon}>🚪</Text>
                  <Text style={styles.navText}>Sign Out</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Sidebar Bottom Background Graphic */}
            <View style={styles.sidebarBgGraphicWrapper}>
              <View style={styles.sidebarDecoCircle} />
            </View>
          </View>
        )}

        {/* Main Content Workspace */}
        <View style={styles.mainContent}>
          {/* Mobile Top Header (Exact match to screenshot) */}
          {!isDesktop && (
            <View style={styles.mobileHeader}>
              <TouchableOpacity
                style={styles.mobileAvatarBtn}
                onPress={() => navigation?.navigate?.('CaregiverProfile', { userId: user?.id })}
                activeOpacity={0.8}
              >
                <View style={styles.mobileAvatarCircle}>
                  <Text style={styles.mobileAvatarEmoji}>👩‍🏫</Text>
                </View>
              </TouchableOpacity>

              <Text style={styles.mobileBrandTitle}>NIVARA</Text>

              <TouchableOpacity
                style={styles.mobileNotificationBtn}
                onPress={() => navigation?.navigate?.('CommunityHome')}
                activeOpacity={0.8}
              >
                <Text style={styles.mobileNotificationIcon}>🔔</Text>
                <View style={styles.notificationDot} />
              </TouchableOpacity>
            </View>
          )}

          {/* Desktop Top Header Bar */}
          {isDesktop && (
            <View style={styles.desktopTopHeader}>
              <View>
                <Text style={styles.desktopPageTitle}>Support Center</Text>
                <Text style={styles.desktopPageSubtitle}>
                  Dedicated assistance and 24/7 resources for autism caregivers
                </Text>
              </View>

              <View style={styles.desktopHeaderRight}>
                <TouchableOpacity
                  style={styles.headerIconButton}
                  onPress={() => setShowTicketModal(true)}
                  activeOpacity={0.8}
                >
                  <Text style={styles.headerActionPillText}>+ New Inquiry</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.headerIconButton}
                  onPress={() => setShowCallbackModal(true)}
                  activeOpacity={0.8}
                >
                  <Text style={styles.headerCallbackPillText}>📅 Callback</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.headerIconButton} activeOpacity={0.8}>
                  <Text style={styles.headerIconText}>🔔</Text>
                  <View style={styles.notificationDot} />
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.userProfileAvatar}
                  onPress={() => navigation?.navigate?.('CaregiverProfile', { userId: user?.id })}
                >
                  <Text style={styles.userAvatarText}>
                    {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {/* Toast Notification */}
          {copiedToast && (
            <View style={styles.toastContainer}>
              <Text style={styles.toastText}>✓ PIN {supportPin} copied to clipboard!</Text>
            </View>
          )}

          {/* Scrollable Content View */}
          <ScrollView
            style={styles.scrollCanvas}
            contentContainerStyle={[
              styles.scrollCanvasContent,
              !isDesktop && styles.scrollCanvasMobileContent,
            ]}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#2563EB']} />
            }
          >
            {/* Desktop Two-Column or Mobile Single Column */}
            <View style={[styles.layoutWrapper, isDesktop && styles.layoutWrapperDesktop]}>
              {/* Primary Column (Matches Reference Screenshot) */}
              <View style={[styles.primaryColumn, isDesktop && styles.primaryColumnDesktop]}>
                {/* 1. Hero Title & Subtitle */}
                <View style={styles.heroSection}>
                  <Text style={styles.heroTitle}>How can we support you today?</Text>
                  <Text style={styles.heroSubtitle}>
                    Find guides, resources, and immediate assistance tailored to your needs.
                  </Text>
                </View>

                {/* 2. Search Bar */}
                <View style={styles.searchBarContainer}>
                  <Text style={styles.searchBarIcon}>🔍</Text>
                  <TextInput
                    style={styles.searchBarInput}
                    placeholder="Search for 'Sensory Overload Help'..."
                    placeholderTextColor="#94A3B8"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                  />
                  {searchQuery.length > 0 && (
                    <TouchableOpacity onPress={() => setSearchQuery('')} style={styles.clearSearchBtn}>
                      <Text style={styles.clearSearchText}>✕</Text>
                    </TouchableOpacity>
                  )}
                </View>

                {/* 3. Showcase Carousel Card (Matching Reference Screenshot 3 Phone Mockups) */}
                <View style={styles.showcaseCard}>
                  <View style={styles.showcasePhonesRow}>
                    {/* Mini Phone 1: Discover and skills */}
                    <View style={styles.miniPhoneFrame}>
                      <View style={styles.miniPhoneNotch} />
                      <View style={styles.miniPhoneScreen}>
                        <View style={styles.miniPhoneAvatarWrap}>
                          <Text style={{ fontSize: 22 }}>👩‍💻</Text>
                        </View>
                        <Text style={styles.miniPhoneTitle} numberOfLines={2}>
                          Discover & improve your skills.
                        </Text>
                        <Text style={styles.miniPhoneDesc} numberOfLines={2}>
                          Interactive modules tailored for caregivers.
                        </Text>
                        <View style={styles.miniPhoneBtn}>
                          <Text style={styles.miniPhoneBtnText}>Get Started</Text>
                        </View>
                      </View>
                    </View>

                    {/* Mini Phone 2: Sign Up */}
                    <View style={[styles.miniPhoneFrame, styles.miniPhoneFrameCenter]}>
                      <View style={styles.miniPhoneNotch} />
                      <View style={styles.miniPhoneScreen}>
                        <Text style={styles.miniPhoneHeader}>Sign Up</Text>
                        <View style={styles.miniPhoneInputBox} />
                        <View style={styles.miniPhoneInputBox} />
                        <View style={styles.miniPhoneInputBox} />
                        <View style={[styles.miniPhoneBtn, { marginTop: 6 }]}>
                          <Text style={styles.miniPhoneBtnText}>Register</Text>
                        </View>
                      </View>
                    </View>

                    {/* Mini Phone 3: Welcome Back */}
                    <View style={styles.miniPhoneFrame}>
                      <View style={styles.miniPhoneNotch} />
                      <View style={styles.miniPhoneScreen}>
                        <View style={styles.miniPhoneAvatarWrap}>
                          <Text style={{ fontSize: 18 }}>🧑‍🏫</Text>
                        </View>
                        <Text style={styles.miniPhoneHeader}>Welcome Back</Text>
                        <View style={styles.miniPhoneInputBox} />
                        <View style={[styles.miniPhoneBtn, { marginTop: 6 }]}>
                          <Text style={styles.miniPhoneBtnText}>Sign In</Text>
                        </View>
                        <View style={styles.miniPhoneSocialRow}>
                          <View style={styles.miniSocialDot} />
                          <View style={styles.miniSocialDot} />
                        </View>
                      </View>
                    </View>
                  </View>

                  {/* Showcase Controls (Expand & Refresh buttons from screenshot) */}
                  <View style={styles.showcaseControls}>
                    <TouchableOpacity
                      style={styles.showcaseIconBtn}
                      onPress={() => setShowShowcaseModal(true)}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.showcaseIconText}>⤢</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.showcaseIconBtn}
                      onPress={() => {
                        setCarouselIndex((prev) => (prev + 1) % showcaseSlides.length);
                      }}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.showcaseIconText}>🔄</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* 4. Caregiver Guides Card */}
                <TouchableOpacity
                  style={styles.featureCard}
                  onPress={() => {
                    setSelectedGuide(filteredGuides[0] || staticCaregiverGuides[0]);
                    setShowGuideModal(true);
                  }}
                  activeOpacity={0.88}
                >
                  <View style={styles.featureIconBadgeBlue}>
                    <Text style={styles.featureIconBlue}>📘</Text>
                  </View>
                  <View style={styles.featureTextWrapper}>
                    <Text style={styles.featureCardTitle}>Caregiver Guides</Text>
                    <Text style={styles.featureCardDesc}>
                      Step-by-step strategies for daily routines and unexpected challenges.
                    </Text>
                    {filteredGuides.length > 0 && searchQuery.length > 0 && (
                      <Text style={styles.filterMatchCount}>
                        {filteredGuides.length} guide{filteredGuides.length > 1 ? 's' : ''} matching "{searchQuery}"
                      </Text>
                    )}
                  </View>
                </TouchableOpacity>

                {/* 5. Community Forums Card */}
                <TouchableOpacity
                  style={styles.featureCard}
                  onPress={() => navigation?.navigate?.('CommunityFeed')}
                  activeOpacity={0.88}
                >
                  <View style={styles.featureIconBadgeLavender}>
                    <Text style={styles.featureIconLavender}>💬</Text>
                  </View>
                  <View style={styles.featureTextWrapper}>
                    <Text style={styles.featureCardTitle}>Community Forums</Text>
                    <Text style={styles.featureCardDesc}>
                      Connect with others who understand the journey.
                    </Text>
                  </View>
                </TouchableOpacity>

                {/* 6. Request Callback Card */}
                <TouchableOpacity
                  style={styles.featureCard}
                  onPress={() => {
                    setCallbackErrorMsg('');
                    setCallbackSuccessMsg('');
                    setShowCallbackModal(true);
                  }}
                  activeOpacity={0.88}
                >
                  <View style={styles.featureIconBadgeGreen}>
                    <Text style={styles.featureIconGreen}>📞</Text>
                  </View>
                  <View style={styles.featureTextWrapper}>
                    <Text style={styles.featureCardTitle}>Request Callback</Text>
                    <Text style={styles.featureCardDesc}>
                      Schedule a call with a trained support specialist.
                    </Text>
                  </View>
                  <View style={styles.featureArrowWrapper}>
                    <Text style={styles.featureBlueArrow}>→</Text>
                  </View>
                </TouchableOpacity>

                {/* 7. Emergency Contacts Section (Connected to Backend Hotlines API) */}
                <View style={styles.emergencyContainer}>
                  {/* Header Row */}
                  <View style={styles.emergencyHeaderRow}>
                    <Text style={styles.emergencyStarIcon}>✱</Text>
                    <Text style={styles.emergencyTitle}>Emergency Contacts</Text>
                  </View>

                  <Text style={styles.emergencyDesc}>
                    If you or someone you care for is in immediate danger, please reach out to these
                    critical resources immediately.
                  </Text>

                  {/* Hotlines Loading State */}
                  {loadingHotlines && (
                    <View style={styles.loadingInlineBox}>
                      <ActivityIndicator size="small" color="#DC2626" />
                      <Text style={styles.loadingInlineText}>Syncing emergency directory...</Text>
                    </View>
                  )}

                  {/* Hotlines Error State with Retry */}
                  {!loadingHotlines && hotlinesError && (
                    <View style={styles.hotlinesErrorBox}>
                      <Text style={styles.hotlinesErrorText}>{hotlinesError}</Text>
                      <TouchableOpacity
                        style={styles.hotlineRetryBtn}
                        onPress={loadSupportCenterData}
                      >
                        <Text style={styles.hotlineRetryBtnText}>Retry</Text>
                      </TouchableOpacity>
                    </View>
                  )}

                  {/* Hotlines Empty State */}
                  {!loadingHotlines && !hotlinesError && backendHotlines.length === 0 && (
                    <View style={styles.hotlinesEmptyBox}>
                      <Text style={styles.hotlinesEmptyText}>No emergency hotlines currently listed.</Text>
                    </View>
                  )}

                  {/* Dynamic Hotlines from Backend */}
                  {!loadingHotlines &&
                    !hotlinesError &&
                    backendHotlines.map((hotline, idx) => (
                      <View key={hotline.number + idx} style={styles.emergencySubCard}>
                        <View style={styles.emergencySubCardTextWrap}>
                          <Text style={styles.emergencySubCardTitle}>{hotline.label}</Text>
                          <Text style={styles.emergencySubCardSubtitle}>
                            {hotline.availability || 'Available 24/7'} • {hotline.number}
                          </Text>
                        </View>
                        <TouchableOpacity
                          style={
                            idx % 2 === 0
                              ? styles.emergencyCallBtnRed
                              : styles.emergencyActionBtnDark
                          }
                          onPress={() => handlePhoneDial(hotline.number)}
                          activeOpacity={0.8}
                        >
                          <Text
                            style={
                              idx % 2 === 0
                                ? styles.emergencyCallIconRed
                                : styles.emergencyActionIconDark
                            }
                          >
                            {idx % 2 === 0 ? '📞' : '🚨'}
                          </Text>
                        </TouchableOpacity>
                      </View>
                    ))}
                </View>

                {/* 8. Active Support Requests Section (Connected to Tickets & Calls Backend API) */}
                <View style={styles.ticketsSectionCard}>
                  <View style={styles.ticketsHeaderRow}>
                    <View>
                      <Text style={styles.sectionHeaderTitle}>Active Support Requests</Text>
                      <Text style={styles.sectionHeaderSub}>
                        Track inquiries and scheduled callbacks submitted to support specialists
                      </Text>
                    </View>
                    <TouchableOpacity
                      style={styles.newTicketPillBtn}
                      onPress={() => {
                        setTicketErrorMsg('');
                        setTicketSuccessMsg('');
                        setShowTicketModal(true);
                      }}
                      activeOpacity={0.8}
                    >
                      <Text style={styles.newTicketPillText}>+ New Inquiry</Text>
                    </TouchableOpacity>
                  </View>

                  {/* Loading State */}
                  {loadingRequests && (
                    <View style={styles.loadingBox}>
                      <ActivityIndicator size="small" color="#2563EB" />
                      <Text style={styles.loadingText}>Fetching active support requests from backend...</Text>
                    </View>
                  )}

                  {/* Error State with Retry */}
                  {!loadingRequests && requestsError && (
                    <View style={styles.errorBox}>
                      <Text style={styles.errorText}>{requestsError}</Text>
                      <TouchableOpacity
                        style={styles.retryBtn}
                        onPress={loadSupportCenterData}
                        activeOpacity={0.8}
                      >
                        <Text style={styles.retryBtnText}>Retry Sync</Text>
                      </TouchableOpacity>
                    </View>
                  )}

                  {/* Empty State: "No active support requests." */}
                  {!loadingRequests && !requestsError && combinedSupportRequests.length === 0 && (
                    <View style={styles.emptyTicketsBox}>
                      <Text style={styles.emptyTicketsIcon}>📋</Text>
                      <Text style={styles.emptyTicketsTitle}>No active support requests.</Text>
                      <Text style={styles.emptyTicketsSub}>
                        You currently have no open inquiries or scheduled callbacks. Need assistance?
                        Schedule a callback or submit an inquiry above.
                      </Text>
                    </View>
                  )}

                  {/* Combined List of Tickets and Scheduled Calls */}
                  {!loadingRequests &&
                    !requestsError &&
                    combinedSupportRequests.map((req, idx) => (
                      <View key={req.id || idx} style={styles.ticketItemCard}>
                        <View style={styles.ticketItemTopRow}>
                          <View style={styles.ticketTypeBadgeRow}>
                            <Text style={styles.ticketTypeIcon}>{req.icon}</Text>
                            <Text style={styles.ticketSubject} numberOfLines={1}>
                              {req.title}
                            </Text>
                          </View>
                          <View
                            style={[
                              styles.ticketStatusBadge,
                              req.status === 'resolved' || req.status === 'completed'
                                ? styles.statusBadgeResolved
                                : req.status === 'in_progress'
                                ? styles.statusBadgeProgress
                                : req.status === 'scheduled'
                                ? styles.statusBadgeScheduled
                                : styles.statusBadgeOpen,
                            ]}
                          >
                            <Text
                              style={[
                                styles.ticketStatusText,
                                req.status === 'resolved' || req.status === 'completed'
                                  ? styles.statusTextResolved
                                  : req.status === 'in_progress'
                                  ? styles.statusTextProgress
                                  : req.status === 'scheduled'
                                  ? styles.statusTextScheduled
                                  : styles.statusTextOpen,
                              ]}
                            >
                              {(req.status || 'Open').toUpperCase()}
                            </Text>
                          </View>
                        </View>
                        <Text style={styles.ticketCategory}>
                          {req.type} {req.ticket_number ? `• ${req.ticket_number}` : ''} •{' '}
                          {req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Recent'}
                          {req.scheduled_time ? ` • Scheduled: ${req.scheduled_time}` : ''}
                        </Text>
                        <Text style={styles.ticketDescription} numberOfLines={2}>
                          {req.details}
                        </Text>
                      </View>
                    ))}
                </View>
              </View>

              {/* Secondary Column (Desktop Viewport: Direct Line, PIN, Hours, Toll-Free) */}
              {isDesktop && (
                <View style={styles.secondaryColumnDesktop}>
                  {/* Direct Phone Support Card */}
                  <View style={styles.desktopSideCard}>
                    <View style={styles.sideCardHeaderRow}>
                      <View style={styles.sideCardIconBox}>
                        <Text style={{ fontSize: 20 }}>🎧</Text>
                      </View>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.sideCardTitle}>Direct Specialist Line</Text>
                        <Text style={styles.sideCardSub}>Immediate live voice support</Text>
                      </View>
                    </View>

                    {/* Support PIN Card */}
                    <View style={styles.supportPinCard}>
                      <View>
                        <Text style={styles.pinLabel}>YOUR SUPPORT PIN</Text>
                        <Text style={styles.pinValue}>{supportPin}</Text>
                      </View>
                      <TouchableOpacity
                        style={styles.copyPinBtn}
                        onPress={copyPinToClipboard}
                        activeOpacity={0.7}
                      >
                        <Text style={styles.copyPinIcon}>📋</Text>
                      </TouchableOpacity>
                    </View>

                    {/* Call Launcher Button */}
                    <TouchableOpacity
                      style={styles.callPrimaryButton}
                      onPress={() =>
                        handleStartCall({
                          name: 'Sarah J.',
                          role: 'Senior Caregiver Specialist',
                          number: hotlinesData?.emergency_hotline || '1-800-CAREGIVER',
                        })
                      }
                      activeOpacity={0.88}
                    >
                      <Text style={styles.callPrimaryIcon}>📞</Text>
                      <Text style={styles.callPrimaryText}>
                        Call {hotlinesData?.emergency_hotline || '1-800-CAREGIVER'}
                      </Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.requestCallbackSecondaryBtn}
                      onPress={() => {
                        setCallbackErrorMsg('');
                        setCallbackSuccessMsg('');
                        setShowCallbackModal(true);
                      }}
                      activeOpacity={0.85}
                    >
                      <Text style={styles.requestCallbackSecondaryText}>📅 Schedule Callback</Text>
                    </TouchableOpacity>
                  </View>

                  {/* Operating Hours Card (from backend or fallback) */}
                  <View style={styles.desktopSideCard}>
                    <View style={styles.sideCardHeaderRow}>
                      <Text style={styles.sideCardHeaderIcon}>🕒</Text>
                      <Text style={styles.sideCardTitle}>Operating Hours</Text>
                    </View>

                    <View style={styles.hoursRow}>
                      <Text style={styles.hoursDay}>Monday - Friday</Text>
                      <Text style={styles.hoursTime}>9:00 AM - 5:00 PM EST</Text>
                    </View>
                    <View style={styles.hoursRow}>
                      <Text style={styles.hoursDay}>Saturday</Text>
                      <Text style={styles.hoursTime}>10:00 AM - 2:00 PM EST</Text>
                    </View>
                    <View style={[styles.hoursRow, { borderBottomWidth: 0 }]}>
                      <Text style={styles.hoursDay}>Sunday & Crisis</Text>
                      <Text style={styles.hoursTimeActive}>24/7 Automated & Crisis</Text>
                    </View>
                  </View>

                  {/* Global Toll-Free Lines (from backend hotlinesData) */}
                  <View style={styles.desktopSideCard}>
                    <View style={styles.sideCardHeaderRow}>
                      <Text style={styles.sideCardHeaderIcon}>🌐</Text>
                      <Text style={styles.sideCardTitle}>Global Support Directory</Text>
                    </View>

                    {tollFreeHotlines.length > 0 ? (
                      tollFreeHotlines.map((item, idx) => (
                        <TouchableOpacity
                          key={item.number + idx}
                          style={[
                            styles.tollRow,
                            idx === tollFreeHotlines.length - 1 && { borderBottomWidth: 0 },
                          ]}
                          onPress={() => handlePhoneDial(item.number)}
                          activeOpacity={0.7}
                        >
                          <Text style={styles.tollLabel}>{item.label.toUpperCase()}</Text>
                          <Text style={styles.tollNumber}>{item.number}</Text>
                        </TouchableOpacity>
                      ))
                    ) : (
                      <TouchableOpacity
                        style={[styles.tollRow, { borderBottomWidth: 0 }]}
                        onPress={() => handlePhoneDial('1-800-CAREGIVER')}
                        activeOpacity={0.7}
                      >
                        <Text style={styles.tollLabel}>US & CANADA SUPPORT</Text>
                        <Text style={styles.tollNumber}>1-800-CAREGIVER</Text>
                      </TouchableOpacity>
                    )}
                  </View>
                </View>
              )}
            </View>

            {/* Desktop / Tablet Footer */}
            {isDesktop && (
              <View style={styles.desktopFooter}>
                <Text style={styles.footerCopyright}>
                  © 2026 NIVARA Caregiver Ecosystem. Safe, confidential & accessible support.
                </Text>
                <View style={styles.footerLinksRow}>
                  <TouchableOpacity onPress={() => navigation?.navigate?.('SafetyPrivacyCenter')}>
                    <Text style={styles.footerLink}>Privacy Policy</Text>
                  </TouchableOpacity>
                  <TouchableOpacity onPress={() => navigation?.navigate?.('SafetyPrivacyCenter')}>
                    <Text style={styles.footerLink}>Safety Guidelines</Text>
                  </TouchableOpacity>
                  <TouchableOpacity onPress={() => handleStartCall()}>
                    <Text style={styles.footerLink}>Help Desk</Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}
          </ScrollView>

          {/* Bottom Tab Navigation Bar (Mobile / Tablet - HIGHLIGHTED SUPPORT TAB) */}
          {!isDesktop && (
            <View style={styles.bottomTabBar}>
              {/* 1. Home */}
              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('CommunityHome')}
                activeOpacity={0.7}
              >
                <Text style={styles.tabIcon}>🏠</Text>
                <Text style={styles.tabLabel}>Home</Text>
              </TouchableOpacity>

              {/* 2. Community */}
              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('CommunityFeed')}
                activeOpacity={0.7}
              >
                <Text style={styles.tabIcon}>👥</Text>
                <Text style={styles.tabLabel}>Community</Text>
              </TouchableOpacity>

              {/* 3. Messages */}
              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('ChatList')}
                activeOpacity={0.7}
              >
                <Text style={styles.tabIcon}>💬</Text>
                <Text style={styles.tabLabel}>Messages</Text>
              </TouchableOpacity>

              {/* 4. Support (ACTIVE & HIGHLIGHTED - Exact match to screenshot) */}
              <TouchableOpacity style={styles.tabItemActive} activeOpacity={0.9}>
                <View style={styles.activeTabPill}>
                  <Text style={styles.activeTabIcon}>🛡️</Text>
                </View>
                <Text style={styles.activeTabLabel}>Support</Text>
              </TouchableOpacity>

              {/* 5. Profile */}
              <TouchableOpacity
                style={styles.tabItem}
                onPress={() => navigation?.navigate?.('CaregiverProfile', { userId: user?.id })}
                activeOpacity={0.7}
              >
                <Text style={styles.tabIcon}>👤</Text>
                <Text style={styles.tabLabel}>Profile</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </View>

      {/* ========================================================================= */}
      {/* MODALS */}
      {/* ========================================================================= */}

      {/* 1. Callback Scheduling Modal (Connected to backend POST /api/v1/support/calls/schedule) */}
      <Modal
        visible={showCallbackModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowCallbackModal(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeaderRow}>
              <Text style={styles.modalTitle}>Request a Callback</Text>
              <TouchableOpacity onPress={() => setShowCallbackModal(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.modalSubtitle}>
              Select your preferred date and time. A certified support specialist will reach out to you.
            </Text>

            {/* Success Message Banner */}
            {callbackSuccessMsg.length > 0 && (
              <View style={styles.modalSuccessBanner}>
                <Text style={styles.modalSuccessBannerText}>{callbackSuccessMsg}</Text>
              </View>
            )}

            {/* Error Message Banner */}
            {callbackErrorMsg.length > 0 && (
              <View style={styles.modalErrorBanner}>
                <Text style={styles.modalErrorBannerText}>{callbackErrorMsg}</Text>
              </View>
            )}

            {/* Date Selection */}
            <Text style={styles.inputLabel}>Select Date:</Text>
            <View style={styles.categoryPillsRow}>
              {['Today', 'Tomorrow', 'This Week'].map((d) => (
                <TouchableOpacity
                  key={d}
                  style={[styles.categoryPill, callbackDate === d && styles.categoryPillSelected]}
                  onPress={() => setCallbackDate(d)}
                >
                  <Text
                    style={[
                      styles.categoryPillText,
                      callbackDate === d && styles.categoryPillTextSelected,
                    ]}
                  >
                    {d}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Time Slot Selection */}
            <Text style={[styles.inputLabel, { marginTop: 8 }]}>Select Available Time:</Text>
            {['2:30 PM', '4:00 PM', '10:00 AM', '1:30 PM', '5:00 PM'].map((slot) => (
              <TouchableOpacity
                key={slot}
                style={[styles.slotOption, callbackTime === slot && styles.slotOptionSelected]}
                onPress={() => setCallbackTime(slot)}
                activeOpacity={0.8}
              >
                <Text style={[styles.slotText, callbackTime === slot && styles.slotTextSelected]}>
                  {slot}
                </Text>
                {callbackTime === slot && <Text style={styles.slotCheckmark}>✓</Text>}
              </TouchableOpacity>
            ))}

            {/* Phone Number Input */}
            <Text style={[styles.inputLabel, { marginTop: 10 }]}>Contact Phone Number (Optional):</Text>
            <TextInput
              style={styles.modalTextInput}
              placeholder="+1 (555) 000-0000"
              placeholderTextColor="#94A3B8"
              value={callbackPhone}
              onChangeText={setCallbackPhone}
              keyboardType="phone-pad"
            />

            <View style={styles.modalActionRow}>
              <TouchableOpacity
                style={styles.modalCancelBtn}
                onPress={() => setShowCallbackModal(false)}
                disabled={bookingCallback}
              >
                <Text style={styles.modalCancelBtnText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.modalConfirmBtn}
                onPress={handleConfirmCallback}
                disabled={bookingCallback}
              >
                {bookingCallback ? (
                  <ActivityIndicator color="#FFFFFF" size="small" />
                ) : (
                  <Text style={styles.modalConfirmBtnText}>Confirm Callback</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* 2. Caregiver Guides Modal */}
      <Modal
        visible={showGuideModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowGuideModal(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={[styles.modalCard, { maxHeight: '85%' }]}>
            <View style={styles.modalHeaderRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.modalTitle}>{selectedGuide?.title || 'Caregiver Guide'}</Text>
                <Text style={styles.modalBadgeText}>{selectedGuide?.badge || 'Practical Strategy'}</Text>
              </View>
              <TouchableOpacity onPress={() => setShowGuideModal(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false} style={{ marginVertical: 12 }}>
              <Text style={styles.guideModalDesc}>{selectedGuide?.description}</Text>

              <Text style={[styles.inputLabel, { marginTop: 14, marginBottom: 8 }]}>
                Actionable Recommendations:
              </Text>
              {selectedGuide?.tips?.map((tip, idx) => (
                <View key={idx} style={styles.guideTipRow}>
                  <Text style={styles.guideTipBullet}>•</Text>
                  <Text style={styles.guideTipText}>{tip}</Text>
                </View>
              ))}

              <View style={styles.guideNoticeBox}>
                <Text style={styles.guideNoticeText}>
                  💡 Tip: Need personalized guidance? You can request a callback with a support
                  specialist at any time.
                </Text>
              </View>
            </ScrollView>

            <TouchableOpacity
              style={styles.modalConfirmBtn}
              onPress={() => setShowGuideModal(false)}
            >
              <Text style={styles.modalConfirmBtnText}>Done</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* 3. New Ticket Modal (Connected to backend POST /api/v1/support/tickets) */}
      <Modal
        visible={showTicketModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowTicketModal(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeaderRow}>
              <Text style={styles.modalTitle}>Submit Support Inquiry</Text>
              <TouchableOpacity onPress={() => setShowTicketModal(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.modalSubtitle}>
              Our caregiver support specialists will review your inquiry and follow up within 2 hours.
            </Text>

            {/* Success Message Banner */}
            {ticketSuccessMsg.length > 0 && (
              <View style={styles.modalSuccessBanner}>
                <Text style={styles.modalSuccessBannerText}>{ticketSuccessMsg}</Text>
              </View>
            )}

            {/* Error Message Banner */}
            {ticketErrorMsg.length > 0 && (
              <View style={styles.modalErrorBanner}>
                <Text style={styles.modalErrorBannerText}>{ticketErrorMsg}</Text>
              </View>
            )}

            <Text style={styles.inputLabel}>Subject / Topic:</Text>
            <TextInput
              style={styles.modalTextInput}
              placeholder="e.g. Assistance with sensory routines"
              placeholderTextColor="#94A3B8"
              value={ticketSubject}
              onChangeText={setTicketSubject}
            />

            <Text style={[styles.inputLabel, { marginTop: 10 }]}>Category:</Text>
            <View style={styles.categoryPillsRow}>
              {['Caregiver Support', 'Verification', 'App Question', 'Other'].map((cat) => (
                <TouchableOpacity
                  key={cat}
                  style={[
                    styles.categoryPill,
                    ticketCategory === cat && styles.categoryPillSelected,
                  ]}
                  onPress={() => setTicketCategory(cat)}
                >
                  <Text
                    style={[
                      styles.categoryPillText,
                      ticketCategory === cat && styles.categoryPillTextSelected,
                    ]}
                  >
                    {cat}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={[styles.inputLabel, { marginTop: 10 }]}>Details:</Text>
            <TextInput
              style={[styles.modalTextInput, styles.modalTextArea]}
              placeholder="Describe your question or the support you need..."
              placeholderTextColor="#94A3B8"
              multiline
              numberOfLines={4}
              value={ticketDesc}
              onChangeText={setTicketDesc}
            />

            <View style={styles.modalActionRow}>
              <TouchableOpacity
                style={styles.modalCancelBtn}
                onPress={() => setShowTicketModal(false)}
                disabled={submittingTicket}
              >
                <Text style={styles.modalCancelBtnText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.modalConfirmBtn}
                onPress={handleCreateTicket}
                disabled={submittingTicket}
              >
                {submittingTicket ? (
                  <ActivityIndicator color="#FFFFFF" size="small" />
                ) : (
                  <Text style={styles.modalConfirmBtnText}>Submit Inquiry</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* 4. Live Voice Call Simulator Modal */}
      <Modal
        visible={callState !== 'idle'}
        transparent={true}
        animationType="fade"
        onRequestClose={handleEndCall}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.callModalContainer}>
            <View style={styles.callAvatarWrap}>
              <Text style={{ fontSize: 36 }}>👩‍💼</Text>
            </View>
            <Text style={styles.callSpecialistName}>
              {activeCallContact?.name || 'Sarah J.'}
            </Text>
            <Text style={styles.callSpecialistRole}>
              {activeCallContact?.role || 'Senior Caregiver Support Specialist'}
            </Text>

            {callState === 'calling' && (
              <View style={styles.callStatusBox}>
                <Text style={styles.callingText}>Connecting to specialist...</Text>
                <Text style={styles.callingSubtext}>
                  Ringing ({activeCallContact?.number || hotlinesData?.emergency_hotline || '1-800-CAREGIVER'})
                </Text>
              </View>
            )}

            {callState === 'connected' && (
              <View style={styles.callStatusBox}>
                <Text style={styles.connectedBadge}>● LIVE VOICE CALL</Text>
                <Text style={styles.callTimerText}>{formatTimer(callDuration)}</Text>
                <View style={styles.waveformContainer}>
                  <View style={[styles.waveBar, { height: 16 }]} />
                  <View style={[styles.waveBar, { height: 28 }]} />
                  <View style={[styles.waveBar, { height: 20 }]} />
                  <View style={[styles.waveBar, { height: 32 }]} />
                  <View style={[styles.waveBar, { height: 18 }]} />
                </View>
              </View>
            )}

            {callState === 'ended' && (
              <View style={styles.callStatusBox}>
                <Text style={styles.endedText}>Call Ended</Text>
                <Text style={styles.callingSubtext}>Thank you for contacting NIVARA Support!</Text>
              </View>
            )}

            {callState === 'connected' && (
              <View style={styles.callControlsRow}>
                <TouchableOpacity
                  style={[styles.controlButton, isMuted && styles.controlButtonActive]}
                  onPress={() => setIsMuted(!isMuted)}
                >
                  <Text style={styles.controlIcon}>{isMuted ? '🔇' : '🎙️'}</Text>
                  <Text style={styles.controlLabel}>{isMuted ? 'Muted' : 'Mute'}</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.controlButton, isSpeaker && styles.controlButtonActive]}
                  onPress={() => setIsSpeaker(!isSpeaker)}
                >
                  <Text style={styles.controlIcon}>🔊</Text>
                  <Text style={styles.controlLabel}>Speaker</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.endCallButton} onPress={handleEndCall}>
                  <Text style={styles.endCallIcon}>📞</Text>
                  <Text style={styles.endCallText}>End Call</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      </Modal>

      {/* 5. Showcase Enlarged Preview Modal */}
      <Modal
        visible={showShowcaseModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowShowcaseModal(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeaderRow}>
              <Text style={styles.modalTitle}>NIVARA Caregiver Suite</Text>
              <TouchableOpacity onPress={() => setShowShowcaseModal(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.modalSubtitle}>
              Experience seamless care navigation with step-by-step guides, live specialists, and
              community moderation.
            </Text>

            <View style={styles.showcaseModalSlideWrap}>
              <Text style={{ fontSize: 48, alignSelf: 'center', marginBottom: 12 }}>
                {showcaseSlides[carouselIndex].illustration}
              </Text>
              <Text style={styles.showcaseModalSlideTitle}>
                {showcaseSlides[carouselIndex].title}
              </Text>
              <Text style={styles.showcaseModalSlideTag}>
                {showcaseSlides[carouselIndex].tagline}
              </Text>
              <Text style={styles.showcaseModalSlideSub}>
                {showcaseSlides[carouselIndex].sub}
              </Text>
            </View>

            <View style={styles.carouselDotsRow}>
              {showcaseSlides.map((slide, i) => (
                <TouchableOpacity
                  key={slide.id}
                  style={[styles.carouselDot, carouselIndex === i && styles.carouselDotActive]}
                  onPress={() => setCarouselIndex(i)}
                />
              ))}
            </View>

            <TouchableOpacity
              style={styles.modalConfirmBtn}
              onPress={() => setShowShowcaseModal(false)}
            >
              <Text style={styles.modalConfirmBtnText}>Close Preview</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },

  /* Top Banner Bar */
  topBannerBar: {
    height: 54,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    zIndex: 10,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  backArrow: {
    fontSize: 16,
    color: '#2563EB',
    marginRight: 6,
    fontWeight: '700',
  },
  backTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
  },
  topNavbarTabs: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  topTabPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
    backgroundColor: '#F8FAFC',
  },
  topTabPillActive: {
    backgroundColor: '#F1F5F9',
  },
  topTabPillActivePrimary: {
    backgroundColor: '#2563EB',
  },
  topTabIcon: {
    fontSize: 13,
    marginRight: 6,
  },
  topTabIconPrimary: {
    fontSize: 13,
    marginRight: 6,
    color: '#FFFFFF',
  },
  topTabText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#475569',
  },
  topTabTextActive: {
    color: '#0F172A',
    fontWeight: '700',
  },
  topTabTextActivePrimary: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 12,
  },

  /* App Container & Sidebar */
  appContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
  },
  sidebar: {
    width: 260,
    backgroundColor: '#FFFFFF',
    borderRightWidth: 1,
    borderRightColor: '#E2E8F0',
    justifyContent: 'space-between',
    position: 'relative',
    overflow: 'hidden',
  },
  sidebarTopContent: {
    paddingVertical: 24,
    paddingHorizontal: 18,
    zIndex: 2,
  },
  brandContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 28,
  },
  brandLogoBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  brandLogoIcon: {
    fontSize: 20,
    color: '#FFFFFF',
    fontWeight: '900',
  },
  brandTextWrapper: {
    flex: 1,
  },
  brandTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
    letterSpacing: 1.5,
  },
  verificationBadge: {
    backgroundColor: '#EFF6FF',
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: 6,
    alignSelf: 'flex-start',
    marginTop: 2,
  },
  verificationBadgeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#2563EB',
  },
  menuContainer: {
    gap: 6,
  },
  navItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 10,
  },
  navItemActive: {
    backgroundColor: '#F1F5F9',
  },
  navItemActivePrimary: {
    backgroundColor: '#EFF6FF',
    borderLeftWidth: 3,
    borderLeftColor: '#2563EB',
  },
  navIcon: {
    fontSize: 16,
    marginRight: 10,
  },
  navIconPrimary: {
    fontSize: 16,
    marginRight: 10,
    color: '#2563EB',
  },
  navText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
  },
  navTextActivePrimary: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
  },
  sidebarBottomNav: {
    marginTop: 32,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    gap: 4,
  },
  sidebarBgGraphicWrapper: {
    position: 'absolute',
    bottom: -30,
    right: -30,
    opacity: 0.08,
  },
  sidebarDecoCircle: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#2563EB',
  },

  /* Main Workspace */
  mainContent: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },

  /* Mobile Top Header (Exact Screenshot Match) */
  mobileHeader: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  mobileAvatarBtn: {
    padding: 2,
  },
  mobileAvatarCircle: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#EFF6FF',
    borderWidth: 1.5,
    borderColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mobileAvatarEmoji: {
    fontSize: 20,
  },
  mobileBrandTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1E3A8A',
    letterSpacing: 2,
  },
  mobileNotificationBtn: {
    width: 38,
    height: 38,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  mobileNotificationIcon: {
    fontSize: 20,
    color: '#475569',
  },
  notificationDot: {
    position: 'absolute',
    top: 6,
    right: 8,
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: '#EF4444',
  },

  /* Desktop Top Header */
  desktopTopHeader: {
    height: 70,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 32,
  },
  desktopPageTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0F172A',
  },
  desktopPageSubtitle: {
    fontSize: 13,
    color: '#64748B',
    marginTop: 2,
  },
  desktopHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  headerActionPillText: {
    backgroundColor: '#2563EB',
    color: '#FFFFFF',
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 20,
    fontSize: 13,
    fontWeight: '700',
  },
  headerCallbackPillText: {
    backgroundColor: '#EFF6FF',
    color: '#2563EB',
    borderWidth: 1,
    borderColor: '#BFDBFE',
    paddingVertical: 7,
    paddingHorizontal: 14,
    borderRadius: 20,
    fontSize: 13,
    fontWeight: '700',
  },
  headerIconButton: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  headerIconText: {
    fontSize: 16,
  },
  userProfileAvatar: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  userAvatarText: {
    fontSize: 15,
    fontWeight: '800',
    color: '#FFFFFF',
  },

  /* Scrollable Canvas */
  scrollCanvas: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  scrollCanvasContent: {
    padding: 32,
    paddingBottom: 48,
  },
  scrollCanvasMobileContent: {
    paddingHorizontal: 18,
    paddingTop: 16,
    paddingBottom: 24,
  },
  layoutWrapper: {
    width: '100%',
  },
  layoutWrapperDesktop: {
    flexDirection: 'row',
    gap: 28,
    alignItems: 'flex-start',
  },
  primaryColumn: {
    width: '100%',
  },
  primaryColumnDesktop: {
    flex: 1,
  },
  secondaryColumnDesktop: {
    width: 340,
    gap: 20,
  },

  /* 1. Hero Title & Subtitle */
  heroSection: {
    alignItems: 'center',
    marginBottom: 18,
    paddingHorizontal: 10,
  },
  heroTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0F172A',
    textAlign: 'center',
    lineHeight: 30,
    letterSpacing: -0.4,
  },
  heroSubtitle: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
    maxWidth: 380,
  },

  /* 2. Search Bar */
  searchBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 14,
    paddingHorizontal: 14,
    height: 48,
    marginBottom: 18,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
    elevation: 1,
  },
  searchBarIcon: {
    fontSize: 16,
    color: '#64748B',
    marginRight: 10,
  },
  searchBarInput: {
    flex: 1,
    fontSize: 14,
    color: '#0F172A',
    paddingVertical: 0,
  },
  clearSearchBtn: {
    padding: 4,
  },
  clearSearchText: {
    fontSize: 14,
    color: '#94A3B8',
  },

  /* 3. Showcase Carousel Card (3 Phones) */
  showcaseCard: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 18,
    padding: 16,
    marginBottom: 16,
    position: 'relative',
    overflow: 'hidden',
  },
  showcasePhonesRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 6,
  },
  miniPhoneFrame: {
    width: 96,
    height: 156,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#E2E8F0',
    padding: 6,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
    alignItems: 'center',
    overflow: 'hidden',
  },
  miniPhoneFrameCenter: {
    transform: [{ scale: 1.04 }],
    borderColor: '#CBD5E1',
  },
  miniPhoneNotch: {
    width: 24,
    height: 3,
    borderRadius: 2,
    backgroundColor: '#CBD5E1',
    marginBottom: 6,
  },
  miniPhoneScreen: {
    flex: 1,
    width: '100%',
    alignItems: 'center',
  },
  miniPhoneAvatarWrap: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  miniPhoneTitle: {
    fontSize: 8,
    fontWeight: '800',
    color: '#0F172A',
    textAlign: 'center',
    lineHeight: 10,
  },
  miniPhoneDesc: {
    fontSize: 6,
    color: '#64748B',
    textAlign: 'center',
    marginTop: 2,
    lineHeight: 8,
  },
  miniPhoneHeader: {
    fontSize: 9,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  miniPhoneInputBox: {
    width: '90%',
    height: 10,
    backgroundColor: '#F1F5F9',
    borderRadius: 3,
    marginBottom: 4,
    borderWidth: 0.5,
    borderColor: '#E2E8F0',
  },
  miniPhoneBtn: {
    width: '90%',
    height: 14,
    backgroundColor: '#2563EB',
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 2,
  },
  miniPhoneBtnText: {
    fontSize: 6,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  miniPhoneSocialRow: {
    flexDirection: 'row',
    gap: 4,
    marginTop: 6,
  },
  miniSocialDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#E2E8F0',
  },
  showcaseControls: {
    position: 'absolute',
    bottom: 10,
    right: 12,
    flexDirection: 'row',
    gap: 8,
  },
  showcaseIconBtn: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 1,
  },
  showcaseIconText: {
    fontSize: 13,
    color: '#475569',
    fontWeight: '700',
  },

  /* 4, 5, 6. Feature Action Cards */
  featureCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#F1F5F9',
    borderRadius: 18,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
  },
  featureIconBadgeBlue: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  featureIconBlue: {
    fontSize: 20,
  },
  featureIconBadgeLavender: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  featureIconLavender: {
    fontSize: 20,
  },
  featureIconBadgeGreen: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#ECFDF5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  featureIconGreen: {
    fontSize: 20,
  },
  featureTextWrapper: {
    flex: 1,
  },
  featureCardTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 3,
  },
  featureCardDesc: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 18,
  },
  filterMatchCount: {
    fontSize: 11,
    color: '#2563EB',
    fontWeight: '700',
    marginTop: 4,
  },
  featureArrowWrapper: {
    paddingLeft: 8,
  },
  featureBlueArrow: {
    fontSize: 20,
    fontWeight: '800',
    color: '#2563EB',
  },

  /* 7. Emergency Contacts Section */
  emergencyContainer: {
    backgroundColor: '#FFF5F5',
    borderWidth: 1,
    borderColor: '#FEE2E2',
    borderRadius: 18,
    padding: 18,
    marginBottom: 18,
  },
  emergencyHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  emergencyStarIcon: {
    fontSize: 20,
    color: '#DC2626',
    marginRight: 8,
    fontWeight: '900',
  },
  emergencyTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#991B1B',
  },
  emergencyDesc: {
    fontSize: 13,
    color: '#7F1D1D',
    lineHeight: 18,
    marginBottom: 14,
  },
  loadingInlineBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 14,
  },
  loadingInlineText: {
    fontSize: 13,
    color: '#991B1B',
    fontWeight: '600',
  },
  hotlinesErrorBox: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#FECACA',
    alignItems: 'center',
    marginBottom: 10,
  },
  hotlinesErrorText: {
    fontSize: 13,
    color: '#DC2626',
    marginBottom: 6,
  },
  hotlineRetryBtn: {
    backgroundColor: '#DC2626',
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 6,
  },
  hotlineRetryBtnText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '700',
  },
  hotlinesEmptyBox: {
    paddingVertical: 14,
    alignItems: 'center',
  },
  hotlinesEmptyText: {
    fontSize: 13,
    color: '#7F1D1D',
    fontStyle: 'italic',
  },
  emergencySubCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#FECACA',
    borderRadius: 14,
    paddingVertical: 12,
    paddingHorizontal: 14,
    marginBottom: 10,
    shadowColor: '#991B1B',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 2,
    elevation: 1,
  },
  emergencySubCardTextWrap: {
    flex: 1,
  },
  emergencySubCardTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  emergencySubCardSubtitle: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  emergencyCallBtnRed: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#FEE2E2',
    justifyContent: 'center',
    alignItems: 'center',
  },
  emergencyCallIconRed: {
    fontSize: 16,
    color: '#DC2626',
  },
  emergencyActionBtnDark: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
  },
  emergencyActionIconDark: {
    fontSize: 16,
    color: '#FFFFFF',
  },

  /* 8. Tickets & Requests Section */
  ticketsSectionCard: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 18,
    padding: 18,
    marginBottom: 20,
  },
  ticketsHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  sectionHeaderTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
  },
  sectionHeaderSub: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  newTicketPillBtn: {
    backgroundColor: '#EFF6FF',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  newTicketPillText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
  },
  loadingBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    gap: 8,
  },
  loadingText: {
    fontSize: 13,
    color: '#64748B',
  },
  errorBox: {
    backgroundColor: '#FEF2F2',
    borderRadius: 10,
    padding: 12,
    alignItems: 'center',
    marginVertical: 6,
  },
  errorText: {
    fontSize: 13,
    color: '#DC2626',
    marginBottom: 8,
  },
  retryBtn: {
    backgroundColor: '#DC2626',
    paddingVertical: 5,
    paddingHorizontal: 12,
    borderRadius: 6,
  },
  retryBtnText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '700',
  },
  emptyTicketsBox: {
    alignItems: 'center',
    paddingVertical: 24,
    paddingHorizontal: 16,
  },
  emptyTicketsIcon: {
    fontSize: 28,
    marginBottom: 6,
    color: '#94A3B8',
  },
  emptyTicketsTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 4,
  },
  emptyTicketsSub: {
    fontSize: 12,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 16,
  },
  ticketItemCard: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
  },
  ticketItemTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  ticketTypeBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 8,
  },
  ticketTypeIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  ticketSubject: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
    flex: 1,
  },
  ticketStatusBadge: {
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  statusBadgeOpen: {
    backgroundColor: '#FEF3C7',
  },
  statusBadgeProgress: {
    backgroundColor: '#EFF6FF',
  },
  statusBadgeScheduled: {
    backgroundColor: '#ECFDF5',
  },
  statusBadgeResolved: {
    backgroundColor: '#F1F5F9',
  },
  ticketStatusText: {
    fontSize: 10,
    fontWeight: '800',
  },
  statusTextOpen: {
    color: '#D97706',
  },
  statusTextProgress: {
    color: '#2563EB',
  },
  statusTextScheduled: {
    color: '#059669',
  },
  statusTextResolved: {
    color: '#64748B',
  },
  ticketCategory: {
    fontSize: 11,
    color: '#64748B',
    marginBottom: 6,
  },
  ticketDescription: {
    fontSize: 12,
    color: '#334155',
    lineHeight: 16,
  },

  /* Desktop Secondary Column Cards */
  desktopSideCard: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 18,
    padding: 20,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 3,
    elevation: 1,
  },
  sideCardHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  sideCardHeaderIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  sideCardIconBox: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  sideCardTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0F172A',
  },
  sideCardSub: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  supportPinCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    padding: 12,
    marginVertical: 12,
  },
  pinLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.5,
  },
  pinValue: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0F172A',
    letterSpacing: 2,
    marginTop: 2,
  },
  copyPinBtn: {
    padding: 6,
  },
  copyPinIcon: {
    fontSize: 18,
  },
  callPrimaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2563EB',
    borderRadius: 12,
    paddingVertical: 12,
    gap: 8,
    marginTop: 4,
  },
  callPrimaryIcon: {
    fontSize: 16,
    color: '#FFFFFF',
  },
  callPrimaryText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  requestCallbackSecondaryBtn: {
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#BFDBFE',
    borderRadius: 12,
    paddingVertical: 10,
    marginTop: 8,
  },
  requestCallbackSecondaryText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#2563EB',
  },
  hoursRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  hoursDay: {
    fontSize: 13,
    color: '#475569',
  },
  hoursTime: {
    fontSize: 13,
    fontWeight: '600',
    color: '#0F172A',
  },
  hoursTimeActive: {
    fontSize: 13,
    fontWeight: '700',
    color: '#059669',
  },
  tollRow: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  tollLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
  },
  tollNumber: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
    marginTop: 2,
  },

  /* Desktop Footer */
  desktopFooter: {
    marginTop: 40,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  footerCopyright: {
    fontSize: 12,
    color: '#94A3B8',
  },
  footerLinksRow: {
    flexDirection: 'row',
    gap: 16,
  },
  footerLink: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },

  /* Bottom Tab Bar (Mobile / Tablet) */
  bottomTabBar: {
    height: 64,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 8,
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 4,
    flex: 1,
  },
  tabItemActive: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 4,
    flex: 1,
  },
  tabIcon: {
    fontSize: 18,
    color: '#64748B',
    marginBottom: 2,
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
  },
  activeTabPill: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 16,
    paddingVertical: 3,
    borderRadius: 14,
    marginBottom: 2,
  },
  activeTabIcon: {
    fontSize: 16,
    color: '#2563EB',
  },
  activeTabLabel: {
    fontSize: 11,
    fontWeight: '800',
    color: '#2563EB',
  },

  /* Modals */
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.65)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalCard: {
    width: '100%',
    maxWidth: 460,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 24,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
  },
  modalHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  modalCloseText: {
    fontSize: 18,
    color: '#94A3B8',
    fontWeight: '700',
    padding: 4,
  },
  modalSubtitle: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 14,
  },
  modalSuccessBanner: {
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#A7F3D0',
    borderRadius: 10,
    padding: 10,
    marginBottom: 12,
  },
  modalSuccessBannerText: {
    fontSize: 13,
    color: '#065F46',
    fontWeight: '600',
  },
  modalErrorBanner: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
    borderRadius: 10,
    padding: 10,
    marginBottom: 12,
  },
  modalErrorBannerText: {
    fontSize: 13,
    color: '#991B1B',
    fontWeight: '600',
  },
  modalBadgeText: {
    fontSize: 11,
    color: '#2563EB',
    fontWeight: '700',
    marginTop: 2,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 6,
  },
  modalTextInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#0F172A',
  },
  modalTextArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  categoryPillsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  categoryPill: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 14,
    backgroundColor: '#F1F5F9',
  },
  categoryPillSelected: {
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#2563EB',
  },
  categoryPillText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#475569',
  },
  categoryPillTextSelected: {
    color: '#2563EB',
    fontWeight: '700',
  },
  slotOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 14,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 10,
    marginBottom: 6,
  },
  slotOptionSelected: {
    backgroundColor: '#EFF6FF',
    borderColor: '#2563EB',
  },
  slotText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#334155',
  },
  slotTextSelected: {
    color: '#2563EB',
    fontWeight: '700',
  },
  slotCheckmark: {
    fontSize: 14,
    fontWeight: '800',
    color: '#2563EB',
  },
  modalActionRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 10,
    marginTop: 18,
  },
  modalCancelBtn: {
    paddingVertical: 11,
    paddingHorizontal: 16,
    borderRadius: 10,
    backgroundColor: '#F1F5F9',
  },
  modalCancelBtnText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#475569',
  },
  modalConfirmBtn: {
    paddingVertical: 11,
    paddingHorizontal: 20,
    borderRadius: 10,
    backgroundColor: '#2563EB',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalConfirmBtnText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },

  /* Guide modal specific */
  guideModalDesc: {
    fontSize: 14,
    color: '#334155',
    lineHeight: 20,
  },
  guideTipRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  guideTipBullet: {
    fontSize: 16,
    color: '#2563EB',
    marginRight: 8,
    lineHeight: 20,
  },
  guideTipText: {
    fontSize: 13,
    color: '#475569',
    lineHeight: 18,
    flex: 1,
  },
  guideNoticeBox: {
    backgroundColor: '#EFF6FF',
    borderRadius: 10,
    padding: 12,
    marginTop: 12,
  },
  guideNoticeText: {
    fontSize: 12,
    color: '#1E40AF',
    lineHeight: 17,
  },

  /* Showcase Modal specific */
  showcaseModalSlideWrap: {
    backgroundColor: '#F8FAFC',
    borderRadius: 14,
    padding: 20,
    alignItems: 'center',
    marginVertical: 10,
  },
  showcaseModalSlideTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 2,
  },
  showcaseModalSlideTag: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563EB',
    marginBottom: 6,
  },
  showcaseModalSlideSub: {
    fontSize: 13,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 18,
  },
  carouselDotsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 6,
    marginVertical: 10,
  },
  carouselDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#CBD5E1',
  },
  carouselDotActive: {
    backgroundColor: '#2563EB',
    width: 20,
  },

  /* Voice Call Simulator Modal */
  callModalContainer: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 28,
    alignItems: 'center',
  },
  callAvatarWrap: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#3B82F6',
  },
  callSpecialistName: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  callSpecialistRole: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  callStatusBox: {
    alignItems: 'center',
    marginVertical: 18,
  },
  callingText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
  },
  callingSubtext: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 4,
  },
  connectedBadge: {
    fontSize: 11,
    fontWeight: '800',
    color: '#059669',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  callTimerText: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0F172A',
    fontVariant: ['tabular-nums'],
  },
  waveformContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 10,
  },
  waveBar: {
    width: 4,
    borderRadius: 2,
    backgroundColor: '#2563EB',
  },
  endedText: {
    fontSize: 16,
    fontWeight: '800',
    color: '#DC2626',
  },
  callControlsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    marginTop: 12,
  },
  controlButton: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#F1F5F9',
  },
  controlButtonActive: {
    backgroundColor: '#EFF6FF',
    borderWidth: 1.5,
    borderColor: '#2563EB',
  },
  controlIcon: {
    fontSize: 18,
  },
  controlLabel: {
    fontSize: 9,
    fontWeight: '600',
    color: '#64748B',
    marginTop: 2,
  },
  endCallButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#DC2626',
    borderRadius: 24,
    paddingVertical: 12,
    paddingHorizontal: 20,
    gap: 6,
  },
  endCallIcon: {
    fontSize: 16,
    color: '#FFFFFF',
  },
  endCallText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },

  /* Toast Notification */
  toastContainer: {
    position: 'absolute',
    top: 14,
    alignSelf: 'center',
    backgroundColor: '#0F172A',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    zIndex: 99,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  toastText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
  },
});
