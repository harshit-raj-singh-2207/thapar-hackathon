import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Modal,
  Alert,
} from 'react-native';
import { useSafety } from '../../hooks/useSafety';
import AppHeader from '../../components/common/AppHeader';
import AppButton from '../../components/common/AppButton';
import AppInput from '../../components/common/AppInput';
import EmptyState from '../../components/common/EmptyState';
import Loading from '../../components/common/Loading';
import EmergencyContactCard from '../../components/safety/EmergencyContactCard';

export default function EmergencyContactsScreen({ navigation }) {
  const {
    emergencyContacts,
    contactsLoading,
    fetchEmergencyContacts,
    addEmergencyContact,
    updateEmergencyContact,
    removeEmergencyContact,
    setPrimaryContact,
  } = useSafety();

  const [modalVisible, setModalVisible] = useState(false);
  const [editingContact, setEditingContact] = useState(null);

  // Form State
  const [name, setName] = useState('');
  const [relationship, setRelationship] = useState('');
  const [phone, setPhone] = useState('');
  const [avatar, setAvatar] = useState('👤');
  const [isPrimary, setIsPrimary] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    fetchEmergencyContacts();
  }, []);

  const openAddModal = () => {
    setEditingContact(null);
    setName('');
    setRelationship('');
    setPhone('');
    setAvatar('👤');
    setIsPrimary(false);
    setFormError('');
    setModalVisible(true);
  };

  const openEditModal = (contact) => {
    setEditingContact(contact);
    setName(contact.name);
    setRelationship(contact.relationship);
    setPhone(contact.phone);
    setAvatar(contact.avatar || '👤');
    setIsPrimary(contact.isPrimary || false);
    setFormError('');
    setModalVisible(true);
  };

  const handleSave = async () => {
    if (!name.trim()) {
      setFormError('Please enter contact full name');
      return;
    }
    if (!phone.trim()) {
      setFormError('Please enter contact phone number');
      return;
    }

    const payload = {
      name: name.trim(),
      relationship: relationship.trim() || 'Caregiver Support',
      phone: phone.trim(),
      avatar,
      isPrimary,
    };

    if (editingContact) {
      await updateEmergencyContact(editingContact.id, payload);
    } else {
      await addEmergencyContact(payload);
    }

    setModalVisible(false);
  };

  const handleDelete = (contactId) => {
    Alert.alert(
      'Remove Emergency Contact',
      'Are you sure you want to remove this contact from the emergency escalation roster?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => removeEmergencyContact(contactId),
        },
      ]
    );
  };

  const avatarOptions = ['👩‍⚕️', '👨‍🏫', '👩', '👨', '👵', '👴', '👮‍♂️', '🚑', '👤'];

  return (
    <SafeAreaView style={styles.safeArea}>
      <AppHeader
        title="Emergency Contacts"
        subtitle="Caregiver escalation roster for safety alerts"
        onBack={() => (navigation.canGoBack() ? navigation.goBack() : navigation.navigate('CaregiverDashboard'))}
        rightElement={
          <TouchableOpacity
            style={styles.addBtn}
            onPress={openAddModal}
            activeOpacity={0.85}
          >
            <Text style={styles.addBtnText}>＋ Add</Text>
          </TouchableOpacity>
        }
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Info Banner */}
        <View style={styles.infoBanner}>
          <Text style={styles.infoIcon}>ℹ️</Text>
          <Text style={styles.infoText}>
            When an SOS panic event or severe separation breach occurs, all contacts listed below receive an instantaneous priority notification.
          </Text>
        </View>

        {contactsLoading ? (
          <Loading message="Loading emergency contacts..." />
        ) : emergencyContacts.length === 0 ? (
          <EmptyState
            icon="👥"
            title="No emergency contacts configured"
            description="Add caregivers, therapists, or school personnel to receive alerts in case of an emergency."
            actionLabel="Add First Contact"
            onAction={openAddModal}
          />
        ) : (
          emergencyContacts.map((contact) => (
            <EmergencyContactCard
              key={contact.id}
              contact={contact}
              onEdit={openEditModal}
              onDelete={handleDelete}
              onSetPrimary={setPrimaryContact}
            />
          ))
        )}
      </ScrollView>

      {/* Add / Edit Contact Modal */}
      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {editingContact ? 'Edit Emergency Contact' : 'Add Emergency Contact'}
              </Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Text style={styles.closeBtnText}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* Avatar Emoji Selector */}
              <Text style={styles.inputLabel}>Choose Icon / Role Avatar</Text>
              <View style={styles.avatarPickerRow}>
                {avatarOptions.map((emoji) => (
                  <TouchableOpacity
                    key={emoji}
                    style={[
                      styles.avatarOption,
                      avatar === emoji && styles.avatarOptionSelected,
                    ]}
                    onPress={() => setAvatar(emoji)}
                  >
                    <Text style={styles.avatarOptionText}>{emoji}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <AppInput
                label="Full Name *"
                value={name}
                onChangeText={(t) => {
                  setName(t);
                  setFormError('');
                }}
                placeholder="e.g. Dr. Jordan Patel"
              />

              <AppInput
                label="Relationship / Role"
                value={relationship}
                onChangeText={setRelationship}
                placeholder="e.g. Primary Caregiver, Speech Therapist"
              />

              <AppInput
                label="Phone Number *"
                value={phone}
                onChangeText={(t) => {
                  setPhone(t);
                  setFormError('');
                }}
                placeholder="e.g. +91 98765 43210"
                keyboardType="phone-pad"
              />

              {formError ? <Text style={styles.formErrorText}>{formError}</Text> : null}

              <TouchableOpacity
                style={styles.primaryToggleRow}
                onPress={() => setIsPrimary(!isPrimary)}
                activeOpacity={0.8}
              >
                <View style={[styles.checkbox, isPrimary && styles.checkboxActive]}>
                  {isPrimary && <Text style={styles.checkmark}>✓</Text>}
                </View>
                <View style={styles.toggleTextCol}>
                  <Text style={styles.toggleTitle}>Mark as Primary Emergency Contact</Text>
                  <Text style={styles.toggleSub}>
                    First to be dialed automatically upon SOS panic trigger
                  </Text>
                </View>
              </TouchableOpacity>
            </ScrollView>

            <View style={styles.modalFooter}>
              <AppButton
                title="Cancel"
                onPress={() => setModalVisible(false)}
                variant="secondary"
                size="md"
                style={styles.modalCancelBtn}
              />
              <AppButton
                title={editingContact ? 'Save Changes' : 'Add Contact'}
                onPress={handleSave}
                variant="primary"
                size="md"
                style={styles.modalSaveBtn}
              />
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  addBtn: {
    backgroundColor: '#2563EB',
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 999,
  },
  addBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  infoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#BFDBFE',
    marginBottom: 16,
  },
  infoIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#1E40AF',
    lineHeight: 18,
    fontWeight: '600',
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 22,
    width: '100%',
    maxWidth: 480,
    maxHeight: '90%',
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 10,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  closeBtnText: {
    fontSize: 18,
    color: '#64748B',
    fontWeight: '800',
    padding: 4,
  },
  modalBody: {
    maxHeight: 400,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 8,
  },
  avatarPickerRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16,
  },
  avatarOption: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
  },
  avatarOptionSelected: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  avatarOptionText: {
    fontSize: 20,
  },
  formErrorText: {
    color: '#DC2626',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 10,
  },
  primaryToggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginTop: 4,
    marginBottom: 16,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#CBD5E1',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    backgroundColor: '#FFFFFF',
  },
  checkboxActive: {
    backgroundColor: '#2563EB',
    borderColor: '#2563EB',
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '900',
  },
  toggleTextCol: {
    flex: 1,
  },
  toggleTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  toggleSub: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  modalFooter: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 16,
  },
  modalCancelBtn: {
    flex: 1,
  },
  modalSaveBtn: {
    flex: 1,
  },
});
