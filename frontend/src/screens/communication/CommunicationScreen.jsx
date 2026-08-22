import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';

export default function CommunicationScreen({ navigation }) {
  const cards = [
    {
      id: 'aac',
      title: 'Picture Communication (AAC)',
      desc: 'Build sentences with tap-to-speak picture symbols and voice synthesis.',
      icon: '🖼️',
      color: '#2563EB',
      bg: '#EFF6FF',
      route: 'AAC',
    },
    {
      id: 'quick',
      title: 'Quick Urgency Needs',
      desc: 'High-contrast emergency tiles (Water, Restroom, Too Loud, Pain, Hug).',
      icon: '⚡',
      color: '#EF4444',
      bg: '#FEF2F2',
      route: 'QuickCommunication',
    },
    {
      id: 'emotion',
      title: 'Emotion-Aware Check-in',
      desc: 'Visual feelings wheel & personalized empathetic sentence builder.',
      icon: '❤️',
      color: '#8B5CF6',
      bg: '#F5F3FF',
      route: 'Emotion',
    },
    {
      id: 'history',
      title: 'Communication History & Saved',
      desc: 'Review frequent requests, spoken logs, and saved favorite phrases.',
      icon: '📖',
      color: '#10B981',
      bg: '#ECFDF5',
      route: 'CommunicationHistory',
    },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.brandTitle}>AI Communication Hub</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.banner}>
          <Text style={styles.bannerIcon}>🗣️</Text>
          <View style={styles.bannerTextCol}>
            <Text style={styles.bannerTitle}>Voice & Picture Support</Text>
            <Text style={styles.bannerSub}>
              Inclusive assistive communication tools tailored for neurodivergent voices.
            </Text>
          </View>
        </View>

        <Text style={styles.sectionHeading}>COMMUNICATION MODES</Text>

        <View style={styles.cardList}>
          {cards.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={[styles.card, { borderLeftColor: item.color }]}
              onPress={() => navigation.navigate(item.route)}
              activeOpacity={0.85}
            >
              <View style={[styles.iconCircle, { backgroundColor: item.bg }]}>
                <Text style={styles.cardIcon}>{item.icon}</Text>
              </View>
              <View style={styles.cardTextCol}>
                <Text style={styles.cardTitle}>{item.title}</Text>
                <Text style={styles.cardDesc}>{item.desc}</Text>
              </View>
              <Text style={styles.arrowIcon}>›</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FAFBFD',
  },
  topHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
  },
  backBtn: {
    paddingVertical: 6,
    paddingHorizontal: 8,
  },
  backText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563EB',
  },
  brandTitle: {
    fontSize: 17,
    fontWeight: '900',
    color: '#0F172A',
  },
  content: {
    padding: 20,
    maxWidth: 680,
    alignSelf: 'center',
    width: '100%',
  },
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: '#DBEAFE',
    marginBottom: 24,
    gap: 14,
  },
  bannerIcon: {
    fontSize: 32,
  },
  bannerTextCol: {
    flex: 1,
  },
  bannerTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#1E40AF',
  },
  bannerSub: {
    fontSize: 13,
    color: '#3B82F6',
    marginTop: 2,
    lineHeight: 18,
  },
  sectionHeading: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 12,
  },
  cardList: {
    gap: 14,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderLeftWidth: 5,
    padding: 16,
    gap: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  iconCircle: {
    width: 50,
    height: 50,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardIcon: {
    fontSize: 24,
  },
  cardTextCol: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  cardDesc: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
    lineHeight: 17,
  },
  arrowIcon: {
    fontSize: 22,
    fontWeight: '700',
    color: '#94A3B8',
  },
});
