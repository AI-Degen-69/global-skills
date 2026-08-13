---
name: lesson-files-consolidate
description: Use when organizing a messy folder of course files into per-chapter folders.
---

# lesson-files-consolidate

## When to use
The user has a folder of mixed course files (exercises, lecture PDFs, exam papers + solution spreadsheets) and wants them filed into per-chapter folders + one exams folder using a consistent templated scheme. Works recursively but skips already-organized / ignored directories.

## Parameters (CLI flags on `scripts/consolidate.py`)
- `--base PATH` — root to scan (required).
- `--out PATH` — output root for chapter/exam folders (default: `--base`). Use when scan base and destination differ.
- `--lang en|he` — folder + noun language. Default `en`.
- `--ignore "old"` — space-separated dir names to skip entirely.
- `--skip-prefix "^\d+_"` — regex; skip dirs whose name matches (use to avoid re-filing an existing `1_מבוא … 9_בחינות` style tree).
- `--skip-dirs "משופצים"` — explicit dir names to skip.
- `--dry-run` — print the plan, move nothing. **ALWAYS run first.**

## Naming templates
- Exercise: `NN-<chapter>-exercise-<num>[-<comment>].ext`  · he: `NN-<chapter>-תרגיל-<num>[-<comment>]`
- Material: `NN-<chapter>-material[-<desc>].ext`            · he: `NN-<chapter>-חומר[-<desc>]`
- Exam:     `NN-accounting-b-exam-<YEAR>-<DD>-<MM>[-management-economics].ext`
- Solution: same slug with `-solution-` (he: `-פתרון-`) instead of `-exam-`
- `NN` = zero-padded per-folder running index (stable ordering). Optional `<comment>`/`<desc>` stays ASCII for readability.

## Algorithm
1. Normalize filenames (NFKC + strip Unicode control chars) to defeat Hebrew RTL gremlins (LRI/PDF/RLM).
2. Classify each file:
   - **Course-general**: formula sheet / workbook / lesson plan → `course-general` (he `כללי הקורס`).
   - **Exams**: filename contains `חשבונאות ב` + a `D.D` date. Extract the 4-digit **YEAR from the .docx header** (filenames lack it). `.xlsx` or `פתרון` ⇒ solution. `ניהול וכלכלה` ⇒ `-management-economics` (he `-ניהול-וכלכלה`). Bare `D.D` files with no course word: inspect content to confirm faculty/date before classifying.
   - **Lecture materials**: `V <topic>.pdf` → map topic keyword to chapter.
   - **Cash-flow statements / template** PDFs & xlsx.
   - **Exercises**: chapter keyword + `תרגיל N` number + optional comment (straight-line, summary, simple, ithai, thirsty-for-freedom, juvenus…).
3. Group by chapter folder; assign `NN`; build new name.
4. Move into `<OUT>/<chapter>/` (or `<OUT>/exams/`).

### Chapter keyword → folder map (extend as needed)
| keyword (Hebrew) | en folder | he folder |
|---|---|---|
| הון עצמי | equity | הון עצמי |
| אגרות חוב / אגח | bonds | אגרות חוב |
| שיטת שווי מאזני | equity-method | שיטת שווי מאזני |
| השקעות בניירות ערך סחירים | investments-tradable-securities | השקעות בניירות ערך סחירים |
| התחייבויות לזמן ארוך | long-term-liabilities-loans | התחייבויות לזמן ארוך |
| תזרים מזומנים | cash-flow | דוח תזרים מזומנים |
| דף נוסחאות / חוברת עבודה / מערך שיעור | course-general | כללי הקורס |
| חשבונאות ב + date | exams | מבחנים |

## Critical pitfalls (learned the hard way)
- **Exam YEAR is NOT in the filename** — it's `6.7`, `25.11`… Extract the 4-digit year from the `.docx` XML header (regex `DD.DD.YYYY`); empirically these were **2015–2017**, NOT the folder's 2026 label. Guessing 2026 = wrong filenames.
- **Hebrew RTL control chars** hide inside filenames. Strip `Unicode category C` chars or matches silently fail / collide.
- **File locks**: an open file (Word/Excel/Explorer preview/Defender) throws `WinError 32` on delete. Script copies then unlinks; if unlink fails it leaves a duplicate and retries with backoff. Close the file in-app, then re-run (idempotent) to clear the leftover.
- **Don't re-file already-filed material**: when the same lecture PDF appears both loose and inside a chapter folder, md5-compare; if identical it's a duplicate — do NOT create a second copy.
- **Backup first** on real (non-temp) data: `cp -r "<BASE>" "<BASE>_BACKUP_$(date +%Y%m%d)"`.
- Skip Office temp files (`~$…`), and skip directories that are already a chapter/exam target so the script never re-files its own output.

## Steps
1. `python3 scripts/consolidate.py --base "<BASE>" --lang he --ignore old --dry-run` → read the plan.
2. Confirm zero `UNMAPPED`. If any, inspect content (`docx`/`xlsx` text) to classify, then extend the map.
3. Backup: `cp -r "<BASE>" "<BASE>_BACKUP_$(date +%Y%m%d)"`.
4. Run without `--dry-run`.
5. Re-run if interrupted (idempotent: skips moved files, reconciles duplicates, retries locks).

## Verification
- `find <OUT> -maxdepth 1 -type f | wc -l` → 0 loose files.
- File count inside subfolders == original count.
- md5 of any "leftover" vs its destination proves duplicate before deleting.
