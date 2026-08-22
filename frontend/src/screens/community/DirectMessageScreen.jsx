import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useChatStore } from '../../store/chatStore';
import chatSocket from '../../services/websocket/chatSocket';
import ChatHeader from '../../components/community/ChatHeader';
import ChatBubble from '../../components/community/ChatBubble';
import ChatInput from '../../components/community/ChatInput';
import TypingIndicator from '../../components/community/TypingIndicator';

export default function DirectMessageScreen({ route, navigation }) {
  const { chatId, recipientId, name } = route.params || {};
  const { messages, fetchMessages, sendDirectMessage, markChatRead, typingUsers, initWebSocket } = useChatStore();
  const [text, setText] = useState('');
  const chatMessages = messages[chatId] || [];
  const isTyping = typingUsers[chatId] || false;
  const flatListRef = useRef();

  useEffect(() => {
    if (chatId) {
      fetchMessages(chatId);
      markChatRead(chatId);
    }
    const unsubscribe = initWebSocket();
    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, [chatId]);

  useEffect(() => {
    if (chatId && chatMessages.length > 0) {
      // If there are unread messages received from the other user, mark as read
      const hasUnreadIncoming = chatMessages.some((m) => !m.is_own && m.status !== 'read');
      if (hasUnreadIncoming) {
        markChatRead(chatId);
      }
    }
  }, [chatMessages.length, chatId]);

  const handleSend = async (image_url = null) => {
    if (!text.trim() && !image_url) return;
    const msgText = text;
    setText('');
    chatSocket.sendTypingStop(chatId, recipientId);
    try {
      await sendDirectMessage(chatId, { text: msgText, image_url });
    } catch (err) {
      console.error('Failed to send DM:', err);
    }
  };


  const handleTextChange = (val) => {
    setText(val);
    if (val.length > 0) {
      chatSocket.sendTypingStart(chatId, recipientId);
    } else {
      chatSocket.sendTypingStop(chatId, recipientId);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      {/* Header */}
      <ChatHeader
        name={name || 'Caregiver'}
        onBack={() => navigation.goBack()}
        onProfile={() => navigation.navigate('CaregiverProfile', { userId: recipientId })}
      />

      {/* Messages Stream */}
      <FlatList
        ref={flatListRef}
        data={chatMessages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ChatBubble message={item} />}
        contentContainerStyle={styles.messagesContainer}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Typing Indicator */}
      {isTyping && <TypingIndicator name={name} />}

      {/* Input */}
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
