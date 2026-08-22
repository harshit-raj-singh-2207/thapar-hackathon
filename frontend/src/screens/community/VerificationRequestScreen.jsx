import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Image,
  useWindowDimensions,
} from 'react-native';
import { useAuthStore } from '../../store/authStore';
import { communityApi } from '../../services/api/communityApi';

const safetyBanner = require('../../../assets/images/safety_guidelines_banner.jpg');
const guideBanner = require('../../../assets/images/getting_started_banner.jpg');
const teamBanner = require('../../../assets/images/meet_the_team_banner.jpg');

export default function VerificationRequestScreen({ navigation }) {
  const { user, verificationStatus: authVerifStatus, logout } = useAuthStore();
  const [roleBio, setRoleBio] = useState('');
  const [docNotes, setDocNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showStatusPortal, setShowStatusPortal] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'status'
  const [latestSubmissionStatus, setLatestSubmissionStatus] = useState(authVerifStatus || 'pending');

  // Post composer & interactions state
  const [newPostText, setNewPostText] = useState('');
  const [sarahLikes, setSarahLikes] = useState(12);
  const [sarahLiked, setSarahLiked] = useState(false);
  const [marcusLikes, setMarcusLikes] = useState(48);
  const [marcusLiked, setMarcusLiked] = useState(false);

  const { width } = useWindowDimensions();
  const isWide = width > 768;

  useEffect(() => {
    loadVerificationStatus();
  }, []);

  const loadVerificationStatus = async () => {
    try {
      const res = await communityApi.getVerificationStatus();
      if (res && res.status) {
        setLatestSubmissionStatus(res.status);
        if (res.role_bio && !roleBio) {
          setRoleBio(res.role_bio);
        }
        if (res.document_notes && !docNotes) {
          setDocNotes(res.document_notes);
        }
      }
    } catch (err) {
      // If 404, status remains default pending
    }
  };

  const handleSubmit = async () => {
    if (!roleBio.trim()) {
      Alert.alert('Required Field', 'Please provide a brief bio or description of your caregiver role.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await communityApi.submitVerificationRequest({
        role_bio: roleBio.trim(),
        document_notes: docNotes.trim(),
      });

      setLatestSubmissionStatus(res.status || 'pending');
      setShowStatusPortal(true);
      setActiveTab('status');
      Alert.alert(
        'Request Submitted',
        'Your caregiver verification request has been submitted for review. You can now track your application status.'
      );
    } catch (err) {
      Alert.alert('Submission Error', err.detail || 'Could not submit verification request.');
    } finally {
      setSubmitting(false);
    }
  };


  const handleCreatePost = () => {
    if (!newPostText.trim()) {
      Alert.alert('Empty Post', 'Please type a message before posting.');
      return;
    }
    Alert.alert('Post Published', 'Your update has been shared with the Caregiver Community!');
    setNewPostText('');
  };

  // Render Dashboard View (Exact UI from screenshot)
  const renderDashboardView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      <View style={[styles.gridRow, !isWide && styles.columnLayout]}>
        {/* Left / Center Main Feed Column */}
        <View style={styles.feedMainCol}>
          {/* Post Composer Box */}
          <View style={styles.composerCard}>
            <View style={styles.composerRow}>
              <View style={styles.composerAvatar}>
                <Text style={styles.composerAvatarText}>{user?.full_name ? user.full_name[0] : 'U'}</Text>
              </View>
              <TextInput
                style={styles.composerInput}
                placeholder="Share an update, ask a question, or post a resource..."
                placeholderTextColor="#94A3B8"
                multiline
                value={newPostText}
                onChangeText={setNewPostText}
              />
            </View>

            <View style={styles.composerActionsRow}>
              <View style={styles.composerTools}>
                <TouchableOpacity style={styles.toolBtn} onPress={() => Alert.alert('Add Photo', 'Select image attachment')}>
                  <Text style={styles.toolIcon}>🖼️</Text>
                  <Text style={styles.toolText}>Photo</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.toolBtn} onPress={() => Alert.alert('Add Tag', 'Select category tag (Question, Resource, Victory)')}>
                  <Text style={styles.toolIcon}>🏷️</Text>
                  <Text style={styles.toolText}>Tag</Text>
                </TouchableOpacity>
              </View>

              <TouchableOpacity style={styles.postSubmitBtn} onPress={handleCreatePost}>
                <Text style={styles.postSubmitBtnText}>Post</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Post 1 Card: Sarah Jenkins */}
          <View style={styles.postCard}>
            <View style={styles.postHeader}>
              <View style={styles.authorRow}>
                <View style={styles.authorAvatar}>
                  <Text style={styles.authorAvatarText}>SJ</Text>
                </View>
                <View>
                  <Text style={styles.authorName}>Sarah Jenkins</Text>
                  <Text style={styles.postTime}>2 hours ago</Text>
                </View>
              </View>

              <View style={styles.tagBadge}>
                <Text style={styles.tagBadgeIcon}>⚙️</Text>
                <Text style={styles.tagBadgeText}>Question</Text>
              </View>
            </View>

            <Text style={styles.postContent}>
              We're currently exploring new occupational therapy routines for my son, specifically around sensory
              integration. Has anyone found particular sensory swings or deep pressure tools that worked well for teens?
              Looking for recommendations that aren't too "childish" looking.
            </Text>

            <View style={styles.postFooter}>
              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() => {
                  setSarahLiked(!sarahLiked);
                  setSarahLikes(sarahLiked ? sarahLikes - 1 : sarahLikes + 1);
                }}
              >
                <Text style={[styles.actionIcon, sarahLiked && { color: '#EF4444' }]}>
                  {sarahLiked ? '❤️' : '🤍'}
                </Text>
                <Text style={styles.actionCount}>{sarahLikes}</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() => Alert.alert('Comments', 'Viewing 5 comments on Sarah Jenkins post')}
              >
                <Text style={styles.actionIcon}>💬</Text>
                <Text style={styles.actionCount}>5 Comments</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Post 2 Card: Marcus T. */}
          <View style={styles.postCard}>
            <View style={styles.postHeader}>
              <View style={styles.authorRow}>
                <View style={[styles.authorAvatar, { backgroundColor: '#F59E0B' }]}>
                  <Text style={styles.authorAvatarText}>MT</Text>
                </View>
                <View>
                  <Text style={styles.authorName}>Marcus T.</Text>
                  <Text style={styles.postTime}>5 hours ago</Text>
                </View>
              </View>

              <View style={[styles.tagBadge, { backgroundColor: '#FEF3C7', borderColor: '#FCD34D' }]}>
                <Text style={styles.tagBadgeIcon}>🏆</Text>
                <Text style={[styles.tagBadgeText, { color: '#D97706' }]}>Victory</Text>
              </View>
            </View>

            <Text style={styles.postContent}>
              Huge milestone today! David managed the entire grocery store run without his noise-canceling headphones. We've
              been practicing gradual exposure for months. So incredibly proud of his resilience. Celebrate the small wins,
              everyone! 🎉
            </Text>

            <View style={styles.postFooter}>
              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() => {
                  setMarcusLiked(!marcusLiked);
                  setMarcusLikes(marcusLiked ? marcusLikes - 1 : marcusLikes + 1);
                }}
              >
                <Text style={styles.actionIcon}>{marcusLiked ? '❤️' : '🧡'}</Text>
                <Text style={styles.actionCount}>{marcusLikes}</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() => Alert.alert('Comments', 'Viewing 14 comments on Marcus T. post')}
              >
                <Text style={styles.actionIcon}>💬</Text>
                <Text style={styles.actionCount}>14 Comments</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Right Sidebar Column Widgets */}
        <View style={[styles.rightColWidgets, !isWide && styles.fullWidth]}>
          {/* Active Groups Widget */}
          <View style={styles.widgetCard}>
            <View style={styles.widgetHeader}>
              <View style={styles.widgetTitleRow}>
                <Text style={styles.widgetTitleIcon}>👥</Text>
                <Text style={styles.widgetTitle}>Active Groups</Text>
              </View>
              <TouchableOpacity onPress={() => setActiveTab('groups')}>
                <Text style={styles.widgetLink}>View All</Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity style={styles.groupItem} onPress={() => navigation.navigate('GroupDetails', { groupId: 'group-1' })}>
              <Text style={styles.groupItemName}>Parents of Newly Diagnosed</Text>
              <Text style={styles.groupItemSub}>14 new posts today</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.groupItem} onPress={() => navigation.navigate('GroupDetails', { groupId: 'group-2' })}>
              <Text style={styles.groupItemName}>Teens & Young Adults Support</Text>
              <Text style={styles.groupItemSub}>Active discussion: Transitioning schools</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.groupItem} onPress={() => navigation.navigate('GroupDetails', { groupId: 'group-3' })}>
              <Text style={styles.groupItemName}>Therapeutic Play Ideas</Text>
              <Text style={styles.groupItemSub}>5 new resources shared</Text>
            </TouchableOpacity>
          </View>

          {/* Upcoming Events Widget */}
          <View style={styles.widgetCard}>
            <View style={styles.widgetHeader}>
              <View style={styles.widgetTitleRow}>
                <Text style={styles.widgetTitleIcon}>📅</Text>
                <Text style={styles.widgetTitle}>Upcoming Events</Text>
              </View>
            </View>

            <View style={styles.eventItem}>
              <View style={styles.eventDateBox}>
                <Text style={styles.eventMonth}>OCT</Text>
                <Text style={styles.eventDay}>12</Text>
              </View>
              <View style={styles.eventContent}>
                <Text style={styles.eventTitle}>Navigating IEP Meetings</Text>
                <View style={styles.eventSubRow}>
                  <Text style={styles.eventSubIcon}>💻</Text>
                  <Text style={styles.eventSubText}>Virtual Webinar</Text>
                </View>
              </View>
            </View>

            <View style={styles.eventItem}>
              <View style={styles.eventDateBox}>
                <Text style={styles.eventMonth}>OCT</Text>
                <Text style={styles.eventDay}>15</Text>
              </View>
              <View style={styles.eventContent}>
                <Text style={styles.eventTitle}>Local Caregiver Coffee Meetup</Text>
                <View style={styles.eventSubRow}>
                  <Text style={styles.eventSubIcon}>📍</Text>
                  <Text style={styles.eventSubText}>Downtown Library</Text>
                </View>
              </View>
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  // Render Verification Status View
  const renderStatusView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Top Row Cards */}
      <View style={[styles.gridRow, !isWide && styles.columnLayout]}>
        {/* Main Status Banner Card */}
        <View style={styles.applicationCard}>
          <View style={styles.applicationHeaderRow}>
            <Text style={styles.applicationTitle}>Application Received</Text>
            <View style={styles.pendingBadge}>
              <View style={styles.pendingDot} />
              <Text style={styles.pendingBadgeText}>PENDING REVIEW</Text>
            </View>
          </View>

          <Text style={styles.applicationBody}>
            Thank you for submitting your details. We are carefully reviewing your profile to ensure the safety and
            integrity of our community.
          </Text>

          {/* Next Steps Inner Container */}
          <View style={styles.nextStepsBox}>
            <Text style={styles.nextStepsTitle}>Next Steps</Text>

            <View style={styles.stepItem}>
              <View style={styles.stepIconCircle}>
                <Text style={styles.stepIcon}>🔍</Text>
              </View>
              <View style={styles.stepTextContent}>
                <Text style={styles.stepTitle}>Manual Safety Review</Text>
                <Text style={styles.stepDescription}>
                  Our specialized team is verifying your credentials against national databases.
                </Text>
              </View>
            </View>

            <View style={styles.stepItem}>
              <View style={styles.stepIconCircle}>
                <Text style={styles.stepIcon}>⏱️</Text>
              </View>
              <View style={styles.stepTextContent}>
                <Text style={styles.stepTitle}>Estimated Turnaround</Text>
                <Text style={styles.stepDescription}>
                  Please allow 24-48 hours for this process to complete. You will be notified via email.
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Right Column Action & Security Cards */}
        <View style={[styles.rightColWidgets, !isWide && styles.fullWidth]}>
          {/* Purple Immediate Help Card */}
          <View style={styles.purpleHelpCard}>
            <View style={styles.purpleIconBox}>
              <Text style={styles.purpleIcon}>🌐</Text>
            </View>
            <Text style={styles.purpleCardTitle}>Need Immediate Help?</Text>
            <Text style={styles.purpleCardBody}>
              If you have questions about your application status or need assistance uploading documents.
            </Text>
            <TouchableOpacity style={styles.supportPillBtn} onPress={handleSupportContact}>
              <Text style={styles.supportPillBtnText}>Contact Support Team</Text>
            </TouchableOpacity>
          </View>

          {/* Secure Process Card */}
          <View style={styles.secureCard}>
            <View style={styles.secureIconBox}>
              <Text style={styles.secureIcon}>🔒</Text>
            </View>
            <View style={styles.secureTextCol}>
              <Text style={styles.secureTitle}>Secure Process</Text>
              <Text style={styles.secureBody}>Your data is encrypted end-to-end.</Text>
            </View>
          </View>
        </View>
      </View>

      {/* Bottom Grid: Community Resources */}
      <View style={styles.resourcesSection}>
        <Text style={styles.resourcesSectionTitle}>While You Wait: Community Resources</Text>

        <View style={[styles.resourceGrid, !isWide && styles.columnLayout]}>
          {/* Card 1: Safety Guidelines */}
          <TouchableOpacity style={styles.resourceCard} activeOpacity={0.85}>
            <Image source={safetyBanner} style={styles.resourceBannerImage} resizeMode="cover" />
            <View style={styles.resourceContent}>
              <View style={styles.resourceTagRow}>
                <Text style={styles.resourceTagIcon}>🛡️</Text>
                <Text style={styles.resourceTagText}>POLICY</Text>
              </View>
              <Text style={styles.resourceCardTitle}>Safety Guidelines</Text>
              <Text style={styles.resourceCardSubtitle}>
                Review our community standards and commitment to a secure environment.
              </Text>
            </View>
          </TouchableOpacity>

          {/* Card 2: Getting Started Guide */}
          <TouchableOpacity style={styles.resourceCard} activeOpacity={0.85}>
            <Image source={guideBanner} style={styles.resourceBannerImage} resizeMode="cover" />
            <View style={styles.resourceContent}>
              <View style={styles.resourceTagRow}>
                <Text style={styles.resourceTagIcon}>📖</Text>
                <Text style={[styles.resourceTagText, { color: '#C084FC' }]}>GUIDE</Text>
              </View>
              <Text style={styles.resourceCardTitle}>Getting Started Guide</Text>
              <Text style={styles.resourceCardSubtitle}>
                Learn how to navigate the portal once your account is fully activated.
              </Text>
            </View>
          </TouchableOpacity>

          {/* Card 3: Meet the Team */}
          <TouchableOpacity style={styles.resourceCard} activeOpacity={0.85}>
            <Image source={teamBanner} style={styles.resourceBannerImage} resizeMode="cover" />
            <View style={styles.resourceContent}>
              <View style={styles.resourceTagRow}>
                <Text style={styles.resourceTagIcon}>👥</Text>
                <Text style={[styles.resourceTagText, { color: '#38BDF8' }]}>COMMUNITY</Text>
              </View>
              <Text style={styles.resourceCardTitle}>Meet the Team</Text>
              <Text style={styles.resourceCardSubtitle}>
                Get to know the dedicated support staff behind the Caregiver Community.
              </Text>
            </View>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );

  // Render Community Guidelines View (Exact UI from screenshot)
  const renderGuidelinesView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Header Banner */}
      <View style={styles.guidelinesHeader}>
        <Text style={styles.guidelinesTitle}>Community Guidelines</Text>
        <Text style={styles.guidelinesSubtitle}>
          Our core mission is to provide a safe, supportive, and respectful digital environment for autism caregivers.
          We expect all community members to uphold these values to ensure a trusted space for sharing, learning, and mutual support.
        </Text>
      </View>

      {/* Section 1: Core Values */}
      <View style={styles.sectionBlock}>
        <View style={styles.sectionTitleRow}>
          <Text style={styles.sectionTitleIcon}>⭐</Text>
          <Text style={styles.sectionTitle}>Core Values</Text>
        </View>

        <View style={[styles.gridRow3, !isWide && styles.columnLayout]}>
          {/* Core Value 1 */}
          <View style={styles.valueCard}>
            <View style={styles.valueIconCircle}>
              <Text style={styles.valueIcon}>🛡️</Text>
            </View>
            <Text style={styles.valueCardTitle}>Safety & Privacy</Text>
            <Text style={styles.valueCardBody}>
              We prioritize the absolute protection of sensitive information and respect the privacy of every family.
            </Text>
          </View>

          {/* Core Value 2 */}
          <View style={styles.valueCard}>
            <View style={[styles.valueIconCircle, { backgroundColor: '#FEF3C7' }]}>
              <Text style={styles.valueIcon}>🧡</Text>
            </View>
            <Text style={styles.valueCardTitle}>Respect & Empathy</Text>
            <Text style={styles.valueCardBody}>
              We foster an environment of understanding, where diverse experiences are met with compassion, not judgment.
            </Text>
          </View>

          {/* Core Value 3 */}
          <View style={styles.valueCard}>
            <View style={[styles.valueIconCircle, { backgroundColor: '#E0F2FE' }]}>
              <Text style={styles.valueIcon}>📖</Text>
            </View>
            <Text style={styles.valueCardTitle}>Evidence-Based Support</Text>
            <Text style={styles.valueCardBody}>
              We encourage the sharing of established, research-backed information alongside personal lived experiences.
            </Text>
          </View>
        </View>
      </View>

      {/* Section 2: Specific Rules of Conduct */}
      <View style={styles.sectionBlock}>
        <View style={styles.sectionTitleRow}>
          <Text style={styles.sectionTitleIcon}>⚖️</Text>
          <Text style={styles.sectionTitle}>Specific Rules of Conduct</Text>
        </View>

        {/* Rule 1: No Medical Advice */}
        <View style={styles.ruleCard}>
          <View style={styles.ruleHeaderRow}>
            <Text style={styles.ruleIcon}>🏥</Text>
            <Text style={styles.ruleTitle}>No Medical Advice</Text>
          </View>
          <Text style={styles.ruleBody}>
            This community is for sharing experiences and emotional support. Do not present yourself as a medical professional
            unless verified, and never offer diagnostic or treatment advice.
          </Text>
          <View style={styles.calloutBox}>
            <Text style={styles.doText}>
              <Text style={{ fontWeight: '700', color: '#10B981' }}>Do:</Text> "In our experience, therapy X helped us."
            </Text>
            <Text style={styles.dontText}>
              <Text style={{ fontWeight: '700', color: '#EF4444' }}>Don't:</Text> "You need to try medication Y for these symptoms."
            </Text>
          </View>
        </View>

        {/* Rule 2: Strict Privacy */}
        <View style={styles.ruleCard}>
          <View style={styles.ruleHeaderRow}>
            <Text style={styles.ruleIcon}>🙈</Text>
            <Text style={styles.ruleTitle}>Strict Privacy</Text>
          </View>
          <Text style={styles.ruleBody}>
            Protect the dignity of those you care for. Do not post identifiable photos of children in vulnerable states (e.g., during meltdowns). Respect the anonymity of other members.
          </Text>
        </View>

        {/* Rule 3: Zero Tolerance for Harassment */}
        <View style={styles.ruleCard}>
          <View style={styles.ruleHeaderRow}>
            <Text style={styles.ruleIcon}>🚫</Text>
            <Text style={styles.ruleTitle}>Zero Tolerance for Harassment</Text>
          </View>
          <Text style={styles.ruleBody}>
            Bullying, hate speech, or personal attacks will result in immediate suspension. We are here to support each other. Disagreements must be handled civilly.
          </Text>
        </View>

        {/* Rule 4: No Promotion or Spam */}
        <View style={styles.ruleCard}>
          <View style={styles.ruleHeaderRow}>
            <Text style={styles.ruleIcon}>📢</Text>
            <Text style={styles.ruleTitle}>No Promotion or Spam</Text>
          </View>
          <Text style={styles.ruleBody}>
            Do not use the community to sell products, services, or solicit donations. Keep discussions focused on caregiving support and resources.
          </Text>
        </View>
      </View>

      {/* Section 3: Reporting Violations Card */}
      <View style={styles.reportingCard}>
        <View style={styles.reportingContent}>
          <View style={styles.reportingHeaderRow}>
            <Text style={styles.reportingIcon}>🛡️</Text>
            <Text style={styles.reportingTitle}>Reporting Violations</Text>
          </View>
          <Text style={styles.reportingBody}>
            If you see behavior that violates these guidelines, please report it immediately. Our moderation team reviews all reports securely and confidentially.
          </Text>
        </View>

        <TouchableOpacity style={styles.contactModeratorBtn} onPress={() => Alert.alert('Contact Moderator', 'Connecting to NIVARA Moderation Team...')}>
          <Text style={styles.contactModeratorBtnText}>Contact Moderator</Text>
        </TouchableOpacity>
      </View>

      {/* Footer Disclaimer */}
      <View style={styles.guidelinesFooter}>
        <Text style={styles.guidelinesFooterText}>
          By using the Caregiver Portal, you agree to abide by these Community Guidelines.
        </Text>
        <Text style={styles.guidelinesFooterDate}>Last updated: October 24, 2023</Text>
      </View>
    </ScrollView>
  );

  const renderFormView = () => (
    <ScrollView style={styles.formContainer} contentContainerStyle={styles.formContent}>
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Text style={styles.backButtonText}>← Back to Community</Text>
      </TouchableOpacity>

      <View style={styles.formCard}>
        <View style={styles.headerRow}>
          <Text style={styles.badgeIcon}>🛡️</Text>
          <View style={styles.headerTextCol}>
            <Text style={styles.title}>Caregiver Verification Request</Text>
            <Text style={styles.subtitle}>Private & Secure Community Safety</Text>
          </View>
        </View>

        <Text style={styles.description}>
          To protect caregiver privacy and ensure child safety, NIVARA requires verification for community feed, messaging, and support groups access.
        </Text>

        <View style={styles.statusBox}>
          <Text style={styles.statusLabel}>Current Verification Status:</Text>
          <Text style={styles.statusValue}>{latestSubmissionStatus?.toUpperCase() || 'PENDING REVIEW'}</Text>
        </View>


        <Text style={styles.inputLabel}>Caregiver Role & Bio</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          multiline
          numberOfLines={4}
          placeholder="Describe your caregiver role (e.g. Parent of child with ASD, ABA Therapist, Special Education Teacher)..."
          placeholderTextColor="#94A3B8"
          value={roleBio}
          onChangeText={setRoleBio}
        />

        <Text style={styles.inputLabel}>Additional Notes or Verification Credentials (Optional)</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          multiline
          numberOfLines={3}
          placeholder="Enter any reference contact or credential notes..."
          placeholderTextColor="#94A3B8"
          value={docNotes}
          onChangeText={setDocNotes}
        />

        <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit} disabled={submitting}>
          {submitting ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.submitBtnText}>Submit Verification Details</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.toggleModeBtn}
          onPress={() => {
            setShowStatusPortal(true);
            setActiveTab('status');
          }}
        >
          <Text style={styles.toggleModeBtnText}>View Verification Status Portal →</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  // FAQ State & Support View
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState(null);

  const handleSupportContact = () => {
    setShowStatusPortal(true);
    setActiveTab('support');
  };

  const faqData = [
    {
      q: 'How long does verification take?',
      a: 'Verification typically takes 24-48 hours. Our safety team manually verifies credentials against official databases to maintain community trust and child safety.',
    },
    {
      q: 'What documents do I need to provide?',
      a: 'You can provide professional credentials, state caregiver certification, ABA/Special Ed licenses, or a reference from a recognized autism support organization.',
    },
    {
      q: 'Is my data secure?',
      a: 'Yes! All submitted data and documents are encrypted end-to-end and stored securely according to HIPAA-compliant security standards.',
    },
    {
      q: 'Can I access the community while pending?',
      a: 'While pending, you can browse guidelines, resources, and set up your profile. Interactive posting and direct messaging unlock automatically once verified.',
    },
  ];

  const renderSupportView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Top Search Hero Box */}
      <View style={styles.supportHeroCard}>
        <Text style={styles.supportHeroTitle}>How can we help you today?</Text>
        <Text style={styles.supportHeroSubtitle}>Search our knowledge base or get in touch with our support specialists.</Text>

        <View style={styles.searchBarBox}>
          <Text style={styles.searchBarIcon}>🔍</Text>
          <TextInput
            style={styles.searchBarInput}
            placeholder="Search for articles..."
            placeholderTextColor="#94A3B8"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
      </View>

      <View style={[styles.gridRow, !isWide && styles.columnLayout]}>
        {/* Left Column: Contact Methods */}
        <View style={styles.contactMethodsCol}>
          <Text style={styles.sectionHeaderTitle}>Contact Methods</Text>

          {/* Method 1: Live Chat */}
          <TouchableOpacity style={styles.contactCard} onPress={() => setActiveTab('livechat')}>
            <View style={styles.contactHeaderRow}>
              <View style={[styles.contactIconBox, { backgroundColor: '#4F46E5' }]}>
                <Text style={styles.contactIcon}>💬</Text>
              </View>
              <View style={styles.contactTextContent}>
                <Text style={styles.contactTitle}>Live Chat</Text>
                <Text style={styles.contactSubtitle}>Chat with a Specialist instantly.</Text>
              </View>
            </View>
            <View style={styles.contactBadgeRow}>
              <View style={styles.amberWaitBadge}>
                <Text style={styles.amberWaitBadgeText}>WAIT: ~5 MINS</Text>
              </View>
            </View>
          </TouchableOpacity>

          {/* Method 2: Email Support */}
          <TouchableOpacity style={styles.contactCard} onPress={() => setActiveTab('email')}>
            <View style={styles.contactHeaderRow}>
              <View style={[styles.contactIconBox, { backgroundColor: '#0284C7' }]}>
                <Text style={styles.contactIcon}>✉️</Text>
              </View>
              <View style={styles.contactTextContent}>
                <Text style={styles.contactTitle}>Email Support</Text>
                <Text style={styles.contactSubtitle}>Send an inquiry for detailed help.</Text>
              </View>
            </View>
            <View style={styles.contactBadgeRow}>
              <View style={styles.blueWaitBadge}>
                <Text style={styles.blueWaitBadgeText}>24H RESPONSE</Text>
              </View>
            </View>
          </TouchableOpacity>

          {/* Method 3: Phone Support */}
          <TouchableOpacity style={styles.contactCard} onPress={() => Alert.alert('Phone Support', 'Calling NIVARA Helpline: +1 (800) 555-NIVARA')}>
            <View style={styles.contactHeaderRow}>
              <View style={[styles.contactIconBox, { backgroundColor: '#10B981' }]}>
                <Text style={styles.contactIcon}>📞</Text>
              </View>
              <View style={styles.contactTextContent}>
                <Text style={styles.contactTitle}>Phone Support</Text>
                <Text style={styles.contactSubtitle}>Call Support directly.</Text>
              </View>
            </View>
            <View style={styles.contactBadgeRow}>
              <View style={styles.greenWaitBadge}>
                <Text style={styles.greenWaitBadgeText}>MON - FRI 9AM - 5PM</Text>
              </View>
            </View>
          </TouchableOpacity>
        </View>

        {/* Right Column: FAQ & Helpful Guides */}
        <View style={styles.faqAndGuidesCol}>
          {/* FAQ Accordion Section */}
          <View style={styles.faqSection}>
            <Text style={styles.sectionHeaderTitle}>Frequently Asked Questions</Text>

            <View style={styles.faqContainerCard}>
              {faqData.map((item, index) => {
                const isExpanded = expandedFaq === index;
                return (
                  <View key={index} style={[styles.faqItem, index < faqData.length - 1 && styles.faqBorder]}>
                    <TouchableOpacity
                      style={styles.faqHeaderRow}
                      onPress={() => setExpandedFaq(isExpanded ? null : index)}
                    >
                      <Text style={styles.faqQuestionText}>{item.q}</Text>
                      <Text style={styles.faqChevronIcon}>{isExpanded ? '▲' : '▼'}</Text>
                    </TouchableOpacity>
                    {isExpanded && (
                      <Text style={styles.faqAnswerText}>{item.a}</Text>
                    )}
                  </View>
                );
              })}
            </View>
          </View>

          {/* Helpful Guides Section */}
          <View style={styles.guidesSection}>
            <Text style={styles.sectionHeaderTitle}>Helpful Guides</Text>

            <View style={styles.guidesGrid}>
              <TouchableOpacity style={styles.guideCard} onPress={() => Alert.alert('Verification Checklist', 'Opening Verification Checklist...')}>
                <View style={styles.guideHeaderRow}>
                  <Text style={styles.guideIcon}>🧩</Text>
                  <Text style={styles.guideTitle}>Verification Checklist</Text>
                </View>
                <Text style={styles.guideBody}>
                  A step-by-step guide to ensure you have all necessary documents ready for approval.
                </Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.guideCard} onPress={() => Alert.alert('Privacy Policy', 'Opening Privacy Policy...')}>
                <View style={styles.guideHeaderRow}>
                  <Text style={styles.guideIcon}>🛡️</Text>
                  <Text style={styles.guideTitle}>Privacy Policy</Text>
                </View>
                <Text style={styles.guideBody}>
                  Detailed information on how we handle, store, and protect your sensitive data.
                </Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity style={[styles.guideCard, { marginTop: 12 }]} onPress={() => Alert.alert('Community Handbook', 'Opening Community Handbook...')}>
              <View style={styles.guideHeaderRow}>
                <Text style={styles.guideIcon}>📖</Text>
                <Text style={styles.guideTitle}>Community Handbook</Text>
              </View>
              <Text style={styles.guideBody}>
                Guidelines and best practices for interacting within the CaregiverConnect platform to ensure a safe space for everyone.
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  // Active Groups State & View
  const [groupFilterQuery, setGroupFilterQuery] = useState('');
  const [joinedState, setJoinedState] = useState({
    'group-3': true,
  });

  const toggleJoinGroup = (groupId) => {
    setJoinedState((prev) => ({
      ...prev,
      [groupId]: !prev[groupId],
    }));
    Alert.alert(
      joinedState[groupId] ? 'Left Group' : 'Joined Group',
      joinedState[groupId]
        ? 'You have left the group.'
        : 'Welcome! You are now a member of this active caregiver group.'
    );
  };

  const groupListData = [
    {
      id: 'group-1',
      title: 'Parents of Newly Diagnosed',
      description: 'A supportive space for parents navigating recent diagnoses. Share...',
      members: '1.2k Members',
      posts: '14 posts today',
      tags: ['#Support', '#Pediatric'],
      bannerBg: '#E0E7FF',
      iconBg: '#4F46E5',
      icon: '🏠',
    },
    {
      id: 'group-2',
      title: 'Teens & Young Adults Support',
      description: 'Discussing transition planning, independence, and supporting ment...',
      members: '856 Members',
      posts: '8 posts today',
      tags: ['#Transition', '#MentalHealth'],
      bannerBg: '#FEF3C7',
      iconBg: '#D97706',
      icon: '🎓',
    },
    {
      id: 'group-3',
      title: 'Therapeutic Play Ideas',
      description: 'Share and discover OT-approved play activities, DIY sensory tools, and...',
      members: '2.4k Members',
      posts: '32 posts today',
      tags: ['#OccupationalTherapy', '#Play'],
      bannerBg: '#E0F2FE',
      iconBg: '#0284C7',
      icon: '🚗',
    },
  ];

  const filteredGroups = groupListData.filter(
    (g) =>
      g.title.toLowerCase().includes(groupFilterQuery.toLowerCase()) ||
      g.description.toLowerCase().includes(groupFilterQuery.toLowerCase()) ||
      g.tags.some((t) => t.toLowerCase().includes(groupFilterQuery.toLowerCase()))
  );

  const renderGroupsView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Sub navigation tab pill bar */}
      <View style={styles.groupSubNavRow}>
        <TouchableOpacity style={[styles.groupSubTabBtn, styles.groupSubTabBtnActive]} onPress={() => setActiveTab('directory')}>
          <Text style={[styles.groupSubTabBtnText, styles.groupSubTabBtnTextActive]}>Browse Directory</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.groupSubTabBtn} onPress={() => setActiveTab('my_groups')}>
          <Text style={styles.groupSubTabBtnText}>My Joined Groups (3)</Text>
        </TouchableOpacity>
      </View>

      {/* Header Row with Title and Create Group Button */}
      <View style={styles.groupsHeaderRow}>
        <View style={styles.groupsHeaderTitleCol}>
          <Text style={styles.groupsPageTitle}>Active Groups</Text>
          <Text style={styles.groupsPageSubtitle}>Connect with caregivers sharing similar experiences and challenges.</Text>
        </View>

        <TouchableOpacity
          style={styles.createGroupBtn}
          onPress={() => Alert.alert('Create Group', 'Opening Create Caregiver Group modal...')}
        >
          <Text style={styles.createGroupBtnText}>+ Create Group</Text>
        </TouchableOpacity>
      </View>

      {/* Filter & Search Bar Box */}
      <View style={styles.groupSearchFilterCard}>
        <View style={styles.groupSearchInputBox}>
          <Text style={styles.searchBarIcon}>🔍</Text>
          <TextInput
            style={styles.searchBarInput}
            placeholder="Search groups by name or topic..."
            placeholderTextColor="#94A3B8"
            value={groupFilterQuery}
            onChangeText={setGroupFilterQuery}
          />
        </View>

        <View style={styles.groupFilterDropdowns}>
          <TouchableOpacity style={styles.filterDropdownPill} onPress={() => Alert.alert('Category Filter', 'Filtering by Category...')}>
            <Text style={styles.filterDropdownLabel}>Category:</Text>
            <Text style={styles.filterDropdownValue}>All Categories ▼</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.filterDropdownPill} onPress={() => Alert.alert('Sort By', 'Sorting groups...')}>
            <Text style={styles.filterDropdownLabel}>Sort by:</Text>
            <Text style={styles.filterDropdownValue}>Most Active ▼</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Groups Grid (3 Column layout matching screenshot) */}
      <View style={[styles.gridRow3, !isWide && styles.columnLayout]}>
        {filteredGroups.map((group) => {
          const isJoined = joinedState[group.id];
          return (
            <View key={group.id} style={styles.groupCard}>
              {/* Top Graphic Banner */}
              <View style={[styles.groupBannerHeader, { backgroundColor: group.bannerBg }]}>
                <View style={[styles.groupAvatarCircle, { backgroundColor: group.iconBg }]}>
                  <Text style={styles.groupAvatarIcon}>{group.icon}</Text>
                </View>
              </View>

              {/* Group Body Details */}
              <View style={styles.groupCardBody}>
                <Text style={styles.groupCardTitle}>{group.title}</Text>
                <Text style={styles.groupCardDescription}>{group.description}</Text>

                {/* Stats Meta Row */}
                <View style={styles.groupMetaRow}>
                  <Text style={styles.groupMetaText}>👥 {group.members}</Text>
                  <Text style={styles.groupMetaText}>💬 {group.posts}</Text>
                </View>

                {/* Tags Row */}
                <View style={styles.groupTagsRow}>
                  {group.tags.map((tag, idx) => (
                    <View key={idx} style={styles.groupTagPill}>
                      <Text style={styles.groupTagText}>{tag}</Text>
                    </View>
                  ))}
                </View>

                {/* Join / View Action Button */}
                <TouchableOpacity
                  style={[
                    styles.groupActionBtn,
                    isJoined && styles.groupActionBtnJoined,
                  ]}
                  onPress={() => {
                    if (!isJoined) {
                      setJoinedState((prev) => ({ ...prev, [group.id]: true }));
                    }
                    setSelectedGroupId(group.id);
                    setActiveTab('group_details');
                  }}
                >
                  <Text
                    style={[
                      styles.groupActionBtnText,
                      isJoined && styles.groupActionBtnTextJoined,
                    ]}
                  >
                    {isJoined ? 'View Group' : 'Join Group'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          );
        })}
      </View>
    </ScrollView>
  );

  // Live Chat State & View
  const [chatInputText, setChatInputText] = useState('');
  const [chatMessages, setChatMessages] = useState([
    {
      id: '1',
      sender: 'agent',
      name: 'Nurse Sarah',
      time: '10:42 AM',
      text: 'Hello! Thank you for reaching out to the Caregiver Support Portal. How can I assist you with your verification process today?',
    },
    {
      id: '2',
      sender: 'user',
      name: user?.full_name || 'You',
      time: '10:45 AM',
      text: 'Hi Sarah, I submitted my documents yesterday but the status still says pending. Do you know how long it usually takes?',
    },
    {
      id: '3',
      sender: 'agent',
      name: 'Nurse Sarah',
      time: '10:46 AM',
      text: 'I can certainly check on that for you. Generally, standard verification takes about 2-3 business days. Let me pull up your file to see if everything was received clearly.',
    },
  ]);

  const handleSendChatMessage = () => {
    if (!chatInputText.trim()) return;

    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      name: user?.full_name || 'You',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: chatInputText.trim(),
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setChatInputText('');

    // Simulate Agent Automated Reply
    setTimeout(() => {
      const agentReply = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        name: 'Nurse Sarah',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: 'Thank you for providing that update! I have flagged your file for expedited review with our verification team. You should receive a confirmation email shortly.',
      };
      setChatMessages((prev) => [...prev, agentReply]);
    }, 1200);
  };

  const renderLiveChatView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Back Link Bar */}
      <View style={styles.chatBackBar}>
        <TouchableOpacity style={styles.chatBackBtn} onPress={() => setActiveTab('support')}>
          <Text style={styles.chatBackBtnText}>← Community</Text>
        </TouchableOpacity>
      </View>

      <View style={[styles.gridRow, !isWide && styles.columnLayout]}>
        {/* Left / Center Main Chat Interface */}
        <View style={styles.feedMainCol}>
          <View style={styles.chatContainerCard}>
            {/* Chat Header Bar */}
            <View style={styles.chatHeaderBar}>
              <View style={styles.agentInfoRow}>
                <View style={styles.agentAvatarCircle}>
                  <Text style={styles.agentAvatarText}>NS</Text>
                </View>

                <View style={styles.agentTitleCol}>
                  <Text style={styles.agentNameText}>Nurse Sarah</Text>
                  <View style={styles.agentRoleRow}>
                    <Text style={styles.agentRoleIcon}>🛡️</Text>
                    <Text style={styles.agentRoleText}>Support Specialist</Text>
                  </View>
                </View>
              </View>

              <View style={styles.chatHeaderRight}>
                <View style={styles.waitBadgeCard}>
                  <Text style={styles.waitBadgeCardText}>Wait: ~5 mins</Text>
                </View>
                <TouchableOpacity style={styles.chatOptionsBtn} onPress={() => Alert.alert('Chat Options', 'Session ID: #LIVE-88219')}>
                  <Text style={styles.chatOptionsIcon}>⋮</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Chat Thread Area */}
            <ScrollView style={styles.chatMessagesArea} contentContainerStyle={styles.chatMessagesContent}>
              {/* System Connection Pill */}
              <View style={styles.systemPillContainer}>
                <View style={styles.systemPill}>
                  <Text style={styles.systemPillText}>You are now connected with Sarah.</Text>
                </View>
              </View>

              {chatMessages.map((msg) => {
                const isUser = msg.sender === 'user';
                return (
                  <View key={msg.id} style={[styles.chatBubbleRow, isUser ? styles.chatBubbleRowUser : styles.chatBubbleRowAgent]}>
                    {!isUser && (
                      <View style={styles.chatSmallAvatar}>
                        <Text style={styles.chatSmallAvatarText}>NS</Text>
                      </View>
                    )}

                    <View style={[styles.chatBubble, isUser ? styles.chatBubbleUser : styles.chatBubbleAgent]}>
                      <Text style={[styles.chatBubbleText, isUser ? styles.chatBubbleTextUser : styles.chatBubbleTextAgent]}>
                        {msg.text}
                      </Text>
                      <Text style={[styles.chatTimeText, isUser ? styles.chatTimeTextUser : styles.chatTimeTextAgent]}>
                        {msg.time}
                      </Text>
                    </View>
                  </View>
                );
              })}
            </ScrollView>

            {/* Chat Input Bar */}
            <View style={styles.chatInputBar}>
              <TouchableOpacity style={styles.chatAttachBtn} onPress={() => Alert.alert('Attach File', 'Select document or image attachment')}>
                <Text style={styles.chatAttachIcon}>📎</Text>
              </TouchableOpacity>

              <TextInput
                style={styles.chatTextInput}
                placeholder="Type your message..."
                placeholderTextColor="#94A3B8"
                value={chatInputText}
                onChangeText={setChatInputText}
                onSubmitEditing={handleSendChatMessage}
              />

              <TouchableOpacity style={styles.chatEmojiBtn} onPress={() => Alert.alert('Emoji', 'Opening emoji picker...')}>
                <Text style={styles.chatEmojiIcon}>😊</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.chatSendBtn} onPress={handleSendChatMessage}>
                <Text style={styles.chatSendIcon}>➤</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Right Sidebar Column Widgets */}
        <View style={[styles.rightColWidgets, !isWide && styles.fullWidth]}>
          {/* Helpful Guides Widget */}
          <View style={styles.widgetCard}>
            <Text style={styles.widgetTitle}>Helpful Guides</Text>

            <TouchableOpacity style={styles.chatGuideItem} onPress={() => Alert.alert('Verification Checklist', 'Opening Checklist...')}>
              <Text style={styles.chatGuideIcon}>🧩</Text>
              <View style={styles.chatGuideTextCol}>
                <Text style={styles.chatGuideTitle}>Verification Checklist</Text>
                <Text style={styles.chatGuideSub}>Ensure you have all necessary documents ready for approval.</Text>
              </View>
            </TouchableOpacity>

            <TouchableOpacity style={styles.chatGuideItem} onPress={() => Alert.alert('Privacy Policy', 'Opening Privacy Policy...')}>
              <Text style={styles.chatGuideIcon}>🛡️</Text>
              <View style={styles.chatGuideTextCol}>
                <Text style={styles.chatGuideTitle}>Privacy Policy</Text>
                <Text style={styles.chatGuideSub}>Information on how we handle, store, and protect sensitive data.</Text>
              </View>
            </TouchableOpacity>
          </View>

          {/* Support Hours Widget */}
          <View style={styles.widgetCard}>
            <View style={styles.supportHoursHeader}>
              <Text style={styles.supportHoursIcon}>🕒</Text>
              <Text style={styles.supportHoursTitle}>Support Hours</Text>
            </View>
            <Text style={styles.supportHoursBody}>Mon - Fri: 9AM - 5PM EST</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  // Email Support Form State & View
  const [emailSubject, setEmailSubject] = useState('');
  const [emailCategory, setEmailCategory] = useState('Verification Assistance');
  const [emailPriority, setEmailPriority] = useState('Medium');
  const [emailMessage, setEmailMessage] = useState('');
  const [attachedFileName, setAttachedFileName] = useState(null);
  const [isSendingEmail, setIsSendingEmail] = useState(false);

  const handleSendEmailTicket = () => {
    if (!emailSubject.trim()) {
      Alert.alert('Required Field', 'Please enter a brief subject for your inquiry.');
      return;
    }
    if (!emailMessage.trim()) {
      Alert.alert('Required Field', 'Please enter detailed information about your inquiry.');
      return;
    }

    setIsSendingEmail(true);
    setTimeout(() => {
      setIsSendingEmail(false);
      Alert.alert(
        'Inquiry Sent! ✉️',
        'Thank you! Your support ticket (#TICK-9042) has been submitted. Our team will respond within 24 hours via email.',
        [
          {
            text: 'OK',
            onPress: () => {
              setEmailSubject('');
              setEmailMessage('');
              setAttachedFileName(null);
              setActiveTab('support');
            },
          },
        ]
      );
    }, 1000);
  };

  const renderEmailSupportView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Back to Support Options link */}
      <View style={styles.emailBackBar}>
        <TouchableOpacity style={styles.emailBackBtn} onPress={() => setActiveTab('support')}>
          <Text style={styles.emailBackBtnText}>← Back to Support Options</Text>
        </TouchableOpacity>
      </View>

      <View style={[styles.gridRow, !isWide && styles.columnLayout]}>
        {/* Left Main Email Form Card */}
        <View style={styles.feedMainCol}>
          <View style={styles.emailFormCard}>
            <Text style={styles.emailFormTitle}>Email Support</Text>
            <Text style={styles.emailFormSubtitle}>
              Fill out the form below to send us an inquiry. We aim to respond to all inquiries within 24 hours.
            </Text>

            {/* Inputs Row 1: Subject & Category */}
            <View style={[styles.formInputsRow, !isWide && styles.columnLayout]}>
              <View style={styles.formInputCol}>
                <Text style={styles.formInputLabel}>Subject *</Text>
                <TextInput
                  style={styles.formTextInput}
                  placeholder="Brief description of your issue"
                  placeholderTextColor="#94A3B8"
                  value={emailSubject}
                  onChangeText={setEmailSubject}
                />
              </View>

              <View style={styles.formInputCol}>
                <Text style={styles.formInputLabel}>Category *</Text>
                <TouchableOpacity
                  style={styles.formDropdownSelect}
                  onPress={() => Alert.alert('Select Category', 'Select category: Verification Assistance, Account Access, Group Support, Technical Issue')}
                >
                  <Text style={styles.formDropdownSelectText}>{emailCategory}</Text>
                  <Text style={styles.formDropdownChevron}>▼</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Priority Radio Row */}
            <View style={styles.prioritySection}>
              <Text style={styles.formInputLabel}>Priority</Text>
              <View style={styles.priorityOptionsRow}>
                {['Low', 'Medium', 'High'].map((level) => {
                  const isSelected = emailPriority === level;
                  return (
                    <TouchableOpacity
                      key={level}
                      style={styles.radioOptionBtn}
                      onPress={() => setEmailPriority(level)}
                    >
                      <View style={[styles.radioCircle, isSelected && styles.radioCircleSelected]}>
                        {isSelected && <View style={styles.radioInnerDot} />}
                      </View>
                      <Text style={styles.radioLabelText}>{level}</Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            {/* Message Textarea */}
            <View style={styles.formInputBlock}>
              <Text style={styles.formInputLabel}>Message *</Text>
              <TextInput
                style={[styles.formTextInput, styles.formTextAreaInput]}
                placeholder="Please provide detailed information about your inquiry..."
                placeholderTextColor="#94A3B8"
                multiline
                numberOfLines={6}
                value={emailMessage}
                onChangeText={setEmailMessage}
              />
            </View>

            {/* Attachments Box */}
            <View style={styles.attachmentsSection}>
              <Text style={styles.formInputLabel}>Attachments (Optional)</Text>
              <TouchableOpacity
                style={styles.dropzoneBox}
                onPress={() => {
                  setAttachedFileName('Document_Verification_Proof.pdf');
                  Alert.alert('File Attached', 'Attached document: Document_Verification_Proof.pdf');
                }}
              >
                <Text style={styles.dropzoneCloudIcon}>☁️</Text>
                <Text style={styles.dropzoneMainText}>
                  {attachedFileName ? `Attached: ${attachedFileName}` : 'Drag and drop files here or browse'}
                </Text>
                <Text style={styles.dropzoneSubText}>Supports JPG, PNG, PDF (Max 5MB)</Text>
              </TouchableOpacity>
            </View>

            {/* Form Footer Buttons */}
            <View style={styles.formFooterButtonsRow}>
              <TouchableOpacity style={styles.cancelFormBtn} onPress={() => setActiveTab('support')}>
                <Text style={styles.cancelFormBtnText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.sendFormBtn}
                onPress={handleSendEmailTicket}
                disabled={isSendingEmail}
              >
                {isSendingEmail ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <Text style={styles.sendFormBtnText}>Send Message »</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Right Sidebar Widgets Column */}
        <View style={[styles.rightColWidgets, !isWide && styles.fullWidth]}>
          {/* Response Time Card */}
          <View style={styles.purpleResponseCard}>
            <View style={styles.purpleResponseHeader}>
              <Text style={styles.purpleResponseHeaderIcon}>🕒</Text>
              <Text style={styles.purpleResponseHeaderTitle}>Response Time</Text>
            </View>

            <Text style={styles.purpleResponseBody}>
              Our typical response time for email inquiries is currently <Text style={{ fontWeight: '700' }}>within 24 hours</Text> during standard business days.
            </Text>

            <TouchableOpacity
              style={styles.purpleResponseChatPill}
              onPress={() => setActiveTab('livechat')}
            >
              <Text style={styles.purpleResponseChatPillText}>💬 Need faster help? Use Live Chat.</Text>
            </TouchableOpacity>
          </View>

          {/* Quick Links Card */}
          <View style={styles.widgetCard}>
            <Text style={styles.widgetTitle}>Quick Links</Text>

            <TouchableOpacity style={styles.quickLinkItem} onPress={() => setActiveTab('guidelines')}>
              <Text style={styles.quickLinkItemText}>Frequently Asked Questions</Text>
              <Text style={styles.quickLinkChevron}>›</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.quickLinkItem} onPress={() => Alert.alert('Verification Checklist', 'Opening Verification Checklist...')}>
              <Text style={styles.quickLinkItemText}>Verification Checklist</Text>
              <Text style={styles.quickLinkChevron}>›</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.quickLinkItem} onPress={() => Alert.alert('System Status', 'System Status: All Services Operational ✅')}>
              <Text style={styles.quickLinkItemText}>System Status</Text>
              <Text style={styles.quickLinkChevron}>›</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  // Group Details & Feed State & View
  const [selectedGroupId, setSelectedGroupId] = useState('group-1');
  const [groupPostInputText, setGroupPostInputText] = useState('');
  const [groupPostSearchQuery, setGroupPostSearchQuery] = useState('');

  const [groupPosts, setGroupPosts] = useState([
    {
      id: 'post-1',
      author: 'Sarah Jenkins',
      avatarBg: '#0284C7',
      avatarInitials: 'SJ',
      timestamp: '2 hours ago',
      content:
        "Hi everyone. We just received my son's official diagnosis yesterday. Feeling incredibly overwhelmed but glad I found this group. Does anyone have recommendations for navigating the first few weeks? The paperwork alone seems daunting.",
      likes: 24,
      commentsCount: 8,
      isLiked: false,
      isSaved: false,
    },
    {
      id: 'post-2',
      author: 'Marcus Reed',
      avatarBg: '#D97706',
      avatarInitials: 'MR',
      badge: 'MODERATOR',
      timestamp: 'Yesterday at 4:30 PM',
      title: 'Weekly Resource Thread 📌',
      content:
        "Drop your favorite helpful links, articles, or local services you've discovered this week below! Let's build our community knowledge base.",
      likes: 42,
      commentsCount: 19,
      isLiked: false,
      isSaved: false,
    },
  ]);

  const handleCreateGroupPost = () => {
    if (!groupPostInputText.trim()) {
      Alert.alert('Empty Post', 'Please type a message before sharing with the group.');
      return;
    }

    const newPostObj = {
      id: Date.now().toString(),
      author: user?.full_name || 'Caregiver User',
      avatarBg: '#4F46E5',
      avatarInitials: user?.full_name ? user.full_name[0] : 'U',
      timestamp: 'Just now',
      content: groupPostInputText.trim(),
      likes: 0,
      commentsCount: 0,
      isLiked: false,
      isSaved: false,
    };

    setGroupPosts((prev) => [newPostObj, ...prev]);
    setGroupPostInputText('');
    Alert.alert('Post Published! 🎉', 'Your message has been shared with group members.');
  };

  const toggleLikePost = (postId) => {
    setGroupPosts((prev) =>
      prev.map((p) => {
        if (p.id === postId) {
          const nextLiked = !p.isLiked;
          return {
            ...p,
            isLiked: nextLiked,
            likes: nextLiked ? p.likes + 1 : p.likes - 1,
          };
        }
        return p;
      })
    );
  };

  const toggleSavePost = (postId) => {
    setGroupPosts((prev) =>
      prev.map((p) => (p.id === postId ? { ...p, isSaved: !p.isSaved } : p))
    );
  };

  const filteredGroupPosts = groupPosts.filter((p) =>
    p.content.toLowerCase().includes(groupPostSearchQuery.toLowerCase()) ||
    (p.title && p.title.toLowerCase().includes(groupPostSearchQuery.toLowerCase())) ||
    p.author.toLowerCase().includes(groupPostSearchQuery.toLowerCase())
  );

  const renderGroupDetailsView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Top Group Hero Cover Banner Card */}
      <View style={styles.groupHeroCard}>
        <View style={styles.groupCoverBanner}>
          <View style={styles.groupHeroAvatarCircle}>
            <Text style={styles.groupHeroAvatarIcon}>👥</Text>
          </View>
        </View>

        <View style={styles.groupHeroDetailsRow}>
          <View style={styles.groupHeroTextCol}>
            <Text style={styles.groupHeroTitle}>Parents of Newly Diagnosed</Text>
            <Text style={styles.groupHeroSubtitle}>
              A supportive space for parents navigating recent diagnoses. Share experiences, resources, and find comfort in community.
            </Text>

            <View style={styles.groupHeroMetaRow}>
              <Text style={styles.groupHeroMetaText}>👥 1.2k Members</Text>
              <Text style={styles.groupHeroMetaText}>💬 14 posts today</Text>
            </View>
          </View>

          <TouchableOpacity style={styles.groupJoinedBtn} onPress={() => Alert.alert('Membership', 'You are a joined member of this group.')}>
            <Text style={styles.groupJoinedBtnText}>✓ Joined</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Main Grid Layout (2 Columns) */}
      <View style={[styles.gridRow, !isWide && styles.columnLayout]}>
        {/* Left Column: Post Composer + Search + Feed */}
        <View style={styles.feedMainCol}>
          {/* Post Composer Card */}
          <View style={styles.composerCard}>
            <View style={styles.composerHeaderRow}>
              <View style={styles.userAvatarCircle}>
                <Text style={styles.userAvatarCircleText}>{user?.full_name ? user.full_name[0] : 'U'}</Text>
              </View>

              <TextInput
                style={styles.composerInputArea}
                placeholder="Share an update, ask a question, or introduce yourself..."
                placeholderTextColor="#94A3B8"
                multiline
                value={groupPostInputText}
                onChangeText={setGroupPostInputText}
              />
            </View>

            <View style={styles.composerFooterRow}>
              <View style={styles.composerToolsRow}>
                <TouchableOpacity style={styles.toolIconBtn} onPress={() => Alert.alert('Add Photo', 'Select image from gallery')}>
                  <Text style={styles.toolIcon}>🖼️</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.toolIconBtn} onPress={() => Alert.alert('Add Emoji', 'Select emoji')}>
                  <Text style={styles.toolIcon}>😊</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.toolIconBtn} onPress={() => Alert.alert('Attach File', 'Select document attachment')}>
                  <Text style={styles.toolIcon}>📎</Text>
                </TouchableOpacity>
              </View>

              <TouchableOpacity style={styles.postSubmitBtn} onPress={handleCreateGroupPost}>
                <Text style={styles.postSubmitBtnText}>Post</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Group Post Search Bar Card */}
          <View style={styles.groupPostSearchCard}>
            <Text style={styles.searchBarIcon}>🔍</Text>
            <TextInput
              style={styles.searchBarInput}
              placeholder="Search posts in this group..."
              placeholderTextColor="#94A3B8"
              value={groupPostSearchQuery}
              onChangeText={setGroupPostSearchQuery}
            />
          </View>

          {/* Posts Feed */}
          {filteredGroupPosts.map((post) => (
            <View key={post.id} style={styles.postCard}>
              <View style={styles.postHeaderRow}>
                <View style={[styles.postAuthorAvatar, { backgroundColor: post.avatarBg }]}>
                  <Text style={styles.postAuthorAvatarText}>{post.avatarInitials}</Text>
                </View>

                <View style={styles.postAuthorCol}>
                  <View style={styles.postAuthorTitleRow}>
                    <Text style={styles.postAuthorName}>{post.author}</Text>
                    {post.badge && (
                      <View style={styles.moderatorBadge}>
                        <Text style={styles.moderatorBadgeText}>{post.badge}</Text>
                      </View>
                    )}
                  </View>
                  <Text style={styles.postTimestamp}>{post.timestamp}</Text>
                </View>

                <TouchableOpacity style={styles.postMenuBtn} onPress={() => Alert.alert('Options', 'Post options menu')}>
                  <Text style={styles.postMenuIcon}>•••</Text>
                </TouchableOpacity>
              </View>

              {post.title && <Text style={styles.postCardHeadline}>{post.title}</Text>}

              <Text style={styles.postCardBodyText}>{post.content}</Text>

              {/* Action Buttons Row */}
              <View style={styles.postActionRow}>
                <TouchableOpacity style={styles.actionItemBtn} onPress={() => toggleLikePost(post.id)}>
                  <Text style={[styles.actionItemIcon, post.isLiked && styles.actionItemIconActive]}>
                    {post.isLiked ? '👍' : '👍'}
                  </Text>
                  <Text style={[styles.actionItemText, post.isLiked && styles.actionItemTextActive]}>
                    {post.likes} Likes
                  </Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.actionItemBtn} onPress={() => Alert.alert('Comments', `Opening ${post.commentsCount} comments...`)}>
                  <Text style={styles.actionItemIcon}>💬</Text>
                  <Text style={styles.actionItemText}>{post.commentsCount} Comments</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.actionItemBtnRight} onPress={() => toggleSavePost(post.id)}>
                  <Text style={[styles.actionItemIcon, post.isSaved && styles.actionItemIconActive]}>
                    {post.isSaved ? '🔖' : '🔖'}
                  </Text>
                  <Text style={[styles.actionItemText, post.isSaved && styles.actionItemTextActive]}>
                    {post.isSaved ? 'Saved' : 'Save'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>

        {/* Right Column: About & Group Rules Sidebar */}
        <View style={[styles.rightColWidgets, !isWide && styles.fullWidth]}>
          {/* About Group Widget */}
          <View style={styles.widgetCard}>
            <View style={styles.widgetHeaderRow}>
              <Text style={styles.widgetHeaderIcon}>ℹ️</Text>
              <Text style={styles.widgetTitleText}>About</Text>
            </View>

            <Text style={styles.aboutBodyText}>
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

          {/* Group Rules Widget */}
          <View style={styles.widgetCard}>
            <View style={styles.widgetHeaderRow}>
              <Text style={styles.widgetHeaderIcon}>⚖️</Text>
              <Text style={styles.widgetTitleText}>Group Rules</Text>
            </View>

            <View style={styles.ruleItemBox}>
              <Text style={styles.ruleTitleText}>1. Be Kind and Courteous:</Text>
              <Text style={styles.ruleBodyText}>We're all in this together to create a welcoming environment. Let's treat everyone with respect.</Text>
            </View>

            <View style={styles.ruleItemBox}>
              <Text style={styles.ruleTitleText}>2. No Hate Speech or Bullying:</Text>
              <Text style={styles.ruleBodyText}>Make sure everyone feels safe. Bullying of any kind isn't allowed.</Text>
            </View>

            <View style={styles.ruleItemBox}>
              <Text style={styles.ruleTitleText}>3. Respect Privacy:</Text>
              <Text style={styles.ruleBodyText}>What's shared in the group should stay in the group.</Text>
            </View>

            <View style={styles.ruleItemBox}>
              <Text style={styles.ruleTitleText}>4. No Medical Advice:</Text>
              <Text style={styles.ruleBodyText}>Share experiences, but do not provide explicit medical directives.</Text>
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  // My Groups Joined Data State & View
  const myJoinedGroupsData = [
    {
      id: 'my-1',
      title: 'Dementia Support Network',
      badge: 'Joined',
      activeText: 'Active 2 hrs ago • "New guidelines for evening care routines..."',
      members: '1,240 Members',
      iconBg: '#EEF2FF',
      icon: '🤲',
    },
    {
      id: 'my-2',
      title: 'Pediatric Care Specialists',
      badge: 'Joined',
      activeText: 'Active 5 hrs ago • "Question about updated dosage charts..."',
      members: '856 Members',
      iconBg: '#FFFBEB',
      icon: '🩺',
    },
    {
      id: 'my-3',
      title: 'Caregiver Mental Wellness',
      badge: 'Joined',
      activeText: 'Active 1 day ago • "Weekly mindfulness session recording..."',
      members: '3,402 Members',
      iconBg: '#E0F2FE',
      icon: '🪷',
    },
  ];

  const recentActivityList = [
    {
      id: 'act-1',
      dotColor: '#0284C7',
      text: '"Has anyone experienced issues with the new charting software..."',
      groupName: 'Dementia Support Network',
      time: '2 hrs ago',
    },
    {
      id: 'act-2',
      dotColor: '#D97706',
      text: '"Reminder: Monthly Q&A session starts in 30 minutes. Link below."',
      groupName: 'Pediatric Care Specialists',
      time: '5 hrs ago',
    },
    {
      id: 'act-3',
      dotColor: '#0284C7',
      text: '"Posted a new resource on managing burnout during long..."',
      groupName: 'Caregiver Mental Wellness',
      time: '1 day ago',
    },
  ];

  const renderMyGroupsView = () => (
    <ScrollView contentContainerStyle={styles.scrollBody} showsVerticalScrollIndicator={false}>
      {/* Sub navigation tab pill bar */}
      <View style={styles.groupSubNavRow}>
        <TouchableOpacity style={styles.groupSubTabBtn} onPress={() => setActiveTab('directory')}>
          <Text style={styles.groupSubTabBtnText}>Browse Directory</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.groupSubTabBtn, styles.groupSubTabBtnActive]} onPress={() => setActiveTab('my_groups')}>
          <Text style={[styles.groupSubTabBtnText, styles.groupSubTabBtnTextActive]}>My Joined Groups (3)</Text>
        </TouchableOpacity>
      </View>

      {/* Page Title & Subtitle */}
      <View style={styles.myGroupsTitleBox}>
        <Text style={styles.groupsPageTitle}>My Groups</Text>
        <Text style={styles.groupsPageSubtitle}>Manage your community memberships and stay updated.</Text>
      </View>

      {/* Main Content Layout (2 Columns) */}
      <View style={[styles.gridRow, !isWide && styles.columnLayout]}>
        {/* Left Column: My Joined Groups List */}
        <View style={styles.feedMainCol}>
          {myJoinedGroupsData.map((group) => (
            <View key={group.id} style={styles.myGroupCardItem}>
              <View style={styles.myGroupLeftCol}>
                <View style={[styles.myGroupIconBox, { backgroundColor: group.iconBg }]}>
                  <Text style={styles.myGroupIcon}>{group.icon}</Text>
                </View>

                <View style={styles.myGroupTextCol}>
                  <View style={styles.myGroupTitleHeaderRow}>
                    <Text style={styles.myGroupTitle}>{group.title}</Text>
                    <View style={styles.joinedPillBadge}>
                      <Text style={styles.joinedPillBadgeText}>{group.badge}</Text>
                    </View>
                  </View>

                  <Text style={styles.myGroupActiveText}>{group.activeText}</Text>
                  <Text style={styles.myGroupMembersText}>👥 {group.members}</Text>
                </View>
              </View>

              <View style={styles.myGroupRightActions}>
                <TouchableOpacity
                  style={styles.openGroupBtn}
                  onPress={() => {
                    setSelectedGroupId(group.id);
                    setActiveTab('group_details');
                  }}
                >
                  <Text style={styles.openGroupBtnText}>Open Group</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.myGroupOptionsBtn}
                  onPress={() =>
                    Alert.alert('Group Options', `Manage notifications or leave ${group.title}?`, [
                      { text: 'Notification Settings', onPress: () => Alert.alert('Settings', 'Notifications enabled.') },
                      { text: 'Leave Group', style: 'destructive', onPress: () => Alert.alert('Left Group', `You left ${group.title}`) },
                      { text: 'Cancel', style: 'cancel' },
                    ])
                  }
                >
                  <Text style={styles.myGroupOptionsIcon}>⋮</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>

        {/* Right Column: Recent Activity Widget */}
        <View style={[styles.rightColWidgets, !isWide && styles.fullWidth]}>
          <View style={styles.widgetCard}>
            <View style={styles.widgetHeaderRow}>
              <Text style={styles.widgetHeaderIcon}>🕒</Text>
              <Text style={styles.widgetTitleText}>Recent Activity</Text>
            </View>

            {recentActivityList.map((item) => (
              <View key={item.id} style={styles.recentActivityItem}>
                <View style={[styles.activityDot, { backgroundColor: item.dotColor }]} />
                <View style={styles.activityContentCol}>
                  <Text style={styles.activityQuoteText}>{item.text}</Text>
                  <Text style={styles.activitySubText}>
                    {item.groupName} • {item.time}
                  </Text>
                </View>
              </View>
            ))}

            <TouchableOpacity
              style={styles.viewAllActivityBtn}
              onPress={() => Alert.alert('Activity Log', 'Opening full activity history log...')}
            >
              <Text style={styles.viewAllActivityBtnText}>View All Activity</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  return (
    <View style={styles.root}>
      {/* Top Floating View Switcher Header */}
      <View style={styles.topSwitcherBar}>
        <TouchableOpacity style={styles.backHomeBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backHomeBtnText}>← Community</Text>
        </TouchableOpacity>

        <View style={styles.switcherPill}>
          <TouchableOpacity
            style={[styles.switcherTab, showStatusPortal && activeTab === 'dashboard' && styles.switcherTabActive]}
            onPress={() => {
              setShowStatusPortal(true);
              setActiveTab('dashboard');
            }}
          >
            <Text style={[styles.switcherTabText, showStatusPortal && activeTab === 'dashboard' && styles.switcherTabTextActive]}>
              📊 Dashboard
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.switcherTab, showStatusPortal && (activeTab === 'groups' || activeTab === 'my_groups' || activeTab === 'group_details') && styles.switcherTabActive]}
            onPress={() => {
              setShowStatusPortal(true);
              setActiveTab('groups');
            }}
          >
            <Text style={[styles.switcherTabText, showStatusPortal && (activeTab === 'groups' || activeTab === 'my_groups' || activeTab === 'group_details') && styles.switcherTabTextActive]}>
              👥 Active Groups
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.switcherTab, showStatusPortal && activeTab === 'status' && styles.switcherTabActive]}
            onPress={() => {
              setShowStatusPortal(true);
              setActiveTab('status');
            }}
          >
            <Text style={[styles.switcherTabText, showStatusPortal && activeTab === 'status' && styles.switcherTabTextActive]}>
              🛡️ Verification Status
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.switcherTab, showStatusPortal && activeTab === 'guidelines' && styles.switcherTabActive]}
            onPress={() => {
              setShowStatusPortal(true);
              setActiveTab('guidelines');
            }}
          >
            <Text style={[styles.switcherTabText, showStatusPortal && activeTab === 'guidelines' && styles.switcherTabTextActive]}>
              📖 Guidelines
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.switcherTab, showStatusPortal && (activeTab === 'support' || activeTab === 'livechat' || activeTab === 'email') && styles.switcherTabActive]}
            onPress={() => {
              setShowStatusPortal(true);
              setActiveTab('support');
            }}
          >
            <Text style={[styles.switcherTabText, showStatusPortal && (activeTab === 'support' || activeTab === 'livechat' || activeTab === 'email') && styles.switcherTabTextActive]}>
              🎧 Support
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.switcherTab, !showStatusPortal && styles.switcherTabActive]}
            onPress={() => setShowStatusPortal(false)}
          >
            <Text style={[styles.switcherTabText, !showStatusPortal && styles.switcherTabTextActive]}>
              📝 Form
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Screen Body */}
      {showStatusPortal ? (
        <View style={styles.portalContainer}>
          {/* Left Sidebar Navigation */}
          {isWide && (
            <View style={styles.sidebar}>
              <View style={styles.brandContainer}>
                <View style={styles.brandIconBox}>
                  <Text style={styles.brandIcon}>🛡️</Text>
                </View>
                <View>
                  <Text style={styles.brandTitle}>Caregiver Portal</Text>
                  <View style={styles.brandBadge}>
                    <Text style={styles.brandBadgeText}>Verification In Progress</Text>
                  </View>
                </View>
              </View>

              <View style={styles.menuList}>
                <TouchableOpacity
                  style={[styles.menuItem, activeTab === 'dashboard' && styles.menuItemActive]}
                  onPress={() => setActiveTab('dashboard')}
                >
                  <Text style={styles.menuIcon}>📊</Text>
                  <Text style={[styles.menuText, activeTab === 'dashboard' && styles.menuTextActive]}>Dashboard</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.menuItem, (activeTab === 'groups' || activeTab === 'my_groups' || activeTab === 'group_details') && styles.menuItemActive]}
                  onPress={() => setActiveTab('groups')}
                >
                  <Text style={styles.menuIcon}>👥</Text>
                  <Text style={[styles.menuText, (activeTab === 'groups' || activeTab === 'my_groups' || activeTab === 'group_details') && styles.menuTextActive]}>Active Groups</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.menuItem, activeTab === 'status' && styles.menuItemActive]}
                  onPress={() => setActiveTab('status')}
                >
                  <Text style={styles.menuIcon}>🛡️</Text>
                  <Text style={[styles.menuText, activeTab === 'status' && styles.menuTextActive]}>Verification Status</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.menuItem, activeTab === 'guidelines' && styles.menuItemActive]}
                  onPress={() => setActiveTab('guidelines')}
                >
                  <Text style={styles.menuIcon}>📖</Text>
                  <Text style={[styles.menuText, activeTab === 'guidelines' && styles.menuTextActive]}>Community Guidelines</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.menuItem, (activeTab === 'support' || activeTab === 'livechat' || activeTab === 'email') && styles.menuItemActive]}
                  onPress={() => setActiveTab('support')}
                >
                  <Text style={styles.menuIcon}>🎧</Text>
                  <Text style={[styles.menuText, (activeTab === 'support' || activeTab === 'livechat' || activeTab === 'email') && styles.menuTextActive]}>Support Center</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.sidebarBottom}>
                <TouchableOpacity style={styles.menuItemSubtle} onPress={() => Alert.alert('Settings', 'Settings menu')}>
                  <Text style={styles.menuIcon}>⚙️</Text>
                  <Text style={styles.menuTextSubtle}>Settings</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.menuItemSubtle}
                  onPress={() => {
                    logout();
                    navigation.navigate('CommunityHome');
                  }}
                >
                  <Text style={styles.menuIcon}>🚪</Text>
                  <Text style={styles.menuTextSubtle}>Sign Out</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {/* Main Content View */}
          <View style={styles.mainContent}>
            {/* Top Header Bar */}
            <View style={styles.topHeader}>
              <Text style={styles.pageTitle}>
                {activeTab === 'dashboard'
                  ? 'Dashboard'
                  : activeTab === 'groups' || activeTab === 'my_groups' || activeTab === 'group_details'
                  ? 'Active Groups'
                  : activeTab === 'guidelines'
                  ? 'Community Guidelines'
                  : activeTab === 'support' || activeTab === 'livechat' || activeTab === 'email'
                  ? 'Support Center'
                  : 'Verification Status'}
              </Text>
              <View style={styles.topHeaderRight}>
                <TouchableOpacity style={styles.iconBtn}>
                  <Text style={styles.headerIcon}>🔔</Text>
                  <View style={styles.notificationDot} />
                </TouchableOpacity>
                <TouchableOpacity style={styles.iconBtn} onPress={handleSupportContact}>
                  <Text style={styles.headerIcon}>❓</Text>
                </TouchableOpacity>
                <View style={styles.userAvatar}>
                  <Text style={styles.userAvatarText}>{user?.full_name ? user.full_name[0] : 'U'}</Text>
                </View>
              </View>
            </View>

            {activeTab === 'dashboard'
              ? renderDashboardView()
              : activeTab === 'groups' || activeTab === 'my_groups'
              ? renderMyGroupsView()
              : activeTab === 'directory'
              ? renderGroupsView()
              : activeTab === 'group_details'
              ? renderGroupDetailsView()
              : activeTab === 'guidelines'
              ? renderGuidelinesView()
              : activeTab === 'email'
              ? renderEmailSupportView()
              : activeTab === 'livechat'
              ? renderLiveChatView()
              : activeTab === 'support'
              ? renderSupportView()
              : renderStatusView()}
          </View>
        </View>
      ) : (
        renderFormView()
      )}
    </View>
  );



}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  topSwitcherBar: {
    height: 52,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    zIndex: 100,
  },
  backHomeBtn: {
    paddingVertical: 6,
    paddingHorizontal: 10,
  },
  backHomeBtnText: {
    color: '#4F46E5',
    fontSize: 14,
    fontWeight: '600',
  },
  switcherPill: {
    flexDirection: 'row',
    backgroundColor: '#F1F5F9',
    borderRadius: 20,
    padding: 3,
  },
  switcherTab: {
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 16,
  },
  switcherTabActive: {
    backgroundColor: '#4F46E5',
  },
  switcherTabText: {
    color: '#64748B',
    fontSize: 12,
    fontWeight: '600',
  },
  switcherTabTextActive: {
    color: '#FFFFFF',
  },
  portalContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
  },
  sidebar: {
    width: 240,
    backgroundColor: '#FFFFFF',
    borderRightWidth: 1,
    borderRightColor: '#E2E8F0',
    padding: 20,
    justifyContent: 'space-between',
  },
  brandContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 32,
  },
  brandIconBox: {
    width: 38,
    height: 38,
    borderRadius: 10,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  brandIcon: {
    fontSize: 20,
  },
  brandTitle: {
    color: '#0F172A',
    fontSize: 15,
    fontWeight: '700',
  },
  brandBadge: {
    marginTop: 3,
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#FCD34D',
  },
  brandBadgeText: {
    color: '#D97706',
    fontSize: 10,
    fontWeight: '700',
  },
  menuList: {
    flex: 1,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 10,
    marginBottom: 6,
  },
  menuItemActive: {
    backgroundColor: '#EEF2FF',
  },
  menuIcon: {
    fontSize: 16,
    marginRight: 12,
  },
  menuText: {
    color: '#64748B',
    fontSize: 14,
    fontWeight: '500',
  },
  menuTextActive: {
    color: '#4F46E5',
    fontWeight: '700',
  },
  sidebarBottom: {
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingTop: 16,
  },
  menuItemSubtle: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  menuTextSubtle: {
    color: '#94A3B8',
    fontSize: 13,
    fontWeight: '500',
  },
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
    paddingHorizontal: 24,
  },
  pageTitle: {
    color: '#0F172A',
    fontSize: 20,
    fontWeight: '700',
  },
  topHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12,
    position: 'relative',
  },
  headerIcon: {
    fontSize: 16,
  },
  notificationDot: {
    position: 'absolute',
    top: 6,
    right: 8,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444',
  },
  userAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 14,
  },
  userAvatarText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  scrollBody: {
    padding: 24,
  },
  gridRow: {
    flexDirection: 'row',
    marginBottom: 28,
  },
  columnLayout: {
    flexDirection: 'column',
  },
  fullWidth: {
    width: '100%',
    marginTop: 16,
  },
  feedMainCol: {
    flex: 2,
    marginRight: 16,
  },
  composerCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  composerRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  composerAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  composerAvatarText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  composerInput: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    padding: 12,
    color: '#0F172A',
    fontSize: 14,
    minHeight: 64,
    textAlignVertical: 'top',
  },
  composerActionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 10,
  },
  composerTools: {
    flexDirection: 'row',
  },
  toolBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  toolIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  toolText: {
    color: '#64748B',
    fontSize: 13,
    fontWeight: '600',
  },
  postSubmitBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 8,
    paddingHorizontal: 20,
    borderRadius: 10,
  },
  postSubmitBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  postCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  postHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  authorRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  authorAvatar: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#0284C7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  authorAvatarText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  authorName: {
    color: '#0F172A',
    fontSize: 15,
    fontWeight: '700',
  },
  postTime: {
    color: '#94A3B8',
    fontSize: 12,
    marginTop: 1,
  },
  tagBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 14,
  },
  tagBadgeIcon: {
    fontSize: 12,
    marginRight: 6,
  },
  tagBadgeText: {
    color: '#475569',
    fontSize: 12,
    fontWeight: '600',
  },
  postContent: {
    color: '#334155',
    fontSize: 14,
    lineHeight: 22,
    marginBottom: 16,
  },
  postFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 12,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 24,
  },
  actionIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  actionCount: {
    color: '#64748B',
    fontSize: 13,
    fontWeight: '600',
  },
  rightColWidgets: {
    flex: 1,
    justifyContent: 'flex-start',
  },
  widgetCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  widgetHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  widgetTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  widgetTitleIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  widgetTitle: {
    color: '#0F172A',
    fontSize: 16,
    fontWeight: '700',
  },
  widgetLink: {
    color: '#4F46E5',
    fontSize: 13,
    fontWeight: '600',
  },
  groupItem: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  groupItemName: {
    color: '#0F172A',
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 2,
  },
  groupItemSub: {
    color: '#64748B',
    fontSize: 12,
  },
  eventItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  eventDateBox: {
    width: 48,
    height: 48,
    borderRadius: 10,
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  eventMonth: {
    color: '#94A3B8',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  eventDay: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '800',
  },
  eventContent: {
    flex: 1,
  },
  eventTitle: {
    color: '#0F172A',
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 2,
  },
  eventSubRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  eventSubIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  eventSubText: {
    color: '#64748B',
    fontSize: 12,
  },
  applicationCard: {
    flex: 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginRight: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  applicationHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  applicationTitle: {
    color: '#0F172A',
    fontSize: 22,
    fontWeight: '700',
  },
  pendingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    borderWidth: 1,
    borderColor: '#FCD34D',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  pendingDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#D97706',
    marginRight: 6,
  },
  pendingBadgeText: {
    color: '#D97706',
    fontSize: 11,
    fontWeight: '700',
  },
  applicationBody: {
    color: '#475569',
    fontSize: 14,
    lineHeight: 22,
    marginBottom: 24,
  },
  nextStepsBox: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  nextStepsTitle: {
    color: '#0F172A',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 16,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  stepIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  stepIcon: {
    fontSize: 16,
  },
  stepTextContent: {
    flex: 1,
  },
  stepTitle: {
    color: '#1E293B',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  stepDescription: {
    color: '#64748B',
    fontSize: 13,
    lineHeight: 18,
  },
  purpleHelpCard: {
    backgroundColor: '#4F46E5',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#4F46E5',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 3,
  },
  purpleIconBox: {
    width: 38,
    height: 38,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
  },
  purpleIcon: {
    fontSize: 20,
  },
  purpleCardTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 8,
  },
  purpleCardBody: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: 13,
    lineHeight: 19,
    marginBottom: 18,
  },
  supportPillBtn: {
    backgroundColor: '#0F172A',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  supportPillBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
  },
  secureCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
  },
  secureIconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  secureIcon: {
    fontSize: 20,
  },
  secureTextCol: {
    flex: 1,
  },
  secureTitle: {
    color: '#0F172A',
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 2,
  },
  secureBody: {
    color: '#64748B',
    fontSize: 12,
  },
  resourcesSection: {
    marginTop: 8,
  },
  resourcesSectionTitle: {
    color: '#0F172A',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
  },
  resourceGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  resourceCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
    marginRight: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  resourceBannerImage: {
    width: '100%',
    height: 120,
  },
  resourceContent: {
    padding: 16,
  },
  resourceTagRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  resourceTagIcon: {
    fontSize: 12,
    marginRight: 6,
  },
  resourceTagText: {
    color: '#0284C7',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  resourceCardTitle: {
    color: '#0F172A',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 6,
  },
  resourceCardSubtitle: {
    color: '#64748B',
    fontSize: 12,
    lineHeight: 18,
  },
  formContainer: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  formContent: {
    padding: 24,
  },
  backButton: {
    marginBottom: 16,
  },
  backButtonText: {
    color: '#4F46E5',
    fontSize: 15,
    fontWeight: '600',
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  badgeIcon: {
    fontSize: 36,
    marginRight: 14,
  },
  headerTextCol: {
    flex: 1,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 13,
    color: '#4F46E5',
    marginTop: 2,
  },
  description: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 20,
    marginBottom: 20,
  },
  statusBox: {
    backgroundColor: '#F8FAFC',
    padding: 14,
    borderRadius: 10,
    marginBottom: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  statusLabel: {
    fontSize: 13,
    color: '#64748B',
  },
  statusValue: {
    fontSize: 13,
    fontWeight: '700',
    color: '#D97706',
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    padding: 14,
    color: '#0F172A',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    marginBottom: 18,
    fontSize: 14,
  },
  textArea: {
    textAlignVertical: 'top',
    minHeight: 90,
  },
  submitBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  submitBtnText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  toggleModeBtn: {
    marginTop: 16,
    alignItems: 'center',
    paddingVertical: 10,
  },
  toggleModeBtnText: {
    color: '#4F46E5',
    fontSize: 14,
    fontWeight: '600',
  },
  // Community Guidelines Styles
  guidelinesHeader: {
    marginBottom: 24,
  },
  guidelinesTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 8,
  },
  guidelinesSubtitle: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 22,
  },
  sectionBlock: {
    marginBottom: 28,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitleIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0F172A',
  },
  gridRow3: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  valueCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginRight: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  valueIconCircle: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
  },
  valueIcon: {
    fontSize: 22,
  },
  valueCardTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 6,
  },
  valueCardBody: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 19,
  },
  ruleCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  ruleHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  ruleIcon: {
    fontSize: 20,
    marginRight: 10,
  },
  ruleTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
  },
  ruleBody: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 21,
  },
  calloutBox: {
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginTop: 12,
  },
  doText: {
    fontSize: 13,
    color: '#1E293B',
    marginBottom: 4,
  },
  dontText: {
    fontSize: 13,
    color: '#1E293B',
  },
  reportingCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  reportingContent: {
    flex: 1,
    marginRight: 16,
  },
  reportingHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  reportingIcon: {
    fontSize: 20,
    marginRight: 10,
  },
  reportingTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  reportingBody: {
    fontSize: 13,
    color: '#94A3B8',
    lineHeight: 18,
  },
  contactModeratorBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 10,
  },
  contactModeratorBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  guidelinesFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingTop: 16,
    marginTop: 8,
  },
  guidelinesFooterText: {
    fontSize: 12,
    color: '#64748B',
  },
  guidelinesFooterDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  // Support Center Styles
  supportHeroCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  supportHeroTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 6,
    textAlign: 'center',
  },
  supportHeroSubtitle: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 20,
    textAlign: 'center',
  },
  searchBarBox: {
    width: '100%',
    maxWidth: 540,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  searchBarIcon: {
    fontSize: 16,
    marginRight: 10,
  },
  searchBarInput: {
    flex: 1,
    fontSize: 14,
    color: '#0F172A',
  },
  sectionHeaderTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 16,
  },
  contactMethodsCol: {
    flex: 1,
    marginRight: 16,
  },
  contactCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  contactHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  contactIconBox: {
    width: 42,
    height: 42,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  contactIcon: {
    fontSize: 20,
  },
  contactTextContent: {
    flex: 1,
  },
  contactTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 2,
  },
  contactSubtitle: {
    fontSize: 13,
    color: '#64748B',
  },
  contactBadgeRow: {
    flexDirection: 'row',
  },
  amberWaitBadge: {
    backgroundColor: '#FEF3C7',
    borderWidth: 1,
    borderColor: '#FCD34D',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 8,
  },
  amberWaitBadgeText: {
    color: '#D97706',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  blueWaitBadge: {
    backgroundColor: '#E0F2FE',
    borderWidth: 1,
    borderColor: '#BAE6FD',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 8,
  },
  blueWaitBadgeText: {
    color: '#0284C7',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  greenWaitBadge: {
    backgroundColor: '#D1FAE5',
    borderWidth: 1,
    borderColor: '#6EE7B7',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 8,
  },
  greenWaitBadgeText: {
    color: '#059669',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  faqAndGuidesCol: {
    flex: 2,
  },
  faqSection: {
    marginBottom: 24,
  },
  faqContainerCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    paddingHorizontal: 20,
    paddingVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  faqItem: {
    paddingVertical: 14,
  },
  faqBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  faqHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  faqQuestionText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#0F172A',
    flex: 1,
    marginRight: 12,
  },
  faqChevronIcon: {
    fontSize: 12,
    color: '#64748B',
  },
  faqAnswerText: {
    fontSize: 13,
    color: '#475569',
    lineHeight: 20,
    marginTop: 10,
  },
  guidesSection: {
    marginBottom: 20,
  },
  guidesGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  guideCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginRight: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  guideHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  guideIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  guideTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  guideBody: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 18,
  },
  // Active Groups Styles
  groupsHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  groupsHeaderTitleCol: {
    flex: 1,
  },
  groupsPageTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  groupsPageSubtitle: {
    fontSize: 14,
    color: '#64748B',
  },
  createGroupBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 10,
    paddingHorizontal: 18,
    borderRadius: 10,
  },
  createGroupBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  groupSearchFilterCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 24,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  groupSearchInputBox: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    paddingHorizontal: 14,
    paddingVertical: 8,
    marginRight: 16,
  },
  groupFilterDropdowns: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterDropdownPill: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 12,
  },
  filterDropdownLabel: {
    fontSize: 13,
    color: '#64748B',
    marginRight: 4,
  },
  filterDropdownValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#0F172A',
  },
  groupCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
    marginRight: 14,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  groupBannerHeader: {
    height: 100,
    position: 'relative',
    justifyContent: 'flex-end',
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  groupAvatarCircle: {
    width: 44,
    height: 44,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3,
  },
  groupAvatarIcon: {
    fontSize: 22,
  },
  groupCardBody: {
    padding: 20,
  },
  groupCardTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 6,
  },
  groupCardDescription: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 19,
    marginBottom: 14,
  },
  groupMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  groupMetaText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748B',
  },
  groupTagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 18,
  },
  groupTagPill: {
    backgroundColor: '#F1F5F9',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
    marginRight: 6,
    marginBottom: 6,
  },
  groupTagText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
  },
  groupActionBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  groupActionBtnJoined: {
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  groupActionBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  groupActionBtnTextJoined: {
    color: '#475569',
  },
  // Live Chat Styles
  chatBackBar: {
    marginBottom: 16,
  },
  chatBackBtn: {
    alignSelf: 'flex-start',
  },
  chatBackBtnText: {
    color: '#4F46E5',
    fontSize: 14,
    fontWeight: '600',
  },
  chatContainerCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  chatHeaderBar: {
    height: 64,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
  },
  agentInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  agentAvatarCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#0284C7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  agentAvatarText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  agentTitleCol: {},
  agentNameText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0F172A',
  },
  agentRoleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  agentRoleIcon: {
    fontSize: 11,
    marginRight: 4,
  },
  agentRoleText: {
    fontSize: 12,
    color: '#64748B',
  },
  chatHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  waitBadgeCard: {
    backgroundColor: '#FEF3C7',
    borderWidth: 1,
    borderColor: '#FCD34D',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
    marginRight: 10,
  },
  waitBadgeCardText: {
    color: '#D97706',
    fontSize: 11,
    fontWeight: '700',
  },
  chatOptionsBtn: {
    padding: 6,
  },
  chatOptionsIcon: {
    fontSize: 18,
    color: '#64748B',
    fontWeight: '700',
  },
  chatMessagesArea: {
    height: 380,
    backgroundColor: '#F8FAFC',
  },
  chatMessagesContent: {
    padding: 20,
  },
  systemPillContainer: {
    alignItems: 'center',
    marginVertical: 14,
  },
  systemPill: {
    backgroundColor: '#E2E8F0',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 14,
  },
  systemPillText: {
    fontSize: 12,
    color: '#475569',
    fontWeight: '500',
  },
  chatBubbleRow: {
    flexDirection: 'row',
    marginBottom: 14,
  },
  chatBubbleRowAgent: {
    justifyContent: 'flex-start',
  },
  chatBubbleRowUser: {
    justifyContent: 'flex-end',
  },
  chatSmallAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#0284C7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
    marginTop: 2,
  },
  chatSmallAvatarText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
  },
  chatBubble: {
    maxWidth: '75%',
    borderRadius: 16,
    padding: 14,
  },
  chatBubbleAgent: {
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderTopLeftRadius: 4,
  },
  chatBubbleUser: {
    backgroundColor: '#4F46E5',
    borderTopRightRadius: 4,
  },
  chatBubbleText: {
    fontSize: 14,
    lineHeight: 20,
  },
  chatBubbleTextAgent: {
    color: '#0F172A',
  },
  chatBubbleTextUser: {
    color: '#FFFFFF',
  },
  chatTimeText: {
    fontSize: 10,
    marginTop: 6,
    alignSelf: 'flex-end',
  },
  chatTimeTextAgent: {
    color: '#94A3B8',
  },
  chatTimeTextUser: {
    color: 'rgba(255, 255, 255, 0.75)',
  },
  chatInputBar: {
    height: 60,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  chatAttachBtn: {
    padding: 8,
    marginRight: 8,
  },
  chatAttachIcon: {
    fontSize: 18,
    color: '#64748B',
  },
  chatTextInput: {
    flex: 1,
    height: 40,
    backgroundColor: '#F8FAFC',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    paddingHorizontal: 16,
    color: '#0F172A',
    fontSize: 14,
  },
  chatEmojiBtn: {
    padding: 8,
    marginLeft: 8,
  },
  chatEmojiIcon: {
    fontSize: 18,
  },
  chatSendBtn: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 10,
  },
  chatSendIcon: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  chatGuideItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  chatGuideIcon: {
    fontSize: 18,
    marginRight: 10,
    marginTop: 2,
  },
  chatGuideTextCol: {
    flex: 1,
  },
  chatGuideTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 2,
  },
  chatGuideSub: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 16,
  },
  supportHoursHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  supportHoursIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  supportHoursTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  supportHoursBody: {
    fontSize: 13,
    color: '#64748B',
  },
  // Email Support Form Styles
  emailBackBar: {
    marginBottom: 16,
  },
  emailBackBtn: {
    alignSelf: 'flex-start',
  },
  emailBackBtnText: {
    color: '#4F46E5',
    fontSize: 14,
    fontWeight: '600',
  },
  emailFormCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  emailFormTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  emailFormSubtitle: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 20,
  },
  formInputsRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  formInputCol: {
    flex: 1,
    marginRight: 12,
  },
  formInputBlock: {
    marginBottom: 16,
  },
  formInputLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 6,
  },
  formTextInput: {
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
    color: '#0F172A',
  },
  formTextAreaInput: {
    height: 120,
    textAlignVertical: 'top',
  },
  formDropdownSelect: {
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    paddingHorizontal: 14,
    paddingVertical: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  formDropdownSelectText: {
    fontSize: 14,
    color: '#0F172A',
  },
  formDropdownChevron: {
    fontSize: 11,
    color: '#64748B',
  },
  prioritySection: {
    marginBottom: 16,
  },
  priorityOptionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  radioOptionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 24,
  },
  radioCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  radioCircleSelected: {
    borderColor: '#4F46E5',
  },
  radioInnerDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#4F46E5',
  },
  radioLabelText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0F172A',
  },
  attachmentsSection: {
    marginBottom: 24,
  },
  dropzoneBox: {
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: '#CBD5E1',
    borderRadius: 12,
    backgroundColor: '#F8FAFC',
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dropzoneCloudIcon: {
    fontSize: 28,
    marginBottom: 6,
  },
  dropzoneMainText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0F172A',
    marginBottom: 4,
    textAlign: 'center',
  },
  dropzoneSubText: {
    fontSize: 12,
    color: '#94A3B8',
    textAlign: 'center',
  },
  formFooterButtonsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  cancelFormBtn: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    backgroundColor: '#FFFFFF',
    marginRight: 12,
  },
  cancelFormBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
  },
  sendFormBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 11,
    paddingHorizontal: 22,
    borderRadius: 10,
  },
  sendFormBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  purpleResponseCard: {
    backgroundColor: '#4F46E5',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  purpleResponseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  purpleResponseHeaderIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  purpleResponseHeaderTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  purpleResponseBody: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: 19,
    marginBottom: 16,
  },
  purpleResponseChatPill: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignItems: 'center',
  },
  purpleResponseChatPillText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#4F46E5',
  },
  quickLinkItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  quickLinkItemText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#0F172A',
  },
  quickLinkChevron: {
    fontSize: 16,
    color: '#94A3B8',
  },
  // Group Details & Feed Styles
  groupHeroCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    overflow: 'hidden',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  groupCoverBanner: {
    height: 140,
    backgroundColor: '#C7D2FE',
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
  },
  groupHeroAvatarCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
    elevation: 4,
  },
  groupHeroAvatarIcon: {
    fontSize: 28,
  },
  groupHeroDetailsRow: {
    padding: 24,
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
  },
  groupHeroTextCol: {
    flex: 1,
    marginRight: 20,
  },
  groupHeroTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 6,
  },
  groupHeroSubtitle: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
    marginBottom: 14,
  },
  groupHeroMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  groupHeroMetaText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
    marginRight: 16,
  },
  groupJoinedBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
  },
  groupJoinedBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  groupPostSearchCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginBottom: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 4,
    elevation: 1,
  },
  widgetHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  widgetHeaderIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  widgetTitleText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
  },
  aboutBodyText: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 19,
    marginBottom: 14,
  },
  aboutMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  aboutMetaIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  aboutMetaText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#475569',
  },
  ruleItemBox: {
    marginBottom: 12,
  },
  ruleTitleText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 2,
  },
  ruleBodyText: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 17,
  },
  // My Groups Styles
  groupSubNavRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  groupSubTabBtn: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#F1F5F9',
    marginRight: 10,
  },
  groupSubTabBtnActive: {
    backgroundColor: '#4F46E5',
  },
  groupSubTabBtnText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
  },
  groupSubTabBtnTextActive: {
    color: '#FFFFFF',
  },
  myGroupsTitleBox: {
    marginBottom: 20,
  },
  myGroupCardItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 20,
    marginBottom: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  myGroupLeftCol: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  myGroupIconBox: {
    width: 52,
    height: 52,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  myGroupIcon: {
    fontSize: 24,
  },
  myGroupTextCol: {
    flex: 1,
  },
  myGroupTitleHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  myGroupTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginRight: 10,
  },
  joinedPillBadge: {
    backgroundColor: '#E0E7FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  joinedPillBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#4F46E5',
  },
  myGroupActiveText: {
    fontSize: 13,
    color: '#475569',
    marginBottom: 4,
  },
  myGroupMembersText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748B',
  },
  myGroupRightActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  openGroupBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 10,
    paddingHorizontal: 18,
    borderRadius: 10,
    marginRight: 10,
  },
  openGroupBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
  },
  myGroupOptionsBtn: {
    padding: 6,
  },
  myGroupOptionsIcon: {
    fontSize: 18,
    color: '#64748B',
    fontWeight: '700',
  },
  recentActivityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 6,
    marginRight: 10,
  },
  activityContentCol: {
    flex: 1,
  },
  activityQuoteText: {
    fontSize: 13,
    color: '#0F172A',
    lineHeight: 18,
    marginBottom: 4,
  },
  activitySubText: {
    fontSize: 11,
    color: '#64748B',
  },
  viewAllActivityBtn: {
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
    marginTop: 14,
    backgroundColor: '#FFFFFF',
  },
  viewAllActivityBtnText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#0F172A',
  },
});

