import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useCommunication } from '../../hooks/useCommunication';

const QUICK_NEEDS = [
  { id: 'water', label: 'I Need Water', icon: '💧', text: 'I need a glass of water, please.', color: '#3B82F6', bg: '#EFF6FF' },
  { id: 'toilet', label: 'Restroom Now', icon: '🚻', text: 'I need to use the restroom right now, please.', color: '#10B981', bg: '#ECFDF5' },
  { id: 'help', label: 'I Need Help', icon: '🛟', text: 'Please help me with this.', color: '#F59E0B', bg: '#FFFBEB' },
  { id: 'too_loud', label: 'Too Loud!', icon: '🎧', text: 'It is too loud here. I need quiet headphones or a break.', color: '#EF4444', bg: '#FEF2F2' },
  { id: 'pain', label: 'It Hurts / Pain', icon: '🩹', text: 'Something hurts and I feel discomfort.', color: '#DC2626', bg: '#FEE2E2' },
  { id: 'break', label: 'I Need a Break', icon: '🛑', text: 'I feel overwhelmed and need a 5 minute break.', color: '#8B5CF6', bg: '#F5F3FF' },
  { id: 'hug', label: 'I Need a Hug', icon: '🫂', text: 'Can I have a gentle hug, please?', color: '#EC4899', bg: '#FDF2F8' },
  { id: 'hungry', label: 'I am Hungry', icon: '🍎', text: 'I am hungry and would like a snack.', color: '#D97706', bg: '#FEF3C7' },
];

export default function QuickCommunicationScreen({ navigation }) {
  const { speakSentence, speaking } = useCommunication();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Quick Urgency Needs</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.subPrompt}>Tap any tile for instant loud and clear audio speech.</Text>

        <View style={styles.grid}>
          {QUICK_NEEDS.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={[styles.tile, { backgroundColor: item.bg, borderColor: item.color }]}
              onPress={() => speakSentence(item.text)}
              activeOpacity={0.8}
            >
              <Text style={styles.tileIcon}>{item.icon}</Text>
              <Text style={[styles.tileLabel, { color: item.color }]}>{item.label}</Text>
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
  subPrompt: {
    fontSize: 13,
    color: '#64748B',
    marginBottom: 16,
    fontWeight: '600',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    justifyContent: 'space-between',
  },
  tile: {
    width: '48%',
    minHeight: 120,
    borderRadius: 22,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  tileIcon: {
    fontSize: 38,
    marginBottom: 8,
  },
  tileLabel: {
    fontSize: 16,
    fontWeight: '900',
    textAlign: 'center',
  },
});
