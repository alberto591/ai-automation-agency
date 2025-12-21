# ADR 029: Mobile Direct-to-Storage Uploads

## Status
Accepted

## Context
The "Anzevino AI" mobile application (React Native/Expo) requires a mechanism to upload rich media (images, voice notes) to the cloud. The web dashboard currently interacts with the backend API for most operations. For large binary files, routing traffic through a Python/FastAPI middleware adds unnecessary latency, bandwidth costs, and complexity (handling multipart streams).

## Decision
We will use the **Supabase Storage Client** directly within the mobile application to upload files to the `chat-attachments` bucket.
- The mobile app will use the `supabase-js` client initialized with the public key.
- Row Level Security (RLS) policies will enforce access control (currently public for the MVP/Beta).
- The returned public URL will be sent as a text message metadata to the chat API (`[IMAGE]url` or `[AUDIO:duration]url`).

## Consequences
### Positive
- **Performance**: Uploads go directly to the CDN edge, bypassing our application server.
- **Simplicity**: No need to implement multipart file handling parsers in the Python backend.
- **Resilience**: The backend is decoupled from large file processing, preventing potential worker blocking.

### Negative
- **Security Logic**: Access control logic is split between API (business logic) and Database (RLS). We must ensure RLS policies are strict.
- **Client Complexity**: The mobile client handles file path generation and mime-type detection.

## Implementation
- `mobile/src/lib/supabase.js`: Initializes client.
- `mobile/src/lib/api.js`: Implements `uploadFile` helper.
- `chat-attachments` bucket: Configured with Public Access.
