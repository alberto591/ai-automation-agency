import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { Play, Pause } from 'lucide-react-native';
import { Audio } from 'expo-av';
import { COLORS } from '../theme/constants';

export const AudioMessage = ({ uri, duration }) => {
    const [sound, setSound] = useState();
    const [isPlaying, setIsPlaying] = useState(false);
    const [position, setPosition] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        return () => {
            if (sound) {
                sound.unloadAsync();
            }
        };
    }, [sound]);

    async function playSound() {
        if (sound) {
            if (isPlaying) {
                await sound.pauseAsync();
                setIsPlaying(false);
            } else {
                await sound.playAsync();
                setIsPlaying(true);
            }
        } else {
            setIsLoading(true);
            try {
                const { sound: newSound } = await Audio.Sound.createAsync(
                    { uri },
                    { shouldPlay: true },
                    onPlaybackStatusUpdate
                );
                setSound(newSound);
                setIsPlaying(true);
            } catch (error) {
                console.error('Error loading sound', error);
            } finally {
                setIsLoading(false);
            }
        }
    }

    function onPlaybackStatusUpdate(status) {
        if (status.isLoaded) {
            setPosition(status.positionMillis);
            if (status.didJustFinish) {
                setIsPlaying(false);
                setPosition(0);
                sound.setPositionAsync(0);
            }
        }
    }

    const formatTime = (millis) => {
        const minutes = Math.floor(millis / 60000);
        const seconds = ((millis % 60000) / 1000).toFixed(0);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    };

    return (
        <View style={styles.container}>
            <TouchableOpacity onPress={playSound} disabled={isLoading}>
                <View style={styles.playButton}>
                    {isLoading ? (
                        <ActivityIndicator size="small" color={COLORS.primary} />
                    ) : isPlaying ? (
                        <Pause fill={COLORS.primary} color={COLORS.primary} size={20} />
                    ) : (
                        <Play fill={COLORS.primary} color={COLORS.primary} size={20} />
                    )}
                </View>
            </TouchableOpacity>
            <View style={styles.track}>
                <View style={[styles.progress, { width: `${(position / (duration || 10000)) * 100}%` }]} />
            </View>
            <Text style={styles.time}>{formatTime(position)}</Text>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.surfaceLight,
        borderRadius: 20,
        padding: 8,
        width: 200,
        marginBottom: 4
    },
    playButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: COLORS.white,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 8
    },
    track: {
        flex: 1,
        height: 4,
        backgroundColor: COLORS.glassBorder,
        borderRadius: 2,
        marginRight: 8,
        overflow: 'hidden'
    },
    progress: {
        height: '100%',
        backgroundColor: COLORS.primary
    },
    time: {
        fontSize: 10,
        color: COLORS.textMuted,
        fontFamily: 'Outfit_400Regular',
        width: 30
    }
});
