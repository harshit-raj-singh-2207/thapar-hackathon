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

export default function LearningHomeScreen({ navigation }) {
  const { routines, toggleStep, reminders, topics } = useLearning();

  const quickFeatures = [
    {
      id: 'routines',
      title: 'Daily Routines',
      sub: 'Visual morning & bedtime schedules',
      icon: '🌅',
      color: '#3B82F6',
      bg: '#EFF6FF',
      route: 'Routine',
    },
    {
      id: 'task_breakdown',
      title: 'AI Task Breakdown',
      sub: 'Turn chores into bite-sized micro-steps',
      icon: '🧩',
      color: '#F59E0B',
      bg: '#FFFBEB',
      route: 'TaskDetails',
    },
    {
      id: 'tutor',
      title: 'AI Tutor Nivi',
      sub: 'Patient learning companion & analogies',
      icon: '🤖',
      color: '#8B5CF6',
      bg: '#F5F3FF',
      route: 'Tutor',
    },
    {
      id: 'topics',
      title: 'Learning Topics',
      sub: 'Social stories & everyday life skills',
      icon: '📚',
      color: '#10B981',
      bg: '#ECFDF5',
      route: 'LearningTopics',
    },
    {
      id: 'reminders',
      title: 'Reminders & Breaks',
      sub: 'Hydration, sensory breaks & alerts',
      icon: '⏰',
      color: '#EC4899',
      bg: '#FDF2F8',
      route: 'Reminders',
    },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <View style={styles.headerLeft}>
          <Text style={styles.headerEmoji}>🎓</Text>
          <Text style={styles.headerTitle}>Learning & Routines</Text>
        </View>
        <TouchableOpacity
          style={styles.tutorHeaderBtn}
          onPress={() => navigation.navigate('Tutor')}
          activeOpacity={0.8}
        >
          <Text style={styles.tutorHeaderIcon}>🤖</Text>
          <Text style={styles.tutorHeaderLabel}>Ask Nivi</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Banner */}
        <View style={styles.heroCard}>
          <View style={styles.heroTextCol}>
            <Text style={styles.heroTitle}>Today's Focus & Growth 🌱</Text>
            <Text style={styles.heroSub}>
              Build consistent habits, master tasks step-by-step, and explore curious topics safely.
            </Text>
          </View>
        </View>

        {/* Feature Grid */}
        <Text style={styles.sectionTitle}>LEARNING & SKILLS TOOLS</Text>
        <View style={styles.featureGrid}>
          {quickFeatures.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={[styles.featureCard, { borderLeftColor: item.color }]}
              onPress={() => navigation.navigate(item.route)}
              activeOpacity={0.85}
            >
              <View style={[styles.iconCircle, { backgroundColor: item.bg }]}>
                <Text style={styles.featureIcon}>{item.icon}</Text>
              </View>
              <View style={styles.featureTextCol}>
                <Text style={styles.featureTitle}>{item.title}</Text>
                <Text style={styles.featureSub}>{item.sub}</Text>
              </View>
              <Text style={styles.arrowIcon}>›</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Active Today Routines */}
        <View style={styles.routinesHeaderRow}>
          <Text style={styles.sectionTitle}>ACTIVE VISUAL ROUTINES</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Routine')}>
            <Text style={styles.viewAllText}>View All ›</Text>
          </TouchableOpacity>
        </View>

        {routines.slice(0, 2).map((routine) => (
          <RoutineCard
            key={routine.id}
            routine={routine}
            onToggleStep={toggleStep}
            onOpenDetails={() => navigation.navigate('RoutineDetails', { routineId: routine.id })}
          />
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
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerEmoji: {
    fontSize: 22,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#0F172A',
  },
  tutorHeaderBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F3FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#DDD6FE',
    gap: 6,
  },
  tutorHeaderIcon: {
    fontSize: 14,
  },
  tutorHeaderLabel: {
    fontSize: 12,
    fontWeight: '800',
    color: '#7C3AED',
  },
  content: {
    padding: 20,
    maxWidth: 720,
    alignSelf: 'center',
    width: '100%',
  },
  heroCard: {
    backgroundColor: '#EFF6FF',
    borderRadius: 22,
    padding: 18,
    borderWidth: 1,
    borderColor: '#DBEAFE',
    marginBottom: 20,
  },
  heroTextCol: {
    width: '100%',
  },
  heroTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#1E40AF',
  },
  heroSub: {
    fontSize: 13,
    color: '#3B82F6',
    marginTop: 4,
    lineHeight: 18,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '900',
    color: '#64748B',
    letterSpacing: 1,
    marginBottom: 12,
  },
  featureGrid: {
    gap: 12,
    marginBottom: 24,
  },
  featureCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderLeftWidth: 5,
    padding: 16,
    gap: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  featureIcon: {
    fontSize: 22,
  },
  featureTextCol: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  featureSub: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  arrowIcon: {
    fontSize: 22,
    fontWeight: '700',
    color: '#94A3B8',
  },
  routinesHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  viewAllText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#2563EB',
  },
});
