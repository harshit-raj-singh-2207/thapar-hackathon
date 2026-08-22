import React from 'react';
import { View, TextInput, StyleSheet, TouchableOpacity, Text, Alert } from 'react-native';
import { communityApi } from '../../services/api/communityApi';

export default function ChatInput({ text, onChangeText, onSend, onSendMedia }) {
  const handleUploadImage = async () => {
    // Demo mock image upload for visual test
    try {
      const mockUrl = '/static/uploads/visual_schedule.jpg';
      onSendMedia(mockUrl);
    } catch (err) {
      Alert.alert('Upload Error', 'Failed to attach image');
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.attachBtn} onPress={handleUploadImage}>
        <Text style={styles.attachIcon}>📷</Text>
      </TouchableOpacity>
      <TextInput
        style={styles.input}
        placeholder="Type a message..."
        value={text}
        onChangeText={onChangeText}
        placeholderTextColor="#94A3B8"
        multiline
      />
      <TouchableOpacity
        style={[styles.sendBtn, !text.trim() && styles.disabledBtn]}
        onPress={onSend}
        disabled={!text.trim()}
      >
        <Text style={styles.sendIcon}>➔</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    gap: 8,
  },
  attachBtn: {
    padding: 8,
  },
  attachIcon: {
    fontSize: 22,
  },
  input: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    fontSize: 15,
    maxHeight: 100,
    color: '#0F172A',
  },
  sendBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  disabledBtn: {
    backgroundColor: '#CBD5E1',
  },
  sendIcon: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '700',
  },
});
