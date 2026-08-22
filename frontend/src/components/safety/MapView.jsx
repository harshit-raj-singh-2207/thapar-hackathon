import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
  Platform,
  Animated,
} from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function MapView({
  childLocation,
  caregiverLocation,
  safeZones = [],
  locationHistory = [],
  gpsStatus = 'ACTIVE',
  isLocationSharingOn = true,
  distanceToCaregiver = 0,
  bearingToChild = { degrees: 45, cardinal: 'NE' },
  onLocateNow,
  onRefresh,
  onSelectZone,
  selectedZoneId,
}) {
  const [viewMode, setViewMode] = useState('DUAL'); // 'DUAL', 'CHILD', 'CAREGIVER'
  const [mapLayer, setMapLayer] = useState('LIGHT'); // 'LIGHT', 'DARK', 'SATELLITE'
  const [zoom, setZoom] = useState(1.0);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [showBreadcrumbs, setShowBreadcrumbs] = useState(true);
  const [showSafeZones, setShowSafeZones] = useState(true);
  const [showTelemetryHUD, setShowTelemetryHUD] = useState(true);
  const [isLocatingAnimation, setIsLocatingAnimation] = useState(false);

  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.4,
          duration: 1200,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1200,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const mapCenter = useMemo(() => {
    if (viewMode === 'CHILD' && childLocation) {
      return { lat: childLocation.latitude, lon: childLocation.longitude };
    }
    if (viewMode === 'CAREGIVER' && caregiverLocation) {
      return { lat: caregiverLocation.latitude, lon: caregiverLocation.longitude };
    }
    const baseLat = childLocation ? childLocation.latitude : 37.775;
    const baseLon = childLocation ? childLocation.longitude : -122.419;
    const cgLat = caregiverLocation ? caregiverLocation.latitude : baseLat;
    const cgLon = caregiverLocation ? caregiverLocation.longitude : baseLon;
    return {
      lat: (baseLat + cgLat) / 2,
      lon: (baseLon + cgLon) / 2,
    };
  }, [viewMode, childLocation, caregiverLocation]);

  const scale = 24000 * zoom;

  const projectToPixels = (lat, lon, containerWidth = 600, containerHeight = 440) => {
    const cx = containerWidth / 2 + pan.x;
    const cy = containerHeight / 2 + pan.y;
    const dx = (lon - mapCenter.lon) * scale;
    const dy = (mapCenter.lat - lat) * scale;
    return { x: cx + dx, y: cy + dy };
  };

  const handleZoomIn = () => setZoom((z) => Math.min(2.5, z + 0.25));
  const handleZoomOut = () => setZoom((z) => Math.max(0.5, z - 0.25));
  const handleResetCenter = () => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
  };

  const triggerLocate = async () => {
    setIsLocatingAnimation(true);
    if (onLocateNow) await onLocateNow();
    handleResetCenter();
    setTimeout(() => setIsLocatingAnimation(false), 1200);
  };

  const isLight = mapLayer === 'LIGHT';
  const layerTheme = {
    bg: isLight ? '#F8FAFC' : mapLayer === 'DARK' ? '#0B1329' : '#080E1E',
    grid: isLight ? 'rgba(203, 213, 225, 0.6)' : 'rgba(51, 65, 85, 0.4)',
    road: isLight ? '#FFFFFF' : '#1E293B',
    roadBorder: isLight ? '#E2E8F0' : '#334155',
    text: isLight ? '#1E293B' : '#E2E8F0',
    textMuted: isLight ? '#94A3B8' : '#64748B',
  };

  const mockStreets = [
    { name: 'Pinecrest Blvd', y: 110, rotate: 0 },
    { name: 'Evergreen Terrace', y: 220, rotate: -4 },
    { name: 'Willow Creek Way', y: 330, rotate: 2 },
    { name: 'Meadow Lane', x: 140, isVertical: true },
    { name: 'School Corridor', x: 380, isVertical: true },
    { name: 'Healing Path Blvd', x: 520, isVertical: true },
  ];

  const childPos = childLocation
    ? projectToPixels(childLocation.latitude, childLocation.longitude)
    : { x: 300, y: 220 };

  const caregiverPos = caregiverLocation
    ? projectToPixels(caregiverLocation.latitude, caregiverLocation.longitude)
    : { x: 220, y: 310 };

  const getStatusColor = () => {
    if (gpsStatus === 'ACTIVE') return '#10B981';
    if (gpsStatus === 'WEAK') return '#F59E0B';
    if (gpsStatus === 'UNAVAILABLE') return '#F97316';
    return '#EF4444';
  };

  return (
    <View style={styles.mapContainer}>
      {/* Top Map Toolbar */}
      <View style={styles.topToolbar}>
        {/* View Mode Switcher */}
        <View style={styles.segmentedControl}>
          <TouchableOpacity
            style={[styles.segBtn, viewMode === 'DUAL' && styles.segBtnActive]}
            onPress={() => setViewMode('DUAL')}
            activeOpacity={0.8}
          >
            <Text style={[styles.segText, viewMode === 'DUAL' && styles.segTextActive]}>
              🧭 Dual View
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.segBtn, viewMode === 'CHILD' && styles.segBtnActive]}
            onPress={() => setViewMode('CHILD')}
            activeOpacity={0.8}
          >
            <Text style={[styles.segText, viewMode === 'CHILD' && styles.segTextActive]}>
              🧒 Child Focus
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.segBtn, viewMode === 'CAREGIVER' && styles.segBtnActive]}
            onPress={() => setViewMode('CAREGIVER')}
            activeOpacity={0.8}
          >
            <Text style={[styles.segText, viewMode === 'CAREGIVER' && styles.segTextActive]}>
              🧑‍⚕️ Caregiver
            </Text>
          </TouchableOpacity>
        </View>

        {/* Map Layer Pill */}
        <View style={styles.layerRow}>
          <TouchableOpacity
            style={[styles.layerChip, mapLayer === 'LIGHT' && styles.layerChipActive]}
            onPress={() => setMapLayer('LIGHT')}
          >
            <Text style={[styles.layerChipText, mapLayer === 'LIGHT' && styles.layerChipTextActive]}>
              ☀️ Clean Light
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.layerChip, mapLayer === 'DARK' && styles.layerChipActive]}
            onPress={() => setMapLayer('DARK')}
          >
            <Text style={[styles.layerChipText, mapLayer === 'DARK' && styles.layerChipTextActive]}>
              🌌 Dark
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.layerChip, mapLayer === 'SATELLITE' && styles.layerChipActive]}
            onPress={() => setMapLayer('SATELLITE')}
          >
            <Text style={[styles.layerChipText, mapLayer === 'SATELLITE' && styles.layerChipTextActive]}>
              🛰️ Satellite
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Interactive Map Canvas Container */}
      <View style={[styles.canvasFrame, { backgroundColor: layerTheme.bg }]}>
        {/* Background Grid Lines */}
        <View style={StyleSheet.absoluteFillObject} pointerEvents="none">
          <View style={[styles.gridLineH, { top: '25%', borderColor: layerTheme.grid }]} />
          <View style={[styles.gridLineH, { top: '50%', borderColor: layerTheme.grid }]} />
          <View style={[styles.gridLineH, { top: '75%', borderColor: layerTheme.grid }]} />
          <View style={[styles.gridLineV, { left: '25%', borderColor: layerTheme.grid }]} />
          <View style={[styles.gridLineV, { left: '50%', borderColor: layerTheme.grid }]} />
          <View style={[styles.gridLineV, { left: '75%', borderColor: layerTheme.grid }]} />
        </View>

        {/* Vector Street Visuals */}
        <View style={StyleSheet.absoluteFillObject} pointerEvents="none">
          {mockStreets.map((st, i) =>
            st.isVertical ? (
              <View
                key={`st-v-${i}`}
                style={[
                  styles.streetV,
                  {
                    left: st.x + pan.x * 0.5,
                    backgroundColor: layerTheme.road,
                    borderColor: layerTheme.roadBorder,
                  },
                ]}
              >
                <Text style={[styles.streetLabelV, { color: layerTheme.textMuted }]}>
                  {st.name}
                </Text>
              </View>
            ) : (
              <View
                key={`st-h-${i}`}
                style={[
                  styles.streetH,
                  {
                    top: st.y + pan.y * 0.5,
                    transform: [{ rotate: `${st.rotate}deg` }],
                    backgroundColor: layerTheme.road,
                    borderColor: layerTheme.roadBorder,
                  },
                ]}
              >
                <Text style={[styles.streetLabelH, { color: layerTheme.textMuted }]}>
                  {st.name}
                </Text>
              </View>
            )
          )}
        </View>

        {/* 1. Safe Zones Boundaries */}
        {showSafeZones &&
          safeZones.map((zone) => {
            const pos = projectToPixels(zone.latitude, zone.longitude);
            const pixelRadius = Math.max(35, ((zone.radius || 150) / 100) * 45 * zoom);
            const isSelected = selectedZoneId === zone.id;

            return (
              <TouchableOpacity
                key={zone.id}
                activeOpacity={0.8}
                onPress={() => onSelectZone && onSelectZone(zone)}
                style={[
                  styles.zoneCircle,
                  {
                    left: pos.x - pixelRadius,
                    top: pos.y - pixelRadius,
                    width: pixelRadius * 2,
                    height: pixelRadius * 2,
                    borderRadius: pixelRadius,
                    borderColor: zone.color || '#3B82F6',
                    backgroundColor: `${zone.color || '#3B82F6'}18`,
                    borderWidth: isSelected ? 3 : 1.5,
                    opacity: zone.active ? 1 : 0.45,
                  },
                ]}
              >
                <View style={[styles.zoneBadgeLabel, { backgroundColor: zone.color || '#3B82F6' }]}>
                  <Text style={styles.zoneBadgeIcon}>{zone.icon || '🛡️'}</Text>
                  <Text style={styles.zoneBadgeText} numberOfLines={1}>
                    {zone.name}
                  </Text>
                </View>
                <Text style={styles.zoneRadiusText}>{zone.radius}m</Text>
              </TouchableOpacity>
            );
          })}

        {/* 2. Breadcrumb Route / Path History Line */}
        {showBreadcrumbs && locationHistory.length > 1 && (
          <View style={StyleSheet.absoluteFillObject} pointerEvents="none">
            {locationHistory.slice(0, 8).map((pt, idx) => {
              const pos = projectToPixels(pt.latitude, pt.longitude);
              return (
                <View
                  key={pt.id || idx}
                  style={[
                    styles.breadcrumbPoint,
                    {
                      left: pos.x - 4,
                      top: pos.y - 4,
                      opacity: Math.max(0.25, 1 - idx * 0.12),
                    },
                  ]}
                >
                  <View style={styles.breadcrumbDot} />
                  {idx < 4 && (
                    <Text style={styles.breadcrumbTime}>
                      {pt.time}
                    </Text>
                  )}
                </View>
              );
            })}
          </View>
        )}

        {/* 3. Caregiver to Child Distance Line */}
        {viewMode === 'DUAL' && caregiverLocation && childLocation && (
          <View
            style={[
              styles.distanceConnector,
              {
                left: Math.min(childPos.x, caregiverPos.x),
                top: Math.min(childPos.y, caregiverPos.y),
                width: Math.abs(childPos.x - caregiverPos.x) || 2,
                height: Math.abs(childPos.y - caregiverPos.y) || 2,
              },
            ]}
            pointerEvents="none"
          >
            <View style={styles.distanceBadgePill}>
              <Text style={styles.distanceBadgeText}>
                📏 {distanceToCaregiver}m ({bearingToChild.cardinal})
              </Text>
            </View>
          </View>
        )}

        {/* 4. Caregiver Marker */}
        {(viewMode === 'DUAL' || viewMode === 'CAREGIVER') && caregiverLocation && (
          <View
            style={[
              styles.caregiverMarker,
              {
                left: caregiverPos.x - 22,
                top: caregiverPos.y - 42,
              },
            ]}
          >
            <View style={styles.caregiverBubble}>
              <Text style={styles.caregiverIcon}>🧑‍⚕️</Text>
              <Text style={styles.caregiverLabel}>Caregiver</Text>
            </View>
            <View style={styles.caregiverPinTail} />
          </View>
        )}

        {/* 5. Child / Current Target Marker */}
        {(viewMode === 'DUAL' || viewMode === 'CHILD') && childLocation && (
          <View
            style={[
              styles.childMarkerWrapper,
              {
                left: childPos.x - 28,
                top: childPos.y - 48,
              },
            ]}
          >
            {/* Accuracy Radius Disc */}
            <View
              style={[
                styles.accuracyDisc,
                {
                  width: Math.max(50, (childLocation.accuracy || 3) * 6 * zoom),
                  height: Math.max(50, (childLocation.accuracy || 3) * 6 * zoom),
                  borderRadius: 100,
                  left: 28 - Math.max(25, (childLocation.accuracy || 3) * 3 * zoom),
                  top: 48 - Math.max(25, (childLocation.accuracy || 3) * 3 * zoom),
                },
              ]}
            />

            {/* Glowing Pulse Ring */}
            <Animated.View
              style={[
                styles.pulseRing,
                {
                  transform: [{ scale: pulseAnim }],
                  borderColor: getStatusColor(),
                },
              ]}
            />

            {/* Child Pin Avatar */}
            <View style={[styles.childPinBody, { borderColor: getStatusColor() }]}>
              <Text style={styles.childAvatarIcon}>🧒</Text>
              <View style={[styles.statusDotSmall, { backgroundColor: getStatusColor() }]} />
            </View>

            {/* Child Floating Name Card */}
            <View style={styles.childNameCard}>
              <Text style={styles.childNameText}>{childLocation.name || 'Leo'}</Text>
              <View style={styles.childBadgeRow}>
                <Text style={styles.childBatteryText}>🔋 {childLocation.battery || 88}%</Text>
                <Text
                  style={[
                    styles.childZoneStatusText,
                    { color: childLocation.isInSafeZone ? '#059669' : '#D97706' },
                  ]}
                >
                  {childLocation.isInSafeZone ? '🛡️ In Zone' : '⚠️ Outside'}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* 6. Locating Scanner Radar Overlay */}
        {isLocatingAnimation && (
          <View style={styles.scannerOverlay} pointerEvents="none">
            <View style={styles.scannerRing} />
            <Text style={styles.scannerText}>🛰️ Locking High-Precision GPS Fix...</Text>
          </View>
        )}

        {/* 7. Floating Telemetry HUD */}
        {showTelemetryHUD && (
          <View style={styles.hudOverlay}>
            <View style={styles.hudRow}>
              <View style={styles.hudItem}>
                <Text style={styles.hudLabel}>GPS STATUS</Text>
                <View style={styles.hudValRow}>
                  <View
                    style={[
                      styles.hudStatusDot,
                      { backgroundColor: getStatusColor() },
                    ]}
                  />
                  <Text
                    style={[
                      styles.hudValue,
                      { color: getStatusColor(), fontWeight: '800' },
                    ]}
                  >
                    {gpsStatus}
                  </Text>
                </View>
              </View>

              <View style={styles.hudDivider} />

              <View style={styles.hudItem}>
                <Text style={styles.hudLabel}>ACCURACY</Text>
                <Text style={styles.hudValue}>±{childLocation?.accuracy || 3.2}m</Text>
              </View>

              <View style={styles.hudDivider} />

              <View style={styles.hudItem}>
                <Text style={styles.hudLabel}>SPEED</Text>
                <Text style={styles.hudValue}>
                  {childLocation?.speed ? `${(childLocation.speed * 3.6).toFixed(1)} km/h` : '0.0 km/h'}
                </Text>
              </View>

              <View style={styles.hudDivider} />

              <View style={styles.hudItem}>
                <Text style={styles.hudLabel}>SATELLITES</Text>
                <Text style={styles.hudValue}>{childLocation?.satellites || 14} locked</Text>
              </View>
            </View>
          </View>
        )}

        {/* 8. Map Action Controls (Zoom, Re-center, Locate Now) */}
        <View style={styles.controlsColumn}>
          <TouchableOpacity
            style={styles.controlBtn}
            onPress={handleZoomIn}
            activeOpacity={0.8}
            accessibilityLabel="Zoom In"
          >
            <Text style={styles.controlBtnText}>＋</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.controlBtn}
            onPress={handleZoomOut}
            activeOpacity={0.8}
            accessibilityLabel="Zoom Out"
          >
            <Text style={styles.controlBtnText}>－</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.controlBtn}
            onPress={handleResetCenter}
            activeOpacity={0.8}
            accessibilityLabel="Re-Center"
          >
            <Text style={styles.controlBtnIcon}>🎯</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlBtn, styles.locateBtn]}
            onPress={triggerLocate}
            activeOpacity={0.8}
            accessibilityLabel="Locate Now"
          >
            <Text style={styles.locateBtnIcon}>📍</Text>
          </TouchableOpacity>

          {onRefresh && (
            <TouchableOpacity
              style={styles.controlBtn}
              onPress={onRefresh}
              activeOpacity={0.8}
              accessibilityLabel="Refresh"
            >
              <Text style={styles.controlBtnIcon}>🔄</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* 9. Layer Toggles (Bottom Left) */}
        <View style={styles.layerTogglesRow}>
          <TouchableOpacity
            style={[styles.layerToggleBtn, showSafeZones && styles.layerToggleBtnActive]}
            onPress={() => setShowSafeZones(!showSafeZones)}
          >
            <Text style={[styles.layerToggleText, showSafeZones && styles.layerToggleTextActive]}>
              {showSafeZones ? '🛡️ Safe Zones: ON' : '🛡️ Safe Zones: OFF'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.layerToggleBtn, showBreadcrumbs && styles.layerToggleBtnActive]}
            onPress={() => setShowBreadcrumbs(!showBreadcrumbs)}
          >
            <Text style={[styles.layerToggleText, showBreadcrumbs && styles.layerToggleTextActive]}>
              {showBreadcrumbs ? '🐾 Trail: ON' : '🐾 Trail: OFF'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.layerToggleBtn, showTelemetryHUD && styles.layerToggleBtnActive]}
            onPress={() => setShowTelemetryHUD(!showTelemetryHUD)}
          >
            <Text style={[styles.layerToggleText, showTelemetryHUD && styles.layerToggleTextActive]}>
              📊 HUD
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  mapContainer: {
    borderRadius: 24,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    backgroundColor: '#FFFFFF',
    marginBottom: 20,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.05,
    shadowRadius: 16,
    elevation: 3,
  },
  topToolbar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 18,
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEF2F6',
    flexWrap: 'wrap',
    gap: 8,
  },
  segmentedControl: {
    flexDirection: 'row',
    backgroundColor: '#F1F5F9',
    borderRadius: 999,
    padding: 3,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  segBtn: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 999,
  },
  segBtnActive: {
    backgroundColor: '#2563EB',
    shadowColor: '#2563EB',
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  segText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748B',
  },
  segTextActive: {
    color: '#FFFFFF',
    fontWeight: '800',
  },
  layerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  layerChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  layerChipActive: {
    borderColor: '#3B82F6',
    backgroundColor: '#EFF6FF',
  },
  layerChipText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#64748B',
  },
  layerChipTextActive: {
    color: '#2563EB',
  },
  canvasFrame: {
    height: 440,
    width: '100%',
    position: 'relative',
    overflow: 'hidden',
  },
  gridLineH: {
    position: 'absolute',
    left: 0,
    right: 0,
    borderBottomWidth: 1,
    borderStyle: 'dashed',
  },
  gridLineV: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    borderRightWidth: 1,
    borderStyle: 'dashed',
  },
  streetH: {
    position: 'absolute',
    left: -40,
    right: -40,
    height: 30,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    justifyContent: 'center',
    paddingLeft: 40,
  },
  streetLabelH: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
  streetV: {
    position: 'absolute',
    top: -40,
    bottom: -40,
    width: 30,
    borderLeftWidth: 1,
    borderRightWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  streetLabelV: {
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 1,
    transform: [{ rotate: '-90deg' }],
  },
  zoneCircle: {
    position: 'absolute',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 5,
  },
  zoneBadgeLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  zoneBadgeIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  zoneBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#FFFFFF',
    maxWidth: 110,
  },
  zoneRadiusText: {
    fontSize: 9,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '700',
  },
  breadcrumbPoint: {
    position: 'absolute',
    alignItems: 'center',
    zIndex: 8,
  },
  breadcrumbDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3B82F6',
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
  },
  breadcrumbTime: {
    fontSize: 8,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '700',
  },
  distanceConnector: {
    position: 'absolute',
    borderWidth: 1,
    borderColor: '#3B82F6',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9,
  },
  distanceBadgePill: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#BFDBFE',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
  distanceBadgeText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#2563EB',
  },
  caregiverMarker: {
    position: 'absolute',
    alignItems: 'center',
    zIndex: 20,
  },
  caregiverBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#3B82F6',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 14,
    shadowColor: '#3B82F6',
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  caregiverIcon: {
    fontSize: 14,
    marginRight: 4,
  },
  caregiverLabel: {
    fontSize: 11,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  caregiverPinTail: {
    width: 0,
    height: 0,
    borderLeftWidth: 6,
    borderRightWidth: 6,
    borderTopWidth: 8,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderTopColor: '#3B82F6',
  },
  childMarkerWrapper: {
    position: 'absolute',
    alignItems: 'center',
    zIndex: 25,
  },
  accuracyDisc: {
    position: 'absolute',
    backgroundColor: 'rgba(59, 130, 246, 0.08)',
    borderWidth: 1,
    borderColor: 'rgba(59, 130, 246, 0.3)',
    borderStyle: 'dashed',
  },
  pulseRing: {
    position: 'absolute',
    width: 52,
    height: 52,
    borderRadius: 26,
    borderWidth: 2,
    top: -2,
    left: 2,
  },
  childPinBody: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    borderWidth: 3,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#0F172A',
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  childAvatarIcon: {
    fontSize: 22,
  },
  statusDotSmall: {
    position: 'absolute',
    top: 0,
    right: 0,
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  childNameCard: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginTop: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 4,
  },
  childNameText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#0F172A',
  },
  childBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 1,
  },
  childBatteryText: {
    fontSize: 9,
    color: '#64748B',
    fontWeight: '700',
  },
  childZoneStatusText: {
    fontSize: 9,
    fontWeight: '800',
  },
  scannerOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.75)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 40,
  },
  scannerRing: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 3,
    borderColor: '#2563EB',
    borderStyle: 'dashed',
    marginBottom: 12,
  },
  scannerText: {
    color: '#1E3A8A',
    fontSize: 13,
    fontWeight: '800',
  },
  hudOverlay: {
    position: 'absolute',
    top: 14,
    left: 14,
    backgroundColor: 'rgba(255, 255, 255, 0.92)',
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    zIndex: 30,
    shadowColor: '#0F172A',
    shadowOpacity: 0.06,
    shadowRadius: 8,
  },
  hudRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  hudItem: {
    paddingHorizontal: 8,
  },
  hudDivider: {
    width: 1,
    height: 24,
    backgroundColor: '#E2E8F0',
  },
  hudLabel: {
    fontSize: 8,
    fontWeight: '800',
    color: '#64748B',
    letterSpacing: 0.5,
  },
  hudValRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  hudStatusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 4,
  },
  hudValue: {
    fontSize: 11,
    fontWeight: '800',
    color: '#0F172A',
  },
  controlsColumn: {
    position: 'absolute',
    right: 14,
    top: 14,
    gap: 8,
    zIndex: 30,
  },
  controlBtn: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#0F172A',
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
  },
  controlBtnText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0F172A',
  },
  controlBtnIcon: {
    fontSize: 16,
  },
  locateBtn: {
    backgroundColor: '#2563EB',
    borderColor: '#1D4ED8',
  },
  locateBtnIcon: {
    fontSize: 18,
  },
  layerTogglesRow: {
    position: 'absolute',
    bottom: 12,
    left: 12,
    flexDirection: 'row',
    gap: 6,
    zIndex: 30,
    flexWrap: 'wrap',
  },
  layerToggleBtn: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowRadius: 4,
  },
  layerToggleBtnActive: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  layerToggleText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
  },
  layerToggleTextActive: {
    color: '#2563EB',
  },
});
