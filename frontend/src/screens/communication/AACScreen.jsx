import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { useCommunication } from '../../hooks/useCommunication';
import SentenceStrip from '../../components/communication/SentenceStrip';
import AACGrid from '../../components/communication/AACGrid';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function AACScreen({ navigation }) {
  const {
    categories,
    selectedCategory,
    setSelectedCategory,
    sentenceTokens,
    generatedSentence,
    addToken,
    removeToken,
    clearTokens,
    speakSentence,
    saveCurrentPhrase,
    speaking,
    loading,
  } = useCommunication();

  // Find cards for the active category
  const activeCat = categories.find((c) => c.name === selectedCategory) || categories[0];
  const activeCards = activeCat?.cards || [];

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* 1. TOP HEADER BRANDING */}
      <View style={styles.topHeader}>
        <View style={styles.headerLeft}>
          <View style={styles.avatarCircle}>
            <Text style={styles.avatarEmoji}>🧒</Text>
          </View>
          <Text style={styles.brandTitle}>Nivara</Text>
        </View>

        <View style={styles.aiBadge}>
          <Text style={styles.aiBadgeText}>AI ACTIVE</Text>
        </View>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* 2. SCREEN TITLE & INTRO */}
        <View style={styles.introHeader}>
          <Text style={styles.screenTitle}>Picture Communication</Text>
          <Text style={styles.screenSubtitle}>Tap pictures to tell us what you need.</Text>
        </View>

        {/* 3. BUILD YOUR SENTENCE CARD */}
        <SentenceStrip
          tokens={sentenceTokens}
          onRemoveToken={removeToken}
          onClear={clearTokens}
          onSave={saveCurrentPhrase}
          onSpeak={() => speakSentence()}
          speaking={speaking}
          generatedSentence={generatedSentence}
        />

        {/* 4. CATEGORIES SELECTOR */}
        <Text style={styles.categoriesTitle}>CATEGORIES</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriesScroll}
        >
          {categories.map((cat) => {
            const isSelected = selectedCategory === cat.name;
            return (
              <TouchableOpacity
                key={cat.id || cat.name}
                style={[
                  styles.categoryPill,
                  isSelected && styles.categoryPillActive,
                ]}
                onPress={() => setSelectedCategory(cat.name)}
                activeOpacity={0.8}
              >
                <Text style={styles.categoryIcon}>{cat.icon || '⭐'}</Text>
                <Text
                  style={[
                    styles.categoryText,
                    isSelected && styles.categoryTextActive,
                  ]}
                >
                  {cat.name}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* 5. AAC PICTURE CARDS GRID */}
        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color="#2563EB" />
            <Text style={styles.loadingText}>Loading picture symbols...</Text>
          </View>
        ) : (
          <AACGrid cards={activeCards} onSelectCard={addToken} />
        )}
      </ScrollView>

      {/* 6. BOTTOM NAVIGATION BAR */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={styles.navItem}
          onPress={() => navigation.navigate('Home')}
          activeOpacity={0.7}
        >
          <Text style={styles.navIcon}>🏠</Text>
          <Text style={styles.navLabel}>Home</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => navigation.navigate('CommunicationTab')}
          activeOpacity={0.7}
        >
          <Text style={[styles.navIcon, styles.navIconActive]}>💬</Text>
          <Text style={[styles.navLabel, styles.navLabelActive]}>Chat</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => navigation.navigate('LearningTab')}
          activeOpacity={0.7}
        >
          <Text style={styles.navIcon}>🎓</Text>
          <Text style={styles.navLabel}>Learn</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => navigation.navigate('SensoryTab')}
          activeOpacity={0.7}
        >
          <Text style={styles.navIcon}>🎮</Text>
          <Text style={styles.navLabel}>Play</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => navigation.navigate('LiveLocation')}
          activeOpacity={0.7}
        >
          <Text style={styles.navIcon}>🛡️</Text>
          <Text style={styles.navLabel}>Safety</Text>
        </TouchableOpacity>
      </View>
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
    backgroundColor: '#FAFBFD',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  avatarCircle: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#FEF3C7',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#FDE68A',
  },
  avatarEmoji: {
    fontSize: 20,
  },
  brandTitle: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0F172A',
    letterSpacing: -0.5,
  },
  aiBadge: {
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  aiBadgeText: {
    fontSize: 11,
    fontWeight: '900',
    color: '#0F172A',
    letterSpacing: 0.5,
  },
  scrollView: {
    flex: 1,
  },
  contentContainer: {
    paddingHorizontal: 20,
    paddingBottom: 24,
    maxWidth: 600,
    alignSelf: 'center',
    width: '100%',
  },
  introHeader: {
    marginVertical: 12,
  },
  screenTitle: {
    fontSize: 26,
    fontWeight: '900',
    color: '#0F172A',
    letterSpacing: -0.5,
    marginBottom: 4,
  },
  screenSubtitle: {
    fontSize: 14,
    color: '#475569',
    fontWeight: '500',
  },
  categoriesTitle: {
    fontSize: 11,
    fontWeight: '900',
    color: '#0F172A',
    letterSpacing: 0.8,
    marginBottom: 10,
    marginTop: 4,
  },
  categoriesScroll: {
    flexDirection: 'row',
    gap: 8,
    paddingBottom: 16,
  },
  categoryPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 999,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    gap: 6,
  },
  categoryPillActive: {
    borderColor: '#0F172A',
    backgroundColor: '#FFFFFF',
  },
  categoryIcon: {
    fontSize: 14,
  },
  categoryText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#475569',
  },
  categoryTextActive: {
    color: '#0F172A',
    fontWeight: '800',
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
  bottomNav: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#EEF2F6',
    paddingVertical: 10,
    paddingBottom: 14,
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  navIcon: {
    fontSize: 20,
    color: '#94A3B8',
    marginBottom: 2,
  },
  navIconActive: {
    color: '#0F172A',
  },
  navLabel: {
    fontSize: 11,
    color: '#94A3B8',
    fontWeight: '700',
  },
  navLabelActive: {
    color: '#0F172A',
    fontWeight: '800',
  },
});
