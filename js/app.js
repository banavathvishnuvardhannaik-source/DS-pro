/* ============================================================
   APP LOGIC — router, rendering & interactions
   Data comes from js/data.js (SITE, STUDENT, EXPERIMENTS)

   Navigation flow (hash router, browser back also works):

     #/home                                  → PAGE 1  Main page
        + ADD / experiment card
     #/experiment/:id                        → PAGE 2  Experiment preview
        Overview
     #/experiment/:id/overview               → PAGE 3  Experiment details
        A / B / C / D ...
     #/experiment/:id/section/:letter        → PAGE 4  Section video + code
   ============================================================ */

const viewEl = document.getElementById("view");
const toastEl = document.getElementById("toast");

/* --------- Apply saved homepage edits (from in-browser editing) --------- */
(function applySavedHomeEdits() {
  try {
    const saved = JSON.parse(localStorage.getItem("mbuHomeEdits") || "{}");
    if (saved.SITE) { const { logoPath, ...rest } = saved.SITE; Object.assign(SITE, rest); }
    if (saved.STUDENT) { const { photo, ...rest } = saved.STUDENT; Object.assign(STUDENT, rest); }
    const sp = localStorage.getItem("studentPhoto");
    if (sp) STUDENT.photo = sp;
  } catch (e) { /* ignore bad data */ }
})();

/* ---------------- In-browser Python compiler (Pyodide) ---------------- */
/* Real CPython compiled to WebAssembly — runs Python only, in the browser. */

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.mjs";
let pyodidePromise = null;

async function getPyodide(statusCb) {
  if (!pyodidePromise) {
    pyodidePromise = (async () => {
      statusCb("Downloading Python runtime (Pyodide / WebAssembly)…");
      const mod = await import(/* @vite-ignore */ PYODIDE_URL);
      const py = await mod.loadPyodide();
      statusCb("Installing scientific packages: numpy, pandas, matplotlib, scipy, scikit-learn…");
      const _bundlePkgs = ["numpy", "pandas", "matplotlib", "sqlite3", "seaborn", "scipy", "scikit-learn", "openpyxl", "requests", "regex", "beautifulsoup4", "lxml", "nltk", "wordcloud", "vaderSentiment"];
      for (const _p of _bundlePkgs) {
        try { await py.loadPackage([_p]); }
        catch (_) {
          try {
            await py.loadPackage(["micropip"]);
            const _mp = py.pyimport("micropip");
            await _mp.install(_p);
          } catch (e2) { console.warn(_p + " could not be installed:", e2); }
        }
      }
      return py;
    })();
    pyodidePromise.catch(() => { pyodidePromise = null; });
  }
  return pyodidePromise;
}

/**
 * Execute Python code in the browser.
 * Returns { stdout, stderr, figures:[base64png...], ok }.
 */
async function runPythonInBrowser(code, statusCb) {
  const py = await getPyodide(statusCb);
  let stdout = "";
  let stderr = "";
  py.setStdout({ batched: (s) => { stdout += s + "\n"; } });
  py.setStderr({ batched: (s) => { stderr += s + "\n"; } });

  // Capture matplotlib figures as PNGs (Agg backend keeps them off the DOM).
  const wrapped =
    "import matplotlib\nmatplotlib.use('agg')\n" + code +
    "\n\nimport matplotlib.pyplot as _plt, io as _io, base64 as _b64" +
    "\n_figs = []" +
    "\nfor _n in _plt.get_fignums():" +
    "\n    _buf = _io.BytesIO()" +
    "\n    _plt.figure(_n).savefig(_buf, format='png', dpi=140, bbox_inches='tight', facecolor='white')" +
    "\n    _figs.append(_b64.b64encode(_buf.getvalue()).decode('ascii'))" +
    "\n_plt.close('all')" +
    "\n_figs";

  statusCb("Running Python code…");
  let figures = [];
  let ok = true;
  try {
    const result = await py.runPythonAsync(wrapped);
    figures = result ? Array.from(result) : [];
    if (result && result.destroy) result.destroy();
  } catch (err) {
    ok = false;
    stderr += (err.message || String(err)) + "\n";
  }
  return { stdout: stdout.trimEnd(), stderr: stderr.trimEnd(), figures, ok };
}

/* ---------------- Utilities ---------------- */

function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

let toastTimer = null;
function toast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2200);
}

function getExperiment(id) {
  return EXPERIMENTS.find((e) => String(e.id) === String(id)) || null;
}

/* ---------------- Lightweight Python syntax highlighter ---------------- */

const PY_REGEX =
  /(?<com>#[^\n]*)|(?<str>"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')|(?<dec>@[\w.]+)|(?<kw>\b(?:import|from|as|def|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|class|try|except|finally|with|lambda|pass|break|continue|raise|del|global|assert|yield)\b)|(?<num>\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b)|(?<fn>\b[A-Za-z_]\w*(?=\s*\())/g;

/**
 * Highlight Python source and render it as numbered lines.
 * Spans are closed & reopened per line so the HTML stays valid.
 */
function renderCodeBlock(src) {
  const lines = [[]]; // array of lines; each line = array of html chunks
  let lastIndex = 0;
  let match;

  const pushText = (text, cls) => {
    const parts = esc(text).split("\n");
    parts.forEach((part, i) => {
      if (i > 0) lines.push([]);
      if (part.length) {
        lines[lines.length - 1].push(
          cls ? `<span class="${cls}">${part}</span>` : part
        );
      }
    });
  };

  PY_REGEX.lastIndex = 0;
  while ((match = PY_REGEX.exec(src)) !== null) {
    if (match.index > lastIndex) pushText(src.slice(lastIndex, match.index), null);
    const cls = match.groups.com ? "tok-com"
      : match.groups.str ? "tok-str"
      : match.groups.dec ? "tok-dec"
      : match.groups.kw ? "tok-kw"
      : match.groups.num ? "tok-num"
      : "tok-fn";
    pushText(match[0], cls);
    lastIndex = PY_REGEX.lastIndex;
  }
  if (lastIndex < src.length) pushText(src.slice(lastIndex), null);

  return lines
    .map(
      (chunks, i) =>
        `<div class="code-line"><span class="ln">${i + 1}</span><span class="lc">${
          chunks.join("") || " "
        }</span></div>`
    )
    .join("");
}

/* ---------------- Hover-to-play preview videos ---------------- */

const PREVIEW_SECONDS = 12; // keep the hover preview around 12 seconds

function bindHoverPreview(video) {
  if (!video) return;
  const frame = video.closest(".video-frame");
  video.muted = true;
  video.playsInline = true;
  video.preload = "metadata";

  const start = () => {
    frame && frame.classList.add("playing");
    const p = video.play();
    if (p && p.catch) p.catch(() => {});
  };
  const reset = () => {
    video.pause();
    video.currentTime = 0;
    frame && frame.classList.remove("playing");
  };

  video.addEventListener("mouseenter", start);
  video.addEventListener("mouseleave", reset);

  // Stop & rewind after ~PREVIEW_SECONDS of preview playback
  video.addEventListener("timeupdate", () => {
    if (video.currentTime >= PREVIEW_SECONDS) reset();
  });

  // Touch devices: tap toggles the preview
  video.addEventListener("click", () => (video.paused ? start() : reset()));

  // Friendly message if the video source is missing/broken
  video.addEventListener("error", () => {
    if (!frame || frame.querySelector(".video-error")) return;
    const err = document.createElement("div");
    err.className = "video-error";
    err.innerHTML =
      "Video not found.<br>Set this video path in <b>js/data.js</b>.";
    frame.appendChild(err);
  });
}

function bindAllHoverPreviews(root) {
  root.querySelectorAll("video[data-preview]").forEach(bindHoverPreview);
}

function videoCardHTML(src, { badge = "Preview", caption = "", preview = true } = {}) {
  const attrs = preview
    ? 'data-preview muted playsinline preload="metadata"'
    : 'controls muted playsinline preload="metadata"';
  const overlay = preview
    ? `<div class="video-overlay"><span class="play-pill">▶&nbsp;&nbsp;Hover to play preview</span></div>`
    : "";
  return `
    <div class="card video-card">
      <div class="video-frame">
        <video src="${esc(src)}?v=${Date.now()}" ${attrs} ${preview ? "" : 'id="sectionVideo"'}></video>
        <span class="video-badge">${esc(badge)}</span>
        ${overlay}
      </div>
      ${caption ? `<div class="video-caption">${esc(caption)}</div>` : ""}
    </div>`;
}

/* ============================================================
   PAGE 1 — HOME
   ============================================================ */

/* ---------------- Portfolio experiments (mirrors dsprojectportfolio) ---------------- */
const PORTFOLIO = [
  { id: 1, title: "Reading and Writing Data",
    desc: "Load data from URLs, CSV, TXT, JSON and Excel files with Pandas, and save it back.",
    items: [
      { tag: "1a", name: "Read CSV from an online URL", path: "FromOnline_exp1/Main.ipynb" },
      { tag: "1b", name: "Read and write CSV", path: "FromLocal/FromCSV_Exp1.2" },
      { tag: "1c", name: "Read and write TXT", path: "FromLocal/FromTXT_Exp1.3" },
      { tag: "1d", name: "Read and write JSON", path: "FromLocal/FromJSON_Exp1B.1" },
      { tag: "1e", name: "Read and write Excel", path: "FromLocal/FromExcel_Exp1C" },
    ]},
  { id: 2, title: "APIs and Databases",
    desc: "Fetch data from a web API and run create, read, update, delete on a SQLite database.",
    items: [
      { tag: "2a", name: "Get data from the GitHub API", path: "Exp_2/Exp2a.ipynb" },
      { tag: "2b", name: "SQLite CRUD operations", path: "Exp_2/Exp2b.ipynb" },
    ]},
  { id: 3, title: "Data Cleaning",
    desc: "Handle missing values, encode categories, find outliers and split messy text.",
    items: [
      { tag: "3a", name: "Missing values", path: "Exp_3/exp3abcd.ipynb" },
      { tag: "3b", name: "Encoding and renaming", path: "Exp_3/exp3abcd.ipynb" },
      { tag: "3c", name: "Outlier detection", path: "Exp_3/exp3abcd.ipynb" },
      { tag: "3d", name: "Text splitting with regex", path: "Exp_3/exp3abcd.ipynb" },
    ]},
  { id: 4, title: "Hierarchical Indexing and Merging",
    desc: "Work with MultiIndex, reshape with stack and unstack, and combine DataFrames.",
    items: [
      { tag: "4a", name: "MultiIndex Series", path: "Exp_4_new/expA.ipynb" },
      { tag: "4b", name: "Stack and unstack", path: "Exp_4_new/expB.ipynb" },
      { tag: "4c", name: "Merge and combine_first", path: "Exp_4_new/expC.ipynb" },
    ]},
  { id: 5, title: "Data Visualization",
    desc: "Draw line, scatter, bar, histogram, density and box plots with Matplotlib and Seaborn.",
    items: [
      { tag: "5a", name: "Line plots with annotations", path: "Exp_5_new/expA.ipynb" },
      { tag: "5b", name: "Five plots on the Iris dataset", path: "Exp_5_new/expA1.ipynb" },
      { tag: "5c", name: "Five plots on the Penguins dataset", path: "Exp_5_new/expA1_own.ipynb" },
      { tag: "5d", name: "Grouped bar plot", path: "Exp_5_new/expB1.ipynb" },
      { tag: "5e", name: "Stacked bar plot", path: "Exp_5_new/expB2.ipynb" },
      { tag: "5f", name: "Histogram and density plot", path: "Exp_5_new/ExpC.ipynb" },
      { tag: "5g", name: "Scatter plot and correlation", path: "Exp_5_new/expD.ipynb" },
      { tag: "5h", name: "Box plot", path: "Exp_5_new/expE.ipynb" },
    ]},
  { id: 6, title: "Time Series Analysis in Pandas",
    desc: "Build time series, date ranges, timezones, periods and resampled aggregates.",
    items: [{ tag: "6a", name: "Section A", path: "TimeSeries/exp6A.ipynb" },
            { tag: "6b", name: "Section B", path: "TimeSeries/exp6B.ipynb" },
            { tag: "6c", name: "Section C", path: "TimeSeries/exp6C.ipynb" },
            { tag: "6d", name: "Section D", path: "TimeSeries/exp6D.ipynb" },
            { tag: "6e", name: "Section E", path: "TimeSeries/exp6E.ipynb" },
            { tag: "6f", name: "Section F", path: "TimeSeries/exp6F.ipynb" },
            { tag: "6g", name: "Section G", path: "TimeSeries/exp6G.ipynb" }]},
  { id: 7, title: "GroupBy and Data Aggregation in Pandas",
    desc: "Group by single or multiple keys and aggregate summary statistics on iris.",
    items: [{ tag: "7a", name: "Section A", path: "GroupBy/exp7A.ipynb" },
            { tag: "7b", name: "Section B", path: "GroupBy/exp7B.ipynb" },
            { tag: "7c", name: "Section C", path: "GroupBy/exp7C.ipynb" }]},
  { id: 8, title: "Sentiment Analysis of Product Reviews",
    desc: "Scrape reviews from HTML with BeautifulSoup, build word clouds, score sentiment with VADER and visualize sentiment intensity.",
    items: [{ tag: "8a", name: "Extract reviews from HTML", path: "Local/Csv/experiment8a.ipynb" },
            { tag: "8b", name: "Word clouds & VADER sentiment", path: "Local/Csv/experiment8b.ipynb" },
            { tag: "8c", name: "Text statistics with NLTK stopwords", path: "Local/Csv/experiment8c.ipynb" },
            { tag: "8d", name: "NLTK VADER vs vaderSentiment", path: "Local/Csv/experiment8d.ipynb" },
            { tag: "8e", name: "Sentiment intensity visualization", path: "Local/Csv/experiment8e.ipynb" }]},
];

function renderHome() {
  viewEl.innerHTML = `
    <div class="home-grid">

      <div class="home-top">
      <!-- ===== CENTER — main university card ===== -->
      <section class="card uni-card">
        <div class="uni-head">
          <img class="uni-logo" src="${esc(SITE.logoPath)}" alt="MBU Logo"
               onerror="this.src='assets/mbu-logo.svg'" />
          <h1 class="uni-name" style="display:none;">${esc(SITE.universityName)}</h1>
        </div>

        <div class="lab-name">${esc(SITE.labName)}</div>
        <div class="subject-code">Subject Code: <strong>${esc(SITE.subjectCode)}</strong></div>

        <div style="margin-top:18px; text-align:center;">
          <a href="https://github.com/dashboard" target="_blank" rel="noopener"
             style="display:inline-flex; align-items:center; gap:8px; padding:8px 18px; border-radius:999px; border:1.5px solid var(--gold); color:var(--gold); font-weight:700; font-size:14px; text-decoration:none;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56 0-.27-.01-1.17-.02-2.12-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.72-1.54-2.55-.29-5.23-1.28-5.23-5.68 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11.1 11.1 0 0 1 5.8 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.18 1.83 1.18 3.09 0 4.41-2.69 5.38-5.25 5.67.41.35.77 1.05.77 2.13 0 1.53-.01 2.76-.01 3.14 0 .31.2.68.8.56A10.52 10.52 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/></svg>
            GitHub
          </a>
        </div>

        <div class="search-wrap" style="margin-bottom:14px;">
          <div class="search-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
              <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
            </svg>
            <input id="searchInput" class="search-input" type="text"
                   placeholder="Search Experiments..." autocomplete="off" />
          </div>
          <div id="searchSuggest" class="search-suggest"></div>
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:center; align-items:center;">
          <span style="font-weight:800; color:var(--muted); font-size:13px; letter-spacing:1px; text-transform:uppercase;">Tools used:</span>
          <span class="chip">Python</span>
          <span class="chip">Pyodide</span>
          <span class="chip">Pandas</span>
          <span class="chip">NumPy</span>
          <span class="chip">Matplotlib</span>
          <span class="chip">Seaborn</span>
          <span class="chip">BeautifulSoup</span>
          <span class="chip">NLTK</span>
          <span class="chip">VADER Sentiment</span>
          <span class="chip">WordCloud</span>
        </div>
      </section>

      <!-- ===== Student ID card (profile) ===== -->
        <section class="card id-card">
          <div class="id-card-banner">
            <h3>Student ID Card</h3>
            <small style="display:none;">${esc(SITE.universityName)}</small>
          </div>
          <div style="display:flex;gap:8px;padding:14px 18px 0;">
            <button id="changePhotoBtn" class="btn" type="button" style="flex:1">📷 Change Photo</button>
            <button id="editDetailsBtn" class="btn btn-primary" type="button" style="flex:1">✏ Edit Details</button>
          </div>
          <div class="id-card-body">
            <div class="id-photo-frame">
              <img class="id-photo" id="studentPhotoImg" src="${esc(STUDENT.photo)}?v=${Date.now()}" alt="Student Photo"
                   onerror="this.src='assets/student-photo.svg'" />
            </div>
            <div class="id-fields">
              <div class="id-field"><span class="label">Name:</span><span class="value">${esc(STUDENT.name)}</span></div>
              <div class="id-field"><span class="label">ID Number:</span><span class="value">${esc(STUDENT.idNumber)}</span></div>
              <div class="id-field"><span class="label">Section:</span><span class="value">${esc(STUDENT.section)}</span></div>
              <div class="id-field"><span class="label">Faculty:</span><span class="value">${esc(STUDENT.faculty)}</span></div>
              <div class="id-field"><span class="label">Profession:</span><span class="value">${esc(STUDENT.profession)}</span></div>
            </div>
          </div>
        </section>
      </div><!-- /home-top -->

      <!-- ===== Modules (one per line, with PDF notes) ===== -->
      <section class="card exp-section">
        <div class="exp-header" id="modulesToggle" style="cursor:pointer;">
          <div>
            <h2>Modules ▾</h2>
            <span class="exp-count">${MODULES.length} modules · PDF notes</span>
          </div>
        </div>
        <div class="exp-list" id="modulesList">
          ${MODULES.map((m, i) => `
            <div class="exp-item" style="display:flex;align-items:center;gap:12px;">
              <button type="button" class="module-link" data-mod="${i}"
                      style="flex:1;display:flex;align-items:center;gap:14px;min-width:0;cursor:pointer;background:none;border:none;padding:0;text-align:left;font-family:inherit;color:inherit;">
                <span class="exp-item-num">${m.name.replace("Module ", "M")}</span>
                <span class="exp-item-info">
                  <span class="exp-item-name">${esc(m.name)}</span>
                  <span class="exp-item-meta">${esc(m.topics)}</span>
                </span>
                <svg class="exp-item-arrow" width="18" height="18" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                  <path d="M9 6l6 6-6 6"/>
                </svg>
              </button>
              ${m.pdf ? `<a class="btn btn-primary" href="${esc(m.pdf)}" target="_blank" rel="noopener"
                            style="flex-shrink:0;text-decoration:none;white-space:nowrap;">📄 View PDF</a>` : ""}
            </div>`).join("")}
        </div>
      </section>

      <!-- ===== Lab Manual (PDF uploads) ===== -->
      <section class="card exp-section">
        <div class="exp-header">
          <div>
            <h2>Lab Manual</h2>
            <span class="exp-count">${labPdfs().length} file(s)</span>
          </div>
          <label class="btn btn-primary" style="cursor:pointer;">+ Upload PDF<input type="file" id="pdfUpload" accept="application/pdf" multiple hidden></label>
        </div>
        <div class="exp-list">
          ${labPdfs().map((p, i) => `
            <div class="exp-item">
              <span class="exp-item-num">📄</span>
              <div class="exp-item-info">
                <a href="${p.url}" target="_blank" style="color:var(--ink);text-decoration:none;font-weight:700;">${esc(p.name)}</a>
              </div>
              <button class="btn" data-pdfrem="${i}" type="button" style="margin-left:auto;">🗑</button>
            </div>`).join("") || '<p class="panel-sub">No PDFs uploaded yet.</p>'}
        </div>
      </section>

      <!-- ===== Experiments (below) — portfolio style ===== -->
        <section class="card exp-section">
          <div class="exp-header">
            <div>
              <h2>Experiments:</h2>
              <span class="exp-count">8 experiments · Python</span>
            </div>
            <button id="addExpBtn" class="btn btn-primary" type="button">+ Create New Experiment</button>
          </div>
          <div id="newExpForm" style="display:none; margin:10px 0; padding:16px; border:1px dashed var(--gold); border-radius:var(--radius);">
            <input id="neTitle" placeholder="Experiment title" style="width:100%; margin-bottom:8px; padding:10px; border-radius:10px; border:1px solid var(--line); background:var(--card); color:var(--ink);" />
            <input id="neDesc" placeholder="Short description" style="width:100%; margin-bottom:8px; padding:10px; border-radius:10px; border:1px solid var(--line); background:var(--card); color:var(--ink);" />
            <input id="neItems" placeholder="Sub-items e.g. 1a: Read CSV, 1b: Write JSON" style="width:100%; margin-bottom:8px; padding:10px; border-radius:10px; border:1px solid var(--line); background:var(--card); color:var(--ink);" />
            <button id="neSave" class="btn btn-primary" type="button">Save Experiment</button>
            <button id="neCancel" class="btn" type="button" style="margin-left:8px;">Cancel</button>
          </div>
          <div id="portfolioList">
            <p class="panel-sub">Reading data, cleaning it, combining it and plotting it.</p>
            <div class="exp-cards">
              ${PORTFOLIO.map(exp => `
              <details class="exp-card">
                <summary class="card-head">
                  <span class="num">${exp.id}</span>
                  <span>
                    <span class="card-title">Experiment ${exp.id}: ${esc(exp.title)}</span>
                    <p class="card-desc">${esc(exp.desc)}</p>
                  </span>
                </summary>
                <div class="panel">
                  <ul>
                    ${exp.items.map(it => `
                    <li><button type="button" class="sub-link" data-exp="${exp.id}" data-tag="${esc(it.tag)}">
                      <span class="tag">${esc(it.tag)}</span><span>${esc(it.name)}</span><span class="ext">&#8599;</span>
                    </button></li>`).join("")}
                  </ul>
                  <p class="video-label">Short demo (10 sec)</p>
                  <div class="video-box">
                    <video controls preload="none" src="${exp.video || ('assets/videos/exp' + exp.id + '-preview.mp4')}?v=${Date.now()}"></video>
                  </div>
                  ${PORTFOLIO_BASE_IDS.has(exp.id) ? "" : `
                  <button class="btn" data-delport="${exp.id}" type="button" style="margin-top:12px;">🗑 Delete this experiment</button>`}
                </div>
              </details>`).join("")}
            </div>
          </div>
        </section>

    </div>
  `;

  bindHomeInteractions();
  bindNewExperimentForm();
  bindSubItemLinks();
}

/* Compatibility shim so notebook code written for local Python runs inside the browser */
const SUB_ITEM_SHIM = `
import sys as _sys
import os as _os
try: _os.chdir("/home/pyodide")
except Exception: pass
from pyodide.http import open_url as _open_url
import pandas as _pd

if not hasattr(_pd, "_orig_read_csv_raw"):
    _pd._orig_read_csv_raw = _pd.read_csv
def _read_csv_shim(path, *a, **k):
    if isinstance(path, str) and path.startswith(("http://", "https://")):
        path = _open_url(path)
    return _pd._orig_read_csv_raw(path, *a, **k)
_pd.read_csv = _read_csv_shim

if not hasattr(_pd, "_orig_read_json_raw"):
    _pd._orig_read_json_raw = _pd.read_json
def _read_json_shim(path, *a, **k):
    if isinstance(path, str) and path.startswith(("http://", "https://")):
        path = _open_url(path)
    return _pd._orig_read_json_raw(path, *a, **k)
_pd.read_json = _read_json_shim

import json as _json
class _Resp:
    def __init__(s, t): s._t = t
    def json(s): return _json.loads(s._t)
    @property
    def text(s): return s._t
    @property
    def content(s): return s._t.encode()
class _Req:
    def get(s, url, *a, **k):
        return _Resp(_open_url(url).read())
_sys.modules['requests'] = _Req()

`;

/* ---- sub-item detail overlay: code + output, saved locally ---- */
function subItemStore() {
  try { return JSON.parse(localStorage.getItem("subItemData") || "{}"); } catch { return {}; }
}
function bindSubItemLinks() {
  document.querySelectorAll(".sub-link").forEach((btn) => {
    btn.addEventListener("click", () => openSubItem(btn.dataset.exp, btn.dataset.tag));
  });
  document.querySelectorAll(".module-link").forEach((btn) => {
    btn.addEventListener("click", () => openModule(btn.dataset.mod));
  });
}
function openModule(idx) {
  const m = MODULES[Number(idx)];
  if (!m) return;
  let overlay = document.getElementById("subItemOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "subItemOverlay";
    overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center;z-index:999;padding:20px;";
    document.body.appendChild(overlay);
  }
  overlay.innerHTML = `
    <div style="background:var(--card);border:1px solid var(--gold);border-radius:20px;max-width:560px;width:100%;max-height:80vh;overflow:auto;padding:24px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <h3 style="color:var(--ink)">${esc(m.name)}</h3>
        <button id="subClose" class="btn" type="button">✕ Close</button>
      </div>
      <p style="margin-top:12px;color:var(--ink)">${esc(m.topics)}</p>
      <p style="margin-top:8px;color:var(--muted);font-size:13px;">These topics are covered in the experiments listed below on the homepage.</p>
      ${m.pdf ? `<a class="btn btn-primary" href="${esc(m.pdf)}" target="_blank" rel="noopener"
                    style="display:inline-block;margin-top:16px;text-decoration:none;">📄 Open ${esc(m.name)} PDF</a>` : ""}
    </div>`;
  overlay.style.display = "flex";
  document.getElementById("subClose").onclick = () => (overlay.style.display = "none");
}
function openPhotoCrop(file) {
  const reader = new FileReader();
  reader.onload = () => {
    const imgEl = new Image();
    imgEl.onload = () => {
      let overlay = document.getElementById("cropOverlay");
      if (overlay) overlay.remove();
      overlay = document.createElement("div");
      overlay.id = "cropOverlay";
      overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;z-index:1000;padding:16px;";
      document.body.appendChild(overlay);
      const SIZE = 240;
      overlay.innerHTML = `
        <div style="background:var(--card);border:1px solid var(--gold);border-radius:20px;padding:22px;max-width:360px;width:100%;text-align:center;">
          <h3 style="color:var(--ink);margin-bottom:14px;">Crop Photo</h3>
          <div id="cropWindow" style="width:${SIZE}px;height:${SIZE}px;border-radius:50%;overflow:hidden;position:relative;margin:0 auto;border:2px solid var(--gold);touch-action:none;cursor:grab;">
            <img id="cropImg" src="${reader.result}" style="position:absolute;user-select:none;">
          </div>
          <p style="font-size:12px;color:var(--muted);margin:10px 0 2px;">Drag the image to align · zoom:</p>
          <input type="range" id="cropZoom" min="0.5" max="4" step="0.01" value="1" style="width:100%;">
          <div style="margin-top:14px;">
            <button id="cropSave" class="btn btn-primary" type="button">Save</button>
            <button id="cropCancel" class="btn" type="button" style="margin-left:8px;">Cancel</button>
          </div>
        </div>`;
      const cImg = overlay.querySelector("#cropImg");
      const w = cImg.naturalWidth, h = cImg.naturalHeight;
      const baseScale = Math.max(SIZE / w, SIZE / h);
      let panX = 0, panY = 0;
      const apply = () => {
        const scale = baseScale * parseFloat(overlay.querySelector("#cropZoom").value);
        cImg.style.width = w * scale + "px";
        cImg.style.height = h * scale + "px";
        cImg.style.left = (SIZE - w * scale) / 2 + panX + "px";
        cImg.style.top = (SIZE - h * scale) / 2 + panY + "px";
      };
      apply();
      const win = overlay.querySelector("#cropWindow");
      let dragging = false, sx = 0, sy = 0;
      win.addEventListener("pointerdown", (e) => { dragging = true; sx = e.clientX - panX; sy = e.clientY - panY; win.setPointerCapture(e.pointerId); });
      win.addEventListener("pointermove", (e) => { if (!dragging) return; panX = e.clientX - sx; panY = e.clientY - sy; apply(); });
      win.addEventListener("pointerup", () => (dragging = false));
      overlay.querySelector("#cropZoom").addEventListener("input", apply);
      overlay.querySelector("#cropCancel").onclick = () => overlay.remove();
      overlay.querySelector("#cropSave").onclick = () => {
        const scale = baseScale * parseFloat(overlay.querySelector("#cropZoom").value);
        const cw = w * scale, ch = h * scale;
        const cv = document.createElement("canvas");
        cv.width = SIZE; cv.height = SIZE;
        const ctx = cv.getContext("2d");
        ctx.beginPath();
        ctx.arc(SIZE / 2, SIZE / 2, SIZE / 2, 0, Math.PI * 2);
        ctx.closePath();
        ctx.clip();
        ctx.drawImage(cImg, (SIZE - cw) / 2 + panX, (SIZE - ch) / 2 + panY, cw, ch);
        const dataUrl = cv.toDataURL("image/jpeg", 0.9);
        STUDENT.photo = dataUrl;
        localStorage.setItem("studentPhoto", dataUrl);
        const img = document.getElementById("studentPhotoImg");
        if (img) img.src = dataUrl;
        toast("Photo updated!");
        overlay.remove();
      };
    };
    imgEl.src = reader.result;
  };
  reader.readAsDataURL(file);
}
function openSubItem(expId, tag) {
  const key = expId + "-" + tag;
  const store = subItemStore();
  const data = store[key] || { code: "", output: "" };
  const title = tag + " — " + (document.querySelector(`.sub-link[data-tag="${tag}"][data-exp="${expId}"] span:nth-child(2)`)?.textContent || "");
  let overlay = document.getElementById("subItemOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "subItemOverlay";
    overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center;z-index:999;padding:20px;";
    document.body.appendChild(overlay);
  }
  overlay.innerHTML = `
    <div style="background:var(--card);border:1px solid var(--gold);border-radius:20px;max-width:760px;width:100%;max-height:88vh;overflow:auto;padding:24px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <h3 style="color:var(--ink)">${esc(title)}</h3>
        <button id="subClose" class="btn" type="button">✕ Close</button>
      </div>
      <label style="display:block;margin:14px 0 6px;font-weight:800;color:var(--muted);font-size:12px;letter-spacing:1px;text-transform:uppercase;">Code</label>
      <textarea id="subCode" style="width:100%;height:200px;padding:12px;border-radius:12px;border:1px solid var(--line);background:var(--code-bg);color:#e8eefc;font-family:var(--mono);font-size:13px;" placeholder="Paste your Python code here...">${esc(data.code)}</textarea>
      <label style="display:block;margin:14px 0 6px;font-weight:800;color:var(--muted);font-size:12px;letter-spacing:1px;text-transform:uppercase;">Output</label>
      <textarea id="subOutput" style="width:100%;height:160px;padding:12px;border-radius:12px;border:1px solid var(--line);background:#0d1420;color:#7dd3fc;font-family:var(--mono);font-size:13px;" placeholder="Paste your output here...">${esc(data.output)}</textarea>
      <div id="subFigures" style="display:flex;flex-wrap:wrap;gap:10px;margin-top:12px;"></div>
      <button id="subRun" class="btn" type="button" style="margin-top:14px; margin-right:8px;">▶ Run Code</button>
      <button id="subSave" class="btn btn-primary" type="button" style="margin-top:14px;">💾 Save</button>
    </div>`;
  overlay.style.display = "flex";

  // Load the real code from the GitHub repo for this sub-item (if not saved yet)
  const item = PORTFOLIO.find((e) => String(e.id) === String(expId))
    ?.items.find((it) => it.tag === tag);
  const codeBox = document.getElementById("subCode");
  if (item && item.path && !data.code) {
    const loadFromPath = async (p) => {
      if (/\.ipynb$/i.test(p)) {
        const r = await fetch(`https://raw.githubusercontent.com/Kanishka1256/Data-Science/main/${p}`);
        if (!r.ok) throw new Error();
        const nb = await r.json();
        return (nb.cells || []).filter((c) => c.cell_type === "code")
          .map((c) => (Array.isArray(c.source) ? c.source.join("") : c.source)).join("\n\n# %%\n\n");
      }
      if (/\.(py|txt|md)$/i.test(p)) {
        const r = await fetch(`https://raw.githubusercontent.com/Kanishka1256/Data-Science/main/${p}`);
        if (!r.ok) throw new Error();
        return await r.text();
      }
      // folder — list its files and pick the first notebook/code file
      const r = await fetch(`https://api.github.com/repos/Kanishka1256/Data-Science/contents/${p}?ref=main`);
      if (!r.ok) throw new Error();
      const files = await r.json();
      const target = (Array.isArray(files) ? files : []).find((f) => /\.(ipynb|py)$/i.test(f.name));
      if (!target) throw new Error();
      const r2 = await fetch(target.download_url);
      if (!r2.ok) throw new Error();
      if (/\.ipynb$/i.test(target.name)) {
        const nb = await r2.json();
        return (nb.cells || []).filter((c) => c.cell_type === "code")
          .map((c) => (Array.isArray(c.source) ? c.source.join("") : c.source)).join("\n\n# %%\n\n");
      }
      return await r2.text();
    };
    loadFromPath(item.path)
      .then((code) => { codeBox.value = code; })
      .catch(() => { codeBox.placeholder = "Could not load code from GitHub — check internet."; });
  }

  // Run the code in the browser and fill the Output box
  document.getElementById("subRun").onclick = async () => {
    const btn = document.getElementById("subRun");
    btn.disabled = true;
    const outBox = document.getElementById("subOutput");
    outBox.value = "Running…";
    try {
      // Copy any companion data files (CSV, TXT, XLSX, JSON) from the same GitHub folder
      try {
        const py = await getPyodide(() => {});
        const p = item && item.path ? item.path : "";
        const dir = p.includes(".") ? p.split("/").slice(0, -1).join("/") : p;
        const r = await fetch(`https://api.github.com/repos/Kanishka1256/Data-Science/contents/${dir}?ref=main`);
        if (r.ok) {
          const files = await r.json();
          if (Array.isArray(files)) {
            for (const f of files) {
              if (f.type === "file" && /\.(csv|txt|json|xlsx|xls)$/i.test(f.name)) {
                const r2 = await fetch(f.download_url);
                const buf = new Uint8Array(await r2.arrayBuffer());
                py.FS.writeFile("/home/pyodide/" + f.name, buf);
              }
            }
          }
        }
      } catch (e) { /* ignore data-file fetch errors */ }

      const res = await runPythonInBrowser(SUB_ITEM_SHIM + codeBox.value, () => {});
      outBox.value = (res.stdout || "") + (res.stderr ? "\n" + res.stderr.replace(/Matplotlib is currently using agg.*\n/g, "") : "");
      const figWrap = document.getElementById("subFigures");
      figWrap.innerHTML = "";
      if (res.figures && res.figures.length) {
        res.figures.forEach((b64) => {
          const img = document.createElement("img");
          img.src = "data:image/png;base64," + b64;
          img.alt = "Plot output";
          img.style.cssText = "max-width:100%;border-radius:10px;background:#fff;padding:8px;border:1px solid var(--line);";
          figWrap.appendChild(img);
        });
      }
    } catch (err) {
      outBox.value = "Error: " + (err.message || err);
    } finally {
      btn.disabled = false;
    }
  };

  document.getElementById("subClose").onclick = () => (overlay.style.display = "none");
  document.getElementById("subSave").onclick = () => {
    const s = subItemStore();
    s[key] = { code: document.getElementById("subCode").value, output: document.getElementById("subOutput").value };
    localStorage.setItem("subItemData", JSON.stringify(s));
    toast("Saved!");
    overlay.style.display = "none";
  };
}

/* ---- custom experiments created in the UI (persisted) ---- */
function labPdfs() {
  try { return JSON.parse(localStorage.getItem("labManualPdfs") || "[]"); } catch { return []; }
}
const PORTFOLIO_BASE_COUNT = PORTFOLIO.length;      // built-in experiments (1..7)
const PORTFOLIO_BASE_IDS = new Set(PORTFOLIO.map((e) => e.id));
try {
  const savedCustom = JSON.parse(localStorage.getItem("customExp") || "[]");
  // Drop old placeholders (e.g. a hand-made "Experiment 6 – New experiment." card)
  // that collide with the built-in experiments — keep only real user-made ones.
  const validCustom = Array.isArray(savedCustom)
    ? savedCustom.filter((c) => c && c.title && !PORTFOLIO_BASE_IDS.has(Number(c.id)))
    : [];
  PORTFOLIO.push(...validCustom);
  localStorage.setItem("customExp", JSON.stringify(PORTFOLIO.slice(PORTFOLIO_BASE_COUNT)));
} catch (e) { /* ignore */ }

function bindNewExperimentForm() {
  const addExpBtn = document.getElementById("addExpBtn");
  const newExpForm = document.getElementById("newExpForm");
  const neCancel = document.getElementById("neCancel");
  const neSave = document.getElementById("neSave");
  if (!addExpBtn) return;
  addExpBtn.addEventListener("click", () => {
    newExpForm.style.display = newExpForm.style.display === "none" ? "block" : "none";
  });
  if (neCancel) neCancel.addEventListener("click", () => { newExpForm.style.display = "none"; });
  if (neSave) neSave.addEventListener("click", () => {
    const title = document.getElementById("neTitle").value.trim();
    const desc = document.getElementById("neDesc").value.trim();
    const raw = document.getElementById("neItems").value.trim();
    if (!title) { toast("Please enter a title."); return; }
    const items = raw
      ? raw.split(",").map((part) => {
          const idx = part.indexOf(":");
          const tag = idx > -1 ? part.slice(0, idx).trim() : "•";
          const name = idx > -1 ? part.slice(idx + 1).trim() : part.trim();
          return { tag, name, path: "" };
        }).filter((it) => it.name)
      : [];
    const nextId = Math.max(0, ...PORTFOLIO.map((e) => e.id)) + 1;
    PORTFOLIO.push({ id: nextId, title, desc: desc || "New experiment.", items, video: "" });
    const customs = PORTFOLIO.slice(PORTFOLIO_BASE_COUNT);
    localStorage.setItem("customExp", JSON.stringify(customs));
    toast("Experiment added!");
    renderHome();
  });
}

let currentFilter = "";

function filteredExperiments() {
  const q = currentFilter.trim().toLowerCase();
  if (!q) return EXPERIMENTS;
  return EXPERIMENTS.filter((e) => e.name.toLowerCase().includes(q));
}

function expListItemHTML(e) {
  const parts = e.sections.map((s) => s.letter).join(" · ");
  return `
    <button class="exp-item" type="button" data-exp="${e.id}">
      <span class="exp-item-num">${e.number}</span>
      <span class="exp-item-info">
        <span class="exp-item-name">${esc(e.name)}</span>
        <span class="exp-item-meta">${e.sections.length} sections &nbsp;(${esc(parts)})</span>
      </span>
      <svg class="exp-item-arrow" width="18" height="18" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
        <path d="M9 6l6 6-6 6"/>
      </svg>
    </button>`;
}

function refreshExperimentList() {
  const listEl = document.getElementById("expList");
  const countEl = document.getElementById("expCount");
  if (!listEl) return;
  const matches = filteredExperiments();
  listEl.innerHTML = matches.length
    ? matches.map(expListItemHTML).join("")
    : `<div class="exp-empty">No experiments match “${esc(currentFilter)}”.</div>`;
  if (countEl) {
    countEl.textContent = `${matches.length} of ${EXPERIMENTS.length} experiments`;
  }
  listEl.querySelectorAll("[data-exp]").forEach((btn) => {
    btn.addEventListener("click", () => {
      location.hash = `#/experiment/${btn.dataset.exp}`;
    });
  });
}

function refreshSuggestions() {
  const box = document.getElementById("searchSuggest");
  if (!box) return;
  const q = currentFilter.trim();
  if (!q) {
    box.classList.remove("open");
    box.innerHTML = "";
    return;
  }
  const matches = filteredExperiments();
  box.innerHTML = matches.length
    ? matches
        .map(
          (e) => `
        <button class="suggest-item" type="button" data-exp="${e.id}">
          <span class="suggest-num">EXP ${e.number}</span>
          <span>${esc(e.name)}</span>
        </button>`
        )
        .join("")
    : `<div class="suggest-empty">No matching experiments…</div>`;
  box.classList.add("open");

  box.querySelectorAll("[data-exp]").forEach((btn) => {
    btn.addEventListener("mousedown", (ev) => {
      ev.preventDefault();
      location.hash = `#/experiment/${btn.dataset.exp}`;
    });
  });
}

function openStudentEdit() {
  let overlay = document.getElementById("studentEditOverlay");
  if (overlay) overlay.remove();
  overlay = document.createElement("div");
  overlay.id = "studentEditOverlay";
  overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center;z-index:1100;padding:20px;";
  document.body.appendChild(overlay);
  const inp = (id, value) => `<input id="${id}" value="${esc(value)}" style="width:100%;padding:10px;margin:6px 0 14px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);font-size:14px;">`;
  overlay.innerHTML = `
    <div style="background:var(--card);border:1px solid var(--gold);border-radius:20px;max-width:520px;width:100%;max-height:90vh;overflow:auto;padding:24px;">
      <h3 style="color:var(--ink);margin-bottom:12px;">✏ Edit Details</h3>
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Name</label>${inp("eName", STUDENT.name)}
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">ID Number</label>${inp("eId", STUDENT.idNumber)}
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Section</label>${inp("eSec", STUDENT.section)}
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Faculty</label>${inp("eFac", STUDENT.faculty)}
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Profession</label>${inp("eProf", STUDENT.profession)}
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">University Name</label>${inp("eUni", SITE.universityName)}
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Lab Name</label>${inp("eLab", SITE.labName)}
      <label style="color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Subject Code</label>${inp("eCode", SITE.subjectCode)}
      <div style="margin-top:6px;">
        <button id="eSave" class="btn btn-primary" type="button">💾 Save Changes</button>
        <button id="eCancel" class="btn" type="button" style="margin-left:8px;">Cancel</button>
      </div>
    </div>`;
  document.getElementById("eSave").onclick = () => {
    STUDENT.name = document.getElementById("eName").value.trim();
    STUDENT.idNumber = document.getElementById("eId").value.trim();
    STUDENT.section = document.getElementById("eSec").value.trim();
    STUDENT.faculty = document.getElementById("eFac").value.trim();
    STUDENT.profession = document.getElementById("eProf").value.trim();
    SITE.universityName = document.getElementById("eUni").value.trim();
    SITE.labName = document.getElementById("eLab").value.trim();
    SITE.subjectCode = document.getElementById("eCode").value.trim();
    localStorage.setItem("mbuHomeEdits", JSON.stringify({ SITE: { ...SITE }, STUDENT: { ...STUDENT } }));
    toast("Saved! Your changes are kept in this browser.");
    overlay.remove();
    renderHome();
  };
  document.getElementById("eCancel").onclick = () => overlay.remove();
}

function bindHomeInteractions() {
  const input = document.getElementById("searchInput");
  const suggest = document.getElementById("searchSuggest");
  const addBtn = document.getElementById("addBtn");

  refreshExperimentList();

  // ---- Search / filter with autocomplete ----
  input.addEventListener("input", () => {
    currentFilter = input.value;
    refreshExperimentList();
    refreshSuggestions();
  });
  input.addEventListener("focus", refreshSuggestions);
  input.addEventListener("blur", () =>
    setTimeout(() => suggest.classList.remove("open"), 150)
  );
  input.addEventListener("keydown", (ev) => {
    const items = [...suggest.querySelectorAll(".suggest-item")];
    let idx = items.findIndex((el) => el.classList.contains("active"));
    if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
      ev.preventDefault();
      idx = ev.key === "ArrowDown" ? idx + 1 : idx - 1;
      if (idx < 0) idx = items.length - 1;
      if (idx >= items.length) idx = 0;
      items.forEach((el) => el.classList.remove("active"));
      if (items[idx]) items[idx].classList.add("active");
    } else if (ev.key === "Enter") {
      const target = items[idx] && idx >= 0 ? items[idx] : items[0];
      if (target) location.hash = `#/experiment/${target.dataset.exp}`;
      else {
        const first = filteredExperiments()[0];
        if (first) location.hash = `#/experiment/${first.id}`;
        else toast("No experiments match your search.");
      }
    } else if (ev.key === "Escape") {
      input.value = "";
      currentFilter = "";
      refreshExperimentList();
      refreshSuggestions();
    }
  });

  // ---- ✏ Edit Details (opens a simple form) ----
  const editBtn = document.getElementById("editDetailsBtn");
  if (editBtn) editBtn.addEventListener("click", openStudentEdit);

  // ---- + ADD → open the next experiment page (first visible) ----
  if (addBtn) addBtn.addEventListener("click", () => {
    const first = filteredExperiments()[0];
    if (first) location.hash = `#/experiment/${first.id}`;
    else toast("No experiments available to add.");
  });

  // ---- Modules heading toggle ----
  const modulesToggle = document.getElementById("modulesToggle");
  const modulesList = document.getElementById("modulesList");
  if (modulesToggle && modulesList) {
    modulesToggle.addEventListener("click", () => {
      const open = modulesList.style.display !== "none";
      modulesList.style.display = open ? "none" : "grid";
      modulesToggle.querySelector("h2").textContent = open ? "Modules ▸" : "Modules ▾";
      modulesToggle.querySelector(".exp-count").textContent = open ? "click to view modules" : `${MODULES.length} modules`;
    });
  }

  // ---- Lab Manual PDF upload ----
  const pdfUpload = document.getElementById("pdfUpload");
  if (pdfUpload) {
    pdfUpload.addEventListener("change", async (ev) => {
      const files = [...ev.target.files];
      const arr = labPdfs();
      for (const f of files) {
        const dataUrl = await new Promise((res) => {
          const r = new FileReader();
          r.onload = () => res(r.result);
          r.readAsDataURL(f);
        });
        arr.push({ name: f.name, url: dataUrl });
      }
      localStorage.setItem("labManualPdfs", JSON.stringify(arr));
      renderHome();
    });
  }
  // ---- Change photo (upload + crop) ----
  const changePhotoBtn = document.getElementById("changePhotoBtn");
  if (changePhotoBtn) {
    changePhotoBtn.addEventListener("click", () => {
      const inp = document.createElement("input");
      inp.type = "file";
      inp.accept = "image/*";
      inp.onchange = () => { if (inp.files && inp.files[0]) openPhotoCrop(inp.files[0]); };
      inp.click();
    });
  }

  document.querySelectorAll("[data-pdfrem]").forEach((b) => {
    b.addEventListener("click", () => {
      const arr = labPdfs().filter((_, i) => i !== Number(b.dataset.pdfrem));
      localStorage.setItem("labManualPdfs", JSON.stringify(arr));
      renderHome();
    });
  });

  // ---- Delete a custom (user-made) experiment card ----
  document.querySelectorAll("[data-delport]").forEach((b) => {
    b.addEventListener("click", () => {
      const id = Number(b.dataset.delport);
      const i = PORTFOLIO.findIndex((e) => e.id === id);
      if (i > -1) PORTFOLIO.splice(i, 1);
      localStorage.setItem("customExp", JSON.stringify(PORTFOLIO.slice(PORTFOLIO_BASE_COUNT)));
      toast("Experiment deleted.");
      renderHome();
    });
  });
}

/* ============================================================
   PAGE 2 — EXPERIMENT PREVIEW
   ============================================================ */

function renderPreview(exp) {
  viewEl.innerHTML = `
    <div class="page-head">
      <button class="btn btn-back" data-back="#/home" type="button">← Back</button>
      <span class="crumb">Home / Experiments / <b>Experiment ${exp.number}</b></span>
    </div>

    <div class="split-grid">

      <!-- RIGHT — experiment name -->
      <section class="card name-panel">
        <div class="panel-eyebrow">Experiment Name</div>
        <h1 class="panel-title">${esc(exp.name)}</h1>
        <p class="panel-sub">Experiment ${exp.number} · ${esc(SITE.labName)}</p>
        <div class="panel-chips">
          <span class="chip">${exp.sections.length} sections</span>
          ${exp.sections.map((s) => `<span class="chip">${esc(s.letter)}</span>`).join("")}
        </div>
      </section>
    </div>

    <!-- BELOW BOTH — clickable Overview -->
    <a class="card overview-cta" href="#/experiment/${exp.id}/overview">
      <div class="overview-cta-text">
        <h3>Overview
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f46e5"
               stroke-width="2.2" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </h3>
        <p>Open the full experiment overview — sections, videos, links & summary.</p>
      </div>
      <span class="overview-cta-arrow">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.6" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg>
      </span>
    </a>
  `;

  bindAllHoverPreviews(viewEl);
  bindBackButtons();
}

/* ============================================================
   PAGE 3 — EXPERIMENT OVERVIEW / DETAILS
   ============================================================ */

function renderOverview(exp) {
  viewEl.innerHTML = `
    <div class="page-head">
      <button class="btn btn-back" data-back="#/experiment/${exp.id}" type="button">← Back</button>
      <span class="crumb">Home / Experiment ${exp.number} / <b>Overview</b></span>
    </div>

    <div class="split-grid">

      <!-- RIGHT — experiment name + dynamic section list -->
      <section class="card name-panel">
        <div class="panel-eyebrow">Experiment Name</div>
        <h1 class="panel-title">${esc(exp.name)}</h1>
        <p class="panel-sub">Select any section below to open its video &amp; code.</p>

        <div class="section-grid">
          ${exp.sections
            .map(
              (s) => `
            <button class="section-tile" type="button"
                    data-section="${esc(s.letter)}" title="${esc(s.title || "Section " + s.letter)}">
              <span class="letter">${esc(s.letter)}</span>
              <span class="tile-label">Section</span>
            </button>`
            )
            .join("")}
        </div>
      </section>
    </div>

    <!-- BELOW — YouTube video (left), links, summary -->
    <div class="detail-grid">
      <div class="detail-stack">

        <div class="card video-card">
          <div class="yt-frame">
            <iframe src="${esc(exp.youtubeVideo)}" title="YouTube video for ${esc(exp.name)}"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen loading="lazy"></iframe>
          </div>
          <div class="video-caption">Full tutorial video for this experiment.</div>
        </div>

        <div class="card detail-card">
          <h3>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#ef4444"><path d="M23 7.2s-.2-1.6-.9-2.3c-.9-.9-1.9-.9-2.4-1C16.6 3.5 12 3.5 12 3.5s-4.6 0-7.7.4c-.5.1-1.5.1-2.4 1-.7.7-.9 2.3-.9 2.3S.6 9.1.6 11v1.8c0 1.9.4 3.8.4 3.8s.2 1.6.9 2.3c.9.9 2 .9 2.5 1 1.9.2 7.6.4 7.6.4s4.6 0 7.7-.4c.5-.1 1.5-.1 2.4-1 .7-.7.9-2.3.9-2.3s.4-1.9.4-3.8V11c0-1.9-.4-3.8-.4-3.8ZM9.7 15V8.4l6.3 3.3L9.7 15Z"/></svg>
            YouTube Link
          </h3>
          <div class="link-row">
            <a href="${esc(exp.youtubeLink)}" target="_blank" rel="noopener noreferrer">${esc(exp.youtubeLink)}</a>
          </div>
        </div>

        <div class="card detail-card">
          <h3>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#0f172a"><path d="M12 .5A11.5 11.5 0 0 0 .5 12a11.5 11.5 0 0 0 7.9 10.9c.6.1.8-.2.8-.5v-2c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.3-1.7-1.3-1.7-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.7 1.3 3.4 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.4-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0C17.3 4.9 18.3 5.2 18.3 5.2c.6 1.6.2 2.8.1 3.1.8.8 1.2 1.8 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.2c0 .3.2.6.8.5A11.5 11.5 0 0 0 23.5 12 11.5 11.5 0 0 0 12 .5Z"/></svg>
            GitHub Link
          </h3>
          <div class="link-row">
            <a href="${esc(exp.githubLink)}" target="_blank" rel="noopener noreferrer">${esc(exp.githubLink)}</a>
          </div>
        </div>

        <div class="card detail-card">
          <h3>📄 Summary of Experiment</h3>
          <p class="summary-text">${esc(exp.summary)}</p>
        </div>

      </div>

      <!-- Right column — quick section jump -->
      <div class="detail-stack">
        <div class="card detail-card">
          <h3>Jump to a section</h3>
          <div class="section-grid">
            ${exp.sections
              .map(
                (s) => `
              <button class="section-tile" type="button" data-section="${esc(s.letter)}">
                <span class="letter">${esc(s.letter)}</span>
                <span class="tile-label">Section</span>
              </button>`
              )
              .join("")}
          </div>
        </div>
        <div class="card detail-card">
          <h3>Experiment info</h3>
          <p class="summary-text">
            <b>Experiment ${exp.number}</b> · ${esc(exp.name)}<br/>
            ${exp.sections.length} sections: ${exp.sections.map((s) => esc(s.letter)).join(", ")}
          </p>
        </div>
      </div>
    </div>
  `;

  bindAllHoverPreviews(viewEl);
  bindBackButtons();
  viewEl.querySelectorAll("[data-section]").forEach((btn) => {
    btn.addEventListener("click", () => {
      location.hash = `#/experiment/${exp.id}/section/${btn.dataset.section}`;
    });
  });
}

/* ============================================================
   PAGE 4 — INDIVIDUAL EXPERIMENT SECTION (video + code)
   ============================================================ */

function renderSection(exp, letter) {
  const section = exp.sections.find(
    (s) => s.letter.toLowerCase() === String(letter).toLowerCase()
  );
  if (!section) {
    location.hash = `#/experiment/${exp.id}/overview`;
    return;
  }

  const codeId = `code-${exp.id}-${section.letter}`;

  viewEl.innerHTML = `
    <div class="page-head">
      <button class="btn btn-back" data-back="#/experiment/${exp.id}/overview" type="button">← Back</button>
      <span class="crumb">Home / Experiment ${exp.number} / Overview / <b>Section ${esc(section.letter)}</b></span>
    </div>

    <div class="section-title-row">
      <h1 class="exp-big-title">Experiment ${exp.number}</h1>
      <span class="section-letter-badge">${esc(section.letter)}</span>
    </div>
    <p class="section-subtitle">${esc(section.title || exp.name)} — ${esc(exp.name)}</p>

    <div class="section-grid-4">
      <div class="section-main">

        <!-- LEFT — section video (normal playback) -->
        ${videoCardHTML(section.video, {
          badge: `Section ${esc(section.letter)}`,
          caption: "Section video — use the player controls to play, pause and seek.",
          preview: false,
        })}

        <!-- BELOW VIDEO — code (independently scrollable) + Python compiler -->
        <div class="code-card">
          <div class="code-head">
            <div class="code-head-left">
              <span class="code-dots"><span></span><span></span><span></span></span>
              <span class="code-title">Code — experiment_${exp.number}${esc(section.letter.toLowerCase())}.py</span>
            </div>
            <div class="code-actions">
              <button class="code-btn run" id="runBtn" type="button">▶ Run Code</button>
              <button class="code-btn" id="playVideoBtn" type="button">🎬 Play Output Video</button>
              <button class="code-btn" id="editBtn" type="button">✎ Edit</button>
              <button class="code-btn" id="copyBtn" type="button">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2.2" stroke-linecap="round"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
                Copy Code
              </button>
            </div>
          </div>
          <div class="code-scroll" id="${codeId}">
            ${renderCodeBlock(section.code)}
          </div>
          <div class="code-footer">
            <span>Python · ${section.code.split("\n").length} lines</span>
            <span>⟳ code area scrolls independently — the page stays still</span>
          </div>
        </div>

        <!-- PYTHON COMPILER CONSOLE -->
        <div class="console-card">
          <div class="console-head">
            <span class="console-title">Python Console — real in-browser execution</span>
            <span class="console-status" id="pyStatus">Runtime loads on first run (≈10 s once)</span>
          </div>
          <div class="console-body" id="pyOut">
            <div class="console-hint">Press <b>▶ Run Code</b> to execute this Python program right here
            in your browser — no server needed. Plots render below the text output.</div>
          </div>
        </div>

      </div>

      <!-- RIGHT — other sections quick nav -->
      <aside class="section-side">
        <div class="card detail-card">
          <h3>Sections of Experiment ${exp.number}</h3>
          <div class="section-grid">
            ${exp.sections
              .map(
                (s) => `
              <button class="section-tile" type="button" data-section="${esc(s.letter)}"
                      ${s.letter === section.letter ? 'style="border-color:#4f46e5;background:#eef2ff"' : ""}>
                <span class="letter">${esc(s.letter)}</span>
                <span class="tile-label">Section</span>
              </button>`
              )
              .join("")}
          </div>
        </div>
      </aside>
    </div>
  `;

  bindBackButtons();
  viewEl.querySelectorAll("[data-section]").forEach((btn) => {
    btn.addEventListener("click", () => {
      location.hash = `#/experiment/${exp.id}/section/${btn.dataset.section}`;
    });
  });

  // ---- Section code state (user can edit before running) ----
  let currentCode = section.code;
  let editing = false;
  const codeBox = document.getElementById(codeId);
  const runBtn = document.getElementById("runBtn");
  const editBtn = document.getElementById("editBtn");
  const copyBtn = document.getElementById("copyBtn");
  const pyOut = document.getElementById("pyOut");
  const pyStatus = document.getElementById("pyStatus");

  // ---- 🎬 Play Output Video: plays the 10s video of this section's output ----
  const playVideoBtn = document.getElementById("playVideoBtn");
  if (playVideoBtn) {
    playVideoBtn.addEventListener("click", () => {
      const vid = document.getElementById("sectionVideo");
      if (!vid) return;
      vid.scrollIntoView({ behavior: "smooth", block: "center" });
      vid.currentTime = 0;
      vid.muted = true;
      const p = vid.play();
      if (p && p.catch) p.catch(() => {});
    });
  }

  // ---- Edit toggle: highlighted view <-> editable textarea ----
  editBtn.addEventListener("click", () => {
    if (!editing) {
      editing = true;
      codeBox.outerHTML = `<textarea class="code-edit" id="${codeId}" spellcheck="false">${esc(currentCode)}</textarea>`;
      editBtn.textContent = "✕ Done";
      toast("Edit mode — modify the code, then press Run.");
    } else {
      editing = false;
      const ta = document.getElementById(codeId);
      currentCode = ta.value;
      ta.outerHTML = `<div class="code-scroll" id="${codeId}">${renderCodeBlock(currentCode)}</div>`;
      editBtn.textContent = "✎ Edit";
    }
  });

  // ---- Copy code ----
  copyBtn.addEventListener("click", async () => {
    if (editing) currentCode = document.getElementById(codeId).value;
    try {
      await navigator.clipboard.writeText(currentCode);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = currentCode;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
    }
    copyBtn.classList.add("copied");
    copyBtn.textContent = "✓ Copied!";
    toast("Code copied to clipboard.");
    setTimeout(() => { copyBtn.classList.remove("copied"); copyBtn.textContent = "Copy Code"; }, 1800);
  });

  // ---- Run code in the browser (Pyodide = real Python) ----
  const setStatus = (msg, spinning = true) => {
    pyStatus.innerHTML = spinning
      ? `<span class="spinner"></span> ${esc(msg)}`
      : esc(msg);
  };

  // Preload the Python runtime in the background so the first Run feels instant
  setStatus("Pre-loading Python runtime in the background…");
  getPyodide(() => {})
    .then(() => setStatus("Python runtime ready — press ▶ Run Code", false))
    .catch(() => setStatus("Runtime will load on first run (internet needed once)", false));

  runBtn.addEventListener("click", async () => {
    if (editing) currentCode = document.getElementById(codeId).value;
    runBtn.disabled = true;
    const fname = `experiment_${exp.number}${section.letter.toLowerCase()}.py`;
    pyOut.innerHTML = `<div class="console-cmd">PS C:\\MBU-DS-Lab&gt; python ${fname}</div>`;
    try {
      const res = await runPythonInBrowser(currentCode, (m) => setStatus(m));
      if (res.stdout) {
        const el = document.createElement("div");
        el.className = "console-stdout";
        el.textContent = res.stdout;
        pyOut.appendChild(el);
      }
      if (res.stderr) {
        const el = document.createElement("div");
        el.className = "console-stderr";
        el.textContent = res.stderr;
        pyOut.appendChild(el);
      }
      res.figures.forEach((b64) => {
        const img = document.createElement("img");
        img.className = "console-img";
        img.alt = "Plot output";
        img.src = "data:image/png;base64," + b64;
        pyOut.appendChild(img);
      });
      const done = document.createElement("div");
      done.className = "console-done";
      done.textContent = res.ok
        ? `✓ Program finished successfully${res.figures.length ? ` — ${res.figures.length} figure(s) rendered` : ""}.`
        : "✗ Program ended with an error.";
      pyOut.appendChild(done);
      setStatus(res.ok ? "Execution complete" : "Execution failed — see console", false);
      if (!res.ok) toast("Python raised an error — see the console output.");
    } catch (err) {
      pyOut.innerHTML += `<div class="console-stderr">${esc(err.message || String(err))}</div>`;
      setStatus("Failed to load the Python runtime (check internet connection).", false);
      toast("Could not load the Python runtime.");
    } finally {
      runBtn.disabled = false;
      pyOut.scrollTop = pyOut.scrollHeight;
    }
  });
}

/* ============================================================
   ROUTER
   ============================================================ */

function bindBackButtons() {
  viewEl.querySelectorAll("[data-back]").forEach((btn) => {
    btn.addEventListener("click", () => {
      location.hash = btn.dataset.back;
    });
  });
}

function route() {
  const hash = location.hash.replace(/^#\/?/, "");
  const parts = hash.split("/").filter(Boolean);

  let html = null;
  if (parts.length === 0 || parts[0] === "home") {
    renderHome();
  } else if (parts[0] === "experiment" && parts[1]) {
    const exp = getExperiment(parts[1]);
    if (!exp) {
      renderHome();
    } else if (parts[2] === "overview") {
      renderOverview(exp);
    } else if (parts[2] === "section" && parts[3]) {
      renderSection(exp, decodeURIComponent(parts[3]));
    } else {
      renderPreview(exp);
    }
  } else {
    renderHome();
  }

  // Smooth page transition
  window.scrollTo(0, 0);
  viewEl.classList.remove("view-active");
  void viewEl.offsetWidth; // restart animation
  viewEl.classList.add("view-active");
}

window.addEventListener("hashchange", route);
document.getElementById("year").textContent = new Date().getFullYear();

if (!location.hash) location.hash = "#/home";
route();
