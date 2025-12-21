import React from 'react';
import { StyleSheet, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS, SHADOWS } from '../theme/constants';

export const GlassCard = ({ children, style }) => {
    return (
        <LinearGradient
            colors={[COLORS.glass, 'rgba(255, 255, 255, 0.05)']}
            style={[styles.card, style]}
        >
            <View style={styles.content}>
                {children}
            </View>
        </LinearGradient>
    );
};

const styles = StyleSheet.create({
    card: {
        borderRadius: 16,
        borderWidth: 1,
        borderColor: COLORS.glassBorder,
        overflow: 'hidden',
        ...SHADOWS.md,
    },
    content: {
        padding: 16,
    },
});
