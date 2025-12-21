import { Platform } from 'react-native';
if (Platform.OS !== 'web') {
    require('react-native-url-polyfill/auto');
}
console.log("Supabase library loading...");
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://zozgvcdnkwtyioyazgmx.supabase.co';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpvemd2Y2Rua3d0eWlveWF6Z214Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzU1MjMsImV4cCI6MjA4MTY1MTUyM30.Z-IsY7vYkwIo6sB22ZpGIMTFD9kXSRdO6Ykv_bXwOvg';

console.log("Initializing Supabase client...");
let supabase;
try {
    supabase = createClient(supabaseUrl, supabaseAnonKey, {
        auth: {
            storage: Platform.OS === 'web' ? undefined : AsyncStorage,
            autoRefreshToken: true,
            persistSession: true,
            detectSessionInUrl: false,
        },
    });
    console.log("Supabase client initialized successfully");
} catch (e) {
    console.error("Supabase initialization failed:", e);
}

export { supabase };
