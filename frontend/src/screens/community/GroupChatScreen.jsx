import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useChatStore } from '../../store/chatStore';
import chatSocket from '../../services/websocket/chatSocket';
import GroupHeader from '../../components/community/GroupHeader';
import ChatBubble from '../../components/community/ChatBubble';
import ChatInput from '../../components/community/ChatInput';
import TypingIndicator from '../../components/community/TypingIndicator';

export default function GroupChatScreen({ route, navigation }) {
  const { groupId, name } = route.params || {};
  const { messages, fetchGroupMessages, sendGroupMessage, typingUsers, initWebSocket } = useChatStore();
  const [text, setText] = useState('');
  const groupMessages = messages[groupId] || [];
  const isTyping = typingUsers[groupId] || false;
  const flatListRef = useRef();

  useEffect(() => {
    if (groupId) {
      fetchGroupMessages(groupId);
    }
    const unsubscribe = initWebSocket();
    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, [groupId]);


  const handleSend = async (image_url = null) => {
    if (!text.trim() && !image_url) return;
    const msgText = text;
    setText('');
    chatSocket.sendTypingStop(null, null, groupId);
    try {
      await sendGroupMessage(groupId, { text: msgText, image_url });
    } catch (err) {
      console.error('Failed to send group message:', err);
    }
  };

  const handleTextChange = (val) => {
    setText(val);
    if (val.length > 0) {
      chatSocket.sendTypingStart(null, null, groupId);
    } else {
      chatSocket.sendTypingStop(null, null, groupId);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      {/* Group Header */}
      <GroupHeader
        name={name || 'Caregiver Group'}
        onBack={() => navigation.goBack()}
        onDetails={() => navigation.navigate('GroupDetails', { groupId })}
        onMembers={() => navigation.navigate('GroupMembers', { groupId })}
      />

      {/* Message Stream */}
      <FlatList
        ref={flatListRef}
        data={groupMessages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ChatBubble message={item} isGroup />}
        contentContainerStyle={styles.messagesContainer}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Typing Indicator */}
      {isTyping && <TypingIndicator name="Group member" />}

      {/* Chat Input */}
      <ChatInput
        text={text}
        onChangeText={handleTextChange}
        onSend={() => handleSend()}
        onSendMedia={(url) => handleSend(url)}
      />
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  messagesContainer: {
    padding: 16,
  },
});
