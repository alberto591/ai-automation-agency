# 🎯 AI Real Estate Agency: Tuscany Demo Guide

This guide will walk you through a professional demonstration of the system's capabilities, showcasing the speed, depth, and intelligence of the Phase 3 optimized solution.

---

## 🏗️ Preparation
Ensure the following services are running in your terminal:
1. **Frontend**: `npm run dev` in `apps/landing-page` (usually [localhost:5173](http://localhost:5173))
2. **Backend**: `uvicorn presentation.api.api:app` (port 8000)
3. **Maintenance**: `python scripts/system_maintenance_worker.py` (running in background)

---

## 🎬 Scenario 1: The "Wow" Speed (Tuscany Optimization)
*Objective: Show the instant response time enabled by the local Tuscany dataset.*

1. **Navigate** to the Appraisal Tool ([localhost:5173/appraisal](http://localhost:5173/appraisal)).
2. **Enter the following "Hot Zone" property**:
   - **City**: `Firenze`
   - **Zone**: `Centro`
   - **Property Type**: `Appartamento`
   - **Surface**: `150` sqm
   - **Condition**: `Ristrutturato` (Renovated)
3. **Action**: Click **"Ottieni Valutazione AI"**.
4. **Highlight**: The response should be near-instant (~300ms). Point out that the system recognized this as a high-demand area and pulled from the **Optimized Local Database** instead of waiting for a global search.

---

## 📊 Scenario 2: Deep Investment Intelligence
*Objective: Show that we provide more than just a price; we provide a business case.*

1. **Review the Results Panel**:
   - **Estimated Range**: Show the ±5% confidence range.
   - **Performance Stars**: Highlight the **5-Star reliability** (driven by the high-quality local comparables).
2. **Expand the Investment Dashboard**:
   - Point out the **Monthly Rent** estimate.
   - Explain the **ROI (Return on Investment)** and **Cap Rate**.
   - Show the **Cash-on-Cash Return** for investors interested in financing.
3. **Comparables**: Click on the individual comparable properties. Mention that these are **real, verified listings** from our Tuscany property graph.

---

## 📄 Scenario 3: Professional Reporting
*Objective: Demonstrate the "Productization" of AI.*

1. **Action**: Click the **"Scarica Report PDF"** button.
2. **Wait for Success**: The button will transform with a checkmark.
3. **Show**: Mention that this report is a professional-grade white-label document ready to be sent directly to the owner/investor.

---

## 🔄 Scenario 4: The Continuous Feedback Loop
*Objective: Show the system is "Alive" and learning.*

1. **Action**: Click **"Lascia un Feedback"** (or use the floating survey if active).
2. **Fill the Form**:
   - Provide a **5-star** rating for Speed and Accuracy.
   - Comment: *"Incredibilmente veloce per Firenze Centro!"*
3. **Submit**: Show the success message.
4. **Behind the Scenes**: Explain that this feedback is now **Linked (UUID)** to that specific appraisal session for analytics.

---

## 📈 Scenario 5: Data Transparency (Optional)
*Objective: For technical stakeholders, show the "Engine Room".*

1. **Navigate** to the Monitoring Endpoint (or local dashboard if open):
   - `GET http://localhost:8000/api/monitoring/performance`
2. **Highlight**:
   - **Local Hit Rate**: Show it at **100%** for the Florence demo.
   - **Avg Response Time**: Show it below **1s**.
   - **Recent Feedback**: Mention that the maintenance worker is syncing this feedback every hour to your executive dashboard.

---

## 📢 Key Talking Points for Demo
- **"Scalabilità"**: We are not limited by API quotas; our system builds its own intelligence as more searches are performed.
- **"Precisione Locale"**: Unlike global AVMs, we understand specific city zones (e.g., *Oltrarno* vs *Centro*).
- **"Resilienza"**: If local data is missing, we fall back to a global LLM search seamlessly.

---
> [!TIP]
> **Pro Tip**: Use the **Firenze Centro** scenario first to guarantee the fastest visual "Wow" factor.
