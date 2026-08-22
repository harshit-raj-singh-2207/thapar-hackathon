import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Linking } from 'react-native';

export default function ContactCard({
  title = 'Primary Contact / Therapist',
  name = 'Dr. Emily Vance',
  role = 'Pediatric Therapist',
  phone = '+1 (555) 234-5678',
  onCall,
  onMessage,
}) {
  const handleCall = () => {
    if (onCall) return onCall();
    if (phone) Linking.openURL(`tel:${phone}`);
  };

  const handleMessage = () => {
    if (onMessage) return onMessage();
    if (phone) Linking.openURL(`sms:${phone}`);
  };

  return (
    <View style={styles.card}>
      <Text style={styles.headerTitle}>{title}</Text>
      <View style={styles.contentRow}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{name ? name[0] : 'C'}</Text>
        </View>
        <View style={styles.info}>
          <Text style={styles.name}>{name}</Text>
          <Text style={styles.role}>{role}</Text>
          <Text style={styles.phone}>{phone}</Text>
        </View>
      </View>

      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.callBtn} onPress={handleCall} activeOpacity={0.8}>
          <Text style={styles.btnText}>📞 Call Now</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.msgBtn} onPress={handleMessage} activeOpacity={0.8}>
          <Text style={styles.btnText}>💬 Send SMS</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  headerTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#818CF8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 10,
  },
  contentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#3730A3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    color: '#E0E7FF',
    fontSize: 18,
    fontWeight: '700',
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: '700',
    color: '#F8FAFC',
  },
  role: {
    fontSize: 13,
    color: '#94A3B8',
    marginTop: 2,
  },
  phone: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  actionRow: {
    flexDirection: 'row',
    gap: 10,
  },
  callBtn: {
    flex: 1,
    backgroundColor: '#059669',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  msgBtn: {
    flex: 1,
    backgroundColor: '#4F46E5',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  btnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
});
