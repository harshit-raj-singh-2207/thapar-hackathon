import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import LearningHomeScreen from '../screens/learning/LearningHomeScreen';
import RoutineScreen from '../screens/learning/RoutineScreen';
import RoutineDetailsScreen from '../screens/learning/RoutineDetailsScreen';
import TaskDetailsScreen from '../screens/learning/TaskDetailsScreen';
import LearningTopicsScreen from '../screens/learning/LearningTopicsScreen';
import TutorScreen from '../screens/learning/TutorScreen';
import RemindersScreen from '../screens/learning/RemindersScreen';

const Stack = createNativeStackNavigator();

export default function LearningNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName="LearningHome">
      <Stack.Screen name="LearningHome" component={LearningHomeScreen} />
      <Stack.Screen name="Routine" component={RoutineScreen} />
      <Stack.Screen name="RoutineDetails" component={RoutineDetailsScreen} />
      <Stack.Screen name="TaskDetails" component={TaskDetailsScreen} />
      <Stack.Screen name="LearningTopics" component={LearningTopicsScreen} />
      <Stack.Screen name="Tutor" component={TutorScreen} />
      <Stack.Screen name="Reminders" component={RemindersScreen} />
    </Stack.Navigator>
  );
}
