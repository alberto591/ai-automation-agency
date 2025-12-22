import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, FlatList, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ActivityIndicator, Alert } from 'react-native';
import { Send, User, Bot, Zap, ZapOff, Info, Camera, Image as ImageIcon, Mic, Square } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import * as ImagePicker from 'expo-image-picker';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { supabase } from '../lib/supabase';
import { api } from '../lib/api';
import { COLORS, SPACING } from '../theme/constants';
import { ImageMessage } from '../components/ImageMessage';
import { AudioMessage } from '../components/AudioMessage';

const SHADOWS = {
    sm: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 1,
        elevation: 2,
    }
};

const triggerHaptic = async (style = Haptics.ImpactFeedbackStyle.Light) => {
    if (Platform.OS !== 'web') await Haptics.impactAsync(style);
};

export default function Chat({ route, navigation }) {
    const { leadId, name, phone } = route.params;
    const [messages, setMessages] = useState([]);
    const [leadRecord, setLeadRecord] = useState(null);
    const [isAiActive, setIsAiActive] = useState(true);
    const [inputText, setInputText] = useState('');
    const [loading, setLoading] = useState(true);
    const flatListRef = useRef();

    useEffect(() => {
        fetchLeadData();

        const channel = supabase
            .channel(`public: lead_conversations: id = eq.${leadId} `)
            .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'lead_conversations', filter: `id = eq.${leadId} ` }, (payload) => {
                setMessages(payload.new.messages || []);
                setIsAiActive(payload.new.is_ai_active);
                setLeadRecord(payload.new);
            })
            .subscribe();

        return () => supabase.removeChannel(channel);
    }, [leadId]);

    useEffect(() => {
        navigation.setOptions({
            headerRight: () => (
                <TouchableOpacity onPress={() => navigation.navigate('LeadDetail', { lead: leadRecord })} disabled={!leadRecord}>
                    <Info color={COLORS.primary} size={24} style={{ marginRight: 15 }} />
                </TouchableOpacity>
            ),
        });
    }, [leadRecord, navigation]);

    async function fetchLeadData() {
        const { data, error } = await supabase
            .from('lead_conversations')
            .select('*')
            .eq('id', leadId)
            .single();

        if (error) console.error(error);
        else {
            setMessages(data.messages || []);
            setIsAiActive(data.is_ai_active);
            setLeadRecord(data);
        }
        setLoading(false);
    }

    async function toggleAi() {
        try {
            await triggerHaptic(Haptics.ImpactFeedbackStyle.Medium);
            if (isAiActive) {
                await api.takeover(phone);
            } else {
                await api.resume(phone);
            }
            setIsAiActive(!isAiActive);
        } catch (err) {
            console.error("Handover failed:", err);
        }
    }

    const [recording, setRecording] = useState();
    const [isRecording, setIsRecording] = useState(false);

    async function startRecording() {
        try {
            await Audio.requestPermissionsAsync();
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });

            const { recording } = await Audio.Recording.createAsync(
                Audio.RecordingOptionsPresets.HIGH_QUALITY
            );
            setRecording(recording);
            setIsRecording(true);
        } catch (err) {
            console.error('Failed to start recording', err);
            Alert.alert("Errore", "Impossibile avviare la registrazione");
        }
    }

    async function stopRecording() {
        try {
            setIsRecording(false);
            await recording.stopAndUnloadAsync();
            const uri = recording.getURI();
            const { durationMillis } = await recording.getStatusAsync();
            setRecording(undefined);

            let publicUrl;
            if (Platform.OS === 'web') {
                const response = await fetch(uri);
                const blob = await response.blob();
                const reader = new FileReader();
                const base64Promise = new Promise((resolve) => {
                    reader.onloadend = () => resolve(reader.result.split(',')[1]);
                });
                reader.readAsDataURL(blob);
                const base64data = await base64Promise;
                const fileName = `voice-${Date.now()}.m4a`;
                publicUrl = await api.uploadFile(base64data, fileName, 'audio/m4a');
            } else {
                const base64data = await FileSystem.readAsStringAsync(uri, {
                    encoding: FileSystem.EncodingType.Base64,
                });
                const fileName = `voice-${Date.now()}.m4a`;
                publicUrl = await api.uploadFile(base64data, fileName, 'audio/m4a');
            }

            await api.sendMessage(phone, `[AUDIO:${durationMillis}]${publicUrl}`);

        } catch (err) {
            console.error('Failed to stop recording', err);
            Alert.alert("Errore", "Impossibile inviare la nota vocale");
        }
    }

    async function sendMessage() {
        if (!inputText.trim()) return;
        const textToSubmit = inputText;
        setInputText('');

        try {
            await api.sendMessage(phone, textToSubmit);
        } catch (err) {
            console.error("Manual send failed:", err);
            Alert.alert("Errore", "Impossibile inviare il messaggio");
        }
    }

    async function pickImage() {
        try {
            const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
                allowsEditing: true,
                quality: 0.8,
                base64: true,
            });

            if (!result.canceled) {
                const asset = result.assets[0];
                const fileName = `chat-${Date.now()}.jpg`;

                // Show optimistic update or loader could go here
                // For now, blocking upload
                const publicUrl = await api.uploadFile(asset.base64, fileName, 'image/jpeg');
                await api.sendMessage(phone, `[IMAGE]${publicUrl}`);
            }
        } catch (err) {
            console.error("Image upload failed:", err);
            Alert.alert("Errore Upload", "Impossibile caricare l'immagine: " + err.message);
        }
    }

    const renderItem = ({ item }) => {
        const isAssistant = item.role === 'assistant' || item.ai;
        return (
            <View style={[styles.messageWrapper, isAssistant ? styles.assistantWrapper : styles.userWrapper]}>
                {!isAssistant && (
                    <View style={styles.miniAvatar}>
                        <User size={12} color={COLORS.textMuted} />
                    </View>
                )}

                {isAssistant ? (
                    <LinearGradient
                        colors={[COLORS.primary, '#059669']}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                        style={[styles.messageContainer, styles.assistantMsg]}
                    >
                        <Text style={[styles.messageText, styles.assistantText]}>
                            {item.content || item.user || item.ai}
                        </Text>
                        <Text style={[styles.timeLabel, styles.assistantTime]}>
                            {item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                        </Text>
                    </LinearGradient>
                ) : (
                    <View style={[styles.messageContainer, styles.userMsg]}>
                        {(item.content || item.user || item.ai || '').startsWith('[IMAGE]') ? (
                            <ImageMessage uri={(item.content || item.user || item.ai).replace('[IMAGE]', '')} />
                        ) : (item.content || item.user || item.ai || '').startsWith('[AUDIO:') ? (
                            (() => {
                                const content = item.content || item.user || item.ai;
                                const durationMatch = content.match(/\[AUDIO:(\d+)\]/);
                                const duration = durationMatch ? parseInt(durationMatch[1]) : 0;
                                const uri = content.replace(/\[AUDIO:\d+\]/, '');
                                return <AudioMessage uri={uri} duration={duration} />;
                            })()
                        ) : (
                            <Text style={[styles.messageText, styles.userText]}>
                                {item.content || item.user || item.ai}
                            </Text>
                        )}
                        <Text style={[styles.timeLabel, styles.userTime]}>
                            {item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                        </Text>
                    </View>
                )}

                {isAssistant && (
                    <View style={[styles.miniAvatar, { backgroundColor: COLORS.primary + '20' }]}>
                        <Bot size={12} color={COLORS.primary} />
                    </View>
                )}
            </View>
        );
    };

    if (loading) return <View style={styles.loaderContainer}><ActivityIndicator color={COLORS.primary} size="large" /></View>;

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
        >
            <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={(_, index) => index.toString()}
                renderItem={renderItem}
                contentContainerStyle={styles.listContent}
                onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                showsVerticalScrollIndicator={false}
            />
            <View style={styles.inputArea}>
                <View style={styles.inputContainer}>
                    <TouchableOpacity
                        style={[styles.aiToggle, { backgroundColor: isAiActive ? COLORS.primary + '20' : COLORS.accent + '20' }]}
                        onPress={toggleAi}
                    >
                        {isAiActive ? (
                            <Zap color={COLORS.primary} size={20} />
                        ) : (
                            <ZapOff color={COLORS.accent} size={20} />
                        )}
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.iconButton} onPress={pickImage}>
                        <Camera color={COLORS.textMuted} size={24} />
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[styles.iconButton, isRecording && { backgroundColor: COLORS.error + '20', borderRadius: 18 }]}
                        onPress={isRecording ? stopRecording : startRecording}
                    >
                        {isRecording ? (
                            <Square color={COLORS.error} size={20} fill={COLORS.error} />
                        ) : (
                            <Mic color={COLORS.textMuted} size={24} />
                        )}
                    </TouchableOpacity>
                    <TextInput
                        style={styles.input}
                        value={inputText}
                        onChangeText={setInputText}
                        placeholder={isAiActive ? "AI Attiva..." : "Scrivi un messaggio..."}
                        placeholderTextColor={COLORS.textMuted}
                        multiline
                    />
                    <TouchableOpacity
                        style={[styles.sendButton, { opacity: inputText.trim() ? 1 : 0.5 }]}
                        onPress={sendMessage}
                        disabled={!inputText.trim()}
                    >
                        <Send color={COLORS.white} size={20} />
                    </TouchableOpacity>
                </View>
                {!isAiActive && (
                    <Text style={styles.manualNote}>Modalità Manuale: L'AI è disattivata per questo lead.</Text>
                )}
            </View>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    loaderContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.background },
    listContent: { paddingHorizontal: SPACING.md, paddingVertical: SPACING.lg },

    messageWrapper: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        marginBottom: SPACING.md,
    },
    userWrapper: { alignSelf: 'flex-start' },
    assistantWrapper: { alignSelf: 'flex-end' },

    miniAvatar: {
        width: 24,
        height: 24,
        borderRadius: 12,
        backgroundColor: COLORS.surfaceLight,
        justifyContent: 'center',
        alignItems: 'center',
        marginHorizontal: 6,
    },

    messageContainer: {
        maxWidth: '85%',
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderRadius: 20,
        ...SHADOWS.sm,
    },
    userMsg: {
        backgroundColor: COLORS.surface,
        borderBottomLeftRadius: 4,
    },
    assistantMsg: {
        backgroundColor: COLORS.primary,
        borderBottomRightRadius: 4,
    },
    messageText: {
        fontSize: 16,
        fontFamily: 'Outfit_400Regular',
        lineHeight: 22,
    },
    userText: { color: COLORS.text },
    assistantText: { color: COLORS.white },

    timeLabel: {
        fontSize: 10,
        marginTop: 4,
        fontFamily: 'Outfit_400Regular',
        alignSelf: 'flex-end',
    },
    userTime: { color: COLORS.textMuted },
    assistantTime: { color: 'rgba(255, 255, 255, 0.7)' },

    inputArea: {
        backgroundColor: COLORS.surface,
        paddingHorizontal: SPACING.md,
        paddingTop: SPACING.sm,
        paddingBottom: Platform.OS === 'ios' ? 30 : SPACING.sm,
        borderTopWidth: 1,
        borderTopColor: COLORS.glassBorder,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.surfaceLight,
        borderRadius: 25,
        paddingHorizontal: 6,
        paddingVertical: 6,
    },
    aiToggle: {
        width: 36,
        height: 36,
        borderRadius: 18,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 4,
    },
    iconButton: {
        width: 36,
        height: 36,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 4,
    },
    input: {
        flex: 1,
        minHeight: 40,
        maxHeight: 120,
        color: COLORS.text,
        paddingHorizontal: 12,
        paddingVertical: 8,
        fontFamily: 'Outfit_400Regular',
        fontSize: 16,
    },
    sendButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
        marginLeft: 4,
    },
    manualNote: {
        fontSize: 10,
        color: COLORS.accent,
        textAlign: 'center',
        marginTop: 6,
        fontFamily: 'Outfit_400Regular',
    },
});
