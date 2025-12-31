# GitHub Repository Setup & Push Guide

Complete guide to push changes and manage the Anzevino AI Real Estate Agent repository.

## Quick Push Commands

```bash
cd /Users/lycanbeats/Desktop/agenzia-ai

# Check status
git status

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: separate frontend apps (landing-page, dashboard, fifi)"

# Push to GitHub
git push origin main
```

---

## Repository Structure

```
agenzia-ai/
├── apps/                   # Frontend applications
│   ├── landing-page/       # Marketing site (/)
│   ├── dashboard/          # Admin panel (/dashboard)
│   └── fifi/               # Appraisal tool (/appraisal)
├── presentation/           # API layer (FastAPI)
├── application/            # Use cases
├── domain/                 # Business entities
├── infrastructure/         # External adapters
├── tests/                  # Unit/integration tests
├── docs/                   # Documentation & ADRs
└── archive/                # Deprecated code
```

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `develop` | Integration branch |
| `feature/*` | New features |
| `fix/*` | Bug fixes |

### Feature Branch Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push feature branch
git push origin feature/new-feature

# Create PR on GitHub for review
```

---

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

Types:
- feat:     New feature
- fix:      Bug fix
- docs:     Documentation
- refactor: Code restructuring
- test:     Adding tests
- chore:    Maintenance
```

**Examples:**
```bash
git commit -m "feat: add appraisal PDF generation endpoint"
git commit -m "fix: resolve disclaimer validation in fifi"
git commit -m "test: add unit tests for appraisal API"
git commit -m "docs: update README with new structure"
```

---

## Pre-Push Checklist

Before pushing, verify:

```bash
# 1. Run backend tests
./venv/bin/pytest tests/unit/test_api.py -v

# 2. Run linter
./venv/bin/ruff check .

# 3. Type check
./venv/bin/mypy .

# 4. Build frontend apps
cd apps/landing-page && npm run build && cd ../..
cd apps/fifi && npm run build && cd ../..
cd apps/dashboard && npm run build && cd ../..

# 5. Verify no secrets exposed
grep -r "API_KEY=" . --include="*.py" | grep -v ".env"
```

---

## Vercel Deployment

This project uses **Vercel** for frontend deployment:

1. Push to `main` branch
2. Vercel auto-deploys via GitHub integration
3. Check deployment at: `https://anzevino.ai` (or your domain)

**vercel.json** handles:
- Building all 3 frontend apps
- Routing `/`, `/dashboard`, `/appraisal`
- API rewrites to backend

---

## Troubleshooting

### Authentication Failed

```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:alberto591/ai-automation-agency.git
```

### Large Files Rejected

```bash
# Check for large files
find . -type f -size +50M

# Add to .gitignore if needed
echo "large_file.ext" >> .gitignore
```

### Merge Conflicts

```bash
# Pull latest changes first
git pull origin main

# Resolve conflicts in editor
# Then commit resolution
git add .
git commit -m "fix: resolve merge conflicts"
git push
```

---

## Quick Reference

```bash
# View recent commits
git log --oneline -10

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View branches
git branch -a

# Switch branch
git checkout branch-name
```

---

*Last updated: 2025-12-31*
