import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import { useCommunityStore } from '../../store/communityStore';

const CATEGORIES = ['Resources', 'Tips', 'Questions', 'Support', 'Milestones', 'Sensory'];

export default function CreatePostScreen({ navigation }) {
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('Resources');
  const [imageUrl, setImageUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { createPost } = useCommunityStore();

  const handlePost = async () => {
    if (!content.trim()) {
      Alert.alert('Error', 'Please enter some content for your post.');
      return;
    }
    setSubmitting(true);
    try {
      await createPost({ content, category, image_url: imageUrl || null });
      Alert.alert('Success', 'Post published to the caregiver community!');
      navigation.goBack();
    } catch (err) {
      Alert.alert('Error', err.detail || 'Could not publish post.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>Cancel</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Create Post</Text>
        <TouchableOpacity
          style={[styles.publishBtn, (!content.trim() || submitting) && styles.disabledBtn]}
          onPress={handlePost}
          disabled={!content.trim() || submitting}
        >
          <Text style={styles.publishText}>Publish</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.body}>
        {/* Category Picker */}
        <Text style={styles.sectionTitle}>Select Category</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.categoryScroll}>
          {CATEGORIES.map((cat) => (
            <TouchableOpacity
              key={cat}
              style={[styles.catPill, category === cat && styles.activeCatPill]}
              onPress={() => setCategory(cat)}
            >
              <Text style={[styles.catPillText, category === cat && styles.activeCatPillText]}>{cat}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Content Input */}
        <Text style={styles.sectionTitle}>Post Content</Text>
        <TextInput
          style={styles.textInput}
          placeholder="Share resources, tips, or ask the caregiver community..."
          value={content}
          onChangeText={setContent}
          multiline
          placeholderTextColor="#94A3B8"
        />

        {/* Image URL input */}
        <Text style={styles.sectionTitle}>Image Attachment URL (Optional)</Text>
        <TextInput
          style={styles.urlInput}
          placeholder="/static/uploads/blanket.jpg or image URL"
          value={imageUrl}
          onChangeText={setImageUrl}
          placeholderTextColor="#94A3B8"
        />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backText: {
    fontSize: 16,
    color: '#64748B',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0F172A',
  },
  publishBtn: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  disabledBtn: {
    backgroundColor: '#CBD5E1',
  },
  publishText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  body: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
    marginTop: 16,
    marginBottom: 8,
  },
  categoryScroll: {
    gap: 8,
    paddingBottom: 8,
  },
  catPill: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#E2E8F0',
  },
  activeCatPill: {
    backgroundColor: '#4F46E5',
  },
  catPillText: {
    fontSize: 13,
    color: '#475569',
    fontWeight: '600',
  },
  activeCatPillText: {
    color: '#FFFFFF',
  },
  textInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#0F172A',
    minHeight: 140,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  urlInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    color: '#0F172A',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
});
