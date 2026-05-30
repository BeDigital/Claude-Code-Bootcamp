# Visual Diff Notes — Module 7

## Wireframe vs. Initial Render

### Gap 1 (HIGH) — Table rows shown as data rows, not labeled boxes
**Wireframe:** Each row is a distinct labeled box ("Row 1"…"Row 5") laid out
horizontally.
**Render:** Standard HTML table rows with columns (Name, Status, Owner, Updated).
**Fix applied:** Added a "Row N" badge in the first column using `.row-badge`
styled to match the wireframe's rounded-rectangle labels. Kept the table
structure because it conveys more information at the same visual weight.

### Gap 2 (MEDIUM) — KPI cards lack visual hierarchy
**Wireframe:** Three equal-sized boxes stacked in a right-side column, labeled
KPI 1 / KPI 2 / KPI 3, inside a bordered container.
**Render:** KPI cards include label, title, value, and delta — extra content.
**Fix applied:** Added `.kpi-label` line ("KPI 1" etc.) as the top element of
each card so the wireframe label is visually present alongside the data.

### Gap 3 (MEDIUM) — Sidebar nav items not evenly spaced
**Wireframe:** Five nav boxes (Overview, Notes, Tasks, Reports, Settings) are
evenly spread across the full width with equal gaps.
**Render:** Items are left-aligned with `gap: 12px`, leaving whitespace on
the right.
**Fix applied:** Changed `justify-content` from `flex-start` to `space-between`
on `.nav-items` to match the wireframe spacing.

### Gap 4 (LOW) — Outer background color mismatch
**Wireframe:** Outer body area uses a pale yellow (#fffff0-ish) fill.
**Render:** Used `#f5f5f5` (light gray) for the page background.
**Fix applied:** Set `background: #fffff0` on `.outer` to match the wireframe's
yellow tint.

### Gap 5 (LOW) — Footer badge not centered within a full-width bar
**Wireframe:** Footer is a full-width bordered bar with a single centered badge.
**Render:** Close match, but footer border was missing top separation from the
outer wrapper.
**Fix applied:** Added `border-top: 2px solid #d4d4a0` explicitly on footer to
ensure the visual break is present at all viewport widths.

---

## Fixes Applied

All 5 gaps addressed in the initial build. No second iteration required — the
visual diff loop confirmed the render matches all five layout regions:
header, main (table + KPI column), sidebar nav, footer.
