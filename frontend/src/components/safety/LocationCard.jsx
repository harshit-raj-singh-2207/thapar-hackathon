import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Platform } from 'react-native';

export default function LocationCard({
  childLocation,
  lastKnownLocation,
  gpsStatus = 'ACTIVE',
  isLocationSharingOn = true,
  distanceToCaregiver = 0,
  bearingToChild = { degrees: 45, cardinal: 'NE' },
  onLocateNow,
  onToggleSharing,
  onOpenSettings,
  onOpenHistory,
}) {
  const [locating, setLocating] = useState(false);
  const [secondsAgo, setSecondsAgo] = useState(0);

  useEffect(() => {
    setSecondsAgo(0);
    const interval = setInterval(() => {
      setSecondsAgo((s) => s + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [childLocation?.lastUpdated]);

  const handleLocateNow = async () => {
    setLocating(true);
    try {
      if (onLocateNow) await onLocateNow();
    } finally {
      setTimeout(() => setLocating(false), 800);
    }
  };

  const getStatusConfig = () => {
    switch (gpsStatus) {
      case 'ACTIVE':
        return {
          label: 'GPS Active',
          color: '#059669',
          bg: '#ECFDF5',
          borderColor: '#A7F3D0',
          dot: '#10B981',
        };
      case 'WEAK':
        return {
          label: 'GPS Weak',
          color: '#D97706',
          bg: '#FEF3C7',
          borderColor: '#FDE68A',
          dot: '#F59E0B',
        };
      case 'UNAVAILABLE':
        return {
          label: 'GPS Unavailable',
          color: '#EA580C',
          bg: '#FFEDD5',
          borderColor: '#FED7AA',
          dot: '#F97316',
        };
      case 'OFFLINE':
      default:
        return {
          label: 'Offline',
          color: '#DC2626',
          bg: '#FEE2E2',
          borderColor: '#FECACA',
          dot: '#EF4444',
        };
    }
  };

  const statusCfg = getStatusConfig();
  const loc = gpsStatus === 'OFFLINE' ? (lastKnownLocation || childLocation) : childLocation;

  return (
    <View style={styles.card}>
      {/* Header Row */}
      <View style={styles.headerRow}>
        <View style={styles.titleWithIcon}>
          <View style={styles.iconCircle}>
            <Text style={styles.headerIcon}>📍</Text>
          </View>
          <View>
            <Text style={styles.headerTitle}>Location Overview</Text>
            <Text style={styles.targetSubtitle}>
              Tracking: <Text style={styles.boldTarget}>{loc?.name || 'Child'}</Text> ({loc?.device || 'SmartBand'})
            </Text>
          </View>
        </View>

        <View style={styles.badgesCol}>
          <View
            style={[
              styles.statusBadge,
              { backgroundColor: statusCfg.bg, borderColor: statusCfg.borderColor },
            ]}
          >
            <View style={[styles.statusDot, { backgroundColor: statusCfg.dot }]} />
            <Text style={[styles.statusText, { color: statusCfg.color }]}>{statusCfg.label}</Text>
          </View>

          <TouchableOpacity
            style={[
              styles.sharingBadge,
              isLocationSharingOn ? styles.sharingOnBg : styles.sharingOffBg,
            ]}
            onPress={onToggleSharing}
            activeOpacity={0.8}
          >
            <Text
              style={[
                styles.sharingText,
                isLocationSharingOn ? styles.sharingOnText : styles.sharingOffText,
              ]}
            >
              {isLocationSharingOn ? '📡 Sharing ON' : '⏸️ Sharing Paused'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Main Location Box */}
      <View style={styles.locationBox}>
        {/* Geofence Status Banner */}
        <View
          style={[
            styles.geofenceBanner,
            loc?.isInSafeZone ? styles.safeGeofence : styles.warnGeofence,
          ]}
        >
          <Text style={styles.geofenceIcon}>{loc?.isInSafeZone ? '🛡️' : '⚠️'}</Text>
          <Text
            style={[
              styles.geofenceText,
              { color: loc?.isInSafeZone ? '#065F46' : '#92400E' },
            ]}
          >
            {loc?.isInSafeZone
              ? `Currently in ${loc?.zoneName || 'Safe Zone'}`
              : 'Outside registered safe zones'}
          </Text>
        </View>

        {/* Address and Coordinates */}
        <Text style={styles.addressText} numberOfLines={2}>
          {loc?.address || 'Locating target coordinates...'}
        </Text>

        <View style={styles.coordRow}>
          <Text style={styles.coordText}>
            Lat: {loc?.latitude?.toFixed(5) || '0.00000'}°, Lon: {loc?.longitude?.toFixed(5) || '0.00000'}°
          </Text>
          {gpsStatus === 'OFFLINE' && (
            <View style={styles.lastKnownTag}>
              <Text style={styles.lastKnownTagText}>Last Known Fix</Text>
            </View>
          )}
        </View>
      </View>

      {/* Telemetry Metrics Grid */}
      <View style={styles.metricsGrid}>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>ACCURACY</Text>
          <Text style={styles.metricValue}>±{loc?.accuracy || 3.2}m</Text>
          <Text style={styles.metricSub}>{loc?.accuracy < 5 ? 'High Precision' : 'Standard'}</Text>
        </View>

        <View style={styles.metricDivider} />

        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>LAST UPDATED</Text>
          <Text style={styles.metricValue}>
            {secondsAgo === 0 ? 'Just now' : `${secondsAgo}s ago`}
          </Text>
          <Text style={styles.metricSub}>
            {loc?.lastUpdated
              ? new Date(loc.lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : '--:--'}
          </Text>
        </View>

        <View style={styles.metricDivider} />

        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>DISTANCE</Text>
          <Text style={styles.metricValue}>
            {distanceToCaregiver > 1000
              ? `${(distanceToCaregiver / 1000).toFixed(2)} km`
              : `${distanceToCaregiver} m`}
          </Text>
          <Text style={styles.metricSub}>Bearing: {bearingToChild?.cardinal || 'NE'}</Text>
        </View>

        <View style={styles.metricDivider} />

        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>BAND BATTERY</Text>
          <Text style={styles.metricValue}>🔋 {loc?.battery || 88}%</Text>
          <Text style={styles.metricSub}>{loc?.satellites || 14} Sats</Text>
        </View>
      </View>

      {/* Actions Row */}
      <View style={styles.actionsRow}>
        <TouchableOpacity
          style={[styles.primaryActionBtn, locating && styles.btnDisabled]}
          onPress={handleLocateNow}
          disabled={locating}
          activeOpacity={0.85}
        >
          {locating ? (
            <ActivityIndicator size="small" color="#FFFFFF" />
          ) : (
            <>
              <Text style={styles.btnIcon}>📍</Text>
              <Text style={styles.primaryBtnText}>Locate Now</Text>
            </>
          )}
        </TouchableOpacity>

        {onOpenHistory && (
          <TouchableOpacity
            style={styles.secondaryActionBtn}
            onPress={onOpenHistory}
            activeOpacity={0.8}
          >
            <Text style={styles.secBtnIcon}>🕒</Text>
            <Text style={styles.secBtnText}>History</Text>
          </TouchableOpacity>
        )}

        {onOpenSettings && (
          <TouchableOpacity
            style={styles.iconActionBtn}
            onPress={onOpenSettings}
            activeOpacity={0.8}
            accessibilityLabel="Location Settings"
          >
            <Text style={styles.gearIcon}>⚙️</Text>
          </TouchableOpacity>
        )}
      </View>
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 18,
    flexWrap: 'wrap',
    gap: 8,
  },
  titleWithIcon: {
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
  headerIcon: {
    fontSize: 22,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
    letterSpacing: -0.2,
  },
  targetSubtitle: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  boldTarget: {
    color: '#2563EB',
    fontWeight: '700',
  },
  badgesCol: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flexWrap: 'wrap',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 999,
    borderWidth: 1,
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 3.5,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '700',
  },
  sharingBadge: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 999,
    borderWidth: 1,
  },
  sharingOnBg: {
    backgroundColor: '#EFF6FF',
    borderColor: '#BFDBFE',
  },
  sharingOffBg: {
    backgroundColor: '#F1F5F9',
    borderColor: '#CBD5E1',
  },
  sharingOnText: {
    color: '#2563EB',
    fontSize: 12,
    fontWeight: '700',
  },
  sharingOffText: {
    color: '#64748B',
    fontSize: 12,
    fontWeight: '700',
  },
  locationBox: {
    backgroundColor: '#F8FAFC',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    marginBottom: 16,
  },
  geofenceBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    marginBottom: 10,
    alignSelf: 'flex-start',
  },
  safeGeofence: {
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#A7F3D0',
  },
  warnGeofence: {
    backgroundColor: '#FEF3C7',
    borderWidth: 1,
    borderColor: '#FDE68A',
  },
  geofenceIcon: {
    fontSize: 12,
    marginRight: 6,
  },
  geofenceText: {
    fontSize: 12,
    fontWeight: '700',
  },
  addressText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0F172A',
    lineHeight: 22,
  },
  coordRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  coordText: {
    fontSize: 11,
    color: '#64748B',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontWeight: '500',
  },
  lastKnownTag: {
    backgroundColor: '#FEE2E2',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
  },
  lastKnownTagText: {
    fontSize: 10,
    color: '#DC2626',
    fontWeight: '700',
  },
  metricsGrid: {
    flexDirection: 'row',
    backgroundColor: '#F8FAFC',
    borderRadius: 18,
    paddingVertical: 14,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: '#EEF2F6',
    marginBottom: 18,
    alignItems: 'center',
  },
  metricItem: {
    flex: 1,
    alignItems: 'center',
  },
  metricDivider: {
    width: 1,
    height: 32,
    backgroundColor: '#E2E8F0',
  },
  metricLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0F172A',
  },
  metricSub: {
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 1,
    fontWeight: '500',
  },
  actionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  primaryActionBtn: {
    flex: 2,
    backgroundColor: '#2563EB',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 999,
    shadowColor: '#2563EB',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  btnDisabled: {
    opacity: 0.6,
  },
  btnIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  primaryBtnText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '800',
  },
  secondaryActionBtn: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  secBtnIcon: {
    fontSize: 14,
    marginRight: 4,
  },
  secBtnText: {
    color: '#1E293B',
    fontSize: 13,
    fontWeight: '700',
  },
  iconActionBtn: {
    width: 48,
    height: 48,
    backgroundColor: '#F1F5F9',
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  gearIcon: {
    fontSize: 18,
  },
});
