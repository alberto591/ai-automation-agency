import React, { useState } from 'react';
import { View, Image, Modal, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { X } from 'lucide-react-native';
import { COLORS } from '../theme/constants';

export const ImageMessage = ({ uri }) => {
    const [modalVisible, setModalVisible] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    return (
        <>
            <TouchableOpacity onPress={() => setModalVisible(true)} activeOpacity={0.9}>
                <View style={styles.imageContainer}>
                    {isLoading && (
                        <View style={styles.loader}>
                            <ActivityIndicator size="small" color={COLORS.primary} />
                        </View>
                    )}
                    <Image
                        source={{ uri }}
                        style={styles.thumbnail}
                        onLoadEnd={() => setIsLoading(false)}
                        resizeMode="cover"
                    />
                </View>
            </TouchableOpacity>

            <Modal visible={modalVisible} transparent={true} animationType="fade">
                <View style={styles.modalBackground}>
                    <TouchableOpacity
                        style={styles.closeButton}
                        onPress={() => setModalVisible(false)}
                    >
                        <X color={COLORS.white} size={30} />
                    </TouchableOpacity>
                    <Image
                        source={{ uri }}
                        style={styles.fullImage}
                        resizeMode="contain"
                    />
                </View>
            </Modal>
        </>
    );
};

const styles = StyleSheet.create({
    imageContainer: {
        width: 200,
        height: 150,
        borderRadius: 12,
        overflow: 'hidden',
        backgroundColor: COLORS.surfaceLight,
        marginBottom: 4
    },
    thumbnail: {
        width: '100%',
        height: '100%',
    },
    loader: {
        ...StyleSheet.absoluteFillObject,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: COLORS.surfaceLight
    },
    modalBackground: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.9)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    fullImage: {
        width: '100%',
        height: '80%',
    },
    closeButton: {
        position: 'absolute',
        top: 50,
        right: 20,
        zIndex: 1,
        padding: 10
    }
});
