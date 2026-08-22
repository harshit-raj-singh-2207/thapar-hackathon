import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import MessageStatus from './MessageStatus';

export default function ChatBubble({ message, isGroup = false }) {
  const { text, attachment_url, is_own, sender_name, status, created_at } = message;

  return (
    <View style={[styles.wrapper, is_own ? styles.ownWrapper : styles.otherWrapper]}>
      {!is_own && isGroup && sender_name && (
        <Text style={styles.senderName}>{sender_name}</Text>
      )}
      <View style={[styles.bubble, is_own ? styles.ownBubble : styles.otherBubble]}>
        {attachment_url && (
          <Image source={{ uri: attachment_url }} style={styles.imageAttachment} resizeMode="cover" />
        )}
        {text && <Text style={[styles.messageText, is_own ? styles.ownText : styles.otherText]}>{text}</Text>}
        <View style={styles.footerRow}>
          <Text style={[styles.timeText, is_own ? styles.ownTime : styles.otherTime]}>
            {new Date(created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </Text>
          {is_own && <MessageStatus status={status || 'sent'} />}
        </View>
      </View>
    </View>
  );
}


const styles = StyleSheet.create({
  wrapper: {
    marginVertical: 4,
    maxWidth: '78%',
  },
  ownWrapper: {
    alignSelf: 'flex-end',
  },
  otherWrapper: {
    alignSelf: 'flex-start',
  },
  senderName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748B',
    marginBottom: 2,
    marginLeft: 4,
  },
  bubble: {
    borderRadius: 16,
    padding: 12,
  },
  ownBubble: {
    backgroundColor: '#4F46E5',
    borderBottomRightRadius: 2,
  },
  otherBubble: {
    backgroundColor: '#FFFFFF',
    borderBottomLeftRadius: 2,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  imageAttachment: {
    width: 200,
    height: 150,
    borderRadius: 10,
    marginBottom: 6,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 21,
  },
  ownText: {
    color: '#FFFFFF',
  },
  otherText: {
    color: '#0F172A',
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-end',
    marginTop: 4,
    gap: 2,
  },
  timeText: {
    fontSize: 11,
  },
  ownTime: {
    color: '#C7D2FE',
  },
  otherTime: {
    color: '#94A3B8',
  },
});

