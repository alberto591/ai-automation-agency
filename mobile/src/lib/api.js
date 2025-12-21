const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

import { supabase } from './supabase';
import { decode } from 'base64-arraybuffer';

export const api = {
    takeover: async (phone) => {
        const response = await fetch(`${API_BASE_URL}/api/leads/takeover`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone }),
        });
        return response.json();
    },
    resume: async (phone) => {
        const response = await fetch(`${API_BASE_URL}/api/leads/resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone }),
        });
        return response.json();
    },
    sendMessage: async (phone, message) => {
        const response = await fetch(`${API_BASE_URL}/api/leads/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, message }),
        });
        return response.json();
    },
    updateLead: async (leadData) => {
        const response = await fetch(`${API_BASE_URL}/api/leads`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(leadData),
        });
        return response.json();
    },
    uploadFile: async (base64Data, fileName, mimeType) => {
        const { data, error } = await supabase.storage
            .from('chat-attachments')
            .upload(fileName, decode(base64Data), {
                contentType: mimeType,
                upsert: false
            });

        if (error) {
            console.error('Upload failed:', error);
            throw error;
        }

        const { data: publicUrlData } = supabase.storage
            .from('chat-attachments')
            .getPublicUrl(data.path);

        return publicUrlData.publicUrl;
    }
};
