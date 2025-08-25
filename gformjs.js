
// ✅ Google Forms → JSON mapping for your Python app
// Works on the public "viewform" page. Copies JSON to clipboard + logs it.

(async function () {
  function findFB() {
    if (typeof window.FB_PUBLIC_LOAD_DATA_ !== "undefined") return window.FB_PUBLIC_LOAD_DATA_;
    // Fallback: parse from a <script> tag if the global isn't set
    for (const s of Array.from(document.scripts)) {
      const t = s.textContent || "";
      if (t.includes("FB_PUBLIC_LOAD_DATA_ =")) {
        const m = t.match(/FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);/s);
        if (m) {
          try { return JSON.parse(m[1]); } catch (_) { /* it isn't strict JSON */ }
          try { /* last resort: eval just the array literal */ return (0, eval)("(" + m[1] + ")"); } catch (_) {}
        }
      }
    }
    return null;
  }

  function isNumber(x){ return typeof x === "number" && isFinite(x); }

  // Heuristic BFS in case Google shuffles indices in the future
  function guessItemsTree(root) {
    // Common fast path first: data[1][1] is the items array on most forms.
    if (Array.isArray(root) && root[1] && Array.isArray(root[1][1]) && Array.isArray(root[1][1][0])) {
      return root[1][1];
    }
    // BFS fallback to locate the "items" list (array of question arrays)
    const q = [root];
    let steps = 0;
    while (q.length && steps < 10000) {
      const n = q.shift(); steps++;
      if (Array.isArray(n) && n.length > 0) {
        const looksLikeItems =
          n.every(el => Array.isArray(el) && isNumber(el[0]) && isNumber(el[3]) && Array.isArray(el[4]));
        if (looksLikeItems) return n;
        for (const v of n) q.push(v);
      } else if (n && typeof n === "object") {
        for (const v of Object.values(n)) q.push(v);
      }
    }
    return null;
  }

  function textArray(a) {
    if (!Array.isArray(a)) return [];
    return a
      .map(x => Array.isArray(x) ? (x[0] != null ? String(x[0]).trim() : "") : (x != null ? String(x).trim() : ""))
      .filter(s => s && !/^choose/i.test(s)); // drop "Choose..." placeholders
  }

  const TYPE = { SHORT:0, PARAGRAPH:1, MC:2, DROPDOWN:3, CHECKBOX:4, LINEAR:5, SECTION:6, MC_GRID:7, CHECKBOX_GRID:8, DATE:9, TIME:10 };

  const fb = findFB();
  if (!fb) {
    console.error("Could not locate FB_PUBLIC_LOAD_DATA_. Make sure you're on the public /viewform page (not the editor).");
    alert("Could not find form data. Open the public 'viewform' URL and run again.");
    return;
  }

  const items = guessItemsTree(fb);
  if (!Array.isArray(items) || items.length === 0) {
    console.error("Failed to locate the questions array inside FB_PUBLIC_LOAD_DATA_.");
    alert("Failed to parse form structure. This form may be unsupported.");
    return;
  }

  const out = {}; // { "entry.<id>": { options: [...], open_ended: boolean } }

  for (const q of items) {
    // Expected question record: [questionId, title, description, typeCode, answerBlocks, ...]
    const type = q && q[3];
    const blocks = q && q[4];

    if (!Array.isArray(blocks)) continue;

    // Grids: each row is its own entry.<id>, with columns as options
    if (type === TYPE.MC_GRID || type === TYPE.CHECKBOX_GRID) {
      for (const row of blocks) {
        if (!Array.isArray(row)) continue;
        const entryId = row[0];
        const columns = textArray(row[1]);
        if (isNumber(entryId)) {
          out["entry." + entryId] = { options: columns, open_ended: false };
        }
      }
      continue;
    }

    // Everything else (single-entry questions) lives in blocks[0]
    const ans = blocks[0];
    if (!Array.isArray(ans)) continue;
    const entryId = ans[0];

    if (!isNumber(entryId)) continue;

    // Open-ended types
    if (type === TYPE.SHORT || type === TYPE.PARAGRAPH || type === TYPE.DATE || type === TYPE.TIME) {
      out["entry." + entryId] = { options: [], open_ended: true };
      continue;
    }

    // Options-based types
    if (type === TYPE.MC || type === TYPE.DROPDOWN || type === TYPE.CHECKBOX || type === TYPE.LINEAR) {
      const opts = textArray(ans[1]);
      out["entry." + entryId] = { options: opts, open_ended: false };
      continue;
    }

    // Fallback: if options exist, treat as options; otherwise open-ended
    const maybeOpts = textArray(ans[1]);
    out["entry." + entryId] = { options: maybeOpts, open_ended: maybeOpts.length === 0 };
  }

  const json = JSON.stringify(out, null, 2);
  console.clear();
  console.log("✅ Parsed Google Form → entry-id map:\n");
  console.log(json);

  try {
    await (navigator.clipboard && navigator.clipboard.writeText(json));
    console.log("\n📋 Copied to clipboard. Paste it into your Python app.");
  } catch (_) {
    console.log("\n(Clipboard write failed — copy from the console output above.)");
  }
})();

