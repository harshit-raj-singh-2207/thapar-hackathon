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

export default function CommunicationHistoryScreen({ navigation }) {
  const { savedPhrases, historyLogs, speakSentence } = useCommunication();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>History & Saved Phrases</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Saved Favorites */}
        <Text style={styles.sectionTitle}>FAVORITE SAVED PHRASES ({savedPhrases.length})</Text>
        {savedPhrases.length === 0 ? (
          <Text style={styles.emptyText}>No saved phrases yet. Tap "Save" in the AAC sentence builder to keep favorites here!</Text>
        ) : (
          <View style={styles.list}>
            {savedPhrases.map((phrase) => (
              <View key={phrase.id} style={styles.savedCard}>
                <Text style={styles.phraseIcon}>⭐</Text>
                <Text style={styles.phraseText}>{phrase.text}</Text>
                <TouchableOpacity
                  style={styles.speakPill}
                  onPress={() => speakSentence(phrase.text)}
                  activeOpacity={0.8}
                >
                  <Text style={styles.speakIcon}>🗣️</Text>
                  <Text style={styles.speakLabel}>Speak</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}

        {/* Recent Communication Logs */}
        <Text style={[styles.sectionTitle, { marginTop: 24 }]}>RECENT SPOKEN REQUESTS</Text>
        {historyLogs.length === 0 ? (
          <Text style={styles.emptyText}>No communication requests logged yet today.</Text>
        ) : (
          <View style={styles.list}>
            {historyLogs.map((log, idx) => (
              <View key={log.id || idx} style={styles.logCard}>
                <View style={styles.logDot} />
                <View style={styles.logBody}>
                  <Text style={styles.logSentence}>"{log.sentence}"</Text>
                  <Text style={styles.logMeta}>Source: {log.source?.toUpperCase()} • Audio Spoken</Text>
                </View>
                <TouchableOpacity
                  style={styles.replayBtn}
                  onPress={() => speakSentence(log.sentence)}
                  activeOpacity={0.8}
                >
                  <Text style={styles.replayIcon}>🔁</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}
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
  sectionTitle: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 10,
  },
  list: {
    gap: 10,
  },
  emptyText: {
    fontSize: 13,
    color: '#94A3B8',
    fontStyle: 'italic',
    paddingVertical: 8,
  },
  savedCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 14,
    gap: 10,
  },
  phraseIcon: {
    fontSize: 18,
  },
  phraseText: {
    flex: 1,
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
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
  speakIcon: {
    fontSize: 13,
  },
  speakLabel: {
    fontSize: 12,
    fontWeight: '800',
    color: '#2563EB',
  },
  logCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    padding: 12,
    gap: 10,
  },
  logDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3B82F6',
  },
  logBody: {
    flex: 1,
  },
  logSentence: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  logMeta: {
    fontSize: 11,
    color: '#94A3B8',
    marginTop: 2,
  },
  replayBtn: {
    padding: 6,
  },
  replayIcon: {
    fontSize: 16,
  },
});
