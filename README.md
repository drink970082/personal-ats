# ATS — Application Tracking System

A self-hosted job-application tracker built with **Next.js 14**, **Prisma**, and **SQLite**. Keep every application, every status transition, and every interview round in one place — then look at it visually instead of scrolling a spreadsheet.

<p align="center">
  <img src="docs/images/dashboard.png" alt="Full dashboard view" width="900">
</p>

The working app lives in [`ats-next/`](./ats-next). The SQLite database lives in [`db/applications.db`](./db) and is symlinked from `ats-next/prisma/applications.db` so it can be bind-mounted by the container.

---

## Why

Job hunting generates a lot of state per application: which company, which role, when applied, current status, how many interview rounds, when it stalled, what category (SWE / MLE / DS / Quant / etc.). A spreadsheet handles the first two columns fine but falls over once you want to ask "what's my offer rate by category?" or "where do most of my applications die?" This app is the spreadsheet plus the answers.

---

## Features

### Header KPIs + searchable, paginated table

<p align="center">
  <img src="docs/images/kpi-and-table.png" alt="KPI strip and applications table" width="900">
</p>

- **Status KPIs** across the top: Applied / Active / Online Assessment / Interviewing / Rejected / Offer
- **Inline status editing** — change an application's status from the table dropdown; the previous status is recorded in history
- **Filters**: by current status, by historical status (find apps that ever reached "Final Round"), by category, plus free-text search over company and job title
- **CSV import / export** — round-trip data with one click
- **Edit URL, date, notes** in place; the URL becomes a click-through link

### Activity heatmap + category donut

<p align="center">
  <img src="docs/images/charts-row.png" alt="Application timeline heatmap and category donut" width="900">
</p>

- **Application Timeline** — GitHub-contributions-style heatmap over the last 365 days. Each cell is a day; colour intensity scales with number of applications submitted. Hover for an exact count.
- **Categories** — donut showing the mix across SWE, MLE, DS, DA, Quant Dev/Analyst/Trader, AI Engineer, Others.

### Status funnel

<p align="center">
  <img src="docs/images/status-funnel.png" alt="Status funnel bar chart" width="900">
</p>

Linear breakdown of how the 850 applications fanned out across the funnel — every stage shows raw count and percentage so you can see conversion at a glance.

### Status flow (Sankey)

<p align="center">
  <img src="docs/images/sankey.png" alt="Status flow Sankey diagram" width="900">
</p>

Reconstructs the actual transitions per application from the `status_history` table and draws them as a Sankey. The palette is intentionally muted (slate / sky / indigo / amber / gold / emerald / rose / stone, all desaturated) so the flow geometry leads, not the colour.

### Per-application history modal

Click the clock icon on any row to open a modal showing every status this application has been in, with timestamps. From the modal you can edit application metadata, add a new status transition, or delete a past history entry.

### Mobile / responsive

<p align="center">
  <img src="docs/images/mobile.png" alt="Mobile layout" width="320">
</p>

Everything stacks vertically below ~640px. Table remains scrollable; charts shrink to fit.

---

## Stack

| Layer       | Choice                                                            |
| ----------- | ----------------------------------------------------------------- |
| Framework   | Next.js 14 (App Router, Server Actions, standalone output)        |
| Language    | TypeScript                                                        |
| Database    | SQLite via Prisma 6                                               |
| UI          | React 18, Tailwind CSS 4, Radix UI primitives (shadcn-style)      |
| Charts      | Recharts (donut) + hand-rolled SVG (heatmap, funnel, Sankey)      |
| Forms       | react-hook-form + Zod                                             |
| Tests       | Jest + Testing Library + jest-mock-extended                       |
| Container   | Alpine multi-stage build, runs as non-root with UID/GID arg       |

---

## Quick start

### Local dev

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

### Docker (recommended for "just run it")

The container does **not** ship with a database — the host's `db/applications.db` is bind-mounted so your data survives image rebuilds and lives where you can back it up.

```bash
cd ats-next
docker compose up --build -d
```

That starts the app on http://localhost:3000 with `../db/applications.db` mounted into the container.

Or without compose:

```bash
docker build \
  --build-arg UID=$(id -u) \
  --build-arg GID=$(id -g) \
  -t ats-next:local ats-next

docker run -d --name ats-next -p 3000:3000 \
  -v "$PWD/db/applications.db:/app/prisma/applications.db" \
  ats-next:local
```

The `UID`/`GID` build args make the container user own the bind-mounted SQLite file, so writes from inside the container work without `chmod 777`.

---

## Configuration

There are no environment variables to set for normal use. A few things to know:

- **Database path** — `prisma/schema.prisma` uses `file:./applications.db`, resolved relative to the schema directory. In the container that path is `/app/prisma/applications.db`; the bind mount lands the host file exactly there.
- **Time zone** — the heatmap uses the server's local "today" as its reference. If you deploy on a server in a different TZ from where you live, set `TZ` on the container.
- **Static / dynamic** — the root page is marked `export const dynamic = 'force-dynamic'` so it always reads from the live database; there is no stale-cache problem.

---

## Data model

```prisma
model applications {
  id              Int              @id @default(autoincrement())
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
  id             Int          @id @default(autoincrement())
  application_id Int
  status         String
  timestamp      String
  applications   applications @relation(fields: [application_id], references: [id], onDelete: Cascade)
}
```

Deleting an application cascades to its status history. Dates are stored as ISO strings (`YYYY-MM-DD`) for sortability and timezone-independence.

### Statuses (in funnel order)

`Applied` → `Online Assessment` → `Phone Screen` → `Interviewing: 1st…5th round` → `Final Round` → `Offer` → `Accepted`

Plus terminal states: `Rejected`, `Withdrew`, `Ghosted`.

### Categories

`SWE`, `MLE`, `DS`, `DA`, `Quant Dev`, `Quant Analyst`, `Quant Trader`, `AI Engineer`, `Others`.

Both lists live in [`src/lib/constants.ts`](./ats-next/src/lib/constants.ts) — edit there to extend.

---

## Project layout

```
ats/
├── db/
│   └── applications.db              # SQLite database (gitignored)
├── docs/
│   └── images/                      # README screenshots (tracked)
└── ats-next/
    ├── prisma/
    │   ├── schema.prisma            # applications + status_history models
    │   └── applications.db          # symlink → ../../db/applications.db
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx           # root layout + theme provider
    │   │   ├── page.tsx             # dashboard entry; SSR + force-dynamic
    │   │   └── globals.css
    │   ├── components/
    │   │   ├── Dashboard.tsx        # client-side state + handlers
    │   │   ├── KPIGrid.tsx          # status chip strip
    │   │   ├── ApplicationTable.tsx # filterable, paginated table
    │   │   ├── AddApplicationForm.tsx
    │   │   ├── StatusHistoryModal.tsx
    │   │   ├── TimelineHeatmap.tsx  # hand-rolled SVG
    │   │   ├── CategoryDonut.tsx    # recharts
    │   │   ├── StatusFunnel.tsx     # hand-rolled SVG
    │   │   ├── SankeyChart.tsx      # hand-rolled SVG
    │   │   ├── ThemeProvider.tsx
    │   │   ├── ui/                  # Radix-based primitives (shadcn-style)
    │   │   └── __tests__/           # component tests
    │   ├── lib/
    │   │   ├── actions.ts           # Server Actions (CRUD + aggregations + CSV)
    │   │   ├── db.ts                # Prisma client singleton
    │   │   ├── constants.ts         # statuses, categories, status→color
    │   │   └── utils.ts             # cn() and small helpers
    │   └── __tests__/
    │       └── actions.test.ts      # server-action tests
    ├── Dockerfile                   # multi-stage standalone build
    ├── docker-compose.yml           # local deploy with mounted db
    └── jest.config.ts
```

---

## Testing

```bash
cd ats-next
npm test
```

The suite covers:

- Server actions in `src/lib/actions.ts` — CRUD on applications, status history, KPI aggregations, CSV import/export, with Prisma mocked via `jest-mock-extended`
- Component behaviour on the table, the add form, and the status history modal

---

## Scripts

Run from `ats-next/`:

| Command         | What it does                              |
| --------------- | ----------------------------------------- |
| `npm run dev`   | Start the Next.js dev server              |
| `npm run build` | Production build (`output: standalone`)   |
| `npm start`     | Run the production build                  |
| `npm run lint`  | ESLint                                    |
| `npm test`      | Run Jest                                  |

---

## Notes & design choices

- **Server Actions, not REST.** All mutations go through Next.js Server Actions in `src/lib/actions.ts`. There is no `/api` directory.
- **One Prisma client.** `src/lib/db.ts` exports a process-singleton so Next.js's dev hot-reload doesn't leak connections.
- **Charts are mostly hand-rolled SVG.** The heatmap, funnel, and Sankey are written directly so they look exactly right on dark backgrounds without per-chart-library theming. Only the category donut uses Recharts.
- **The Sankey palette is desaturated on purpose.** Each stage gets a tone (sky / indigo / amber / gold / emerald / rose / stone / slate) at low saturation so the flow geometry leads, not the colour.
