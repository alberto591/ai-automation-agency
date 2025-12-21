import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { User, Phone, Euro, MapPin, Save, Trash2, X, Plus } from 'lucide-react-native';
import { api } from '../lib/api';
import { COLORS, SPACING } from '../theme/constants';

export default function LeadDetail({ route, navigation }) {
    const { lead } = route.params;
    const [name, setName] = useState(lead.customer_name || '');
    const [budget, setBudget] = useState(lead.budget_max?.toString() || '');
    const [zones, setZones] = useState(lead.zones || []);
    const [newZone, setNewZone] = useState('');
    const [loading, setLoading] = useState(false);

    function addZone() {
        if (newZone.trim() && !zones.includes(newZone.trim())) {
            setZones([...zones, newZone.trim()]);
            setNewZone('');
        }
    }

    function removeZone(zoneToRemove) {
        setZones(zones.filter(z => z !== zoneToRemove));
    }

    async function handleSave() {
        setLoading(true);
        try {
            const updatedData = {
                phone: lead.customer_phone,
                name: name,
                budget: parseInt(budget) || null,
                zones: zones,
            };

            await api.updateLead(updatedData);
            Alert.alert("Successo", "Lead aggiornato con successo");
            navigation.goBack();
        } catch (err) {
            console.error(err);
            Alert.alert("Errore", "Impossibile aggiornare il lead");
        } finally {
            setLoading(false);
        }
    }

    async function handleArchive() {
        Alert.alert(
            "Archivia Lead",
            "Sei sicuro di voler archiviare questo lead? Non comparirà più nella lista attiva.",
            [
                { text: "Annulla", style: "cancel" },
                {
                    text: "Archivia",
                    style: "destructive",
                    onPress: async () => {
                        setLoading(true);
                        try {
                            await api.updateLead({ phone: lead.customer_phone, status: 'archived' });
                            Alert.alert("Successo", "Lead archiviato");
                            navigation.goBack();
                        } catch (err) {
                            console.error(err);
                            Alert.alert("Errore", "Impossibile archiviare il lead");
                        } finally {
                            setLoading(false);
                        }
                    }
                }
            ]
        );
    }

    return (
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Anagrafica</Text>
                <View style={styles.inputBox}>
                    <User size={20} color={COLORS.primary} style={styles.icon} />
                    <TextInput
                        style={styles.input}
                        value={name}
                        onChangeText={setName}
                        placeholder="Nome Completo"
                        placeholderTextColor={COLORS.textMuted}
                    />
                </View>
                <View style={[styles.inputBox, styles.readOnly]}>
                    <Phone size={20} color={COLORS.textMuted} style={styles.icon} />
                    <Text style={styles.readOnlyText}>{lead.customer_phone}</Text>
                </View>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Requisiti</Text>
                <View style={styles.inputBox}>
                    <Euro size={20} color={COLORS.secondary} style={styles.icon} />
                    <TextInput
                        style={styles.input}
                        value={budget}
                        onChangeText={setBudget}
                        placeholder="Budget Massimo"
                        placeholderTextColor={COLORS.textMuted}
                        keyboardType="numeric"
                    />
                </View>

                <View style={styles.zonesLabelRow}>
                    <MapPin size={16} color={COLORS.accent} style={styles.labelIcon} />
                    <Text style={styles.inputLabel}>Zone di interesse</Text>
                </View>

                <View style={styles.chipsContainer}>
                    {zones.map((zone, index) => (
                        <TouchableOpacity key={index} style={styles.chip} onPress={() => removeZone(zone)}>
                            <Text style={styles.chipText}>{zone}</Text>
                            <X size={12} color={COLORS.white} style={styles.chipClose} />
                        </TouchableOpacity>
                    ))}
                </View>

                <View style={styles.inputBox}>
                    <Plus size={20} color={COLORS.accent} style={styles.icon} />
                    <TextInput
                        style={styles.input}
                        value={newZone}
                        onChangeText={setNewZone}
                        placeholder="Aggiungi zona..."
                        placeholderTextColor={COLORS.textMuted}
                        onSubmitEditing={addZone}
                        returnKeyType="add"
                    />
                    {newZone.trim() !== '' && (
                        <TouchableOpacity onPress={addZone} style={styles.addZoneBtn}>
                            <Text style={styles.addZoneBtnText}>Aggiungi</Text>
                        </TouchableOpacity>
                    )}
                </View>
            </View>

            <TouchableOpacity
                style={[styles.saveButton, loading && styles.disabled]}
                onPress={handleSave}
                disabled={loading}
            >
                {loading ? <ActivityIndicator color={COLORS.white} /> : (
                    <>
                        <Save size={20} color={COLORS.white} />
                        <Text style={styles.saveText}>Salva Modifiche</Text>
                    </>
                )}
            </TouchableOpacity>

            <TouchableOpacity
                style={styles.archiveButton}
                onPress={handleArchive}
                disabled={loading}
            >
                <Trash2 size={20} color={COLORS.accent} />
                <Text style={styles.archiveText}>Archivia Lead</Text>
            </TouchableOpacity>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    content: { padding: SPACING.lg },
    section: { marginBottom: SPACING.xl },
    sectionTitle: {
        color: COLORS.text,
        fontSize: 14,
        fontFamily: 'Outfit_700Bold',
        textTransform: 'uppercase',
        marginBottom: SPACING.md,
        letterSpacing: 1,
    },
    inputBox: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.surface,
        borderRadius: 12,
        paddingHorizontal: 16,
        height: 56,
        marginBottom: SPACING.md,
        borderWidth: 1,
        borderColor: COLORS.glassBorder,
    },
    icon: { marginRight: 12 },
    input: {
        flex: 1,
        color: COLORS.text,
        fontSize: 16,
        fontFamily: 'Outfit_400Regular',
    },
    zonesLabelRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: SPACING.sm,
        marginLeft: 4,
    },
    labelIcon: { marginRight: 6 },
    inputLabel: {
        color: COLORS.textMuted,
        fontSize: 14,
        fontFamily: 'Outfit_600SemiBold',
    },
    chipsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: SPACING.md,
    },
    chip: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.accent,
        borderRadius: 20,
        paddingHorizontal: 12,
        paddingVertical: 6,
        marginRight: 8,
        marginBottom: 8,
    },
    chipText: {
        color: COLORS.white,
        fontSize: 14,
        fontFamily: 'Outfit_600SemiBold',
    },
    chipClose: {
        marginLeft: 6,
    },
    addZoneBtn: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        backgroundColor: COLORS.accent + '20',
        borderRadius: 12,
    },
    addZoneBtnText: {
        color: COLORS.accent,
        fontSize: 12,
        fontFamily: 'Outfit_700Bold',
    },
    readOnly: { backgroundColor: COLORS.background, borderColor: 'transparent' },
    readOnlyText: { color: COLORS.textMuted, fontSize: 16, fontFamily: 'Outfit_400Regular' },
    saveButton: {
        backgroundColor: COLORS.primary,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        height: 56,
        borderRadius: 16,
        marginTop: SPACING.md,
    },
    saveText: { color: COLORS.white, fontSize: 18, fontFamily: 'Outfit_600SemiBold', marginLeft: 8 },
    disabled: { opacity: 0.6 },
    archiveButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: SPACING.xl,
    },
    archiveText: { color: COLORS.accent, fontSize: 14, fontFamily: 'Outfit_600SemiBold', marginLeft: 8 },
});
