---
name: release-notes
description: Generate user-facing release notes from a Git diff or changelog. Output groups changes by audience impact, not by commit author.
---

## Purpose

Convert a noisy `git log` into a release note that a customer or downstream engineer would actually read. Group by impact, not by commit.

## When to use

- Cutting a release tag.
- Producing notes for a downstream team that does not read your commits.
- Summarising a long-running branch before merge.

Skip when: the change is a single internal-only patch with no public impact.

## Body

1. Provide the input as either:
   - `git log --oneline <prev_tag>..HEAD`
   - `git diff <prev_tag>..HEAD --stat`
   - A pre-summarised changelog.
2. Group changes into four buckets:
   - **Highlights** (1–3 items the reader cares about most).
   - **Added** (new capability).
   - **Changed** (existing behavior modified — call out breakage explicitly).
   - **Fixed** (bugs).
3. Drop internal-only changes (test refactors, lint fixes) unless they unblocked something user-visible.
4. For every "Changed" item, state the migration in one line.
5. Cap the whole document at 30 lines.

## Inputs

- Source: `git log` text, `git diff --stat`, or a changelog.
- The previous version / tag string.
- The new version / tag string.

## Outputs

A markdown document of this exact shape:

```markdown
# v<new> — <short tagline>

**Highlights**
- ...

## Added
- ...

## Changed
- ...  (Migration: ...)

## Fixed
- ...
```

≤ 30 lines total.

## Worked example

Input: 14 commits on a Notes API feature branch.

Output:

```markdown
# v1.2.0 — Substring search across notes

**Highlights**
- New `GET /notes?q=<term>` returns notes whose title or body contains `<term>`.

## Added
- Substring search via `?q=` query parameter (case-sensitive).

## Changed
- `GET /notes` now returns results ordered by `id` ascending. (Migration: callers relying on the previous undefined order should specify `?sort=id` explicitly when we add it.)

## Fixed
- `PATCH /notes/:id` now returns 404 for unknown ids instead of 200 with stale fields.
- Search no longer requires the term in both title *and* body.
```
