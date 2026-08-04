// ============================================================
//  Pinterest Board Pin Extractor — Browser Console Script
// ============================================================
//  Usage:
//    1. Open a Pinterest board page in your browser
//    2. Open DevTools (F12) → Console tab
//    3. Paste this entire script and press Enter
//    4. Wait for it to finish auto-scrolling
//    5. All pin URLs will be printed & copied to clipboard
// ============================================================

(async () => {
  const SCROLL_STEP = window.innerHeight * 2;
  const SCROLL_DELAY = 1500;
  const STABLE_THRESHOLD = 5;

  const getUniquePinIds = () => {
    const ids = new Set();
    document.querySelectorAll('a[href*="/pin/"]').forEach(a => {
      const m = a.href.match(/\/pin\/(\d+)/);
      if (m) ids.add(m[1]);
    });
    return ids;
  };

  // ── Auto-scroll ──────────────────────────────────────────
  console.log("%c⏳ Scrolling to load all pins...", "color: #E60023; font-size: 14px; font-weight: bold;");

  window.scrollTo(0, 0);
  await new Promise(r => setTimeout(r, 800));

  let lastCount = 0;
  let stableRounds = 0;

  while (stableRounds < STABLE_THRESHOLD) {
    window.scrollBy(0, SCROLL_STEP);
    await new Promise(r => setTimeout(r, SCROLL_DELAY));

    const currentCount = getUniquePinIds().size;
    if (currentCount === lastCount) {
      stableRounds++;
    } else {
      stableRounds = 0;
      lastCount = currentCount;
      console.log(`   Loaded: ${currentCount} pins`);
    }
  }

  // ── Extract ──────────────────────────────────────────────
  const pinIds = getUniquePinIds();
  const domain = window.location.hostname;
  const urls = [...pinIds].map(id => `https://${domain}/pin/${id}/`);

  // ── Output ───────────────────────────────────────────────
  console.log(`\n%c✅ Extraction complete: ${urls.length} unique pins found`, "color: #00C853; font-size: 14px; font-weight: bold;");
  console.log("\n" + urls.join("\n"));

  // ── Copy to clipboard ────────────────────────────────────
  try {
    await navigator.clipboard.writeText(urls.join("\n"));
    console.log(`\n%c📋 All ${urls.length} URLs copied to clipboard`, "color: #2196F3; font-size: 13px; font-weight: bold;");
  } catch {
    console.log("\n⚠️ Clipboard copy failed — manually select and copy the URLs above.");
  }

  // ── Scroll back to top ───────────────────────────────────
  window.scrollTo({ top: 0, behavior: "smooth" });
})();
