# Ultra-Fast Test Mode - Quick Start Guide

## What is Test Mode?

Test Mode bypasses all API calls and returns instant mock data, reducing response time from **~10s to <1s** for rapid UI development.

---

## How to Enable

### 1. Update `.env` file

```bash
# Change this line in your .env file
TEST_MODE=true
```

### 2. Restart the backend

```bash
# Kill the current server (Ctrl+C or pkill)
pkill -f uvicorn

# Restart with test mode enabled
./venv/bin/uvicorn presentation.api.api:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test the form

Navigate to [http://localhost:5173/appraisal/](http://localhost:5173/appraisal/) and submit the form. You should see:

- ⚡ **Instant response** (<1 second)
- **"TEST MODE"** indicator in the reasoning field
- **No animations** - values appear immediately
- **Realistic mock data** for all metrics

---

## When to Use

| Scenario | Use Test Mode? |
|----------|----------------|
| **UI development** | ✅ Yes - ultra-fast iteration |
| **Frontend testing** | ✅ Yes - no API dependencies |
| **Integration testing** | ❌ No - need real APIs |
| **Production** | ❌ No - need real data |
| **User demos** | ❌ No - show real accuracy |

---

## Disabling Test Mode

```bash
# In .env file
TEST_MODE=false
```

Then restart the backend. The system will return to normal operation with real API calls.

---

## Technical Details

### Backend Changes

- **File**: `application/services/appraisal.py`
- **Method**: `_create_test_result()` - generates instant mock data
- **Trigger**: Checks `settings.TEST_MODE` at start of `estimate_value()`

### Frontend Changes

- **File**: `apps/landing-page/appraisal/script.js`
- **Detection**: Checks if `appraisal.reasoning` contains "TEST MODE"
- **Behavior**: Skips animations and displays values instantly

### Mock Data

Test mode returns:
- Base price: €3,500/sqm
- 3 realistic comparables
- Full investment metrics
- 85% confidence level
- 4-star reliability

---

## Troubleshooting

**Q: Test mode not working?**
- Verify `TEST_MODE=true` in `.env`
- Restart backend server
- Check logs for "TEST_MODE_ENABLED" message

**Q: Still seeing delays?**
- Clear browser cache
- Hard refresh (Cmd+Shift+R / Ctrl+Shift+F5)
- Check Network tab - should see instant 200 response

**Q: Want to test specific scenarios?**
- Edit `_create_test_result()` in `appraisal.py`
- Customize mock data for edge cases
- Restart backend to apply changes
