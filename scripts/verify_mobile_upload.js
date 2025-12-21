require('dotenv').config({ path: '.env' });
const { createClient } = require('@supabase/supabase-js');
const { decode } = require('base64-arraybuffer');

// Mock dependencies
const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_KEY || process.env.SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error("Missing SUPABASE credentials in env");
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function uploadFile(base64Data, fileName, mimeType) {
    console.log(`Uploading ${fileName} (${mimeType})...`);
    const { data, error } = await supabase.storage
        .from('chat-attachments')
        .upload(fileName, decode(base64Data), {
            contentType: mimeType,
            upsert: false
        });

    if (error) {
        console.error('Upload failed:', error);
        return null;
    }

    const { data: publicUrlData } = supabase.storage
        .from('chat-attachments')
        .getPublicUrl(data.path);

    return publicUrlData.publicUrl;
}

// Emulate a small text file as base64
const mockBase64 = "SGVsbG8gV29ybGQ="; // "Hello World"
const mockFilename = `test-upload-${Date.now()}.txt`;
const mockMime = 'text/plain';

(async () => {
    try {
        const url = await uploadFile(mockBase64, mockFilename, mockMime);
        if (url) {
            console.log("SUCCESS: File uploaded.");
            console.log("Public URL:", url);
        } else {
            console.log("FAILURE: Upload returned no URL.");
        }
    } catch (e) {
        console.error("CRITICAL ERROR:", e);
    }
})();
