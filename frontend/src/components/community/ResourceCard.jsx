import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Linking, Alert } from 'react-native';

export default function ResourceCard({ resource, onDelete }) {
  const { title, description, category, url, file_type, author_name, is_own } = resource;

  const handleOpen = () => {
    if (url) {
      Linking.openURL(url).catch(() => {
        Alert.alert('Resource Link', `Opening resource: ${url}`);
      });
    } else {
      Alert.alert('Resource', `${title}\n\n${description}`);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'template':
        return '📋';
      case 'guide':
        return '📖';
      case 'checklist':
        return '✅';
      case 'pdf':
        return '📄';
      default:
        return '📌';
    }
  };

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.typeBadge}>
          <Text style={styles.icon}>{getIcon(file_type)}</Text>
          <Text style={styles.typeText}>{file_type?.toUpperCase() || 'RESOURCE'}</Text>
        </View>
        <View style={styles.categoryBadge}>
          <Text style={styles.categoryText}>{category}</Text>
        </View>
      </View>

      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>

      <View style={styles.footer}>
        <Text style={styles.authorText}>Shared by {author_name || 'Caregiver'}</Text>
        <View style={styles.actionRow}>
          {is_own && onDelete && (
            <TouchableOpacity onPress={() => onDelete(resource.id)} style={styles.deleteBtn}>
              <Text style={styles.deleteText}>Delete</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity style={styles.accessBtn} onPress={handleOpen}>
            <Text style={styles.accessText}>View Resource →</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderLeftWidth: 4,
    borderLeftColor: '#4F46E5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  typeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  icon: {
    fontSize: 16,
  },
  typeText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#4F46E5',
    letterSpacing: 0.5,
  },
  categoryBadge: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
  },
  categoryText: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '500',
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 6,
  },
  description: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 20,
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#F8FAFC',
    paddingTop: 10,
  },
  authorText: {
    fontSize: 12,
    color: '#94A3B8',
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  deleteText: {
    fontSize: 13,
    color: '#DC2626',
    fontWeight: '600',
  },
  accessBtn: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  accessText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#4F46E5',
  },
});
