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

export default function SensoryHomeScreen({ navigation }) {
  const [activeTab, setActiveTab] = useState('TOOLS'); // 'TOOLS' | 'SOUNDS' | 'DE_ESCALATION'
  const [noiseLevel, setNoiseLevel] = useState(42); // dB
  const [isCalmingActive, setIsCalmingActive] = useState(false);

  const calmingSounds = [
    { id: '1', title: 'Gentle Ocean Waves', icon: '🌊', category: 'Nature' },
    { id: '2', title: 'Pink Noise Breeze', icon: '💨', category: 'White Noise' },
    { id: '3', title: 'Soft Raindrops', icon: '🌧️', category: 'Rain' },
    { id: '4', title: 'Deep Forest Echoes', icon: '🌲', category: 'Ambient' },
  ];

  const deEscalationStrategies = [
    {
      id: 'strat-1',
      title: '5-4-3-2-1 Grounding Method',
      icon: '👁️',
      steps: [
        '5 things you can see',
        '4 things you can physically touch',
        '3 things you hear around you',
        '2 things you can smell',
        '1 deep breath in and slow exhale',
      ],
    },
    {
      id: 'strat-2',
      title: 'Deep Pressure Touch Protocol',
      icon: '🫂',
      steps: [
        'Apply weighted blanket across shoulders',
        'Firm, slow hugs with steady count',
        'Dim ambient room lights to 20%',
        'Play low-tempo calming frequency',
      ],
    },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Navigation Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>‹ Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Sensory Sanctuary & Support</Text>
        <TouchableOpacity
          style={styles.sosQuickBtn}
          onPress={() => navigation.navigate('Emergency')}
        >
          <Text style={styles.sosQuickText}>🚨 SOS</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
        {/* Banner */}
        <View style={styles.banner}>
          <View style={styles.bannerIconBox}>
            <Text style={styles.bannerIcon}>🎧</Text>
          </View>
          <View style={styles.bannerTextCol}>
            <Text style={styles.bannerTitle}>Auditory & Visual Comfort Center</Text>
            <Text style={styles.bannerSub}>
              Tools and de-escalation strategies designed for sensory regulation and distress relief.
            </Text>
          </View>
        </View>

        {/* Live Noise Meter Widget */}
        <View style={styles.noiseWidgetCard}>
          <View style={styles.widgetHeader}>
            <Text style={styles.widgetTitle}>🔊 Live Room Noise Monitor</Text>
            <View style={[styles.noisePill, noiseLevel < 60 ? styles.noisePillSafe : styles.noisePillWarn]}>
              <Text style={[styles.noisePillText, noiseLevel < 60 ? styles.noiseTextSafe : styles.noiseTextWarn]}>
                {noiseLevel < 60 ? 'Optimal Range (Quiet)' : 'High Noise Warning'}
              </Text>
            </View>
          </View>
          <View style={styles.decibelGauge}>
            <Text style={styles.decibelNumber}>{noiseLevel}</Text>
            <Text style={styles.decibelUnit}>dB</Text>
          </View>
          <Text style={styles.noiseAdvice}>
            Current environment sound pressure is comfortable. Keep noise cancelling headphones handy if visiting outdoor venues.
          </Text>
        </View>

        {/* Calming Audio Player */}
        <Text style={styles.sectionTitle}>CALMING AMBIENT AUDIO</Text>
        <View style={styles.soundsGrid}>
          {calmingSounds.map((sound) => (
            <TouchableOpacity
              key={sound.id}
              style={styles.soundCard}
              onPress={() => setIsCalmingActive(!isCalmingActive)}
              activeOpacity={0.8}
            >
              <Text style={styles.soundIcon}>{sound.icon}</Text>
              <View style={styles.soundInfo}>
                <Text style={styles.soundTitle}>{sound.title}</Text>
                <Text style={styles.soundCategory}>{sound.category}</Text>
              </View>
              <Text style={styles.playBtn}>{isCalmingActive ? '⏸️' : '▶️'}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* De-escalation Protocol */}
        <Text style={styles.sectionTitle}>DE-ESCALATION STRATEGIES</Text>
        {deEscalationStrategies.map((strat) => (
          <View key={strat.id} style={styles.stratCard}>
            <View style={styles.stratHeader}>
              <Text style={styles.stratIcon}>{strat.icon}</Text>
              <Text style={styles.stratTitle}>{strat.title}</Text>
            </View>
            <View style={styles.stepsList}>
              {strat.steps.map((step, idx) => (
                <View key={idx} style={styles.stepRow}>
                  <View style={styles.stepBadge}>
                    <Text style={styles.stepBadgeText}>{idx + 1}</Text>
                  </View>
                  <Text style={styles.stepText}>{step}</Text>
                </View>
              ))}
            </View>
          </View>
        ))}
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
  sosQuickBtn: {
    backgroundColor: '#DC2626',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
  },
  sosQuickText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 11,
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
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#3B82F6',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
  },
  bannerIconBox: {
    width: 48,
    height: 48,
    borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  bannerIcon: {
    fontSize: 26,
  },
  bannerTextCol: {
    flex: 1,
  },
  bannerTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '900',
  },
  bannerSub: {
    color: '#DBEAFE',
    fontSize: 12,
    marginTop: 4,
    lineHeight: 16,
  },
  noiseWidgetCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 24,
  },
  widgetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  widgetTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  noisePill: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  noisePillSafe: {
    backgroundColor: '#ECFDF5',
  },
  noisePillWarn: {
    backgroundColor: '#FEF2F2',
  },
  noisePillText: {
    fontSize: 11,
    fontWeight: '800',
  },
  noiseTextSafe: {
    color: '#059669',
  },
  noiseTextWarn: {
    color: '#DC2626',
  },
  decibelGauge: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginVertical: 14,
  },
  decibelNumber: {
    fontSize: 48,
    fontWeight: '900',
    color: '#2563EB',
  },
  decibelUnit: {
    fontSize: 20,
    fontWeight: '800',
    color: '#64748B',
    marginLeft: 6,
  },
  noiseAdvice: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 18,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 12,
  },
  soundsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  soundCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    minWidth: isDesktop ? '48%' : '100%',
    flex: 1,
  },
  soundIcon: {
    fontSize: 26,
    marginRight: 12,
  },
  soundInfo: {
    flex: 1,
  },
  soundTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  soundCategory: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  playBtn: {
    fontSize: 20,
  },
  stratCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
  },
  stratHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  stratIcon: {
    fontSize: 22,
    marginRight: 10,
  },
  stratTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  stepsList: {
    gap: 8,
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stepBadge: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  stepBadgeText: {
    color: '#2563EB',
    fontSize: 11,
    fontWeight: '800',
  },
  stepText: {
    fontSize: 13,
    color: '#334155',
    flex: 1,
  },
});
