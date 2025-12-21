# 13. Vercel Deployment Strategy

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-03-20 (Retroactive)

## Context and Problem Statement

We needed a friction-less way to deploy the React Dashboard and potentially the API. The solution needed to support CI/CD (deploy on push), handling of environment variables, and fast global delivery.

## Considered Options

*   **Docker + VPS**: Building containers and hosting on DigitalOcean/AWS EC2.
*   **Heroku / Render**: PaaS solutions, good but slower cold starts on free tiers.
*   **Vercel**: Optimized for frontend, with serverless capabilities.

## Decision Outcome

Chosen option: **Vercel**.

### Reasoning
1.  **Frontend First**: Vercel is the gold standard for deploying Vite/React apps. It handles build caching, CDN distribution, and asset compression automatically.
2.  **Serverless API**: Vercel can also host the Python API as Serverless Functions (`api/index.py` pattern), allowing us to keep frontend and backend in the same repo/deployment (Monorepo-lite).
3.  **Preview Environments**: Critical for testing changes before merging to main.

### Implementation
*   `vercel.json`: Configures the build command and rewrites.
*   **Environment**: Secrets managed via Vercel Project Settings.

### Positive Consequences
*   Zero DevOps overhead.
*   Instant rollbacks.
*   Automatic HTTPS/SSL.

### Negative Consequences
*   Serverless functions have execution time limits (problematic for long-running AI tasks if not careful). (Mitigation: Use background tasks or external queues if needed).
