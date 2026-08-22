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

const CATEGORIES = ['Sensory', 'Communication', 'Routines', 'Education', 'Wellbeing', 'Family'];

export default function CreateGroupScreen({ navigation }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Sensory');
  const [submitting, setSubmitting] = useState(false);
  const { fetchGroups } = useCommunityStore();
  const communityApi = require('../../services/api/communityApi').communityApi;

  const handleCreate = async () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter a group name.');
      return;
    }
    setSubmitting(true);
    try {
      await communityApi.createGroup({ name, description, category });
      await fetchGroups();
      Alert.alert('Success', `Group "${name}" created!`);
      navigation.goBack();
    } catch (err) {
      Alert.alert('Error', err.detail || 'Could not create group.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>Cancel</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Create Caregiver Group</Text>
        <TouchableOpacity
          style={[styles.createBtn, (!name.trim() || submitting) && styles.disabledBtn]}
          onPress={handleCreate}
          disabled={!name.trim() || submitting}
        >
          <Text style={styles.createText}>Create</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.body}>
        <Text style={styles.sectionTitle}>Group Name</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. IEP Advocacy Network"
          value={name}
          onChangeText={setName}
          placeholderTextColor="#94A3B8"
        />

        <Text style={styles.sectionTitle}>Category</Text>
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

        <Text style={styles.sectionTitle}>Description</Text>
        <TextInput
          style={[styles.input, styles.multiline]}
          placeholder="Describe the purpose of this caregiver support circle..."
          value={description}
          onChangeText={setDescription}
          multiline
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
    fontSize: 17,
    fontWeight: '700',
    color: '#0F172A',
  },
  createBtn: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  disabledBtn: {
    backgroundColor: '#CBD5E1',
  },
  createText: {
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
  input: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    fontSize: 15,
    color: '#0F172A',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  multiline: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
});
