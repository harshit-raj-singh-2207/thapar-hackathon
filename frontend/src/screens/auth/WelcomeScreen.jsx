import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Dimensions,
} from 'react-native';

export default function WelcomeScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* Top Branding Header */}
        <View style={styles.brandHeader}>
          <Text style={styles.sparkleIcon}>✦</Text>
          <Text style={styles.brandTitle}>NIVARA</Text>
        </View>

        {/* Decorative Graphic & Illustration */}
        <View style={styles.illustrationContainer}>
          <View style={styles.bgGlow} />
          {/* Subtle geometric floating elements */}
          <Text style={[styles.floatingDeco, { top: 10, left: 24 }]}>🪐</Text>
          <Text style={[styles.floatingDeco, { top: 20, right: 30 }]}>✨</Text>
          <Text style={[styles.floatingDeco, { bottom: 30, left: 16 }]}>📐</Text>
          <Text style={[styles.floatingDeco, { bottom: 20, right: 20 }]}>⚛️</Text>

          {/* Caregiver Hero Avatar & Visual */}
          <View style={styles.avatarCard}>
            <View style={styles.caregiverBadge}>
              <Text style={styles.caregiverEmoji}>👩‍🏫</Text>
            </View>
            <View style={styles.laptopBadge}>
              <Text style={styles.laptopEmoji}>💻 📖</Text>
            </View>
            <Text style={styles.heroTagline}>Private Caregiver Network</Text>
          </View>
        </View>

        {/* Title & Narrative */}
        <View style={styles.textContainer}>
          <Text style={styles.mainTitle}>
            Support, Connect, and Grow Together.
          </Text>
          <Text style={styles.subTitle}>
            Connect with verified caregivers, share experiences, and find
            trusted support in a safe and private community.
          </Text>
        </View>

        {/* Action Controls */}
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={styles.primaryButton}
            activeOpacity={0.85}
            onPress={() => navigation.navigate('Register')}
          >
            <Text style={styles.primaryButtonText}>Get Started</Text>
            <View style={styles.arrowCircle}>
              <Text style={styles.arrowText}>→</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.signInLink}
            activeOpacity={0.7}
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.signInText}>
              Already have an account?{' '}
              <Text style={styles.signInTextBold}>Sign In</Text>
            </Text>
          </TouchableOpacity>
        </View>

        {/* Trust & Safety Footer */}
        <View style={styles.trustBadge}>
          <Text style={styles.trustIcon}>🛡️</Text>
          <Text style={styles.trustText}>
            Your privacy, child safety, and verified identity come first.
          </Text>
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
  scrollContainer: {
    flexGrow: 1,
    paddingHorizontal: 28,
    paddingVertical: 24,
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: 480,
    alignSelf: 'center',
    width: '100%',
  },
  brandHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
    marginBottom: 24,
  },
  sparkleIcon: {
    fontSize: 20,
    color: '#2563EB',
    marginRight: 6,
    fontWeight: '900',
  },
  brandTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0F172A',
    letterSpacing: 1.5,
  },
  illustrationContainer: {
    width: '100%',
    height: 220,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    marginVertical: 12,
  },
  bgGlow: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: '#EFF6FF',
    opacity: 0.8,
  },
  floatingDeco: {
    position: 'absolute',
    fontSize: 20,
    opacity: 0.6,
  },
  avatarCard: {
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    paddingVertical: 20,
    paddingHorizontal: 28,
    borderRadius: 24,
    shadowColor: '#1E293B',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 4,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  caregiverBadge: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#C7D2FE',
  },
  caregiverEmoji: {
    fontSize: 40,
  },
  laptopBadge: {
    marginBottom: 6,
  },
  laptopEmoji: {
    fontSize: 18,
  },
  heroTagline: {
    fontSize: 12,
    fontWeight: '700',
    color: '#3B82F6',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  textContainer: {
    marginVertical: 20,
    alignItems: 'center',
    width: '100%',
  },
  mainTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#0F172A',
    textAlign: 'center',
    lineHeight: 36,
    letterSpacing: -0.5,
    marginBottom: 14,
  },
  subTitle: {
    fontSize: 15,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 23,
    paddingHorizontal: 8,
  },
  actionContainer: {
    width: '100%',
    marginVertical: 12,
  },
  primaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    borderRadius: 32,
    paddingVertical: 8,
    paddingLeft: 24,
    paddingRight: 8,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 10,
    elevation: 2,
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1E293B',
  },
  arrowCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  arrowText: {
    fontSize: 20,
    color: '#FFFFFF',
    fontWeight: '700',
  },
  signInLink: {
    marginTop: 18,
    paddingVertical: 8,
    alignItems: 'center',
  },
  signInText: {
    fontSize: 14,
    color: '#64748B',
  },
  signInTextBold: {
    color: '#2563EB',
    fontWeight: '700',
  },
  trustBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F1F5F9',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 16,
    marginTop: 8,
  },
  trustIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  trustText: {
    fontSize: 12,
    color: '#64748B',
    flexShrink: 1,
    fontWeight: '500',
  },
});
