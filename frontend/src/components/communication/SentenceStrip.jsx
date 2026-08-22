import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';

export default function SentenceStrip({
  tokens = [],
  onRemoveToken,
  onClear,
  onSave,
  onSpeak,
  speaking = false,
  generatedSentence = '',
}) {
  return (
    <View style={styles.container}>
      <Text style={styles.headerLabel}>BUILD YOUR SENTENCE</Text>

      {/* Visual Sequence Strip */}
      <View style={styles.stripBox}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.stripContent}>
          {tokens.length === 0 ? (
            <View style={styles.emptyPlaceholder}>
              <Text style={styles.emptyIcon}>👆</Text>
              <Text style={styles.emptyText}>Tap picture cards below to build your words</Text>
            </View>
          ) : (
            tokens.map((t, idx) => (
              <React.Fragment key={`${t.label || t}-${idx}`}>
                <TouchableOpacity
                  style={[
                    styles.tokenCard,
                    idx === tokens.length - 1 && styles.lastTokenCardDashed,
                  ]}
                  onPress={() => onRemoveToken && onRemoveToken(idx)}
                  activeOpacity={0.7}
                >
                  <Text style={styles.tokenIcon}>{t.icon || '💬'}</Text>
                  <Text style={styles.tokenLabel}>{t.label || t}</Text>
                </TouchableOpacity>
                {idx < tokens.length - 1 && <Text style={styles.arrowIcon}>→</Text>}
              </React.Fragment>
            ))
          )}
        </ScrollView>
      </View>

      {/* Generated AI Sentence Text if available */}
      {generatedSentence ? (
        <View style={styles.aiSentenceBubble}>
          <Text style={styles.aiSparkle}>✨</Text>
          <Text style={styles.aiSentenceText}>"{generatedSentence}"</Text>
        </View>
      ) : null}

      {/* Bottom Action Bar: Clear, Save, Speak */}
      <View style={styles.actionBar}>
        <View style={styles.leftActions}>
          <TouchableOpacity style={styles.actionBtn} onPress={onClear} activeOpacity={0.7}>
            <Text style={styles.actionIcon}>🗑</Text>
            <Text style={styles.actionLabel}>Clear</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionBtn} onPress={onSave} activeOpacity={0.7}>
            <Text style={styles.actionIcon}>🔖</Text>
            <Text style={styles.actionLabel}>Save</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={[styles.speakBtn, speaking && styles.speakBtnActive]}
          onPress={() => onSpeak && onSpeak()}
          activeOpacity={0.85}
        >
          <Text style={styles.speakIcon}>🗣️</Text>
          <Text style={styles.speakLabel}>{speaking ? 'Speaking...' : 'Speak'}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 18,
    marginBottom: 18,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 12,
    elevation: 3,
  },
  headerLabel: {
    fontSize: 12,
    fontWeight: '900',
    color: '#475569',
    letterSpacing: 1,
    marginBottom: 12,
  },
  stripBox: {
    backgroundColor: '#F8FAFC',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    minHeight: 110,
    justifyContent: 'center',
    padding: 12,
    marginBottom: 12,
  },
  stripContent: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  emptyPlaceholder: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    gap: 8,
  },
  emptyIcon: {
    fontSize: 20,
  },
  emptyText: {
    fontSize: 14,
    color: '#94A3B8',
    fontWeight: '600',
  },
  tokenCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 70,
    minHeight: 75,
  },
  lastTokenCardDashed: {
    borderStyle: 'dashed',
    borderColor: '#94A3B8',
    borderWidth: 2,
    backgroundColor: '#FAFBFD',
  },
  tokenIcon: {
    fontSize: 22,
    marginBottom: 4,
  },
  tokenLabel: {
    fontSize: 12,
    fontWeight: '800',
    color: '#0F172A',
  },
  arrowIcon: {
    fontSize: 18,
    color: '#94A3B8',
    marginHorizontal: 10,
    fontWeight: '700',
  },
  aiSentenceBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#DBEAFE',
    gap: 8,
  },
  aiSparkle: {
    fontSize: 16,
  },
  aiSentenceText: {
    fontSize: 14,
    color: '#1E40AF',
    fontWeight: '700',
    flex: 1,
  },
  actionBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 6,
  },
  leftActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 20,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 6,
    paddingHorizontal: 8,
  },
  actionIcon: {
    fontSize: 16,
  },
  actionLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#475569',
  },
  speakBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 999,
    gap: 8,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  speakBtnActive: {
    backgroundColor: '#EFF6FF',
    borderColor: '#2563EB',
  },
  speakIcon: {
    fontSize: 16,
  },
  speakLabel: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
});
