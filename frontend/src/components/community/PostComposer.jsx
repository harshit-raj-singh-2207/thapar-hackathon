import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from 'react-native';
import AttachmentButton from './AttachmentButton';

export default function PostComposer({ onSubmit, loading }) {
  const [content, setContent] = useState('');

  const handlePost = () => {
    if (!content.trim()) return;
    onSubmit({ content });
    setContent('');
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Share an update or question with fellow caregivers..."
        value={content}
        onChangeText={setContent}
        multiline
      />
      <View style={styles.actions}>
        <AttachmentButton onPress={() => {}} />
        <TouchableOpacity
          style={[styles.btn, (!content.trim() || loading) && styles.disabled]}
          onPress={handlePost}
          disabled={!content.trim() || loading}
        >
          <Text style={styles.btnText}>{loading ? 'Posting...' : 'Post'}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  input: {
    fontSize: 15,
    color: '#0F172A',
    minHeight: 80,
    textAlignVertical: 'top',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 12,
  },
  btn: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
  },
  disabled: {
    backgroundColor: '#94A3B8',
  },
  btnText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
});
