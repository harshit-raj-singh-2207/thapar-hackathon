import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { communityApi } from '../../services/api/communityApi';
import { useChatStore } from '../../store/chatStore';

export default function CaregiverProfileScreen({ route, navigation }) {
  const { userId } = route.params || {};
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const { startChat } = useChatStore();

  useEffect(() => {
    if (userId) {
      loadProfile();
    }
  }, [userId]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = await communityApi.getCaregiverProfile(userId);
      setProfile(data);
    } catch (err) {
      Alert.alert('Error', err.detail || 'Could not load caregiver profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartChat = async () => {
    try {
      const chat = await startChat(userId);
      navigation.navigate('DirectMessage', {
        chatId: chat.id,
        recipientId: userId,
        name: profile?.name,
      });
    } catch (err) {
      Alert.alert('Chat Error', err.detail || 'Failed to start direct message.');
    }
  };

  const handleBlock = async () => {
    Alert.alert('Block Caregiver', 'Are you sure you want to block this caregiver?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Block',
        style: 'destructive',
        onPress: async () => {
          try {
            await communityApi.blockCaregiver(userId);
            Alert.alert('Blocked', 'Caregiver has been blocked.');
            navigation.goBack();
          } catch (err) {
            Alert.alert('Error', err.detail || 'Could not block caregiver.');
          }
        },
      },
    ]);
  };

  const handleReport = async () => {
    Alert.alert('Report Caregiver', 'Why are you reporting this caregiver profile?', [
      { text: 'Inappropriate content', onPress: () => sendReport('Inappropriate content') },
      { text: 'Harassment / Spam', onPress: () => sendReport('Harassment or spam') },
      { text: 'Unverified claim', onPress: () => sendReport('Unverified claim') },
      { text: 'Cancel', style: 'cancel' },
    ]);
  };

  const sendReport = async (reason) => {
    try {
      await communityApi.submitReport({ target_type: 'user', target_id: userId, reason });
      Alert.alert('Reported', 'Thank you for reporting. Our safety team will review this profile.');
    } catch (err) {
      Alert.alert('Error', err.detail || 'Could not submit report.');
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header Bar */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Caregiver Profile</Text>
        <View style={{ width: 40 }} />
      </View>

      {/* Avatar & Verification Badge */}
      <View style={styles.avatarSection}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{profile?.name ? profile.name[0] : 'C'}</Text>
        </View>
        <Text style={styles.name}>{profile?.name}</Text>
        {profile?.is_verified && (
          <View style={styles.verifiedBadge}>
            <Text style={styles.verifiedBadgeText}>✓ Verified Caregiver</Text>
          </View>
        )}
        <View style={styles.statusRow}>
          <View style={[styles.statusDot, profile?.is_online ? styles.onlineDot : styles.offlineDot]} />
          <Text style={styles.statusText}>{profile?.is_online ? 'Online' : 'Offline'}</Text>
        </View>
      </View>

      {/* Bio Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Bio & Role</Text>
        <Text style={styles.bioText}>{profile?.bio || 'Parent caregiver on NIVARA.'}</Text>
      </View>

      {/* Action Buttons */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.chatBtn} onPress={handleStartChat}>
          <Text style={styles.chatBtnText}>💬 Start Direct Message</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.reportBtn} onPress={handleReport}>
          <Text style={styles.reportBtnText}>🚩 Report Caregiver</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.blockBtn} onPress={handleBlock}>
          <Text style={styles.blockBtnText}>🚫 Block Caregiver</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backText: {
    fontSize: 16,
    color: '#4F46E5',
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0F172A',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarSection: {
    alignItems: 'center',
    paddingVertical: 24,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatarText: {
    color: '#FFFFFF',
    fontSize: 32,
    fontWeight: '700',
  },
  name: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 6,
  },
  verifiedBadge: {
    backgroundColor: '#DCFCE7',
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 16,
    marginBottom: 8,
  },
  verifiedBadgeText: {
    color: '#15803D',
    fontWeight: '600',
    fontSize: 13,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  onlineDot: {
    backgroundColor: '#22C55E',
  },
  offlineDot: {
    backgroundColor: '#94A3B8',
  },
  statusText: {
    fontSize: 13,
    color: '#64748B',
  },
  card: {
    margin: 16,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#334155',
    marginBottom: 8,
  },
  bioText: {
    fontSize: 15,
    color: '#475569',
    lineHeight: 22,
  },
  actions: {
    padding: 16,
    gap: 12,
  },
  chatBtn: {
    backgroundColor: '#4F46E5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  chatBtnText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  reportBtn: {
    backgroundColor: '#FEF2F2',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#FCA5A5',
  },
  reportBtnText: {
    color: '#DC2626',
    fontSize: 15,
    fontWeight: '600',
  },
  blockBtn: {
    backgroundColor: '#F8FAFC',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  blockBtnText: {
    color: '#64748B',
    fontSize: 15,
    fontWeight: '600',
  },
});
