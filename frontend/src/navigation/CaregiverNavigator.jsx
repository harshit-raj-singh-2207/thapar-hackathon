import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import CaregiverDashboard from '../screens/caregiver/CaregiverDashboard';
import ChildProfileScreen from '../screens/caregiver/ChildProfileScreen';
import ChildStatusScreen from '../screens/caregiver/ChildStatusScreen';
import DeviceStatusScreen from '../screens/caregiver/DeviceStatusScreen';
import SafetyOverviewScreen from '../screens/caregiver/SafetyOverviewScreen';
import LiveLocationScreen from '../screens/safety/LiveLocationScreen';
import SafeZonesScreen from '../screens/safety/SafeZonesScreen';
import AddSafeZoneScreen from '../screens/safety/AddSafeZoneScreen';
import GPSBandScreen from '../screens/safety/GPSBandScreen';
import EmergencyScreen from '../screens/safety/EmergencyScreen';
import EmergencyContactsScreen from '../screens/safety/EmergencyContactsScreen';
import SafetyEventDetailsScreen from '../screens/safety/SafetyEventDetailsScreen';
import { ROUTES } from './routes';

const Stack = createNativeStackNavigator();

export default function CaregiverNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{ headerShown: false }}
      initialRouteName={ROUTES.CAREGIVER_DASHBOARD}
    >
      <Stack.Screen name={ROUTES.CAREGIVER_DASHBOARD} component={CaregiverDashboard} />
      <Stack.Screen name={ROUTES.CHILD_PROFILE} component={ChildProfileScreen} />
      <Stack.Screen name={ROUTES.CHILD_STATUS} component={ChildStatusScreen} />
      <Stack.Screen name={ROUTES.DEVICE_STATUS} component={DeviceStatusScreen} />
      <Stack.Screen name={ROUTES.SAFETY_OVERVIEW} component={SafetyOverviewScreen} />
      <Stack.Screen name={ROUTES.LIVE_LOCATION} component={LiveLocationScreen} />
      <Stack.Screen name={ROUTES.SAFE_ZONES} component={SafeZonesScreen} />
      <Stack.Screen name={ROUTES.ADD_SAFE_ZONE} component={AddSafeZoneScreen} />
      <Stack.Screen name={ROUTES.GPS_BAND} component={GPSBandScreen} />
      <Stack.Screen name={ROUTES.EMERGENCY} component={EmergencyScreen} />
      <Stack.Screen name={ROUTES.EMERGENCY_CONTACTS} component={EmergencyContactsScreen} />
      <Stack.Screen name={ROUTES.SAFETY_EVENT_DETAILS} component={SafetyEventDetailsScreen} />
    </Stack.Navigator>
  );
}
