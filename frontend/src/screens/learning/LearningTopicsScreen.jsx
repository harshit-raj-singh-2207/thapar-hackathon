import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useLearning } from '../../hooks/useLearning';

export default function LearningTopicsScreen({ navigation }) {
  const { topics } = useLearning();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Personalized Topics & Stories</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.subPrompt}>
          Interactive social stories, sensory regulation modules, and daily life skill guides.
        </Text>

        <View style={styles.topicList}>
          {topics.map((topic) => (
            <TouchableOpacity
              key={topic.id}
              style={[styles.topicCard, { borderLeftColor: topic.color || '#10B981' }]}
              activeOpacity={0.88}
            >
              <View style={styles.topicHeader}>
                <Text style={styles.topicIcon}>{topic.icon || '📖'}</Text>
                <View style={styles.topicTextCol}>
                  <View style={styles.categoryBadge}>
                    <Text style={styles.categoryText}>{topic.category}</Text>
                  </View>
                  <Text style={styles.topicTitle}>{topic.title}</Text>
                </View>
                {topic.is_completed ? (
                  <View style={styles.doneBadge}>
                    <Text style={styles.doneText}>✓ Completed</Text>
                  </View>
                ) : null}
              </View>

              {topic.description ? (
                <Text style={styles.topicDesc}>{topic.description}</Text>
              ) : null}

              {/* Progress bar */}
              <View style={styles.progressRow}>
                <View style={styles.progressTrack}>
                  <View
                    style={[
                      styles.progressFill,
                      { width: `${topic.progress_pct || 0}%`, backgroundColor: topic.color || '#10B981' },
                    ]}
                  />
                </View>
                <Text style={styles.progressPct}>{topic.progress_pct || 0}%</Text>
              </View>
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
    fontSize: 16,
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
    lineHeight: 18,
  },
  topicList: {
    gap: 14,
  },
  topicCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderLeftWidth: 5,
    padding: 18,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  topicHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 8,
  },
  topicIcon: {
    fontSize: 28,
  },
  topicTextCol: {
    flex: 1,
  },
  categoryBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    marginBottom: 4,
  },
  categoryText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#475569',
  },
  topicTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  doneBadge: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  doneText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#059669',
  },
  topicDesc: {
    fontSize: 13,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 12,
  },
  progressRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  progressTrack: {
    flex: 1,
    height: 6,
    backgroundColor: '#F1F5F9',
    borderRadius: 999,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 999,
  },
  progressPct: {
    fontSize: 12,
    fontWeight: '800',
    color: '#475569',
  },
});
