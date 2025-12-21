---
description: Policy for UI Testing
---

# UI Testing Policy

To ensure optimal resource usage and user control, the following policy applies to all UI testing activities:

1. **User Confirmation Required**: No UI testing (automated browser scripts, manual browser navigation, or visual regression tests) shall be initiated without direct confirmation from the user.
2. **Scope**: This applies to all tools that interact with a browser (e.g., Playwright, Selenium, or internal browser subagents).
3. **Verification**: Before running tests that affect the UI, the agent must:
    - Describe the test to be performed.
    - Explicitly ask the user for permission to proceed.
    - Wait for a positive confirmation.
