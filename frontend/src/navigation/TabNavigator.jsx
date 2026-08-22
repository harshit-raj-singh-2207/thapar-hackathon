import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import HomeScreen from '../screens/home/HomeScreen';
import SafetyNavigator from './SafetyNavigator';
import CommunityNavigator from './CommunityNavigator';
import ROUTES from './routes';

const Stack = createNativeStackNavigator();

export default function TabNavigator() {
  return (
    <Stack.Navigator
      initialRouteName={ROUTES.HOME}
      screenOptions={{
        headerShown: false,
        animation: 'fade',
      }}
    >
      <Stack.Screen name={ROUTES.HOME} component={HomeScreen} />
      <Stack.Screen name={ROUTES.COMMUNITY} component={CommunityNavigator} />
      <Stack.Screen name={ROUTES.SAFETY} component={SafetyNavigator} />
    </Stack.Navigator>
  );
}
