import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useLearning } from '../../hooks/useLearning';

export default function TutorScreen({ navigation }) {
  const { tutorMessages, askTutor, tutorLoading } = useLearning();
  const [inputText, setInputText] = useState('');
  const scrollViewRef = useRef(null);

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [tutorMessages]);

  const handleSend = (textToSend) => {
    const q = textToSend || inputText;
    if (!q.trim()) return;
    setInputText('');
    askTutor(q.trim());
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <View style={styles.tutorHeaderTitleCol}>
          <Text style={styles.headerTitle}>Nivi the AI Tutor 🤖</Text>
          <Text style={styles.headerSub}>Patient learning & simple analogies</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesList}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        >
          {tutorMessages.map((msg) => {
            const isTutor = msg.sender === 'tutor';
            return (
              <View
                key={msg.id}
                style={[
                  styles.messageBubbleWrapper,
                  isTutor ? styles.tutorWrapper : styles.childWrapper,
                ]}
              >
                {isTutor && (
                  <View style={styles.tutorAvatar}>
                    <Text style={{ fontSize: 18 }}>{msg.icon || '🤖'}</Text>
                  </View>
                )}

                <View
                  style={[
                    styles.messageBubble,
                    isTutor ? styles.tutorBubble : styles.childBubble,
                  ]}
                >
                  <Text style={[styles.messageText, !isTutor && styles.childMessageText]}>
                    {msg.text}
                  </Text>

                  {/* Simple Analogy Box */}
                  {msg.simple_analogy ? (
                    <View style={styles.analogyBox}>
                      <Text style={styles.analogyTag}>💡 SIMPLE ANALOGY</Text>
                      <Text style={styles.analogyText}>{msg.simple_analogy}</Text>
                    </View>
                  ) : null}

                  {/* Follow-up question chips */}
                  {msg.follow_up_questions && msg.follow_up_questions.length > 0 ? (
                    <View style={styles.followUpsRow}>
                      {msg.follow_up_questions.map((q, qIdx) => (
                        <TouchableOpacity
                          key={qIdx}
                          style={styles.followUpPill}
                          onPress={() => handleSend(q)}
                          activeOpacity={0.8}
                        >
                          <Text style={styles.followUpText}>✨ {q}</Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  ) : null}
                </View>
              </View>
            );
          })}

          {tutorLoading && (
            <View style={styles.loadingBubble}>
              <ActivityIndicator size="small" color="#8B5CF6" />
              <Text style={styles.loadingText}>Nivi is thinking of an analogy...</Text>
            </View>
          )}
        </ScrollView>

        {/* Chat Input Bar */}
        <View style={styles.inputBar}>
          <TextInput
            style={styles.input}
            placeholder="Ask Nivi anything! (e.g. Why is the sky blue?)"
            placeholderTextColor="#94A3B8"
            value={inputText}
            onChangeText={setInputText}
            onSubmitEditing={() => handleSend()}
          />
          <TouchableOpacity
            style={[styles.sendBtn, !inputText.trim() && styles.sendBtnDisabled]}
            onPress={() => handleSend()}
            disabled={!inputText.trim() || tutorLoading}
            activeOpacity={0.85}
          >
            <Text style={styles.sendIcon}>🚀</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
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
  tutorHeaderTitleCol: {
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0F172A',
  },
  headerSub: {
    fontSize: 11,
    color: '#64748B',
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    paddingBottom: 24,
    maxWidth: 680,
    alignSelf: 'center',
    width: '100%',
  },
  messageBubbleWrapper: {
    flexDirection: 'row',
    marginVertical: 8,
    gap: 8,
  },
  tutorWrapper: {
    justifyContent: 'flex-start',
  },
  childWrapper: {
    justifyContent: 'flex-end',
  },
  tutorAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F5F3FF',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#DDD6FE',
  },
  messageBubble: {
    borderRadius: 20,
    padding: 14,
    maxWidth: '85%',
  },
  tutorBubble: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
  },
  childBubble: {
    backgroundColor: '#2563EB',
    alignSelf: 'flex-end',
  },
  messageText: {
    fontSize: 15,
    color: '#0F172A',
    lineHeight: 21,
    fontWeight: '600',
  },
  childMessageText: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  analogyBox: {
    backgroundColor: '#FFFBEB',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FDE68A',
    padding: 10,
    marginTop: 10,
  },
  analogyTag: {
    fontSize: 10,
    fontWeight: '900',
    color: '#B45309',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  analogyText: {
    fontSize: 13,
    color: '#92400E',
    fontWeight: '600',
    lineHeight: 18,
  },
  followUpsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 10,
  },
  followUpPill: {
    backgroundColor: '#F5F3FF',
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: '#DDD6FE',
  },
  followUpText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#7C3AED',
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignSelf: 'flex-start',
    gap: 8,
    marginVertical: 6,
  },
  loadingText: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#EEF2F6',
    gap: 8,
    maxWidth: 680,
    alignSelf: 'center',
    width: '100%',
  },
  input: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 14,
    color: '#0F172A',
    fontWeight: '600',
  },
  sendBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#8B5CF6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendBtnDisabled: {
    opacity: 0.4,
  },
  sendIcon: {
    fontSize: 18,
  },
});
