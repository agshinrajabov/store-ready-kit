import { createUserWithEmailAndPassword, getAuth } from 'firebase/auth';
import { GoogleSignin } from '@react-native-google-signin/google-signin';

export const signUpEmail = (email: string, password: string) =>
  createUserWithEmailAndPassword(getAuth(), email, password);

export const signInGoogle = () => GoogleSignin.signIn();
