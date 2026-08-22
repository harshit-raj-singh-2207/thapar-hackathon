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
import RoutineCard from '../../components/learning/RoutineCard';

export default function RoutineScreen({ navigation }) {
  const { routines, toggleStep, resetRoutine } = useLearning();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Daily Visual Routines</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.subPrompt}>
          Consistent visual schedules help manage transitions smoothly and build autonomy.
        </Text>

        {routines.map((routine) => (
          <View key={routine.id} style={styles.routineWrapper}>
            <RoutineCard
              routine={routine}
              onToggleStep={toggleStep}
              onOpenDetails={() => navigation.navigate('RoutineDetails', { routineId: routine.id })}
            />
            <TouchableOpacity
              style={styles.resetBtn}
              onPress={() => resetRoutine(routine.id)}
              activeOpacity={0.7}
            >
              <Text style={styles.resetBtnText}>🔄 Reset for Today</Text>
            </TouchableOpacity>
          </View>
        ))}
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
    fontWeight: '500',
    lineHeight: 18,
  },
  routineWrapper: {
    marginBottom: 16,
  },
  resetBtn: {
    alignSelf: 'flex-end',
    marginTop: -4,
    marginBottom: 12,
    paddingHorizontal: 12,
    paddingVertical: 4,
  },
  resetBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748B',
  },
});
