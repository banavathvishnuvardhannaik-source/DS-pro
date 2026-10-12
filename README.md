# Mohan Babu University — Data Science Laboratory Management System Website

A complete, interactive, responsive lab website with:

- **Real execution videos** for every experiment & section (generated from the
  actual code in `C:\Users\HP\OneDrive\Desktop\Data-Science` — fast typewriter
  editor → run → real terminal output, silent, 720p / H.264, 12 s each).
- **In-browser Python compiler** — every section page has a **▶ Run Code** button
  that executes the code with real CPython (Pyodide / WebAssembly), showing
  stdout, errors and rendered plots. Includes an **✎ Edit** mode.
- **Professional "Academic Gold" theme** — deep burgundy + champagne gold on
  warm ivory.

## Run it

```
cd mbu-ds-lab
python -m http.server 8000
```

then visit **http://localhost:8000**
(opening index.html directly also works, but the Python compiler and videos
behave best through the local server).

## Page flow

```
Home (#/home)
  → + ADD / click experiment
Experiment Preview (#/experiment/ID)               ← hover = ~12s preview video
  → Overview
Experiment Details (#/experiment/ID/overview)      ← sections, YouTube, GitHub, summary
  → click A / B / C ...
Section Page (#/experiment/ID/section/LETTER)      ← video + code + Run/Edit/Copy
```

## Current experiments (from Desktop\Data-Science)

| # | Name | Sections |
|---|------|----------|
| 1 | Data Import & Export with Pandas | A–H (CSV, JSON, Web APIs, Excel, Multi-sheet Excel, Text, Online, SQL) |
| 3 | Data Cleaning & Preprocessing | A–D |
| 4 | Hierarchical Indexing & Reshaping | A–C |
| 5 | Data Visualization with Matplotlib & Seaborn | A–E (with real plot outputs) |

## Editing content

Everything lives in **`js/data.js`** (student details, experiments, links,
summaries, code). Sections are fully dynamic.

To change the logo: drop the real file into `assets/` and set
`logoPath` in `js/data.js`.

## Regenerating videos

The videos in `assets/videos/` were produced by `tools/make_videos.py`,
which executes each section's code for real, renders the typewriter
screen-recording-style animation (no audio), and rewrites `js/data.js`:

```
python tools/make_videos.py            # everything
python tools/make_videos.py exp1A      # only matching videos
```

Sources for the generator: `tools/experiments_spec.py`.
