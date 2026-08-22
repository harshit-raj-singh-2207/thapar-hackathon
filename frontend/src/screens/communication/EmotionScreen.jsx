import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useCommunication } from '../../hooks/useCommunication';
import EmotionSelector from '../../components/communication/EmotionSelector';

export default function EmotionScreen({ navigation }) {
  const {
    currentEmotion,
    checkinEmotion,
    emotionRecommendations,
    sensoryTip,
    speakSentence,
    speaking,
  } = useCommunication();

  const [intensity, setIntensity] = useState(5);

  const handleSelectEmotion = (emId) => {
    checkinEmotion(emId, intensity);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Emotion Check-in</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <EmotionSelector
          selectedEmotion={currentEmotion}
          onSelectEmotion={handleSelectEmotion}
        />

        {/* Intensity Level Selector */}
        <View style={styles.intensityCard}>
          <Text style={styles.intensityTitle}>HOW STRONG IS THIS FEELING? ({intensity}/10)</Text>
          <View style={styles.intensityButtonsRow}>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
              <TouchableOpacity
                key={num}
                style={[
                  styles.intensityNumBtn,
                  intensity === num && styles.intensityNumBtnActive,
                ]}
                onPress={() => {
                  setIntensity(num);
                  if (currentEmotion) checkinEmotion(currentEmotion, num);
                }}
              >
                <Text
                  style={[
                    styles.intensityNumText,
                    intensity === num && styles.intensityNumTextActive,
                  ]}
                >
                  {num}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Sensory Grounding Tip */}
        {sensoryTip ? (
          <View style={styles.tipCard}>
            <Text style={styles.tipIcon}>💡</Text>
            <View style={styles.tipTextCol}>
              <Text style={styles.tipTitle}>Sensory Support Tip</Text>
              <Text style={styles.tipText}>{sensoryTip}</Text>
            </View>
          </View>
        ) : null}

        {/* Recommended Phrases */}
        <Text style={styles.sectionTitle}>RECOMMENDED PHRASES TO SPEAK</Text>
        <View style={styles.phraseList}>
          {emotionRecommendations.length === 0 ? (
            <Text style={styles.emptyPrompt}>Select an emotion above to see personalized phrases.</Text>
          ) : (
            emotionRecommendations.map((phrase, idx) => (
              <TouchableOpacity
                key={idx}
                style={styles.phraseCard}
                onPress={() => speakSentence(phrase)}
                activeOpacity={0.85}
              >
                <Text style={styles.phraseText}>"{phrase}"</Text>
                <View style={styles.speakPill}>
                  <Text style={styles.speakPillIcon}>🗣️</Text>
                  <Text style={styles.speakPillText}>Speak</Text>
                </View>
              </TouchableOpacity>
            ))
          )}
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
  headerTitle: {
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
  intensityCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 16,
    marginVertical: 12,
  },
  intensityTitle: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 10,
  },
  intensityButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  intensityNumBtn: {
    width: 28,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  intensityNumBtnActive: {
    backgroundColor: '#2563EB',
  },
  intensityNumText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#475569',
  },
  intensityNumTextActive: {
    color: '#FFFFFF',
  },
  tipCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: '#A7F3D0',
    marginVertical: 10,
    gap: 12,
  },
  tipIcon: {
    fontSize: 24,
  },
  tipTextCol: {
    flex: 1,
  },
  tipTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#065F46',
  },
  tipText: {
    fontSize: 12,
    color: '#047857',
    marginTop: 2,
    lineHeight: 16,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginTop: 14,
    marginBottom: 10,
  },
  phraseList: {
    gap: 10,
  },
  emptyPrompt: {
    fontSize: 13,
    color: '#94A3B8',
    fontStyle: 'italic',
    paddingVertical: 12,
  },
  phraseCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 16,
    gap: 12,
  },
  phraseText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0F172A',
    flex: 1,
  },
  speakPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    gap: 4,
  },
  speakPillIcon: {
    fontSize: 13,
  },
  speakPillText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#2563EB',
  },
});
