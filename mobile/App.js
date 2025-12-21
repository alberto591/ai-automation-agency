import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useFonts, Outfit_400Regular, Outfit_600SemiBold, Outfit_700Bold } from '@expo-google-fonts/outfit';
import { Platform, ActivityIndicator, View, Text, StyleSheet } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { COLORS } from './src/theme/constants';
import LeadList from './src/screens/LeadList';
import Chat from './src/screens/Chat';
import LeadDetail from './src/screens/LeadDetail';
import BiometricLock from './src/screens/BiometricLock';

const Stack = createNativeStackNavigator();

const AnzevinoTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: COLORS.background,
    card: COLORS.surface,
    text: COLORS.text,
    border: COLORS.glassBorder,
    primary: COLORS.primary,
  },
};

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(Platform.OS === 'web');
  let [fontsLoaded] = useFonts({
    Outfit_400Regular,
    Outfit_600SemiBold,
    Outfit_700Bold,
  });

  console.log("App state:", { isAuthenticated, fontsLoaded, OS: Platform.OS });

  if (!fontsLoaded && Platform.OS !== 'web') {
    return (
      <View style={{ flex: 1, backgroundColor: COLORS.background, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator color={COLORS.primary} size="large" />
      </View>
    );
  }

  if (!isAuthenticated) {
    console.log("Rendering BiometricLock");
    return <BiometricLock onAuthenticated={() => setIsAuthenticated(true)} />;
  }

  console.log("Rendering NavigationContainer");
  return (
    <SafeAreaProvider>
      <NavigationContainer theme={AnzevinoTheme}>
        <StatusBar style="light" />
        <Stack.Navigator
          initialRouteName="Leads"
          screenOptions={{
            headerStyle: { backgroundColor: COLORS.surface },
            headerTintColor: COLORS.text,
            headerTitleStyle: { fontWeight: 'bold' },
          }}
        >
          <Stack.Screen name="Leads" component={LeadList} options={{ title: 'Anzevino AI' }} />
          <Stack.Screen
            name="Chat"
            component={Chat}
            options={({ route }) => ({ title: route.params?.name || 'Chat' })}
          />
          <Stack.Screen name="LeadDetail" component={LeadDetail} options={{ title: 'Dettagli Lead' }} />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
