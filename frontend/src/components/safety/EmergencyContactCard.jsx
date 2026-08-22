import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Linking, Platform } from 'react-native';

export default function EmergencyContactCard({
  contact,
  onCall,
  onEdit,
  onDelete,
  onSetPrimary,
}) {
  const { name, relationship, phone, isPrimary, priority, avatar } = contact;

  const handleCall = () => {
    if (onCall) {
      onCall(contact);
    } else if (phone) {
      const cleaned = phone.replace(/[^0-9+]/g, '');
      Linking.openURL(`tel:${cleaned}`).catch(() => {});
    }
  };

  return (
    <View style={[styles.card, isPrimary && styles.primaryCard]}>
      <View style={styles.header}>
        <View style={[styles.avatarCircle, isPrimary && styles.primaryAvatar]}>
          <Text style={styles.avatarEmoji}>{avatar || '👤'}</Text>
        </View>

        <View style={styles.infoCol}>
          <View style={styles.nameRow}>
            <Text style={styles.name}>{name}</Text>
            {isPrimary && (
              <View style={styles.primaryBadge}>
                <Text style={styles.primaryBadgeText}>★ Primary Contact</Text>
              </View>
            )}
          </View>
          <Text style={styles.relationship}>{relationship}</Text>
          <Text style={styles.phoneText}>📞 {phone}</Text>
        </View>
      </View>

      <View style={styles.actionRow}>
        <TouchableOpacity
          style={styles.callBtn}
          onPress={handleCall}
          activeOpacity={0.85}
        >
          <Text style={styles.callBtnText}>📞 Call Contact</Text>
        </TouchableOpacity>

        {!isPrimary && onSetPrimary && (
          <TouchableOpacity
            style={styles.setPrimaryBtn}
            onPress={() => onSetPrimary(contact.id)}
            activeOpacity={0.85}
          >
            <Text style={styles.setPrimaryText}>Set as Primary</Text>
          </TouchableOpacity>
        )}

        {onEdit && (
          <TouchableOpacity
            style={styles.iconBtn}
            onPress={() => onEdit(contact)}
            activeOpacity={0.85}
          >
            <Text style={styles.iconBtnText}>✏️</Text>
          </TouchableOpacity>
        )}

        {onDelete && !isPrimary && (
          <TouchableOpacity
            style={[styles.iconBtn, styles.deleteBtn]}
            onPress={() => onDelete(contact.id)}
            activeOpacity={0.85}
          >
            <Text style={styles.iconBtnText}>🗑️</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 12,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  primaryCard: {
    borderColor: '#93C5FD',
    backgroundColor: '#FAFDFE',
    borderLeftWidth: 5,
    borderLeftColor: '#2563EB',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  avatarCircle: {
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
  },
  primaryAvatar: {
    backgroundColor: '#EFF6FF',
    borderColor: '#BFDBFE',
  },
  avatarEmoji: {
    fontSize: 22,
  },
  infoCol: {
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: 6,
  },
  name: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  primaryBadge: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  primaryBadgeText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#2563EB',
  },
  relationship: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '500',
  },
  phoneText: {
    fontSize: 12,
    color: '#334155',
    fontWeight: '700',
    marginTop: 4,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  callBtn: {
    flex: 1,
    backgroundColor: '#059669',
    paddingVertical: 9,
    paddingHorizontal: 12,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  callBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  setPrimaryBtn: {
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#BFDBFE',
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 10,
  },
  setPrimaryText: {
    color: '#2563EB',
    fontSize: 11,
    fontWeight: '700',
  },
  iconBtn: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  deleteBtn: {
    backgroundColor: '#FEF2F2',
    borderColor: '#FECACA',
  },
  iconBtnText: {
    fontSize: 14,
  },
});
