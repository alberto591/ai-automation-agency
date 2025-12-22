# 🏠 Project Documentation

> [!IMPORTANT]
> **ADR Policy**: Every new feature or architectural change MUST be preceded by an **Architectural Decision Record (ADR)**.
> This document explains *why* a decision was made, the options considered, and the chosen implementation path.
> See `docs/adr/template.md` for the format. Code reviews will fail without a corresponding ADR.

Welcome to the **Anzevino AI Real Estate Agent** documentation. This folder contains all the technical and operational guides for the system.

## 📂 Documentation Sections

### 🚀 Getting Started & Deployment
- [**Production Deployment Guide**](PRODUCTION_DEPLOYMENT.md) - **[START HERE]** Complete guide for Vercel, Render, and Twilio.
- [Next Steps Roadmap](roadmap.md) - Path to scaling and scaling phase.
- [Basic Setup](file:///Users/lycanbeats/Desktop/agenzia-ai/README.md) - Local install and project overview.

### 🔄 Integrations & Data
- [Portal Integration Guide](portal-integration.md) - How to connect Immobiliare.it, Idealista, and Casa.it.
- [Property Import (CSV)](property-import.md) - Managing your listings database.
- [Customer Flow](customer-flow).md - Visual and logical map of the lead journey.

### 🛡️ Security & API
- [Webhook Security](api-security.md) - Documentation on `X-Webhook-Key` header authentication.
- [Database Upgrade (Pro Chat)](database-upgrade.md) - SQL commands for full dashboard history.

### 📈 Growth & Lead Generation
- [Portal Integrations](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/portal-integration.md): How to connect Immobiliare.it and Idealista.
- [Sales Journey Blueprint](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/sales-journey-blueprint.md): Detailed step-by-step from lead capture to sale.
- [Database Migration](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/database-upgrade.md): SQL scripts for Pro Dashboard.
- [WhatsApp Migration](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/whatsapp-migration-guide.md): **[STRATEGIC]** How to move from Twilio to Meta to save costs.
- [Business ROI Report](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/business-roi-report.md): **[PARTNER FOCUS]** Data-driven pitch for the AI Agency value.
- [Testing & Demo Guide](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/testing-and-demo-guide.md): **[NEW]** How to run Mock Mode, Partner Demos, and Simulations.
- [Market Scraper](file:///Users/lycanbeats/Desktop/agenzia-ai/market_scraper.py) - Tool to gather competitive property data.
- [Agency Outreach](file:///Users/lycanbeats/Desktop/agenzia-ai/agency_outreach.py) - Script to generate B2B lead lists of real estate agencies.
- [Market Data SQL Migration](file:///Users/lycanbeats/Desktop/agenzia-ai/sql/market-data-migration.sql) - Schema for the competitive data table.

### 🎨 Frontend
- [Appraisal Tool Architecture](appraisal-tool-architecture.md) - Technical details on the appraisal tool structure.

---
*Created by Antigravity AI Assistant.*
