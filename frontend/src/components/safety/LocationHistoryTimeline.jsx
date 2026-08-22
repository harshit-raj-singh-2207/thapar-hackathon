import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Platform,
} from 'react-native';

export default function LocationHistoryTimeline({
  locationHistory = [],
  onClearHistory,
  onSelectPoint,
}) {
  const [selectedFilter, setSelectedFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filterOptions = [
    { id: 'ALL', label: 'All Events', icon: '📋' },
    { id: 'ZONE_ENTRY', label: 'Zone Entries', icon: '🚪' },
    { id: 'ZONE_EXIT', label: 'Zone Exits', icon: '⚠️' },
    { id: 'LOCATE_NOW', label: 'Locate Pings', icon: '📍' },
    { id: 'BREADCRUMB', label: 'Path Steps', icon: '🐾' },
  ];

  const getEventBadge = (eventType) => {
    switch (eventType) {
      case 'ZONE_ENTRY':
        return {
          label: 'Safe-Zone Entry',
          icon: '🛡️',
          color: '#059669',
          bg: '#ECFDF5',
          borderColor: '#A7F3D0',
        };
      case 'ZONE_EXIT':
        return {
          label: 'Safe-Zone Exit',
          icon: '⚠️',
          color: '#D97706',
          bg: '#FEF3C7',
          borderColor: '#FDE68A',
        };
      case 'LOCATE_NOW':
        return {
          label: 'Locate Ping',
          icon: '📍',
          color: '#2563EB',
          bg: '#EFF6FF',
          borderColor: '#BFDBFE',
        };
      case 'SOS_ALERT':
        return {
          label: '🚨 Emergency SOS',
          icon: '🚨',
          color: '#DC2626',
          bg: '#FEE2E2',
          borderColor: '#FECACA',
        };
      case 'BREADCRUMB':
      default:
        return {
          label: 'Route Step',
          icon: '🐾',
          color: '#64748B',
          bg: '#F1F5F9',
          borderColor: '#E2E8F0',
        };
    }
  };

  const filteredHistory = useMemo(() => {
    return locationHistory.filter((item) => {
      if (selectedFilter !== 'ALL' && item.eventType !== selectedFilter) {
        return false;
      }
      if (searchQuery.trim().length > 0) {
        const query = searchQuery.toLowerCase();
        const addressMatch = item.address?.toLowerCase().includes(query);
        const zoneMatch = item.zoneName?.toLowerCase().includes(query);
        if (!addressMatch && !zoneMatch) return false;
      }
      return true;
    });
  }, [locationHistory, selectedFilter, searchQuery]);

  return (
    <View style={styles.card}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <View style={styles.iconCircle}>
            <Text style={styles.icon}>📜</Text>
          </View>
          <View>
            <Text style={styles.title}>Location History & Timeline</Text>
            <Text style={styles.subtitle}>
              {filteredHistory.length} recorded position waypoints
            </Text>
          </View>
        </View>

        {onClearHistory && (
          <TouchableOpacity
            style={styles.clearBtn}
            onPress={onClearHistory}
            activeOpacity={0.8}
          >
            <Text style={styles.clearBtnText}>Clear Log</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Search and Filters */}
      <View style={styles.filterSection}>
        <View style={styles.searchBox}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.searchInput}
            placeholder="Search address, zone or time..."
            placeholderTextColor="#94A3B8"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Text style={styles.clearSearchIcon}>✕</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Filter Pills */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.filterScroll}
          contentContainerStyle={styles.filterScrollContent}
        >
          {filterOptions.map((f) => {
            const isSelected = selectedFilter === f.id;
            return (
              <TouchableOpacity
                key={f.id}
                style={[styles.filterPill, isSelected && styles.filterPillActive]}
                onPress={() => setSelectedFilter(f.id)}
                activeOpacity={0.8}
              >
                <Text style={styles.filterPillIcon}>{f.icon}</Text>
                <Text
                  style={[
                    styles.filterPillText,
                    isSelected && styles.filterPillTextActive,
                  ]}
                >
                  {f.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Timeline List */}
      {filteredHistory.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>🧭</Text>
          <Text style={styles.emptyTitle}>No Waypoints Found</Text>
          <Text style={styles.emptyText}>
            No location events match the current filter or search criteria.
          </Text>
        </View>
      ) : (
        <View style={styles.timelineList}>
          {filteredHistory.map((item, index) => {
            const badge = getEventBadge(item.eventType);
            const isFirst = index === 0;
            const isLast = index === filteredHistory.length - 1;

            return (
              <TouchableOpacity
                key={item.id || index}
                style={styles.timelineItem}
                onPress={() => onSelectPoint && onSelectPoint(item)}
                activeOpacity={0.85}
              >
                {/* Left Connector Line & Dot */}
                <View style={styles.connectorCol}>
                  <View
                    style={[
                      styles.timelineDot,
                      { backgroundColor: badge.bg, borderColor: badge.color },
                    ]}
                  >
                    <Text style={styles.dotIconText}>{badge.icon}</Text>
                  </View>
                  {!isLast && <View style={styles.connectorLine} />}
                </View>

                {/* Main Content Card */}
                <View style={styles.timelineCard}>
                  {/* Top Line: Time + Event Type Badge */}
                  <View style={styles.cardHeaderRow}>
                    <View style={styles.timeRow}>
                      <Text style={styles.timeText}>{item.time || '4:15 PM'}</Text>
                      <Text style={styles.dateText}>({item.date || 'Today'})</Text>
                    </View>

                    <View
                      style={[
                        styles.eventBadge,
                        { backgroundColor: badge.bg, borderColor: badge.borderColor },
                      ]}
                    >
                      <Text style={[styles.eventBadgeText, { color: badge.color }]}>
                        {badge.label}
                      </Text>
                    </View>
                  </View>

                  {/* Location Address */}
                  <Text style={styles.itemAddress}>{item.address}</Text>

                  {/* Zone Tag */}
                  {item.zoneName && (
                    <View style={styles.zoneTagRow}>
                      <Text style={styles.zoneTagText}>
                        🛡️ {item.zoneName}
                      </Text>
                    </View>
                  )}

                  {/* Telemetry Metrics Row */}
                  <View style={styles.itemFooterRow}>
                    <Text style={styles.itemFooterMetric}>
                      🎯 Accuracy: ±{item.accuracy || 3.0}m
                    </Text>
                    {typeof item.speed === 'number' && (
                      <Text style={styles.itemFooterMetric}>
                        ⚡ Speed: {(item.speed * 3.6).toFixed(1)} km/h
                      </Text>
                    )}
                    {item.battery && (
                      <Text style={styles.itemFooterMetric}>
                        🔋 {item.battery}%
                      </Text>
                    )}
                  </View>
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 22,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 20,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.05,
    shadowRadius: 16,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    flexWrap: 'wrap',
    gap: 8,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  icon: {
    fontSize: 20,
  },
  title: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  clearBtn: {
    backgroundColor: '#FEE2E2',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  clearBtnText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#DC2626',
  },
  filterSection: {
    marginBottom: 16,
    gap: 10,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 999,
    paddingHorizontal: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    height: 44,
  },
  searchIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    color: '#0F172A',
    fontSize: 13,
    paddingVertical: 6,
  },
  clearSearchIcon: {
    color: '#94A3B8',
    fontSize: 12,
    paddingHorizontal: 6,
  },
  filterScroll: {
    flexGrow: 0,
  },
  filterScrollContent: {
    gap: 8,
  },
  filterPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  filterPillActive: {
    backgroundColor: '#2563EB',
    borderColor: '#1D4ED8',
  },
  filterPillIcon: {
    fontSize: 12,
    marginRight: 6,
  },
  filterPillText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748B',
  },
  filterPillTextActive: {
    color: '#FFFFFF',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyIcon: {
    fontSize: 36,
    marginBottom: 8,
  },
  emptyTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0F172A',
  },
  emptyText: {
    fontSize: 12,
    color: '#64748B',
    textAlign: 'center',
    marginTop: 4,
    maxWidth: 280,
  },
  timelineList: {
    marginTop: 4,
  },
  timelineItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  connectorCol: {
    alignItems: 'center',
    width: 32,
    marginRight: 10,
  },
  timelineDot: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 2,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 2,
  },
  dotIconText: {
    fontSize: 12,
  },
  connectorLine: {
    width: 2,
    flex: 1,
    backgroundColor: '#E2E8F0',
    marginVertical: 2,
  },
  timelineCard: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#EEF2F6',
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  timeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  timeText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  dateText: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
  },
  eventBadge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 999,
    borderWidth: 1,
  },
  eventBadgeText: {
    fontSize: 10,
    fontWeight: '800',
  },
  itemAddress: {
    fontSize: 13,
    color: '#334155',
    fontWeight: '600',
    marginBottom: 6,
  },
  zoneTagRow: {
    backgroundColor: '#EFF6FF',
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 999,
    marginBottom: 6,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  zoneTagText: {
    fontSize: 11,
    color: '#2563EB',
    fontWeight: '700',
  },
  itemFooterRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingTop: 6,
  },
  itemFooterMetric: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
  },
});
