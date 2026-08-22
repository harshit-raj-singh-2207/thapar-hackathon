import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function TutorMessage({ message }) {
  const isTutor = message.sender === 'tutor';

  return (
    <View style={[styles.wrapper, isTutor ? styles.tutorWrapper : styles.childWrapper]}>
      {isTutor && (
        <View style={styles.avatar}>
          <Text style={{ fontSize: 16 }}>{message.icon || '🤖'}</Text>
        </View>
      )}
      <View style={[styles.bubble, isTutor ? styles.tutorBubble : styles.childBubble]}>
        <Text style={[styles.text, !isTutor && styles.childText]}>{message.text}</Text>
        {message.simple_analogy ? (
          <View style={styles.analogyBox}>
            <Text style={styles.analogyTag}>💡 SIMPLE ANALOGY</Text>
            <Text style={styles.analogyText}>{message.simple_analogy}</Text>
          </View>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    marginVertical: 6,
    gap: 8,
  },
  tutorWrapper: {
    justifyContent: 'flex-start',
  },
  childWrapper: {
    justifyContent: 'flex-end',
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F5F3FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  bubble: {
    borderRadius: 18,
    padding: 12,
    maxWidth: '85%',
  },
  tutorBubble: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
  },
  childBubble: {
    backgroundColor: '#2563EB',
  },
  text: {
    fontSize: 14,
    color: '#0F172A',
    fontWeight: '600',
    lineHeight: 20,
  },
  childText: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  analogyBox: {
    backgroundColor: '#FFFBEB',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#FDE68A',
    padding: 8,
    marginTop: 8,
  },
  analogyTag: {
    fontSize: 9,
    fontWeight: '900',
    color: '#B45309',
    marginBottom: 2,
  },
  analogyText: {
    fontSize: 12,
    color: '#92400E',
    fontWeight: '600',
  },
});
