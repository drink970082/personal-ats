# ATS — Application Tracking System

A personal job-application tracker. Built with Next.js 14 (App Router), Prisma, and SQLite.

The working app lives in [`ats-next/`](./ats-next). The shared SQLite database lives in [`db/applications.db`](./db) and is symlinked from `ats-next/prisma/applications.db`.

## Features

- Add, edit, and delete job applications
- Track status transitions over time (status history with timestamps)
- KPI cards: total applied, active, online assessment, interviewing, rejected, offer
- Charts: status-flow Sankey, timeline heatmap, status funnel, category donut
- Filter and search by status, historical status, category, company, or job title
- Paginated application table with inline status editing

## Stack

- **Framework**: Next.js 14 (App Router, Server Actions)
- **Database**: SQLite via Prisma 6
- **UI**: React 18, Tailwind CSS 4, Radix UI primitives (shadcn-style), Recharts
- **Forms**: react-hook-form + Zod
- **Tests**: Jest + Testing Library

## Getting started

```bash
cd ats-next
npm install
npx prisma generate
npm run dev
```

Open http://localhost:3000.

If `db/applications.db` does not exist yet, create it with:

```bash
npx prisma db push
```

## Scripts

Run from `ats-next/`:

| Command         | Description                       |
| --------------- | --------------------------------- |
| `npm run dev`   | Start the dev server              |
| `npm run build` | Production build                  |
| `npm start`     | Run the production build          |
| `npm run lint`  | ESLint                            |
| `npm test`      | Jest test suite                   |

## Docker

```bash
cd ats-next
docker build -t ats .
docker run -p 3000:3000 -v $(pwd)/../db:/app/db ats
```

The Dockerfile produces a standalone Next.js image. Mount the host `db/` directory so the SQLite file persists across container restarts.

## Project layout

```
ats/
├── db/
│   └── applications.db          # SQLite database (gitignored)
└── ats-next/
    ├── prisma/
    │   ├── schema.prisma        # applications + status_history models
    │   └── applications.db      # symlink → ../../db/applications.db
    ├── src/
    │   ├── app/                 # Next.js App Router entry
    │   ├── components/          # Dashboard, table, charts, forms
    │   │   └── ui/              # Radix-based primitives
    │   ├── lib/
    │   │   ├── actions.ts       # Server Actions (CRUD, aggregations)
    │   │   ├── db.ts            # Prisma client
    │   │   └── constants.ts     # statuses, categories
    │   └── __tests__/           # Jest tests
    └── Dockerfile
```

## Data model

```prisma
model applications {
  id              Int
  company_name    String
  job_title       String
  application_url String?
  date_applied    String
  category        String?
  status          String
  notes           String?
  last_updated    String?
  status_history  status_history[]
}

model status_history {
  id             Int
  application_id Int
  status         String
  timestamp      String
}
```

Deleting an application cascades to its status history.
