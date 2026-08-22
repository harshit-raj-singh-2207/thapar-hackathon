import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Switch } from 'react-native';

export default function SafeZoneCard({
  zone,
  isChildInside = false,
  onToggleActive,
  onEdit,
  onDelete,
  onFocusMap,
}) {
  return (
    <View
      style={[
        styles.card,
        isChildInside && styles.cardActiveInside,
        !zone.active && styles.cardDisabled,
      ]}
    >
      {/* Top Header */}
      <View style={styles.headerRow}>
        <View style={styles.nameSection}>
          <View style={[styles.iconBox, { backgroundColor: `${zone.color || '#2563EB'}15` }]}>
            <Text style={styles.icon}>{zone.icon || '🛡️'}</Text>
          </View>
          <View style={styles.titleCol}>
            <Text style={styles.zoneName} numberOfLines={1}>
              {zone.name}
            </Text>
            <View style={styles.categoryBadge}>
              <Text style={[styles.categoryText, { color: zone.color || '#2563EB' }]}>
                {zone.category || 'Safe Zone'}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.switchWrapper}>
          <Switch
            value={zone.active}
            onValueChange={() => onToggleActive && onToggleActive(zone.id)}
            trackColor={{ false: '#E2E8F0', true: '#BFDBFE' }}
            thumbColor={zone.active ? '#2563EB' : '#94A3B8'}
          />
        </View>
      </View>

      {/* Address */}
      <Text style={styles.addressText}>{zone.address}</Text>

      {/* Geofence Status Pill */}
      <View style={styles.statusRow}>
        <View
          style={[
            styles.occupancyBadge,
            isChildInside ? styles.occupiedBg : styles.vacantBg,
          ]}
        >
          <Text style={styles.statusDot}>{isChildInside ? '🟢' : '⚪'}</Text>
          <Text
            style={[
              styles.occupancyText,
              { color: isChildInside ? '#065F46' : '#64748B' },
            ]}
          >
            {isChildInside ? 'Child Inside Zone' : 'Child Outside'}
          </Text>
        </View>

        <View style={styles.radiusBadge}>
          <Text style={styles.radiusText}>Radius: {zone.radius || 150}m</Text>
        </View>
      </View>

      {/* Schedule and Alerts Meta */}
      <View style={styles.metaBox}>
        <Text style={styles.scheduleText}>🕒 Schedule: {zone.schedule || 'Always Active'}</Text>
        <Text style={styles.alertsText}>
          🔔 Alerts: {zone.notifyOnEntry ? 'Entry ✓' : ''} {zone.notifyOnExit ? 'Exit ✓' : ''}
        </Text>
      </View>

      {/* Action Footer */}
      <View style={styles.actionsRow}>
        {onFocusMap && (
          <TouchableOpacity
            style={styles.focusBtn}
            onPress={() => onFocusMap(zone)}
            activeOpacity={0.8}
          >
            <Text style={styles.focusBtnText}>🗺️ Center on Map</Text>
          </TouchableOpacity>
        )}

        {onEdit && (
          <TouchableOpacity
            style={styles.editBtn}
            onPress={() => onEdit(zone)}
            activeOpacity={0.8}
          >
            <Text style={styles.editBtnText}>✏️ Edit</Text>
          </TouchableOpacity>
        )}

        {onDelete && (
          <TouchableOpacity
            style={styles.deleteBtn}
            onPress={() => onDelete(zone.id)}
            activeOpacity={0.8}
          >
            <Text style={styles.deleteBtnText}>🗑️</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 2,
  },
  cardActiveInside: {
    borderColor: '#A7F3D0',
    backgroundColor: '#F0FDF4',
  },
  cardDisabled: {
    opacity: 0.6,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  nameSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconBox: {
    width: 42,
    height: 42,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  icon: {
    fontSize: 20,
  },
  titleCol: {
    flex: 1,
  },
  zoneName: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  categoryBadge: {
    marginTop: 2,
  },
  categoryText: {
    fontSize: 11,
    fontWeight: '700',
  },
  switchWrapper: {
    marginLeft: 8,
  },
  addressText: {
    fontSize: 12,
    color: '#475569',
    marginBottom: 12,
    fontWeight: '500',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  occupancyBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    borderWidth: 1,
  },
  occupiedBg: {
    backgroundColor: '#ECFDF5',
    borderColor: '#A7F3D0',
  },
  vacantBg: {
    backgroundColor: '#F8FAFC',
    borderColor: '#E2E8F0',
  },
  statusDot: {
    fontSize: 8,
    marginRight: 6,
  },
  occupancyText: {
    fontSize: 11,
    fontWeight: '700',
  },
  radiusBadge: {
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  radiusText: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '700',
  },
  metaBox: {
    backgroundColor: '#F8FAFC',
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    marginBottom: 14,
    gap: 4,
  },
  scheduleText: {
    fontSize: 11,
    color: '#334155',
    fontWeight: '600',
  },
  alertsText: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '500',
  },
  actionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  focusBtn: {
    flex: 1,
    backgroundColor: '#2563EB',
    paddingVertical: 10,
    borderRadius: 999,
    alignItems: 'center',
  },
  focusBtnText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  editBtn: {
    backgroundColor: '#F1F5F9',
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  editBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
  deleteBtn: {
    backgroundColor: '#FEE2E2',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  deleteBtnText: {
    fontSize: 12,
  },
});
