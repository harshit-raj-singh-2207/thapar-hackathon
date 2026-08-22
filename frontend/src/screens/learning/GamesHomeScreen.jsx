import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Dimensions,
  Platform,
} from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const isDesktop = Platform.OS === 'web' ? SCREEN_WIDTH >= 1024 : SCREEN_WIDTH >= 768;

export default function GamesHomeScreen({ navigation }) {
  const [stars, setStars] = useState(128);
  const [badges, setBadges] = useState(8);
  const [activeTab, setActiveTab] = useState('ALL'); // 'ALL' | 'EMOTIONS' | 'AAC' | 'ROUTINES'

  const games = [
    {
      id: 'game-emotion-match',
      title: 'Emotion Memory Match',
      category: 'Emotions',
      icon: '😊',
      color: '#ECFDF5',
      accent: '#059669',
      description: 'Match expressions with emotional feelings to earn stars!',
      starsReward: 15,
      completedSessions: 12,
    },
    {
      id: 'game-aac-builder',
      title: 'AAC Sentence Builder Challenge',
      category: 'AAC',
      icon: '💬',
      color: '#EFF6FF',
      accent: '#2563EB',
      description: 'Drag and drop AAC cards to form complete spoken sentences.',
      starsReward: 20,
      completedSessions: 8,
    },
    {
      id: 'game-routine-sorter',
      title: 'Morning Routine Order Puzzle',
      category: 'Routines',
      icon: '🌅',
      color: '#FEF3C7',
      accent: '#D97706',
      description: 'Sort morning steps in proper sequence for streak points.',
      starsReward: 10,
      completedSessions: 15,
    },
    {
      id: 'game-sensory-sound',
      title: 'Sensory Sound Explorer',
      category: 'Sensory',
      icon: '🎧',
      color: '#F5F3FF',
      accent: '#7C3AED',
      description: 'Identify gentle nature sounds and calming audio frequencies.',
      starsReward: 25,
      completedSessions: 6,
    },
  ];

  const badgesList = [
    { id: 'b1', title: 'First Words Master', icon: '🏆', unlocked: true },
    { id: 'b2', title: '7-Day Routine Streak', icon: '⭐', unlocked: true },
    { id: 'b3', title: 'Emotion Scholar', icon: '❤️', unlocked: true },
    { id: 'b4', title: 'Sensory Explorer', icon: '🎧', unlocked: true },
    { id: 'b5', title: 'AAC Expert', icon: '💬', unlocked: true },
    { id: 'b6', title: 'Super Star Gamer', icon: '🌟', unlocked: true },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Navigation Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>‹ Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Educational Games & Progress</Text>
        <View style={styles.statsHeaderPill}>
          <Text style={styles.starText}>⭐ {stars}</Text>
          <Text style={styles.badgeText}>🏆 {badges}</Text>
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
        {/* Banner */}
        <View style={styles.banner}>
          <View style={styles.bannerTextCol}>
            <Text style={styles.bannerTitle}>Interactive Learning Games 🎮</Text>
            <Text style={styles.bannerSub}>
              Engaging visual mini-games designed to enhance emotion recognition, sentence building, and daily routine sequencing.
            </Text>
          </View>
        </View>

        {/* Progress Grid */}
        <View style={styles.metricsRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricVal}>⭐ {stars}</Text>
            <Text style={styles.metricLabel}>Total Stars Earned</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricVal}>🏆 {badges}</Text>
            <Text style={styles.metricLabel}>Badges Unlocked</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricVal}>🔥 14 Days</Text>
            <Text style={styles.metricLabel}>Current Streak</Text>
          </View>
        </View>

        {/* Games Grid */}
        <Text style={styles.sectionTitle}>AVAILABLE GAMES & CHALLENGES</Text>
        <View style={styles.gamesGrid}>
          {games.map((g) => (
            <View key={g.id} style={[styles.gameCard, { backgroundColor: '#FFFFFF', borderColor: '#E2E8F0' }]}>
              <View style={[styles.gameIconBox, { backgroundColor: g.color }]}>
                <Text style={styles.gameIcon}>{g.icon}</Text>
              </View>
              <View style={styles.gameBody}>
                <View style={styles.gameTitleRow}>
                  <Text style={styles.gameTitle}>{g.title}</Text>
                  <View style={[styles.rewardTag, { backgroundColor: g.color }]}>
                    <Text style={[styles.rewardTagText, { color: g.accent }]}>+ {g.starsReward} Stars</Text>
                  </View>
                </View>
                <Text style={styles.gameDesc}>{g.description}</Text>
                <TouchableOpacity
                  style={[styles.playGameBtn, { backgroundColor: g.accent }]}
                  onPress={() => setStars(stars + g.starsReward)}
                  activeOpacity={0.85}
                >
                  <Text style={styles.playGameBtnText}>▶ Play Game (+{g.starsReward} ⭐)</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>

        {/* Achievements / Badges Section */}
        <Text style={styles.sectionTitle}>UNLOCKED ACHIEVEMENTS & BADGES</Text>
        <View style={styles.badgesGrid}>
          {badgesList.map((b) => (
            <View key={b.id} style={styles.badgeItem}>
              <Text style={styles.badgeIcon}>{b.icon}</Text>
              <Text style={styles.badgeTitle}>{b.title}</Text>
              <Text style={styles.badgeStatus}>✓ Unlocked</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backBtn: {
    paddingVertical: 6,
    paddingHorizontal: 10,
  },
  backText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#2563EB',
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: '900',
    color: '#0F172A',
  },
  statsHeaderPill: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
  },
  starText: {
    fontSize: 13,
    fontWeight: '900',
    color: '#D97706',
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '900',
    color: '#2563EB',
  },
  scroll: {
    flex: 1,
  },
  content: {
    padding: 20,
    maxWidth: 1100,
    width: '100%',
    alignSelf: 'center',
  },
  banner: {
    backgroundColor: '#2563EB',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
  },
  bannerTextCol: {
    flex: 1,
  },
  bannerTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '900',
  },
  bannerSub: {
    color: '#DBEAFE',
    fontSize: 13,
    marginTop: 4,
    lineHeight: 18,
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
  },
  metricVal: {
    fontSize: 20,
    fontWeight: '900',
    color: '#0F172A',
  },
  metricLabel: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 4,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 12,
  },
  gamesGrid: {
    gap: 16,
    marginBottom: 24,
  },
  gameCard: {
    flexDirection: isDesktop ? 'row' : 'column',
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    gap: 16,
    alignItems: 'center',
  },
  gameIconBox: {
    width: 60,
    height: 60,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  gameIcon: {
    fontSize: 30,
  },
  gameBody: {
    flex: 1,
    width: '100%',
  },
  gameTitleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  gameTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  rewardTag: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  rewardTagText: {
    fontSize: 11,
    fontWeight: '900',
  },
  gameDesc: {
    fontSize: 13,
    color: '#64748B',
    marginVertical: 6,
    lineHeight: 18,
  },
  playGameBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 6,
    alignSelf: isDesktop ? 'flex-start' : 'stretch',
  },
  playGameBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '900',
  },
  badgesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  badgeItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
    minWidth: isDesktop ? '30%' : '47%',
    flex: 1,
  },
  badgeIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  badgeTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
    textAlign: 'center',
  },
  badgeStatus: {
    fontSize: 11,
    fontWeight: '800',
    color: '#059669',
    marginTop: 4,
  },
});
