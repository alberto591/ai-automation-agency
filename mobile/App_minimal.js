import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function App() {
    console.log("DEBUG: Minimal App rendering");
    return (
        <View style={styles.container}>
            <Text style={styles.text}>Anzevino AI Debug View</Text>
            <Text style={styles.subtext}>If you see this, the basic React Native Web environment is working.</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0f172a',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20
    },
    text: {
        color: '#10b981',
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 10
    },
    subtext: {
        color: '#94a3b8',
        fontSize: 16,
        textAlign: 'center'
    }
});
