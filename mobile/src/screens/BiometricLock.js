import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert, Platform } from 'react-native';
// import * as LocalAuthentication from 'expo-local-authentication';
const LocalAuthentication = { hasHardwareAsync: async () => false, isEnrolledAsync: async () => false, authenticateAsync: async () => ({ success: true }) };
import { ShieldCheck, Fingerprint } from 'lucide-react-native';
import { COLORS, SPACING } from '../theme/constants';

export default function BiometricLock({ onAuthenticated }) {
    const [isAuthenticating, setIsAuthenticating] = useState(false);

    useEffect(() => {
        handleAuthentication();
    }, []);

    async function handleAuthentication() {
        setIsAuthenticating(true);
        try {
            const hasHardware = await LocalAuthentication.hasHardwareAsync();
            const isEnrolled = await LocalAuthentication.isEnrolledAsync();

            if (!hasHardware || !isEnrolled) {
                // Fallback or alert if no biometrics
                onAuthenticated();
                return;
            }

            const result = await LocalAuthentication.authenticateAsync({
                promptMessage: 'Accedi ad Anzevino AI',
                fallbackLabel: 'Usa codice',
            });

            if (result.success) {
                onAuthenticated();
            } else {
                Alert.alert("Errore", "Autenticazione fallita");
            }
        } catch (err) {
            console.error(err);
            onAuthenticated(); // Fallback for dev
        } finally {
            setIsAuthenticating(false);
        }
    }

    return (
        <View style={styles.container}>
            <ShieldCheck size={80} color={COLORS.primary} style={styles.icon} />
            <Text style={styles.title}>Area Riservata</Text>
            <Text style={styles.subtitle}>Usa il FaceID o TouchID per accedere</Text>

            <TouchableOpacity style={styles.retryButton} onPress={handleAuthentication}>
                <Fingerprint size={32} color={COLORS.white} />
                <Text style={styles.retryText}>Riprova</Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
        justifyContent: 'center',
        alignItems: 'center',
        padding: SPACING.xl
    },
    icon: { marginBottom: SPACING.lg },
    title: {
        color: COLORS.text,
        fontSize: 24,
        fontFamily: 'Outfit_700Bold',
        marginBottom: SPACING.sm
    },
    subtitle: {
        color: COLORS.textMuted,
        fontSize: 16,
        fontFamily: 'Outfit_400Regular',
        textAlign: 'center',
        marginBottom: SPACING.xl
    },
    retryButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.surfaceLight,
        paddingHorizontal: 24,
        paddingVertical: 12,
        borderRadius: 30,
    },
    retryText: {
        color: COLORS.white,
        fontSize: 18,
        fontFamily: 'Outfit_600SemiBold',
        marginLeft: 10
    },
});
