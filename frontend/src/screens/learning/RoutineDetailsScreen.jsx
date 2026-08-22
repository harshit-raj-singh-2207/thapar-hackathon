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

export default function RoutineDetailsScreen({ route, navigation }) {
  const { routineId } = route.params || {};
  const { routines, toggleStep } = useLearning();

  const routine = routines.find((r) => r.id === routineId) || routines[0];
  const steps = routine?.steps || [];
  const completedCount = steps.filter((s) => s.is_completed).length;

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{routine?.title || 'Routine Details'}</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Hero Card */}
        <View style={[styles.heroCard, { backgroundColor: `${routine?.color || '#3B82F6'}15` }]}>
          <Text style={styles.heroEmoji}>{routine?.icon || '🌅'}</Text>
          <Text style={styles.heroTitle}>{routine?.title}</Text>
          <Text style={styles.heroSub}>
            {completedCount} of {steps.length} steps completed
          </Text>
        </View>

        <Text style={styles.sectionTitle}>STEP-BY-STEP CHECKLIST</Text>

        <View style={styles.stepList}>
          {steps.map((step, idx) => (
            <TouchableOpacity
              key={step.id || idx}
              style={[styles.stepItem, step.is_completed && styles.stepItemDone]}
              onPress={() => toggleStep(routine.id, step.id)}
              activeOpacity={0.85}
            >
              <View style={[styles.checkCircle, step.is_completed && styles.checkCircleDone]}>
                <Text style={styles.checkIcon}>{step.is_completed ? '✓' : step.step_number}</Text>
              </View>

              <View style={styles.stepTextCol}>
                <Text style={[styles.stepTitle, step.is_completed && styles.stepTitleDone]}>
                  {step.title}
                </Text>
                {step.instruction ? (
                  <Text style={styles.stepInstruction}>{step.instruction}</Text>
                ) : null}
              </View>

              <View style={styles.stepRightIcon}>
                <Text style={{ fontSize: 24 }}>{step.icon || '✨'}</Text>
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
  heroCard: {
    borderRadius: 22,
    padding: 22,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  heroEmoji: {
    fontSize: 44,
    marginBottom: 8,
  },
  heroTitle: {
    fontSize: 20,
    fontWeight: '900',
    color: '#0F172A',
  },
  heroSub: {
    fontSize: 13,
    color: '#64748B',
    marginTop: 4,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 12,
  },
  stepList: {
    gap: 12,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 16,
    gap: 14,
  },
  stepItemDone: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  checkCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkCircleDone: {
    backgroundColor: '#10B981',
  },
  checkIcon: {
    fontSize: 14,
    fontWeight: '900',
    color: '#0F172A',
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
  stepRightIcon: {
    width: 36,
    alignItems: 'center',
  },
});
