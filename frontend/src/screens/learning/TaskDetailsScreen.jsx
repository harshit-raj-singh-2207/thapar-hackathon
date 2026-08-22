import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { useLearning } from '../../hooks/useLearning';

export default function TaskDetailsScreen({ navigation }) {
  const { brokenDownSteps, breakdownTask, loading } = useLearning();
  const [taskInput, setTaskInput] = useState('');
  const [completedSteps, setCompletedSteps] = useState({});

  const sampleTasks = ['Brush Teeth', 'Pack Backpack', 'Wash Hands', 'Tidy Room', 'Make Bed'];

  const handleBreakdown = (title) => {
    const t = title || taskInput;
    if (!t.trim()) return;
    setCompletedSteps({});
    breakdownTask(t.trim());
  };

  const toggleStepDone = (idx) => {
    setCompletedSteps((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>AI Task Breakdown</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Input Card */}
        <View style={styles.inputCard}>
          <Text style={styles.inputLabel}>WHAT TASK WOULD YOU LIKE TO BREAK DOWN?</Text>
          <View style={styles.inputRow}>
            <TextInput
              style={styles.textInput}
              placeholder="e.g. Brushing teeth, packing school bag..."
              placeholderTextColor="#94A3B8"
              value={taskInput}
              onChangeText={setTaskInput}
            />
            <TouchableOpacity
              style={styles.breakdownBtn}
              onPress={() => handleBreakdown()}
              activeOpacity={0.85}
            >
              <Text style={styles.breakdownBtnText}>Break Down</Text>
            </TouchableOpacity>
          </View>

          {/* Quick task pills */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.quickPillsRow}>
            {sampleTasks.map((t) => (
              <TouchableOpacity
                key={t}
                style={styles.quickPill}
                onPress={() => {
                  setTaskInput(t);
                  handleBreakdown(t);
                }}
              >
                <Text style={styles.quickPillText}>+ {t}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color="#2563EB" />
            <Text style={styles.loadingText}>AI is generating bite-sized micro-steps...</Text>
          </View>
        ) : brokenDownSteps.length > 0 ? (
          <View style={styles.resultsContainer}>
            <Text style={styles.sectionTitle}>VISUAL STEP-BY-STEP GUIDE</Text>
            {brokenDownSteps.map((step, idx) => {
              const isDone = !!completedSteps[idx];
              return (
                <TouchableOpacity
                  key={idx}
                  style={[styles.stepCard, isDone && styles.stepCardDone]}
                  onPress={() => toggleStepDone(idx)}
                  activeOpacity={0.85}
                >
                  <View style={[styles.stepNumberBadge, isDone && styles.stepNumberBadgeDone]}>
                    <Text style={styles.stepNumberText}>{isDone ? '✓' : step.step_number}</Text>
                  </View>
                  <View style={styles.stepTextCol}>
                    <Text style={[styles.stepTitle, isDone && styles.stepTitleDone]}>
                      {step.title}
                    </Text>
                    <Text style={styles.stepInstruction}>{step.instruction}</Text>
                    {step.duration_sec ? (
                      <Text style={styles.stepDuration}>⏱️ ~{step.duration_sec} seconds</Text>
                    ) : null}
                  </View>
                  <Text style={styles.stepIcon}>{step.icon || '⭐'}</Text>
                </TouchableOpacity>
              );
            })}
          </View>
        ) : null}
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
  inputCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 18,
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 0.8,
    marginBottom: 10,
  },
  inputRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 12,
  },
  textInput: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
    color: '#0F172A',
    fontWeight: '600',
  },
  breakdownBtn: {
    backgroundColor: '#2563EB',
    paddingHorizontal: 16,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  breakdownBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '800',
  },
  quickPillsRow: {
    flexDirection: 'row',
    gap: 8,
  },
  quickPill: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
  },
  quickPillText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
  },
  loadingBox: {
    paddingVertical: 40,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  loadingText: {
    fontSize: 14,
    color: '#64748B',
    fontWeight: '600',
  },
  resultsContainer: {
    gap: 12,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 10,
  },
  stepCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 16,
    gap: 14,
  },
  stepCardDone: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  stepNumberBadge: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#EFF6FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepNumberBadgeDone: {
    backgroundColor: '#10B981',
  },
  stepNumberText: {
    fontSize: 14,
    fontWeight: '900',
    color: '#2563EB',
  },
  stepTextCol: {
    flex: 1,
  },
  stepTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  stepTitleDone: {
    color: '#047857',
    textDecorationLine: 'line-through',
  },
  stepInstruction: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
    lineHeight: 16,
  },
  stepDuration: {
    fontSize: 11,
    color: '#94A3B8',
    marginTop: 4,
    fontWeight: '600',
  },
  stepIcon: {
    fontSize: 26,
  },
});
