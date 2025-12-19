# 📱 Agency CRM Dashboard: "Zen Mode" Specification

## 🎯 Design Philosophy
**"Minimalism First"**. The interface should look and feel exactly like **WhatsApp Web**, but with "Superpowers" hidden in plain sight. NO complex menus. NO dense tables.

## 🏗️ Technical Stack
*   **React + Vite + TailwindCSS** (For speed and clean styling).
*   **Phosphor Icons** or **Lucide** (Thin, elegant lines).

## 🧩 The 2-Pane Layout (Simplistic)

### 1. The "Inbox" (Left Sidebar - 30% width)
*   **Clean List**: Avatar, Name, and Last Message snippet.
*   **Smart Badges** (Subtle dots):
    *   🟢 **Green Dot**: AI Active (Autopilot).
    *   🔴 **Red Halo**: Human Needed (Takeover).
*   **Search Bar**: "Search Marco..." (Instant filter).

### 2. The "Focus Thread" (Main View - 70% width)
*   **Header**:
    *   **Name**: Big and bold.
    *   **The Switch**: A single "Toggle Switch" 🏳️ to stop the AI. (Green = AI On, Gray = AI Muted).
    *   **Context**: Small subtitle "Looking for: Trilocale, ~500k" (Auto-extracted).
*   **Chat Stream**:
    *   **Bubbles**: Standard message bubbles.
    *   **Ghost Bubbles**: When AI replies, show a distinct (but subtle) color so you know who sent what.
*   **Input Area**: Large text box to reply manually.

### 3. "The Drawer" (Details on Demand)
*   *Hidden by default to keep the interface clean.*
*   Accessible via an **"Info ⓘ"** icon in the header.
*   Slides in from the right to show:
    *   **CRM Data**: Email, Phone, Budget, Zone.
    *   **Notes**: Text area for private agency notes.
    *   **Actions**: "Send Calendar Link", "Archive Lead".

## 🚀 Implementation Steps

### Phase 1: The "Shell"
*   [ ] Setup React project with a simplified "WhatsApp Clone" template.
*   [ ] Connect Supabase to fetch the `lead_conversations` list.

### Phase 2: The "Interaction"
*   [ ] Implement the **Chat Stream** (Real-time message syncing).
*   [ ] Build the **AI Toggle Switch** (The most important button).
*   [ ] Add the **Quick Stats** header (Budget/Zone).

### Phase 3: Polish
*   [ ] Add "Typing..." animations.
*   [ ] Implement "Message Sent" double-ticks.
*   [ ] Mobile responsiveness (work from phone).
