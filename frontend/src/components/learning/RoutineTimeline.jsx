import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function RoutineTimeline({ steps = [], onToggleStep }) {
  return (
    <View style={styles.container}>
      {steps.map((step, idx) => {
        const isLast = idx === steps.length - 1;
        return (
          <View key={step.id || idx} style={styles.stepRow}>
            {/* Timeline Line & Node */}
            <View style={styles.timelineCol}>
              <TouchableOpacity
                style={[styles.node, step.is_completed && styles.nodeDone]}
                onPress={() => onToggleStep && onToggleStep(step.id)}
                activeOpacity={0.8}
              >
                <Text style={styles.nodeText}>{step.is_completed ? '✓' : step.step_number || idx + 1}</Text>
              </TouchableOpacity>
              {!isLast ? <View style={[styles.line, step.is_completed && styles.lineDone]} /> : null}
            </View>

            {/* Step Card Content */}
            <TouchableOpacity
              style={[styles.contentCard, step.is_completed && styles.contentCardDone]}
              onPress={() => onToggleStep && onToggleStep(step.id)}
              activeOpacity={0.85}
            >
              <Text style={styles.stepIcon}>{step.icon || '✨'}</Text>
              <View style={styles.textCol}>
                <Text style={[styles.stepTitle, step.is_completed && styles.stepTitleDone]}>
                  {step.title}
                </Text>
                {step.instruction ? (
                  <Text style={styles.stepInstruction}>{step.instruction}</Text>
                ) : null}
              </View>
            </TouchableOpacity>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: 8,
  },
  stepRow: {
    flexDirection: 'row',
    marginBottom: 8,
    gap: 12,
  },
  timelineCol: {
    alignItems: 'center',
    width: 36,
  },
  node: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#CBD5E1',
    zIndex: 1,
  },
  nodeDone: {
    backgroundColor: '#10B981',
    borderColor: '#059669',
  },
  nodeText: {
    fontSize: 12,
    fontWeight: '900',
    color: '#334155',
  },
  line: {
    width: 3,
    flex: 1,
    backgroundColor: '#E2E8F0',
    marginVertical: 4,
  },
  lineDone: {
    backgroundColor: '#10B981',
  },
  contentCard: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 14,
    gap: 12,
  },
  contentCardDone: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  stepIcon: {
    fontSize: 24,
  },
  textCol: {
    flex: 1,
  },
  stepTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  stepTitleDone: {
    color: '#047857',
    textDecorationLine: 'line-through',
  },
  stepInstruction: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
});
