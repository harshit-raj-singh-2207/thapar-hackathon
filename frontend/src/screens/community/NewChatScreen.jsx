import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useChatStore } from '../../store/chatStore';

export default function NewChatScreen({ navigation }) {
  const [recipientId, setRecipientId] = useState('user-verified-david');
  const { startChat } = useChatStore();

  const handleStart = async () => {
    if (!recipientId.trim()) {
      Alert.alert('Error', 'Please enter a caregiver user ID.');
      return;
    }
    try {
      const chat = await startChat(recipientId);
      navigation.replace('DirectMessage', {
        chatId: chat.id,
        recipientId,
        name: 'Verified Caregiver',
      });
    } catch (err) {
      Alert.alert('Error', err.detail || 'Could not start direct conversation.');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>Cancel</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>New Direct Message</Text>
        <TouchableOpacity onPress={handleStart} style={styles.startBtn}>
          <Text style={styles.startText}>Start</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.body}>
        <Text style={styles.label}>Caregiver User ID</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. user-verified-david"
          value={recipientId}
          onChangeText={setRecipientId}
          placeholderTextColor="#94A3B8"
        />

        <View style={styles.quickList}>
          <Text style={styles.quickTitle}>Verified Caregivers:</Text>
          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => setRecipientId('user-verified-david')}
          >
            <Text style={styles.quickName}>David Nguyen</Text>
            <Text style={styles.quickId}>user-verified-david</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.quickItem}
            onPress={() => setRecipientId('user-verified-sarah')}
          >
            <Text style={styles.quickName}>Sarah Mitchell</Text>
            <Text style={styles.quickId}>user-verified-sarah</Text>
          </TouchableOpacity>
        </View>
      </View>
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
  startBtn: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  startText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  body: {
    padding: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    fontSize: 15,
    color: '#0F172A',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    marginBottom: 24,
  },
  quickList: {
    gap: 10,
  },
  quickTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
  },
  quickItem: {
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  quickName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#0F172A',
  },
  quickId: {
    fontSize: 12,
    color: '#64748B',
  },
});
