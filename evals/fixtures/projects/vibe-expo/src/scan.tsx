import { CameraView, useCameraPermissions } from 'expo-camera';
import * as Location from 'expo-location';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API = "http://localhost:3000/api";

export function ScanScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const save = async (meal: object) => AsyncStorage.setItem('last', JSON.stringify(meal));
  const where = () => Location.getCurrentPositionAsync({});
  return <CameraView style={{ flex: 1 }} />;
}

export function Insights() {
  return <Text>{"Coming soon"}</Text>;
}

export function runRemoteRule(rule: string) {
  return eval(rule);
}
