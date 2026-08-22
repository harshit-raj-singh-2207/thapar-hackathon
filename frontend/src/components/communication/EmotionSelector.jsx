import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';

const EMOTIONS = [
  { id: 'happy', label: 'Happy', icon: '😊', color: '#10B981', bg: '#ECFDF5' },
  { id: 'calm', label: 'Calm', icon: '😌', color: '#3B82F6', bg: '#EFF6FF' },
  { id: 'anxious', label: 'Anxious', icon: '😰', color: '#F59E0B', bg: '#FFFBEB' },
  { id: 'overwhelmed', label: 'Overwhelmed', icon: '🤯', color: '#EF4444', bg: '#FEF2F2' },
  { id: 'sad', label: 'Sad', icon: '😢', color: '#6366F1', bg: '#EEF2FF' },
  { id: 'angry', label: 'Angry', icon: '😡', color: '#DC2626', bg: '#FEE2E2' },
  { id: 'tired', label: 'Tired', icon: '😴', color: '#64748B', bg: '#F1F5F9' },
  { id: 'excited', label: 'Excited', icon: '🤩', color: '#EC4899', bg: '#FDF2F8' },
];

export default function EmotionSelector({ selectedEmotion, onSelectEmotion }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>HOW ARE YOU FEELING?</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {EMOTIONS.map((em) => {
          const isSelected = selectedEmotion?.toLowerCase() === em.id;
          return (
            <TouchableOpacity
              key={em.id}
              style={[
                styles.emotionCard,
                { backgroundColor: em.bg },
                isSelected && { borderColor: em.color, borderWidth: 2.5, transform: [{ scale: 1.05 }] },
              ]}
              onPress={() => onSelectEmotion(em.id)}
              activeOpacity={0.8}
            >
              <Text style={styles.icon}>{em.icon}</Text>
              <Text style={[styles.label, { color: em.color }]}>{em.label}</Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
  },
  title: {
    fontSize: 12,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 10,
  },
  scrollContent: {
    flexDirection: 'row',
    gap: 10,
    paddingVertical: 4,
  },
  emotionCard: {
    borderRadius: 20,
    paddingVertical: 14,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 80,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
  },
  icon: {
    fontSize: 28,
    marginBottom: 6,
  },
  label: {
    fontSize: 13,
    fontWeight: '800',
  },
});
