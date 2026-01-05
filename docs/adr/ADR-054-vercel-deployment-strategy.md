# ADR-054: Vercel Deployment Strategy

## Status
Accepted

## Date
2026-01-05

## Context
The project uses a frontend application that requires a build step (Vite) to generate static assets. When deploying to Vercel, we faced issues where the build command configured in `vercel.json` was a no-op (`echo 'Build already completed locally'`), but the expected output directory (`dist`) was missing because it was Git-ignored.

We considered two main approaches:
1.  **Build on Vercel**: Configure Vercel to install dependencies and run `npm run build` during deployment.
2.  **Commit Pre-built Assets**: Run the build locally, commit the `dist` directory, and have Vercel simply serve these files.

## Decision
We decided to **Commit Pre-built Assets** and upload them to Vercel.

**Implementation Details**:
- Remove `dist/` from `.gitignore`.
- Keep `vercel.json` "build" command as a no-op.
- Ensure developers run `npm run build` before committing changes to the frontend.

## Consequences

**Positive**:
- **Faster Deployments**: Skipping the install and build steps on Vercel reduces deployment time significantly (e.g., ~9 seconds).
- **Reliability**: We deploy exactly what we tested locally; no surprises from different Node versions or environment differences on the build server.
- **Simplicity**: `vercel.json` configuration remains minimal.

**Negative**:
- **Repo Size**: Binary assets (images, minified code) increase repository size and git history.
- **Developer Friction**: Developers must remember to build before pushing; failure to do so means deploying stale code.
- **Merge Conflicts**: Periodic conflicts in `dist/` files if multiple developers work on frontend simultaneously.

## Mitigation
- We deemed the 1.8MB size of `dist` acceptable.
- Future mitigation could involves a pre-commit hook to ensure `dist` is fresh, or moving to a Github Action that builds and deploys artifacts if repo size becomes an issue.
