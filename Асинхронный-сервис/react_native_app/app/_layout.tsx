import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { createStackNavigator } from '@react-navigation/stack';

import HomeScreen from "@/screens/HomeScreen";
import FullPostScreen from "@/screens/FullPostScreen";

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {

  const [loaded] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
  });

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  const Stack = createStackNavigator();

  return (
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} options={{title: "Вещества"}} />
        <Stack.Screen name="FullPost" component={FullPostScreen} options={{title: "Вещество"}}/>
      </Stack.Navigator>
  );
}
