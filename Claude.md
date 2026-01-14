# AI Coding Standards - Anzevino AI Real Estate Agent

## Goals
- Enforce SOLID principles by default
- Produce modular, scalable, testable, observable, and deployable code
- Use clear file naming and a consistent project layout
- Ask for approval before major decisions via a strict Decision Request template
- Favor composition over inheritance and dependency injection at the composition root
- Maintain clean, organized project structure with proper file placement
- All AI coding agents must follow these standards when working on this codebase.

## Best Practices Pattern Library

This document works alongside the **queryable best_practices/ pattern library** which contains
machine-readable patterns with examples, gotchas, and detection rules.

**Usage:**
```python
from best_practices import get_patterns, get_pattern_ids, get_gotchas_for_file

# Get all pattern IDs
ids = get_pattern_ids()  # ['LEAD_QUALIFICATION', 'APPRAISAL_DISCLAIMER', ...]

# Get patterns for a file you're editing
patterns = get_patterns_for_file("infrastructure/adapters/mistral_adapter.py")

# Get critical compliance patterns
patterns = get_patterns(tags=["compliance"], severity="critical")

# Get gotchas before editing a file
gotchas = get_gotchas_for_file("infrastructure/adapters/twilio_adapter.py")
```

**CLI Tools:**
```bash
# Regenerate pattern catalog
python -m best_practices.retriever

# Validate all patterns
python -m best_practices.capture --validate
```

**Key Patterns to Know:**

**Lead & Compliance:**
- `LEAD_QUALIFICATION` - Use AI reasoning for lead scoring, never keyword lists
- `APPRAISAL_DISCLAIMER_REQUIREMENT` - All property valuations need appropriate disclaimers
- `PROPERTY_VALUATION_VALIDATION` - Validate AVM outputs with audit trails
- `PORTAL_SYNC_VERIFICATION` - Verify multi-portal property consistency
- `AI_REASONING_OVER_KEYWORDS` - LLM reasoning over hardcoded lists

**Error Handling & Resilience:**
- `FAIL_FAST_NO_MOCK` - Never hide errors with mock data
- `STRUCTURED_LOGGING_LIFECYCLE` - Log lifecycle with prefixes, full context, exc_info
- `RESILIENT_INTEGRATION` - Circuit breakers, graceful degradation, typed errors

**Configuration & Performance:**
- `TYPE_SAFE_CONFIGURATION` - Pydantic BaseSettings with fail-fast validation
- `LAZY_DEPENDENCY_INITIALIZATION` - Defer expensive init until first use
- `EMBEDDING_1024D_STANDARD` - All embeddings must be 1024 dimensions (Mistral standard)

**Architecture & Testing:**
- `HEXAGONAL_ARCHITECTURE` - Ports & adapters with inward dependencies
- `PROTOCOL_ADAPTER_PATTERN` - Wrapper classes for external library isolation
- `DOMAIN_TRANSLATION_MAPPER` - Centralized type mappings, defensive conversion
- `INTEGRATION_TESTING_STRATEGY` - Separate unit (mocked) from integration (real)
- `STATUS_REPORTING_PATTERN` - get_status() on all services

**Integrations:**
- `MODEL_TIER_ROUTING` - Route queries to appropriate model tiers (Mistral for general, Perplexity for research)
- `WHATSAPP_INTEGRATION` - Use Meta WhatsApp Adapter (primary) or Twilio for messaging
- `REAL_TIME_RESEARCH` - Use Perplexity for live data (legal, market comps) instead of hallucinations

**Workflow:**
- `RESEARCH_BEFORE_IMPLEMENTATION` - Web research before new features/complex fixes

When editing code, query relevant patterns first to avoid known gotchas.

**Pattern Discovery:**
The patterns above were extracted from production code analysis.

## Quick Reference - Top Rules

### Never:
1. Use emojis in code, logs or messages (causes rendering issues)
2. Place tests in application or infrastructure directories (use `tests/`)
3. Create MD files in root (only use `docs/` subdirectories and follow docs/doc_manifest.json)
4. Log errors without full traceback and context
5. Use global singletons outside composition root
6. Hardcode keywords/rules instead of AI reasoning
7. Skip Pydantic validation for user inputs
8. Commit secrets or use `.env` without `.env.example`
9. Block async event loops with sync calls
10. Use raw SQL without parameterization
11. **Use mock/fallback data to hide errors** - Always fail visibly for debugging
12. **Create duplicate classes or models** - Each entity/model must have ONE canonical definition

### Always:
1. Check logs before claiming code works
2. Use structured logging with `exc_info=` and context
3. Inject dependencies at composition root only
4. Keep domain layer pure (no I/O)
5. Type hint all function signatures
6. Ask when requirements unclear
7. Validate all user input with Pydantic
8. Use circuit breakers on external dependencies
9. **Fail visibly** - Show real errors, never hide with mock data
10. **Research before implementing** - Use WebSearch for new features, integrations, and complex bug fixes

## No Mock Data / Fail Fast Principle

**CRITICAL: Never use mock/fallback data to hide system failures.**

### The Problem with Mock Data Fallbacks:
```typescript
// ❌ BAD: Hides real errors, makes debugging impossible
useEffect(() => {
  const timeout = setTimeout(() => {
    if (!isConnected && !data) {
      setData(getMockData());  // NEVER DO THIS
      setLoading(false);
    }
  }, 3000);
}, [isConnected, data]);
```

### Why This Is Wrong:
1. **Hides Real Problems**: System appears to work when it's actually broken
2. **Prevents Debugging**: No visible error means no one investigates
3. **Silent Failures**: Users see stale/fake data without knowing it's fake
4. **Production Risk**: Mock data in production creates false confidence
5. **Wastes Time**: Developers debug phantom issues because real errors are hidden

### The Correct Approach:
```typescript
// ✅ GOOD: Shows error, enables debugging
useEffect(() => {
  if (error && !isConnected) {
    // Widget error boundary will catch this and display error UI
    throw new Error(`Failed to connect to WebSocket: ${error.message}`);
  }
}, [error, isConnected]);
```

### Implementation Rules:
1. **Frontend Widgets**: If WebSocket/API fails, throw error or show error UI
2. **Backend Endpoints**: Return 500 with error details, never return mock data
3. **Error Boundaries**: Use React Error Boundaries to catch and display errors gracefully
4. **Monitoring**: Log all errors for investigation
5. **User Communication**: Show clear error messages: "Unable to load data. Check backend logs."

### When Mock Data IS Acceptable:
- **Development seed scripts**: For initializing test databases
- **Unit tests**: For isolated component testing
- **Demos/presentations**: When explicitly showing UI with fake data
- **Never in production code paths**: Real systems must fail visibly

## Research Before Implementation

**CRITICAL: Conduct web research before implementing new features or fixing complex bugs.**

This follows the Agile "spike" methodology - a time-boxed research activity to reduce uncertainty before implementation. For AI coding assistants, research grounds the implementation in real-world documentation, preventing hallucinated solutions.

### When to Research (ALWAYS):
1. **New feature implementation** - Ensure you're using current best practices
2. **External API/library integration** - Verify API signatures and patterns exist
3. **Complex bug fixes** - Especially hallucination or edge case issues
4. **Security-related changes** - Critical to use verified, current practices
5. **Performance optimization** - Research proven patterns, not invented ones
6. **Architecture decisions** - Understand trade-offs from real implementations
7. **Dependency upgrades** - Check migration guides and breaking changes
8. **Adding or modifying LLM prompts** - Prompt engineering best practices evolve rapidly

### When Research is Optional:
- Simple typo fixes
- Documentation updates
- Code formatting changes
- Adding logs to existing code
- Small bug fixes in familiar code

### Time-Boxing Guidelines:
| Type | Duration | Use Cases |
|------|----------|-----------|
| Quick Lookup | 2-5 min | Verify package exists, check API signature |
| Standard Research | 5-15 min | New library, bug fix approach, prompt engineering |
| Deep Dive | 15-30 min | Architecture decisions, security, performance |
| Spike Story | 1-4 hours | Major technology adoption (requires ADR) |

### Source Trust Hierarchy:
1. **Official documentation** (high trust)
2. **GitHub official examples** (high trust)
3. **Vendor engineering blogs** - Anthropic, Google, Microsoft (medium-high)
4. **Reputable publications** - InfoQ, Martin Fowler (medium-high)
5. **Stack Overflow** - accepted, >10 votes (medium)
6. **Medium/Dev.to** - cross-reference required (low-medium)
7. **Random blog posts** - last resort (low)
8. **AI suggestions without sources** - always verify independently

### Research Query Templates by Domain:
```python
# Security
"{topic} OWASP 2025", "{library} security best practices"

# LLM/Prompts
"{task} prompt engineering 2025", "reducing hallucination {task} prompts"

# API Integration
"{api} official documentation", "{api} error handling patterns"

# Italian Real Estate Domain
"Italian real estate {topic} requirements", "GDPR-IT compliance {feature}"
```

### Verification Checklist (Post-Research):
- [ ] Package exists on PyPI/npm (`pip show` or `npm info`)
- [ ] Package actively maintained (check last commit)
- [ ] No security vulnerabilities (Snyk/GitHub advisories)
- [ ] License compatible with project
- [ ] API signature matches official docs
- [ ] Pattern is current (2024-2025)

### Research Output Template:
```markdown
### Research Summary: {topic}

**Sources Consulted:**
- [Official Docs](url) - Description
- [Best Practice Guide](url) - Description

**Key Findings:**
1. Finding one
2. Finding two
3. Finding three

**Decision:** What approach and why

**Alternatives Rejected:** What else was considered and why not
```

### Workflow Integration:
Research integrates with other patterns in sequence:
1. **RESEARCH_BEFORE_IMPLEMENTATION** - Gather knowledge
2. **MEASURE_TWICE_CUT_ONCE** - Mental simulation and critique
3. **Implementation** - Write code with confidence

### Why This Matters:
- **LLMs hallucinate packages**: Research shows 19.6% average package hallucination rate
- **APIs change**: 2023 documentation may be outdated in 2025
- **Prevent wasted time**: 15 min research saves hours debugging fabricated code
- **Better solutions**: Often a library already solves your problem
- **Audit trail**: Sources provide justification during code review

## Critical Project Organization Rules
- Avoid using emojis or images in messages as they may cause rendering issues

### Test File Placement
**NEVER place test files in the root or main directories.**

- ✅ **Correct**: `test_scripts/scripts/test/test_*.py` - System-level test scripts
- ✅ **Correct**: `tests/unit/test_*.py` - Unit tests
- ✅ **Correct**: `tests/integration/test_*.py` - Integration tests
- ✅ **Correct**: `tests/e2e/test_*.py` - End-to-end tests
- ❌ **WRONG**: `test_*.py` in root directory
- ❌ **WRONG**: `test_*.py` in api or infrastructure directory

### Test Script Naming Convention
Test scripts in `test_scripts/scripts/test/` must follow the pattern: `test_{target}_{qualifier}.py`

**Examples**:
- `test_chatbot_api.py` - Tests chatbot API endpoints
- `test_rag_retrieval.py` - Tests RAG retrieval functionality
- `test_whatsapp_integration.py` - Tests WhatsApp message handling
- `test_lead_qualification.py` - Tests lead scoring model

### Markdown File Naming Convention
Documentation files must follow the pattern: `{YYYY-MM-DD}_{descriptive-slug}.md`

**Rules**:
- Use ISO date format (YYYY-MM-DD) as prefix
- Use lowercase with hyphens for slug (no underscores)
- Be descriptive but concise
- No spaces in filenames

**Examples**:
- `2024-11-15_lead-qualification-architecture.md`
- `2024-10-20_avm-integration.md`
- `2024-09-05_whatsapp-twilio-integration.md`

**Anti-patterns** (avoid):
- `phase1_review.md` - No date, unclear purpose
- `IMPLEMENTATION_NOTES.md` - No date, ALL CAPS
- `stuff.md` - Non-descriptive
- `2024_11_15_notes.md` - Wrong date separator (use hyphens)

### Documentation Standards
**File Placement**:
- **Root Directory** (Essential Docs Only):
  - ✅ `README.md` - Project overview and links
  - ✅ `ARCHITECTURE.md` - System architecture
  - ✅ `GETTING_STARTED.md` - Quick start guide
  - ✅ `DEVELOPMENT.md` - Development workflows
  - ✅ `DEPLOYMENT.md` - Deployment guide
  - ✅ `STATUS.md` - Current status and roadmap
  - ✅ `Claude.md` - This file (coding standards)
  - ❌ **NO other MD files in root**

- **docs/ Directory Structure**:
  ```
  docs/
  ├── reference/                 # Living documentation
  │   ├── architecture/          # Analyses, models, classifications
  │   ├── operations/            # Runbooks, deployment SOPs
  │   └── integrations/          # Provider/API integration notes
  │       └── api/               # External/public API references
  ├── guides/                    # How-to guides and tutorials
  ├── reports/                   # Generated outputs
  │   ├── tests/                 # Test results (+ artifacts/)
  │   ├── audits/                # Code reviews, debugging reports
  │   └── sessions/              # Session summaries & transcripts
  ├── roadmap/                   # Future work, TODOs, epic plans
  └── archive/                   # Historical documentation only
      ├── phases/                # Phase deliverables
      ├── refactors/             # Completed migrations/refactors
      └── lessons/               # Lessons-learned write-ups
  ```

**Documentation Manifest**:
- `docs/doc_manifest.json` is the canonical source that maps `doc_type` to the correct directory, filename template, and naming rules.
- Every Markdown file MUST match one of the manifest entries. If the required `doc_type` does not exist you must extend the manifest first.
- Always create docs via the helper script (`python scripts/docs/create_doc.py --type <doc_type> --title "..."`) so filenames and directories are enforced automatically.
- Snapshot of the manifest:
  ```
  root_docs.allowed = [README.md, CONTRIBUTING.md, DEPLOYMENT.md, Claude.md]

  doc_types:
    reference_architecture      -> docs/reference/architecture/{slug}.md
    reference_operations        -> docs/reference/operations/{slug}.md
    reference_operations_team   -> docs/reference/operations/{team}/{slug}.md
    reference_integrations      -> docs/reference/integrations/{slug}.md
    reference_integrations_api  -> docs/reference/integrations/api/{slug}.md
    guides                      -> docs/guides/{slug}.md
    roadmap                     -> docs/roadmap/{slug}.md
    report_test                 -> docs/reports/tests/{date}_{slug}.md
    report_test_artifact        -> docs/reports/tests/artifacts/{slug}.md
    report_audit                -> docs/reports/audits/{date}_{slug}.md
    report_session              -> docs/reports/sessions/{date}_{slug}.md
    archive_phase               -> docs/archive/phases/{phase_id}_{slug}.md
    archive_refactor            -> docs/archive/refactors/{slug}.md
    archive_lessons             -> docs/archive/lessons/{slug}.md
  ```
- New Markdown paths outside `docs/` or outside these templates are rejected.

**Documentation Management**:
- **Consolidation**: Avoid creating endless MD files - combine related documents
- **Updates**: Modify existing docs rather than creating new ones
- **Archiving**: Move superseded docs to `docs/archive/`
- **Cleanup**: Delete truly obsolete docs to prevent accumulation
- **Review**: Peer review all documentation changes
- **Validation**: Test all code examples and commands
- **Accessibility**: Ensure documentation is searchable and well-organized

**Documentation Creation**:
1. **Essential and current?** → Root directory (only eight allowed files)
2. **Reference or runbook?** → `docs/reference/architecture|operations|integrations`
3. **Guide or tutorial?** → `docs/guides/`
4. **Tests/audits/session output?** → `docs/reports/(tests|audits|sessions)`
5. **Future work?** → `docs/roadmap/`
6. **Historical/completed work?** → `docs/archive/(phases|refactors|lessons)`
7. **Default**: No Markdown outside these directories. Update the manifest first if you need a new category.

## Rules
1) Title and Purpose
   - State that this file governs code generation standards and behaviors.
   - Emphasize SOLID, composition, DI, tests, observability, CI, and reproducible builds.

2) Operating Mode
   - Address senior engineers. Be explicit, terse, precise.

3) Non-negotiables (Architecture Principles)
   **Core Principles** (enforce strictly):
   - SOLID principles in all new code
   - Composition over inheritance - use dependency injection
   - Small modules - one responsibility per file
   - Explicit interfaces - define ports for all external dependencies
   - Dependency Injection - all dependencies injected at composition root
   - Hermetic unit tests - no external dependencies in unit tests
   - Structured logs with context fields (request_id, correlation_id, user_id)
   - Basic metrics (counters, latency histograms, error rates)
   - Typed errors with causes and remediation hints
   - Twelve-Factor config - all config from environment
   - Reproducible builds with locked dependencies
   - Documented decisions using ADR (Architecture Decision Records)

   **Design Constraints** (never violate):
   - **Avoid global singletons** - Use dependency injection instead (except at composition root in main.py/container.py)
   - **No magic constants** - use configuration files, database, or environment variables
   - **Side effects at edges only** - Keep domain layer pure with no I/O, handle I/O in infrastructure layer
   - **Explicit types and schemas** - use type hints, Pydantic models, strict validation
   - **Fail fast on config errors** - validate all configuration at startup, crash immediately if invalid
   - **Avoid hardcoded decision lists** - Use AI agents with reasoning capabilities instead of keyword/pattern matching
   - **Plugin/registry pattern** - use dynamic registration for extensibility, not hardcoded instantiation
   - **No duplicate classes** - Each entity/model must have ONE canonical definition; delete old versions immediately

   **Debugging Practices**:
   - Always check log files to find bugs when evaluating code
   - Trace through initialization code to find parameter mismatches
   - Verify foreign key types match between tables
   - Check for race conditions in singleton initialization

   **Refactoring & Code Cleanup Practices**:
   - **No backwards compatibility during major refactoring** - Backwards compatibility code adds complexity and creates technical debt; delete legacy code completely during major refactors instead of maintaining parallel implementations
   - **Delete old code immediately after refactoring** - When migrating to new implementations, delete old versions immediately
   - **One canonical definition per class** - Each entity/model must have exactly ONE authoritative definition
   - **Check for usage before deletion** - Use import analysis to verify files are unused before deletion
   - **Create backups during major refactoring** - Back up deleted files temporarily during cleanup
   - **Update all imports** - When moving/refactoring classes, update ALL import statements project-wide
   - **Test after cleanup** - Run full test suite after deleting old code to verify nothing broke
   - **Plan migrations deliberately**:
     - Conduct a codebase + schema review BEFORE implementation to identify reusable components, integration points, and schema gaps.
     - Decide **extend vs rewrite** by evaluating structure, tests, change scope, regression risk, and time; default to extending when the existing module is healthy.
     - Break major refactors into atomic phases with clear checkpoints; make the target implementation feature-complete before migrating callers.
     - Verify tooling up front (pytest, linters) and layer validation (syntax, unit, integration, import sweeps) after every phase.
     - Leave breadcrumbs in deprecated modules (docstring or log note) pointing to the canonical implementation until all consumers move.



4) Decision Gates and Template
   - Stop and request approval when touching: new frameworks, datastores, queues, cloud services, public API shapes, new env vars, build toolchains, logging/testing stacks, third-party licenses, data models/migrations, or performance/cost-impacting patterns.
   - Decision Request template (mandatory):
     1. **Context** — What problem are we solving?
     2. **Options A/B/C** — Each with pros, cons, estimated effort.
     3. **Recommendation** — Choose one option with rationale plus fallback.
     4. **Blocking Questions** — Explicit unknowns that need input.
   - After submitting the template, PAUSE until the user approves. No workarounds, no silent deviations.

5) Output Contract for every deliverable
   - Header fields: S (summary), D (decisions), R (risks and mitigations), N (next steps with exact commands or files), T (tests and how to run).

6) File Naming and Layout
   **Naming Rules**:
   - lowercase, hyphenated or snake_case filenames
   - One module per responsibility (Single Responsibility Principle)
   - Descriptive names: `user_repository.py` not `repo.py`

   **Hexagonal Architecture Layout** (Ports & Adapters):
   ```
   project/
   ├── apps/                      # Frontend Monorepo
   │   ├── dashboard/            # React Admin Dashboard
   │   │   ├── src/
   │   │   │   ├── features/     # Feature-based texture
   │   │   │   ├── components/   # Shared components
   │   │   │   └── lib/          # Utilities
   │   ├── landing-page/         # Marketing Landing Page
   │   └── fifi/                 # Fifi Appraisal Tool
   ├── domain/                    # Core business logic (innermost layer)
   │   ├── entities/             # Business entities with identity
   │   ├── value_objects/        # Immutable values
   │   ├── services/             # Domain services (pure business rules)
   │   ├── ports.py              # Abstract interfaces (dependency inversion)
   │   └── events/               # Domain events
   ├── application/               # Use cases (orchestration layer)
   │   ├── use_cases/            # Application-specific business flows
   │   └── services/             # Application services (cross-cutting concerns)
   ├── infrastructure/            # Adapters (outermost layer)
   │   ├── adapters/             # Concrete implementations of ports
   │   │   ├── mistral_adapter.py
   │   │   ├── perplexity_adapter.py
   │   │   ├── meta_whatsapp_adapter.py
   │   │   └── supabase_adapter.py
   │   ├── logging.py
   │   └── monitoring/
   ├── api/                       # HTTP endpoints (FastAPI)
   │   ├── routes/
   │   └── dependencies.py
   ├── config/                    # Configuration
   │   ├── container.py          # Dependency injection container (composition root)
   │   └── settings.py           # Application settings
   ├── tests/
   │   ├── unit/                 # Fast, isolated tests
   │   ├── integration/          # Tests with external dependencies
   │   └── e2e/                  # End-to-end tests
   ├── docs/                     # See Documentation Standards section for layout
   ├── scripts/                   # Operational scripts
   └── test_scripts/             # System-level test scripts
   ```

   **Layer Rules** (enforce strictly):
   - Domain layer: No dependencies on outer layers, no I/O, pure business logic
   - Application layer: Depends on domain ports, orchestrates use cases
   - Infrastructure layer: Implements domain ports, handles I/O
   - Presentation layer: Depends on application layer, handles HTTP/UI concerns
   - Dependencies flow inward: Presentation → Application → Domain ← Infrastructure

   **Project-specific**:
   - Tests: `test_scripts/` (system-level) or `tests/` (unit/integration), NOT in root
   - Docs: `docs/` subdirectories, NOT in root (max 8 essential MD files in root)

   **Script Naming Standards**:
   Scripts in `scripts/` and `test_scripts/` must follow the pattern: `{action}_{target}_{qualifier}.py`

   *Actions* (verb first):
   - `migrate_` - Data migration/transformation
   - `ingest_` - Import new data
   - `sync_` - Synchronize between systems
   - `validate_` - Check/verify data
   - `cleanup_` - Remove/archive data
   - `backup_` - Create backups
   - `test_` - Test scripts
   - `check_` - Health/status checks

   *Targets* (what it operates on):
   - `_properties_` - Property listings
   - `_leads_` - Lead data
   - `_weaviate_` - Vector database
   - `_postgres_` - PostgreSQL database
   - `_embeddings_` - Embedding vectors

   *Qualifiers* (optional specifics):
   - `_768d` - 768-dimension embeddings
   - `_gemini` - Gemini provider
   - `_kanon` - Kanon/Isaacus provider

   *Examples*:
   - `migrate_legal_authorities_768d.py`
   - `sync_cases_to_weaviate.py`
   - `validate_embeddings_dimensions.py`
   - `cleanup_weaviate_orphans.py`
   - `ingest_legislation_govuk.py`

   *Anti-patterns* (avoid):
   - `batch_migrate_768d.py` - Unclear target
   - `run_migration.py` - Too generic
   - `script1.py` - Meaningless
   - `fix_stuff.py` - Not descriptive

7) SOLID Enforcement Checklist
   For every class/module, verify:

   **S - Single Responsibility Principle**:
   - ✓ Does this class have only ONE reason to change?
   - ✓ Can you describe the class purpose in one sentence without "and" or "or"?
   - ❌ Red flags: Classes named "Manager", "Helper", "Util" often violate SRP

   **O - Open/Closed Principle**:
   - ✓ Can behavior be extended without modifying existing code?
   - ✓ Are extension points defined (interfaces, abstract classes, plugins)?
   - ❌ Red flags: Feature flags switching between implementations, hardcoded lists of implementations

   **L - Liskov Substitution Principle**:
   - ✓ Can subclasses be used interchangeably with parent classes?
   - ✓ Do subclasses honor parent class contracts?
   - ❌ Red flags: Subclasses throwing NotImplementedError, subclasses weakening preconditions

   **I - Interface Segregation Principle**:
   - ✓ Are interfaces focused and cohesive?
   - ✓ Do clients depend only on methods they use?
   - ❌ Red flags: "God interfaces" with 10+ methods, clients forced to implement unused methods

   **D - Dependency Inversion Principle**:
   - ✓ Do high-level modules depend on abstractions (interfaces), not concrete implementations?
   - ✓ Are all external dependencies (databases, LLMs, APIs) behind interfaces?
   - ✓ Is dependency injection used at composition root?
   - ❌ Red flags: Direct imports of concrete infrastructure classes in domain/application layers

8) Coding Standards
   - Deterministic builds and committed lock files, lint and format configs, no magic constants, side effects at edges, explicit types and schemas, fail fast on config errors.

8a) Python Tooling Standards
   **Required Tools**:
   - **Formatting**: `ruff format` (configured in `pyproject.toml`)
   - **Linting**: `ruff check .` with strict ruleset
   - **Type Checking**: `mypy --strict` (or near-strict configuration)
   - **Testing**: `pytest` with coverage reporting (`pytest-cov`)
   - **Security**: `bandit` for security issues, `pip-audit` for vulnerable dependencies
   - **Pre-commit hooks**: Enforce formatting, linting, type checks before commit
   - **Lock files**: Use `pip-tools` (`pip-compile`) or `uv` for reproducible builds

   **Configuration Example** (`pyproject.toml`):
   ```toml
   [tool.ruff]
   line-length = 100
   target-version = "py311"

   [tool.ruff.lint]
   select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "DTZ", "T10", "EM", "ISC", "ICN", "PIE", "PT", "Q", "RET", "SIM", "TID", "ARG", "PLE", "PLR", "PLW", "RUF"]
   ignore = ["E501"]  # Line length handled by formatter

   [tool.mypy]
   strict = true
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = true

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = "test_*.py"
   addopts = "--cov=backend --cov-report=term-missing --cov-report=xml"
   ```

   **One-Command Testing**:
   ```bash
   # Run all checks
   make test  # or: pytest && ruff check . && mypy backend
   ```

8b) Pre-Implementation Reconnaissance & Mock Validation
   - **Review before building**: Perform a focused codebase + schema review before writing a line of implementation. Identify reusable modules, stale columns, middleware ordering, and integration points so the plan extends what exists instead of recreating it.
   - **Integration map**: Document upstream/downstream dependencies, required data flow, and any systems to avoid (e.g., unreliable buses) before coding.
   - **Quick mocks**: Write 5–10 minute mock scripts to surface concurrency issues (race-condition simulations) and validate performance targets (hashing benchmarks, query timing) before committing to an architecture decision.
   - **Tooling check**: Confirm pytest, linters, and other validation tools resolve correctly in the environment before starting critical work; fix PATH/env gaps first.
   - **Middleware order**: Explicitly define and test middleware execution order. When logic is endpoint-specific, use helper functions instead of forcing it into global middleware.

8c) Migration & Feature Flag Execution
   - **Extend vs rewrite rubric**: Default to extending when existing code is structured, tested, and changes are additive. Rewrite only when the module is fundamentally broken.
   - **Feature-complete target first**: Make the destination implementation a superset before migrating any callers (extend-then-migrate). Use factory methods or properties to bridge API differences without breaking consumers.
   - **Atomic phases**: Break migrations into independently testable phases (extend, add adapters, migrate files one-per-commit, delete duplicate, add compatibility shims). Run syntax/unit/import verification after each phase.
   - **Granular commits**: When migrating many files, use one commit per file so regressions are traceable and selective rollbacks are trivial.
   - **Breadcrumbs**: Leave a docstring/log note in deprecated modules that points to the canonical location until the last consumer moves.
   - **Instrumentation**: During feature-flag rollouts, add `[LEGACY]` / `[NEW]` log markers and feature-flag decision logs so it is obvious which path executed. Remove markers once the migration is stable.
    - **Execution verification**: After wiring new logic, add temporary structured logs and enhance E2E tests to assert response fields (not just status codes) to prove the new path actually ran and no early `return` blocks it.

8e) Frontend Standards (React/Vite)
    **Tech Stack**:
    - **Framework**: React 19 + Vite
    - **Data Fetching**: TanStack Query (React Query) - **MANDATORY** for server state
    - **Styling**: Tailwind CSS + `clsx` + `tailwind-merge`
    - **Icons**: Lucide React
    - **Testing**: Vitest + React Testing Library
    - **State**: URL state (first) > Local state (`useState`) > Global state (Zustand/Context)

    **Core Rules**:
    - **No `useEffect` for data fetching**: ALways use `useQuery` or `useMutation`.
    - **No manual fetch**: Use the `supabase` client or custom typed API clients.
    - **Component Structure**:
      ```
      components/
      ├── ui/                # Generic, reusable UI components (Buttons, Inputs)
      ├── domain/            # Domain-specific components (LeadCard, PropertyGrid)
      └── layout/            # Layout components (Sidebar, Navbar)
      ```
    - **Error Handling**: Use Error Boundaries for UI crashes; `isError` state for queries.
    - **Tailwind**: Use utility classes. For complex conditionals, use `cn()` utility (`clsx` + `tailwind-merge`).
    - **Routing**: React Router DOM v7.
    - **Strict Types**: All props and API responses must be typed.

    **Example: Data Fetching**:
    ```typescript
    // ✅ GOOD: using useQuery
    const { data: leads, isLoading } = useQuery({
      queryKey: ['leads', filter],
      queryFn: () => getLeads(filter)
    });

    if (isLoading) return <Skeleton />;
    ```

8d) Data & Concurrency Patterns
   - **Domain state machines**: Encode business workflows as explicit domain methods that validate state transitions and raise when invalid (e.g., pending → claimed). Keep validation out of controllers.
   - **Database locking**: Use `SELECT FOR UPDATE` for concurrency-sensitive mutations (claiming reviews, dequeuing work) instead of optimistic application checks.
   - **Partial indexes**: For hot queries that always filter on a status/flag, create partial indexes (`WHERE status='pending'`) so indexes stay small and fast.
   - **Database-driven config**: Thresholds, confidence settings, and other business controls belong in tables + admin APIs, not constants. Every change must be audited and adjustable without redeploying.
   - **Classification logic**: When deriving behavior (e.g., review types) from metadata, document the priority order and rationale in code/docstrings so future changes are deliberate.

8e) Compliance & Observability Practices
   - **API-first compliance**: Build compliance features (audit log verification, human review queues, stats) as first-class APIs so inspectors, automation, and dashboards can consume them directly.
   - **Fail-safe non-critical features**: Background safeguards (confidence gating, review triggers) must log errors and fall back gracefully instead of blocking user responses.
   - **Full-phase testing cadence**: Run the full E2E suite after **every** infrastructure change or implementation phase, not just at the end, and inspect logs to confirm new fields/flags are present.

8f) SQL & Migration Hygiene
   - **Dollar-quote parsing**: When executing SQL migrations, handle PostgreSQL dollar-quoted functions (`$$` or `$tag$`). Use stateful parsing/regex to avoid splitting statements incorrectly.
   - **Serialization symmetry**: Whenever you add or rename fields on domain entities, update both `to_dict()` and `from_dict()` paths in the same commit and bump the semantic version maintained on the entity.

9) Errors, Logging, Observability
   - **ALWAYS use detailed logging** - Never truncate error messages
   - Every exception handler MUST log:
     - Exception type: `type(e).__name__`
     - Full error message: `str(e)`
     - Complete traceback: `traceback.format_exc()`
   - Example pattern for structured exception handling:
     ```python
     except Exception as e:
         import traceback
         logger.error(
             "Error occurred",
             exc_info=e,
             extra={
                 "function": function_name,
                 "type": type(e).__name__,
                 "message": str(e),
                 "traceback": traceback.format_exc(),
                 "context": {
                     "request_id": request_id,
                     "user_id": user_id
                 }
             }
         )
     ```
   - Typed errors with causes and remediation
   - Single structured logger with context fields (request_id, correlation_id, user_id when applicable)
   - Minimal metrics (counters, latency histograms, error rates)
   - Tracing hooks or middleware stubs
   - **Never use generic error messages** like "Error occurred" - always include context

9a) Detailed Initialization and Event Logging
   **Core Principle**: Comprehensive logging at initialization and decision points accelerates debugging by 10x and prevents hours of guessing.

   **ALWAYS log when**:
   1. **Initialization**: Every agent, service, or component starts
   2. **Decision points**: Feature flags, routing decisions, conditional paths
   3. **Configuration loading**: Show what settings are being used
   4. **Workflow stages**: Entry/exit of major functions
   5. **State transitions**: Agent activations, mode changes, pathway routing

   **Logging Best Practices**:
   - **Use structured prefixes** for easy filtering:
     - `[FEATURE FLAG]` - Feature flag checks and values
     - `[WORKFLOW]` - LangGraph/workflow execution
     - `[ORCHESTRATOR]` - Orchestrator initialization and routing
     - `[AGENT INIT]` - Agent initialization and configuration
     - `[PATHWAY]` - Pathway triage and routing decisions
     - `[LEAD]` - Lead qualification and scoring events
     - `[LEGACY]` - Legacy code paths (for migration tracking)

   - **Include context in every log**:
     ```python
     # ❌ BAD: No context
     logger.info("Initialized")

     # ✅ GOOD: Full context
     logger.info(
         "[ORCHESTRATOR INIT] EnhancedMultiAgentOrchestrator initialized",
         extra={
             "workflow_type": type(workflow).__name__,
             "database_url": bool(database_url),
             "enable_checkpointing": enable_checkpointing,
             "user_id": user_id,
             "session_id": session_id
         }
     )
     ```

   - **Log feature flag decisions**:
     ```python
     # Show flag value AND decision made
     flag_value = is_feature_enabled("langgraph_workflow")
     logger.info(
         f"[FEATURE FLAG] langgraph_workflow={flag_value}, "
         f"using {'EnhancedMultiAgentOrchestrator' if flag_value else 'MultiAgentOrchestrator'}"
     )
     ```

   - **Log workflow progression**:
     ```python
     logger.info(f"[WORKFLOW] Entering lead_qualification node, message_length={len(message)}")
     result = await lead_qualification(state)
     logger.info(f"[WORKFLOW] Exiting lead_qualification, score={result.score}, took={elapsed}ms")
     ```

   - **Log configuration at startup**:
     ```python
     # Log critical settings when app starts
     logger.info(
         "[CONFIG] Application settings loaded",
         extra={
             "embedding_provider": settings.embedding.provider,
             "embedding_dimensions": settings.embedding.dimensions,
             "llm_provider": settings.llm.provider,
             "features_enabled": {
                 "langgraph_workflow": settings.features.langgraph_workflow,
                 "lead_qualification": settings.features.lead_qualification,
                 "rag": settings.features.rag
             }
         }
     )
     ```

   **Real-World Example** (from Phase 4 LangGraph debugging):
   - **Problem**: Feature flag `ENABLE_LANGGRAPH_WORKFLOW=True` not activating workflow
   - **Without detailed logging**: Hours of guessing, checking .env, restarting services
   - **With detailed logging**: Found root cause in 15 minutes by seeing:
     ```
     [FEATURE FLAG DEBUG] langgraph_workflow from settings: False
     [FEATURE FLAG DEBUG] is_feature_enabled('langgraph_workflow'): False
     [LEGACY] Factory returning MultiAgentOrchestrator (feature flag disabled)
     ```
   - Logs immediately showed flag reading as `False` despite `.env` having `True`, leading directly to Pydantic configuration bug

   **Debug Logging for Complex Integrations**:
   - Add temporary `[DEBUG]` logs when integrating new features
   - Log function entry with parameters
   - Log function exit with results
   - Log all decision branches taken
   - Remove or reduce verbosity after integration validated

   **Why This Matters**:
   - **Faster debugging**: See exactly what code executed and what values were used
   - **Easier troubleshooting**: Support can read logs to understand user issues
   - **Migration tracking**: `[LEGACY]` markers show when old code still executing
   - **Performance analysis**: Timing logs enable bottleneck identification
   - **Audit trail**: Know what happened when for compliance and security

10) Testing Requirements
    **General Testing Principles**:
    - Unit tests for public functions in domain and adapters
    - Integration tests with fakes or testcontainers where relevant
    - E2E smoke tests for golden paths
    - Deterministic seeds for randomized tests
    - Coverage targets with emphasis on domain layer (80%+ minimum)
    - One-command test execution: `make test` or `pytest`

    **🚨 CRITICAL: Verify Execution Path After Refactoring/Integration**:
    **Unit tests passing ≠ feature working.** After major refactoring or integration, you MUST verify the code actually executes:

    1. **Add Execution Logging**: Insert temporary debug logs at integration points
       ```python
       logger.debug(f"FEATURE_X: Entering new code path with params={...}")
       ```

    2. **Run E2E Test and Check Logs**: Verify debug logs appear in backend logs
       ```bash
       # Run test
       python test_scripts/test_feature.py

       # Check logs for execution proof
       grep "FEATURE_X" server_logs.txt
       ```

    3. **Validate Response Structure**: E2E tests must check new fields exist, not just status codes
       ```python
       # ❌ BAD: Only checks status
       assert response.status_code == 200

       # ✅ GOOD: Validates feature output
       assert response.status_code == 200
       data = response.json()
       assert "new_field" in data, "Feature not executing!"
       assert isinstance(data["new_field"], expected_type)
       ```

    4. **Check for Early Returns**: In large functions, verify no early `return` statements skip your code
       ```python
       # Search for all returns in modified file
       grep -n "return" api/endpoint.py
       # Verify your code executes before ALL returns
       ```

    5. **Verify Try/Except Placement**: Ensure new code is INSIDE try block, not after except
       ```python
       # ❌ BAD: Code never executes (outside try)
       try:
           existing_code()
       except Exception as e:
           handle_error()
       # Code here is OUTSIDE try block!
       new_feature_code()  # Never runs if exception thrown

       # ✅ GOOD: Code inside try block
       try:
           existing_code()
           new_feature_code()  # Executes correctly
       except Exception as e:
           handle_error()
       ```

    **Why This Matters**:
    - **Silent failures**: Feature appears implemented but doesn't work
    - **Unit tests give false confidence**: They test components in isolation
    - **E2E tests may be too permissive**: Status 200 doesn't mean feature executed
    - **Production risk**: Could ship non-functional feature

    **When to Apply** (every time):
    - After integrating new feature into existing endpoint
    - After major refactoring of large functions (>500 lines)
    - After moving code between layers (domain → service → API)
    - After adding middleware or interceptors
    - Before declaring feature "complete"

    **Test Placement**:
    - Backend unit tests: `tests/unit/`
    - Backend integration tests: `tests/integration/`
    - Backend e2e tests: `tests/e2e/`
    - System-level tests: `test_scripts/`
    - **NEVER** place tests in `application/` or `infrastructure/` directories

    **AI-Specific Testing**:

    *Unit Testing*:
    - Test prompt templates for correct formatting and structure
    - Validate model input/output schemas with Pydantic
    - Test fallback behaviors for model failures
    - Verify error handling for API rate limits and timeouts
    - Mock LLM responses for deterministic tests

    *Integration Testing*:
    - Test end-to-end AI workflows with mock models
    - Validate model response processing and parsing
    - Test caching and batching implementations
    - Verify error recovery and retry mechanisms

    *E2E Testing*:
    - Test complete AI system with real models (use test API keys)
    - Validate performance against SLAs (response time, token usage)
    - Test security controls (input validation, rate limiting)
    - Verify monitoring and alerting systems

    *Performance Testing*:
    - Measure response times under load (p50, p90, p99)
    - Test model scaling and batching efficiency
    - Validate token usage optimization
    - Monitor for model drift and degradation

    *Security Testing*:
    - Test for prompt injection vulnerabilities
    - Validate input sanitization against adversarial inputs
    - Test rate limiting and abuse detection
    - Verify audit logging and PII redaction

    *Test Automation*:
    - Automate regression testing for prompt changes
    - Implement continuous testing for model updates
    - Include all tests in CI/CD pipelines
    - Maintain versioned test datasets with edge cases
    - Anonymize sensitive test data (GDPR compliance)

11) Configuration and Secrets
    **Configuration Management**:
    - Use Pydantic Settings for type-safe configuration
    - Load from environment variables via `.env` file
    - Provide `.env.example` with all required variables (no values)
    - Fail fast at startup if configuration invalid
    - Never commit `.env` to version control (add to `.gitignore`)
    - Use different configs per environment (dev/staging/prod)

    **Secret Management**:
    - Abstract secrets behind interfaces (SecretProvider port)
    - Use secret managers in production (AWS Secrets Manager, Azure Key Vault, etc.)
    - Never hardcode API keys, passwords, tokens in code
    - Rotate secrets regularly (90-day maximum)
    - Use different secrets per environment
    - Never log secrets or PII

    **Example Configuration**:
    ```python
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        # Required settings (no defaults)
        database_url: str
        openai_api_key: str
        anthropic_api_key: str

        # Optional settings (with defaults)
        redis_url: str = "redis://localhost:6379"
        log_level: str = "INFO"
        max_token_limit: int = 4000

        class Config:
            env_file = ".env"
            case_sensitive = False

    # Validate at startup (fails fast if misconfigured)
    settings = Settings()  # Raises ValidationError if required vars missing
    ```

11a) Security Requirements
    **Input Validation** (OWASP Top 10):
    - ✓ Sanitize all user input with Pydantic models
    - ✓ Use parameterized queries (SQLAlchemy ORM, no raw SQL)
    - ✓ Escape output in templates (Jinja auto-escaping enabled)
    - ✓ Validate file uploads (type, size, content scanning)
    - ✓ Implement request size limits

    **Authentication & Authorization**:
    - ✓ Never log passwords, tokens, API keys, or PII
    - ✓ Use bcrypt or argon2 for password hashing (min 10 rounds)
    - ✓ Implement rate limiting on auth endpoints (5 attempts/minute)
    - ✓ Check authorization before data access (RBAC)
    - ✓ Use short-lived JWTs with refresh tokens

    **Data Protection** (GDPR/Legal Requirements):
    - ✓ Encrypt sensitive data at rest (database encryption)
    - ✓ Use HTTPS/TLS 1.3+ for all external communication
    - ✓ Anonymize PII in logs and error messages
    - ✓ Implement data retention policies (automatic deletion)
    - ✓ Provide data export/deletion APIs (GDPR right to erasure)
    - ✓ Audit all access to sensitive legal documents
    - ✓ Store case data with encryption at rest

    **Prompt Injection Protection** (AI-specific):
    - ✓ Validate and sanitize prompts before LLM calls
    - ✓ Use structured prompt templates, not raw user input
    - ✓ Implement content filtering on model outputs
    - ✓ Rate limit LLM API calls per user/session
    - ✓ Monitor for adversarial inputs and prompt leakage

    **Security Scanning & Compliance**:
    - ✓ Run `bandit` for Python security issues in CI
    - ✓ Run `pip-audit` for vulnerable dependencies weekly
    - ✓ Scan for committed secrets (`git-secrets`, `trufflehog`)
    - ✓ Include security tests in CI/CD pipeline
    - ✓ Conduct quarterly security audits
    - ✓ Maintain security incident response plan

11b) RAG & Embedding Standards (1024D MISTRAL STANDARD)
    **CRITICAL: All embeddings MUST use 1024 dimensions (Mistral standard)**

    **Why 1024d Mistral Standard**:
    - Mistral `mistral-embed` native output: 1024 dimensions
    - Supabase pgvector configured for 1024d
    - Single collection strategy: No multi-dimensional complexity
    - Cost-effective: Mistral embeddings are economical for high-volume usage

    **Enforced Rules**:
    - ✓ **ALWAYS use Mistral for embeddings** - Primary and only provider
    - ✓ **ALWAYS use** Supabase pgvector for vector storage
    - ✓ **NEVER create** separate collections for different providers
    - ✓ Mistral: Primary provider (native 1024d, via `mistralai` SDK)

    **Implementation Example**:
    ```python
    # infrastructure/adapters/mistral_adapter.py
    from mistralai import Mistral

    async def get_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create_async(
            model=settings.MISTRAL_EMBEDDING_MODEL,  # mistral-embed
            inputs=[text]
        )
        return response.data[0].embedding  # 1024-dim vector
    ```

    **Configuration Validation**:
    - Verify `.env` has `MISTRAL_EMBEDDING_MODEL=mistral-embed`
    - Verify Supabase table has `embedding vector(1024)` column type
    - Verify no conflicting embedding providers configured

    **Why This Matters**:
    - Prevents architecture fragmentation
    - Consistent with LLM provider (Mistral for both chat and embeddings)
    - Reduces integration complexity (single AI provider)
    - Simplifies query logic (single collection, single dimension)

    All embedding operations use Mistral exclusively. Do not introduce additional embedding providers without ADR approval.

11c) Real-Time Research Standards (Perplexity)
    **Purpose**: providing up-to-date facts where LLMs hallucinate (laws, market prices).

    **When to use Perplexity (`sonar-pro`)**:
    - **Legal Compliance**: Checking recent Gazzetta Ufficiale or EU AI Act updates
    - **Market Analysis**: Finding active listings for comparative analysis
    - **Fact Verification**: Validating claims about entities/companies

    **Implementation**:
    - Use `PerplexityAdapter` via `ResearchPort`.
    - Always provide a `context` to ground the research (e.g., "You are an expert Italian real estate lawyer").
    - Cache results where possible (market comps) but not for breaking news.
    - **NEVER** use Perplexity for generic chat; use Mistral for that.


12) Performance and Reliability
    **Performance Requirements**:
    - Define measurable targets: latency p95 (e.g., <3s), memory limits, QPS thresholds, error rate budgets
    - Establish baselines: measure current performance before optimization
    - Monitor continuously: track metrics against targets

    **Performance Patterns**:
    - Avoid N+1 queries: use eager loading, batch queries, or caching
    - Batch or stream appropriately: don't load entire datasets into memory
    - Use async for I/O: don't block event loops with synchronous calls
    - Cache strategically: use Redis/in-memory caching for hot paths
    - Implement connection pooling: for databases, external APIs

    **Async/Concurrency Patterns** (Python):
    - ✓ Use `async def` for I/O-bound operations (DB, HTTP, LLM calls)
    - ✓ Use `asyncio.gather()` for concurrent independent operations
    - ✓ Never use `time.sleep()` in async code → use `asyncio.sleep()`
    - ✓ Use async context managers: `async with`
    - ✓ Don't mix sync/async incorrectly (causes blocking)
    - ❌ Don't use `requests` in async code → use `httpx` or `aiohttp`

    **Database Transaction Patterns**:
    ```python
    # Good: Async session with proper transaction handling
    async with db.session() as session:
        async with session.begin():
            await repo.update(entity)
            await event_bus.publish(event)
        # Auto-commit on success, rollback on exception

    # Good: Explicit transaction boundaries
    async def transfer_funds(from_id, to_id, amount):
        async with db.transaction() as tx:
            await accounts.debit(from_id, amount)
            await accounts.credit(to_id, amount)
            # Commits atomically
    ```

    **AI-Specific Performance**:
    - Monitor model response times (p50, p90, p99)
    - Track token usage and efficiency (cost optimization)
    - Implement caching for frequent or expensive LLM calls
    - Use streaming responses for long-form generation
    - Batch multiple requests when possible
    - Monitor API call success rates and retry patterns
    - Track model accuracy and drift over time
    - Set up alerts for performance degradation
    - Monitor resource utilization (CPU, memory, GPU if applicable)

    **Reliability Patterns**:
    - **Circuit breakers**: prevent cascading failures from external dependencies
      - Open circuit after N consecutive failures
      - Half-open state for testing recovery
      - Close circuit after M successful calls
    - **Retries with exponential backoff**: transient failure handling
      - Use jitter to prevent thundering herd
      - Set maximum retry limits
    - **Graceful shutdown**: handle SIGTERM, finish in-flight requests
    - **Health checks**: `/health` endpoint checks database, cache, critical dependencies
    - **Timeouts**: set explicit timeouts for all external calls (LLMs, databases, APIs)

    **Resilience Checklist**:
    - ✓ All external calls have timeouts?
    - ✓ Retries implemented with backoff?
    - ✓ Circuit breakers on critical paths?
    - ✓ Fallback behavior defined for failures?
    - ✓ Health checks monitor dependencies?

13) Git and Pull Request Standards
    **Commit Messages** (Conventional Commits):
    - Format: `type(scope): description`
    - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`, `style`
    - Examples:
      - `feat(api): add user profile endpoint`
      - `fix(domain): correct calculation in settlement analysis`
      - `docs(readme): update deployment instructions`
      - `test(agents): add unit tests for trigger analysis`

    **Pull Request Requirements**:
    - Keep PRs small and focused (<400 lines when possible)
    - Include tests for all new features and bug fixes
    - Update relevant documentation (code comments, README, docs/)
    - Pass all CI checks (lint, type, test, security)
    - Require at least one approval before merge
    - No force-push to main or after review starts
    - Link to related issues/tickets

    **Branch Strategy**:
    - `main`: production-ready code, protected branch
    - `feature/*`: new features
    - `fix/*`: bug fixes
    - `docs/*`: documentation only
    - `refactor/*`: code refactoring
    - Delete branches after merge

14) Deployment and CI
    - Minimal CI steps: install deps, lint and format check, build, test, package artifact.
    - Container recipe guidance: non-root user, read-only filesystem when possible.
    - Runbook: env vars, ports, datastores, migrations, first-run steps.

15) Documentation Standards
    - Follow the centralized rules in the **Documentation Standards** section above (`docs/` tree, manifest, creation workflow, and templates).
    - This section is intentionally lean to avoid conflicting guidance—when in doubt, read that canonical section and keep docs within the manifest.

16) When Requirements Are Ambiguous
    - Follow the Decision Request process defined in Section 4 verbatim; do not continue coding until approval is granted.

17) Self-Review Checklist
    **Architecture Compliance**:
    - ✓ Structure conforms to hexagonal architecture layout?
    - ✓ Domain layer has no dependencies on outer layers?
    - ✓ All infrastructure dependencies behind ports (interfaces)?
    - ✓ Dependency injection used at composition root?
    - ✓ No global singletons except at composition root (main.py/container.py)?
    - ✓ No magic constants - all configuration externalized?
    - ✓ No hardcoded lists for decisions - using AI agents instead?
    - ✓ Plugin/registry pattern used for extensibility?

    **SOLID Compliance**:
    - ✓ Review the SOLID Enforcement Checklist (Section 7) and ensure every point is satisfied before submitting.

    **Testing & Quality**:
    - ✓ Tests run with one command (make test or pytest)?
    - ✓ Unit tests are hermetic (no external dependencies)?
    - ✓ Integration tests use testcontainers or fakes?
    - ✓ Coverage targets met (especially domain layer)?

    **Observability**:
    - ✓ Logging and error paths present with full context?
    - ✓ All exceptions logged with type, message, and traceback?
    - ✓ Structured logging with correlation IDs?
    - ✓ Metrics collection implemented (counters, histograms)?
    - ✓ Health checks for critical dependencies?

    **Performance & Reliability**:
    - ✓ Performance targets defined and measured?
    - ✓ Circuit breakers on external dependencies?
    - ✓ Retries with backoff for transient failures?
    - ✓ Timeouts on all external calls?
    - ✓ No blocking calls in async code paths?

    **File Placement**:
    - ✓ Tests comply with the **Test File Placement** section (only `test_scripts/` or `tests/`)?
    - ✓ Documentation follows the manifest-driven **Documentation Standards** (only eight files in root)?
    - ✓ Historical docs in `docs/archive/`?
    - ✓ No test files in root or backend directories?
    - ✓ No stale/duplicate docs in root?

    **Documentation**:
    - ✓ README covers: build, test, run, deploy?
    - ✓ CI and run commands are runnable?
    - ✓ Architecture documented (layers, dependencies)?
    - ✓ ADRs (Architecture Decision Records) for major decisions?

19) Agents and AI-Driven Decision Making
    **Core Principle**: Agents should use AI reasoning, not hardcoded rules

    **Agent Design Rules**:
    - ✓ Use LLM reasoning for decisions, not if/else chains or keyword matching
    - ✓ Design agents to be model-agnostic: support OpenAI, Anthropic, Gemini, Grok, etc.
    - ✓ Use plugin/registry pattern for agent extensibility
    - ✓ Compose complex agents from simpler sub-agents (composition over inheritance)
    - ✓ Store agent configuration in database, not hardcoded in code
    - ❌ NEVER use hardcoded keyword lists for detection (cultural bias, false positives)
    - ❌ NEVER use rigid decision trees or state machines for conversational flow
    - ❌ NEVER hardcode form requirements, legal rules, or domain knowledge

    **Agent Architecture Pattern**:
    ```python
    # Good: Plugin-based agent registry with type safety
    class AgentRegistry:
        def __init__(self):
            self._agents: Dict[str, Agent] = {}

        def register_agent(self, name: str, agent: Agent) -> None:
            if not isinstance(agent, Agent):
                raise TypeError("Registered agent must be of type Agent")
            self._agents[name] = agent

        def get_agent(self, name: str) -> Agent:
            if name not in self._agents:
                raise KeyError(f"Agent {name} not found")
            return self._agents[name]

    # Good: AI-driven decision making with error handling
    async def make_decision(self, context: Dict) -> Decision:
        try:
            prompt = self._build_decision_prompt(context)
            decision = await self.llm.generate(prompt)
            return self._parse_decision(decision)
        except Exception as e:
            logger.error("Decision making failed", exc_info=e)
            return self._get_fallback_decision(context)

    # Bad: Hardcoded keyword matching (anti-pattern)
    def detect_issue(self, text: str) -> bool:
        keywords = ["abuse", "violence", "harm"]  # ❌ DON'T DO THIS
        return any(kw in text.lower() for kw in keywords)
    ```

    **Model Agnostic Design**:
    - Define abstract LLMProvider interface
    - Implement adapters for each provider (OpenAI, Anthropic, etc.)
    - Use dependency injection to swap providers
    - Store model selection in configuration, not code

    **Prompt Engineering Best Practices**:
    - Use structured templates with clear sections (system, user, examples)
    - Maintain version control for prompts (track changes, rationale)
    - Include fallback behaviors for unexpected model responses
    - Implement prompt testing and validation in CI/CD
    - Validate and sanitize prompts before LLM calls (prevent injection)
    - Use few-shot examples for consistent outputs
    - Document prompt design decisions and iteration history

    **Model Management**:
    - Use model-agnostic interfaces for all AI interactions
    - Implement version control for model configurations
    - Monitor model performance, accuracy, and drift
    - Maintain documentation of training data and parameters
    - Set up alerts for performance degradation
    - Plan for model updates and A/B testing

    **Error Handling for AI Operations**:
    - Implement fallback behaviors for model failures
    - Log all model interactions with request/response details
    - Implement retry logic with exponential backoff
    - Provide clear, actionable error messages to end users
    - Monitor API rate limits and quota usage
    - Handle timeout scenarios gracefully

    **AI Performance Optimization**:
    - Implement caching for frequent or expensive LLM calls
    - Use streaming responses for long-form generation
    - Batch multiple requests when possible
    - Monitor and optimize token usage (cost control)
    - Compress prompts without losing context
    - Use smaller models for simpler tasks

20) Architecture Decision Records (ADRs)
    **Purpose**: Document significant architectural decisions and their rationale

    **When to Create an ADR**:
    - Choosing between architectural patterns (hexagonal, microservices, etc.)
    - Selecting core technologies (frameworks, databases, LLM providers)
    - Major refactoring decisions
    - Trade-offs between competing design approaches

    **ADR Template**:
    ```markdown
    # ADR-NNN: [Title]

    **Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]
    **Date**: YYYY-MM-DD
    **Deciders**: [List of decision makers]

    ## Context
    [What is the issue we're addressing? What factors are we considering?]

    ## Decision
    [What decision did we make? Be specific and concrete.]

    ## Consequences
    **Positive**:
    - [List benefits and advantages]

    **Negative**:
    - [List drawbacks and trade-offs]

    **Risks**:
    - [List potential risks and mitigation strategies]

    ## Alternatives Considered
    **Option A**: [Description]
    - Pros: [...]
    - Cons: [...]

    **Option B**: [Description]
    - Pros: [...]
    - Cons: [...]

    ## Implementation Notes
    [Guidance for implementing this decision]
    ```

    **ADR Storage**: `docs/decisions/` directory

    **Example ADRs**:
    - ADR-001: Choice of Hexagonal Architecture
    - ADR-002: Model-Agnostic LLM Design
    - ADR-003: PostgreSQL over NoSQL for Primary Database
    - ADR-004: Plugin-Based Agent Registry Pattern

---

## Summary

This document establishes the coding standards for the Anzevino AI Real Estate Agent project. All contributors (human and AI) must follow these standards to ensure code quality, maintainability, security, and compliance with Italian data protection requirements.

**Key Principles**:
- SOLID architecture with hexagonal design
- Test-driven development with emphasis on domain coverage
- Security-first approach (GDPR-IT, OWASP, prompt injection protection)
- AI reasoning over hardcoded rules
- Fail fast on configuration errors
- Comprehensive logging and observability

**Quick Start**:
1. Review Quick Reference section for top rules
2. Follow Python Tooling Standards for setup
3. Use hexagonal architecture layout for new modules
4. Check Self-Review Checklist before submitting PRs
5. Create ADRs for significant architectural decisions

**Questions or clarifications**: Open an issue or contact the architecture team.
