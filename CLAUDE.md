# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Principles

### I. Frontend-Backend Separation

System architecture MUST maintain strict separation between frontend and backend:

- Frontend and backend MUST be developed as independent codebases
- Frontend MUST consume backend exclusively through well-defined RESTful APIs
- Backend MUST have no direct dependencies on frontend implementation
- Communication MUST occur only via network protocols (HTTP/HTTPS)
- No shared state between frontend and backend except via API contracts
- Frontend and backend MAY be deployed, versioned, and scaled independently

**Rationale**: Separation enables independent development, testing, deployment, and scaling of frontend and backend. It reduces coupling and allows technology flexibility for each layer.

### II. Responsive Web First

Frontend MUST be a responsive web application that adapts to all device sizes:

- Application MUST be web-based (HTML/CSS/JavaScript)
- UI MUST be responsive and adapt seamlessly to mobile, tablet, and desktop viewports
- Progressive enhancement approach: core functionality MUST work on all devices
- Touch interactions MUST be first-class citizens (not afterthoughts)
- Performance MUST be acceptable on mobile networks (3G+)
- Testing MUST include validation on multiple viewport sizes

**Rationale**: Users access educational tools from diverse devices. A responsive web approach ensures universal accessibility without platform-specific development overhead.

### IV. Code Quality Standards

All code MUST meet established quality thresholds:

- Code MUST pass static analysis (linting) before commit
- Code MUST follow language-specific best practices
- Functions MUST be small and single-purpose
- Complex logic MUST be extracted into well-named functions
- Code MUST be self-documenting with clear naming
- Comments ONLY for "why", never for "what"
- Maximum cyclomatic complexity MUST be enforced
- Code duplication MUST be minimized

**Rationale**: High-quality code is maintainable, readable, and less error-prone. Enforced standards prevent technical debt accumulation.

### V. Unified Code Style

Code style MUST be consistent across the entire codebase:

- Automated formatting MUST be configured (Prettier, Black, rustfmt, etc.)
- Style MUST be enforced via CI/CD gates
- No style debates - adopt language-community standards
- Format-on-save MUST be used by all developers
- Pre-commit hooks MUST validate style compliance
- Style configuration MUST be version-controlled

**Rationale**: Consistent style reduces cognitive load, minimizes merge conflicts, and eliminates subjective code review discussions about formatting.

## Architecture

### Project Structure

```text
.
├── backend/
│   ├── alembic/          # Database migrations
│   ├── src/
│   │   ├── api/          # API routes (auth, wrong_questions)
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   └── services/     # Business logic
│   └── tests/            # pytest tests
├── frontend/
│   ├── public/           # Static assets
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts
│   │   ├── hooks/        # Custom hooks
│   │   ├── lib/          # Utilities (api, swr, utils)
│   │   ├── styles/       # Global styles
│   │   └── types/        # TypeScript types
│   └── tests/            # Jest tests
├── docs/                 # Documentation
└── openspec/             # OpenSpec specifications
```

- `frontend/` - Next.js 16 with React 19, TypeScript, Tailwind CSS v4, shadcn/ui components
- `backend/` - FastAPI with SQLAlchemy 2.0 async, SQLite, JWT auth, Alembic migrations

### Frontend Tech Stack

- **Framework**: Next.js 16 (App Router)
- **UI Library**: React 19
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Data Fetching**: SWR
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form (via shadcn/ui)
- **Icons**: Lucide React
- **Testing**: Jest + React Testing Library
- **Linting**: ESLint

### Backend Tech Stack

- **Python**: 3.11+
- **Framework**: FastAPI 0.115+
- **Server**: Uvicorn
- **Database**: SQLite (async with aiosqlite)
- **ORM**: SQLAlchemy 2.0+ (async)
- **Migrations**: Alembic
- **Authentication**: JWT + Bcrypt (passlib)
- **Validation**: Pydantic 2.10+
- **Testing**: pytest + pytest-asyncio + httpx
- **Linting**: ruff
- **Type Checking**: mypy

## Quality Gates

- **Pre-commit**: Linting, formatting, type checking
- **Pre-push**: All tests must pass
- **Pre-merge**: Code review approval, test coverage threshold met
