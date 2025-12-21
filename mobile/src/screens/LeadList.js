import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, FlatList, TouchableOpacity, ActivityIndicator, SafeAreaView, TextInput, RefreshControl } from 'react-native';
import { MessageSquare, User, ChevronRight, Bell, Search } from 'lucide-react-native';
// import * as Notifications from 'expo-notifications';
const Notifications = { getPermissionsAsync: async () => ({ status: 'denied' }), requestPermissionsAsync: async () => ({ status: 'denied' }) };
import { supabase } from '../lib/supabase';
import { COLORS, SPACING } from '../theme/constants';
import { GlassCard } from '../components/GlassCard';

export default function LeadList({ navigation }) {
    const [leads, setLeads] = useState([]);
    const [filteredLeads, setFilteredLeads] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const onRefresh = () => { setRefreshing(true); fetchLeads().finally(() => setRefreshing(false)); };

    useEffect(() => {
        registerForPushNotifications();
        fetchLeads();
        const channel = supabase
            .channel('public:lead_conversations')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'lead_conversations' }, () => {
                fetchLeads();
            })
            .subscribe();

        return () => supabase.removeChannel(channel);
    }, []);

    useEffect(() => {
        if (searchQuery.trim() === '') {
            setFilteredLeads(leads);
        } else {
            const query = searchQuery.toLowerCase();
            const filtered = leads.filter(lead =>
                (lead.customer_name?.toLowerCase().includes(query)) ||
                (lead.customer_phone?.toLowerCase().includes(query)) ||
                (lead.last_message?.toLowerCase().includes(query))
            );
            setFilteredLeads(filtered);
        }
    }, [searchQuery, leads]);

    async function registerForPushNotifications() {
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;
        if (existingStatus !== 'granted') {
            const { status } = await Notifications.requestPermissionsAsync();
            finalStatus = status;
        }
        if (finalStatus !== 'granted') {
            console.log('Failed to get push token for push notification!');
            return;
        }
    }

    async function fetchLeads() {
        const { data, error } = await supabase
            .from('lead_conversations')
            .select('*')
            .neq('status', 'archived')
            .order('updated_at', { ascending: false });

        if (error) console.error(error);
        else setLeads(data);
        setLoading(false);
    }

    const renderItem = ({ item }) => (
        <TouchableOpacity
            activeOpacity={0.7}
            onPress={() => navigation.navigate('Chat', {
                leadId: item.id,
                name: item.customer_name || item.customer_phone,
                phone: item.customer_phone
            })}
            style={styles.itemContainer}
        >
            <GlassCard style={styles.card}>
                <View style={styles.topRow}>
                    <View style={styles.avatarContainer}>
                        <User color={COLORS.primary} size={20} />
                    </View>
                    <View style={styles.headerInfo}>
                        <Text style={styles.leadName}>{item.customer_name || item.customer_phone}</Text>
                        <Text style={styles.timeText}>
                            {new Date(item.updated_at || item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </Text>
                    </View>
                    <ChevronRight color={COLORS.textMuted} size={20} />
                </View>

                <View style={styles.messageRow}>
                    <MessageSquare color={COLORS.secondary} size={16} style={styles.msgIcon} />
                    <Text style={styles.lastMsg} numberOfLines={2}>
                        {item.last_message || "Nuova conversazione"}
                    </Text>
                </View>

                <View style={styles.footer}>
                    <View style={[styles.statusBadge, { backgroundColor: item.status === 'active' ? COLORS.primary + '20' : COLORS.textMuted + '20' }]}>
                        <View style={[styles.statusDot, { backgroundColor: item.status === 'active' ? COLORS.primary : COLORS.textMuted }]} />
                        <Text style={[styles.statusText, { color: item.status === 'active' ? COLORS.primary : COLORS.textMuted }]}>
                            {item.status.toUpperCase()}
                        </Text>
                    </View>
                </View>
            </GlassCard>
        </TouchableOpacity>
    );

    if (loading) return <View style={styles.loaderContainer}><ActivityIndicator color={COLORS.primary} size="large" /></View>;

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.searchContainer}>
                <View style={styles.searchBar}>
                    <Search color={COLORS.textMuted} size={18} style={styles.searchIcon} />
                    <TextInput
                        style={styles.searchInput}
                        placeholder="Cerca lead o messaggi..."
                        placeholderTextColor={COLORS.textMuted}
                        value={searchQuery}
                        onChangeText={setSearchQuery}
                        clearButtonMode="while-editing"
                    />
                </View>
            </View>
            <FlatList
                data={filteredLeads}
                keyExtractor={(item) => item.id.toString()}
                renderItem={renderItem}
                contentContainerStyle={styles.listPadding}
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={onRefresh}
                        tintColor={COLORS.primary}
                        colors={[COLORS.primary]}
                    />
                }
                ListEmptyComponent={
                    !loading && (
                        <View style={styles.emptyContainer}>
                            <Text style={styles.emptyText}>Nessun lead trovato</Text>
                        </View>
                    )
                }
            />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    loaderContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.background },
    searchContainer: {
        paddingHorizontal: SPACING.md,
        paddingTop: SPACING.sm,
        paddingBottom: SPACING.xs
    },
    searchBar: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.surface,
        borderRadius: 12,
        paddingHorizontal: 12,
        height: 48,
        borderWidth: 1,
        borderColor: COLORS.glassBorder,
    },
    searchIcon: { marginRight: 8 },
    searchInput: {
        flex: 1,
        color: COLORS.text,
        fontFamily: 'Outfit_400Regular',
        fontSize: 16
    },
    listPadding: { padding: SPACING.md },
    emptyContainer: {
        marginTop: 100,
        alignItems: 'center'
    },
    emptyText: {
        color: COLORS.textMuted,
        fontFamily: 'Outfit_400Regular',
        fontSize: 16
    },
    itemContainer: { marginBottom: SPACING.md },
    card: { padding: 0 },
    topRow: { flexDirection: 'row', alignItems: 'center', marginBottom: SPACING.sm },
    avatarContainer: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: COLORS.surfaceLight,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: SPACING.sm,
    },
    headerInfo: { flex: 1 },
    leadName: {
        color: COLORS.text,
        fontSize: 17,
        fontFamily: 'Outfit_600SemiBold'
    },
    timeText: {
        color: COLORS.textMuted,
        fontSize: 12,
        fontFamily: 'Outfit_400Regular'
    },
    messageRow: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        backgroundColor: COLORS.surfaceLight + '40',
        padding: SPACING.sm,
        borderRadius: 12,
        marginTop: SPACING.xs
    },
    msgIcon: { marginTop: 2, marginRight: 8 },
    lastMsg: {
        flex: 1,
        color: COLORS.textMuted,
        fontSize: 14,
        lineHeight: 20,
        fontFamily: 'Outfit_400Regular'
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
        marginTop: SPACING.sm
    },
    statusBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 20,
    },
    statusDot: {
        width: 6,
        height: 6,
        borderRadius: 3,
        marginRight: 6,
    },
    statusText: {
        fontSize: 10,
        fontFamily: 'Outfit_700Bold',
    },
});
