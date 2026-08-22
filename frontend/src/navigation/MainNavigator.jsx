import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import HomeScreen from '../screens/home/HomeScreen';
import CommunityNavigator from './CommunityNavigator';
import SafetyNavigator from './SafetyNavigator';
import CommunicationNavigator from './CommunicationNavigator';
import LearningNavigator from './LearningNavigator';

// Direct Safety & GPS screens
import LiveLocationScreen from '../screens/safety/LiveLocationScreen';
import SafeZonesScreen from '../screens/safety/SafeZonesScreen';
import AddSafeZoneScreen from '../screens/safety/AddSafeZoneScreen';
import GPSBandScreen from '../screens/safety/GPSBandScreen';
import EmergencyScreen from '../screens/safety/EmergencyScreen';
import EmergencyContactsScreen from '../screens/safety/EmergencyContactsScreen';
import SafetyEventDetailsScreen from '../screens/safety/SafetyEventDetailsScreen';
import CaregiverDashboard from '../screens/caregiver/CaregiverDashboard';
import ChildProfileScreen from '../screens/caregiver/ChildProfileScreen';
import ChildStatusScreen from '../screens/caregiver/ChildStatusScreen';
import DeviceStatusScreen from '../screens/caregiver/DeviceStatusScreen';
import SafetyOverviewScreen from '../screens/caregiver/SafetyOverviewScreen';
import SupportCenterScreen from '../screens/caregiver/SupportCenterScreen';

// Direct Communication screens
import AACScreen from '../screens/communication/AACScreen';
import CommunicationScreen from '../screens/communication/CommunicationScreen';
import EmotionScreen from '../screens/communication/EmotionScreen';
import QuickCommunicationScreen from '../screens/communication/QuickCommunicationScreen';
import CommunicationHistoryScreen from '../screens/communication/CommunicationHistoryScreen';

// Direct Learning screens
import LearningHomeScreen from '../screens/learning/LearningHomeScreen';
import RoutineScreen from '../screens/learning/RoutineScreen';
import RoutineDetailsScreen from '../screens/learning/RoutineDetailsScreen';
import TaskDetailsScreen from '../screens/learning/TaskDetailsScreen';
import LearningTopicsScreen from '../screens/learning/LearningTopicsScreen';
import TutorScreen from '../screens/learning/TutorScreen';
import RemindersScreen from '../screens/learning/RemindersScreen';

// Direct Sensory & Support screens
import SensoryHomeScreen from '../screens/sensory/SensoryHomeScreen';

// Direct Games & Learning Progress screens
import GamesHomeScreen from '../screens/learning/GamesHomeScreen';

const Stack = createNativeStackNavigator();

export default function MainNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName="Home">
      {/* 1. Flagship Unified Home Dashboard */}
      <Stack.Screen name="Home" component={HomeScreen} />

      {/* 2. Main Hub Portals */}
      <Stack.Screen name="CommunicationTab" component={CommunicationNavigator} />
      <Stack.Screen name="LearningTab" component={LearningNavigator} />
      <Stack.Screen name="CommunityTab" component={CommunityNavigator} />
      <Stack.Screen name="SafetyTab" component={SafetyNavigator} />

      {/* 3. Communication Routes */}
      <Stack.Screen name="AAC" component={AACScreen} />
      <Stack.Screen name="CommunicationHome" component={CommunicationScreen} />
      <Stack.Screen name="Emotion" component={EmotionScreen} />
      <Stack.Screen name="QuickCommunication" component={QuickCommunicationScreen} />
      <Stack.Screen name="CommunicationHistory" component={CommunicationHistoryScreen} />

      {/* 4. Learning & Routine Routes */}
      <Stack.Screen name="LearningHome" component={LearningHomeScreen} />
      <Stack.Screen name="Routine" component={RoutineScreen} />
      <Stack.Screen name="RoutineDetails" component={RoutineDetailsScreen} />
      <Stack.Screen name="TaskDetails" component={TaskDetailsScreen} />
      <Stack.Screen name="LearningTopics" component={LearningTopicsScreen} />
      <Stack.Screen name="Tutor" component={TutorScreen} />
      <Stack.Screen name="Reminders" component={RemindersScreen} />

      {/* 5. Safety & GPS Routes */}
      <Stack.Screen name="CaregiverDashboard" component={CaregiverDashboard} />
      <Stack.Screen name="LiveLocation" component={LiveLocationScreen} />
      <Stack.Screen name="SafeZones" component={SafeZonesScreen} />
      <Stack.Screen name="AddSafeZone" component={AddSafeZoneScreen} />
      <Stack.Screen name="GPSBand" component={GPSBandScreen} />
      <Stack.Screen name="Emergency" component={EmergencyScreen} />
      <Stack.Screen name="EmergencyContacts" component={EmergencyContactsScreen} />
      <Stack.Screen name="SafetyEventDetails" component={SafetyEventDetailsScreen} />
      <Stack.Screen name="ChildProfile" component={ChildProfileScreen} />
      <Stack.Screen name="ChildStatus" component={ChildStatusScreen} />
      <Stack.Screen name="DeviceStatus" component={DeviceStatusScreen} />
      <Stack.Screen name="SafetyOverview" component={SafetyOverviewScreen} />
      <Stack.Screen name="SupportCenter" component={SupportCenterScreen} />

      {/* 6. Sensory Support Routes */}
      <Stack.Screen name="SensoryHome" component={SensoryHomeScreen} />
      <Stack.Screen name="SensoryTab" component={SensoryHomeScreen} />

      {/* 7. Educational Games & Progress Routes */}
      <Stack.Screen name="GamesHome" component={GamesHomeScreen} />
      <Stack.Screen name="Games" component={GamesHomeScreen} />
    </Stack.Navigator>
  );
}
