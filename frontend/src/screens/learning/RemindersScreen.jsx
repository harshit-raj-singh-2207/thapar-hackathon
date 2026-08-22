import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Switch,
} from 'react-native';
import { useLearning } from '../../hooks/useLearning';

export default function RemindersScreen({ navigation }) {
  const { reminders, toggleReminder } = useLearning();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Reminders & Sensory Breaks</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.subPrompt}>
          Timely prompts for hydration, transition warnings, and calming sensory breaks.
        </Text>

        <View style={styles.remindersList}>
          {reminders.map((rem) => (
            <View key={rem.id} style={styles.reminderCard}>
              <View style={styles.iconCircle}>
                <Text style={styles.reminderIcon}>{rem.icon || '⏰'}</Text>
              </View>

              <View style={styles.reminderTextCol}>
                <Text style={styles.reminderTitle}>{rem.title}</Text>
                <Text style={styles.reminderMeta}>
                  {rem.time_str} • {rem.frequency} • {rem.category}
                </Text>
              </View>

              <Switch
                value={rem.is_active}
                onValueChange={() => toggleReminder(rem.id)}
                trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
                thumbColor={rem.is_active ? '#2563EB' : '#94A3B8'}
              />
            </View>
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
  remindersList: {
    gap: 12,
  },
  reminderCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 16,
    gap: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  iconCircle: {
    width: 46,
    height: 46,
    borderRadius: 14,
    backgroundColor: '#EFF6FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  reminderIcon: {
    fontSize: 22,
  },
  reminderTextCol: {
    flex: 1,
  },
  reminderTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  reminderMeta: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
});
