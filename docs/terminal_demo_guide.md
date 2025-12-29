# Terminal Demo Test - Usage Guide

## Overview

The **Terminal Demo Test** is an interactive CLI tool that simulates WhatsApp conversations without consuming API credits. It uses mocked dependencies (Twilio, Supabase) while maintaining full LangGraph workflow execution.

## Features

✅ **Zero API Costs**: All external services mocked
✅ **Full LangGraph Execution**: Tests the complete 9-node StateGraph
✅ **State Inspection**: Displays extracted intent, sentiment, preferences, and matched properties
✅ **Multi-Language**: Supports Italian and English conversations
✅ **In-Memory Database**: 3 sample properties pre-loaded

## Usage

### Basic Usage

```bash
./venv/bin/python scripts/terminal_demo.py
```

### With Options

```bash
# English conversation
./venv/bin/python scripts/terminal_demo.py --language en

# Custom phone number
./venv/bin/python scripts/terminal_demo.py --phone "+393331234567"
```

### Interactive Commands

- **Type your message**: Simulates user input
- **`reset`**: Clear conversation history and start fresh
- **`quit` or `exit`**: End the session

## Example Session

```
🤖 AGENZIA AI - TERMINAL DEMO TEST
================================================================================
📞 Simulating conversation for: +39333999000
🌍 Language: IT

👤 You: Ciao, cerco una casa in Toscana con budget 500k

⏳ Processing...

📊 EXTRACTED STATE
--------------------------------------------------------------------------------
Intent: PURCHASE
Budget: €500,000
Entities: Toscana
Sentiment: NEUTRAL (Urgency: MEDIUM)
Preferences: ['Toscana']

Matched Properties (3):
  • Villa Toscana con Vista - €450,000 (0.92)
  • Rustico Chianti - €520,000 (0.85)
  • Appartamento Centro Milano - €380,000 (0.88)
--------------------------------------------------------------------------------

================================================================================
📱 OUTGOING MESSAGE
================================================================================
To: +39333999000

Ciao! Perfetto, con 500k in Toscana hai ottime opzioni. 😊

Dalle ricerche attuali, ti segnalo subito una **Villa in Toscana con Vista**
a **€450.000** – un vero affare per la zona...
================================================================================
```

## Architecture

### Mocked Components

1. **TerminalMessagingAdapter**: Prints messages to console instead of Twilio
2. **TerminalDatabaseAdapter**: In-memory storage with 3 sample properties
3. **Mock Calendar**: Returns fake Google Calendar links
4. **Mock Document Generator**: Returns placeholder PDF paths

### Real Components

- **LangChainAdapter**: Uses actual Mistral AI API
- **LangGraph StateGraph**: Full 9-node workflow execution
- **LeadProcessor**: Production code path

## Testing

Run automated test:

```bash
bash scripts/test_terminal_demo.sh
```

## Sample Properties

The demo includes 3 pre-loaded properties:

1. **Villa Toscana con Vista** - €450,000 (Firenze, 4 rooms, 180 sqm)
2. **Appartamento Centro Milano** - €380,000 (Milano, 3 rooms, 120 sqm)
3. **Rustico Chianti** - €520,000 (Siena, 5 rooms, 220 sqm)

## Development Benefits

- **Cost Savings**: No Twilio credits consumed
- **Fast Iteration**: Instant feedback without API latency
- **Debugging**: Full state visibility for troubleshooting
- **Testing**: Validate LangGraph nodes without external dependencies
