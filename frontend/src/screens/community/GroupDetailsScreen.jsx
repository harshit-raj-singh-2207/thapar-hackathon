import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  SafeAreaView,
} from 'react-native';
import { useCommunityStore } from '../../store/communityStore';

export default function GroupDetailsScreen({ route, navigation }) {
  const { groupId } = route.params || {};
  const { groups, joinGroup, leaveGroup } = useCommunityStore();
  const group = groups.find((g) => g.id === groupId) || {
    id: groupId || 'default-1',
    name: 'Parents of Newly Diagnosed',
    description:
      'A supportive space for parents and guardians navigating recent diagnoses. Share experiences, resources, and find comfort in a community that understands your journey.',
    category: 'Sensory',
    member_count: 1200,
    is_joined: true,
    created_at: 'March 2023',
    privacy: 'Public Group (Visible in Directory)',
  };

  const handleToggleJoin = async () => {
    try {
      if (group.is_joined) {
        await leaveGroup(group.id);
        Alert.alert('Left Group', 'You have left the group.');
      } else {
        await joinGroup(group.id);
        Alert.alert('Joined!', 'Welcome to the group. You can now participate in group chat.');
      }
    } catch (err) {
      Alert.alert('Error', err.detail || 'Action failed.');
    }
  };

  const formattedDate = group.created_at
    ? typeof group.created_at === 'string' && group.created_at.includes('March')
      ? group.created_at
      : new Date(group.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : 'March 2023';

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header Navigation */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Group Details</Text>
          <View style={{ width: 60 }} />
        </View>

        {/* Main Content Area */}
        <ScrollView style={styles.scrollCanvas} contentContainerStyle={styles.scrollContent}>
          {/* Main Hero Group Info Header */}
          <View style={styles.heroCard}>
            <View style={styles.iconCircle}>
              <Text style={styles.iconText}>👥</Text>
            </View>
            <Text style={styles.name}>{group.name}</Text>
            <Text style={styles.categoryBadge}>{group.category || 'General Support'}</Text>
            <Text style={styles.description}>{group.description}</Text>
            <Text style={styles.memberCount}>👥 {group.member_count || 1} Members</Text>

            <TouchableOpacity
              style={[styles.mainBtn, group.is_joined ? styles.leaveBtn : styles.joinBtn]}
              onPress={handleToggleJoin}
            >
              <Text style={[styles.mainBtnText, group.is_joined && styles.leaveBtnText]}>
                {group.is_joined ? '✓ Joined (Click to Leave)' : '+ Join Group'}
              </Text>
            </TouchableOpacity>

            {group.is_joined && (
              <TouchableOpacity
                style={styles.chatBtn}
                onPress={() => navigation.navigate('GroupChat', { groupId: group.id, name: group.name })}
              >
                <Text style={styles.chatBtnText}>💬 Open Group Chat</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* About Card */}
          <View style={styles.cardContainer}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardHeaderIcon}>ℹ️</Text>
              <Text style={styles.cardHeaderTitle}>About</Text>
            </View>

            <Text style={styles.aboutText}>{group.description}</Text>

            <View style={styles.metaRow}>
              <Text style={styles.metaIcon}>🌐</Text>
              <Text style={styles.metaText}>
                {group.privacy || 'Public Group (Visible in Directory)'}
              </Text>
            </View>

            <View style={styles.metaRow}>
              <Text style={styles.metaIcon}>📅</Text>
              <Text style={styles.metaText}>Created {formattedDate}</Text>
            </View>
          </View>

          {/* Group Rules Card */}
          <View style={styles.cardContainer}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardHeaderIcon}>📜</Text>
              <Text style={styles.cardHeaderTitle}>Group Rules</Text>
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
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backBtn: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    backgroundColor: '#F1F5F9',
  },
  backText: {
    fontSize: 14,
    color: '#4F46E5',
    fontWeight: '700',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  scrollCanvas: {
    flex: 1,
  },
  scrollContent: {
    padding: 24,
    maxWidth: 800,
    alignSelf: 'center',
    width: '100%',
  },

  /* Hero Group Header Card */
  heroCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    padding: 24,
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 10,
    elevation: 2,
  },
  iconCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  iconText: {
    fontSize: 32,
    color: '#FFFFFF',
  },
  name: {
    fontSize: 24,
    fontWeight: '900',
    color: '#0F172A',
    textAlign: 'center',
    marginBottom: 6,
  },
  categoryBadge: {
    fontSize: 13,
    color: '#4F46E5',
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    fontWeight: '700',
    marginBottom: 14,
  },
  description: {
    fontSize: 14,
    color: '#475569',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 16,
  },
  memberCount: {
    fontSize: 14,
    color: '#64748B',
    fontWeight: '600',
    marginBottom: 20,
  },
  mainBtn: {
    width: '100%',
    paddingVertical: 13,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 10,
  },
  joinBtn: {
    backgroundColor: '#4F46E5',
  },
  leaveBtn: {
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  mainBtnText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  leaveBtnText: {
    color: '#475569',
  },
  chatBtn: {
    width: '100%',
    backgroundColor: '#DCFCE7',
    paddingVertical: 13,
    borderRadius: 12,
    alignItems: 'center',
  },
  chatBtnText: {
    color: '#15803D',
    fontSize: 15,
    fontWeight: '700',
  },

  /* Card Component Styles */
  cardContainer: {
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
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardHeaderIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  cardHeaderTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  aboutText: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 22,
    marginBottom: 18,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  metaIcon: {
    fontSize: 15,
    marginRight: 10,
    color: '#64748B',
  },
  metaText: {
    fontSize: 13,
    color: '#64748B',
    fontWeight: '600',
  },

  /* Rules Styles */
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
