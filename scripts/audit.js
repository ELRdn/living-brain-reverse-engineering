// Compact in-page audit: headings, alt text, contrast, tap targets, overflow.
() => {
  const doc = document;
  const de = doc.documentElement;
  const parse = (c) => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(",").map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const lum = ({ r, g, b }) => {
    const f = (v) => ((v /= 255), v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => {
    const x = lum(a), y = lum(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  };
  const bgOf = (el) => {
    let n = el;
    while (n && n !== de) {
      const raw = getComputedStyle(n).backgroundColor;
      if (raw && raw !== "rgba(0, 0, 0, 0)" && raw !== "transparent") {
        const c = parse(raw);
        // Unparseable colour space (e.g. lab()) — stop and report unknown.
        return c && c.a > 0.5 ? c : null;
      }
      n = n.parentElement;
    }
    return { r: 255, g: 255, b: 255 };
  };

  const hs = [...doc.querySelectorAll("h1,h2,h3,h4,h5,h6")].map((h) => ({
    l: +h.tagName[1],
    t: h.textContent.trim().slice(0, 40),
  }));
  const skips = [];
  for (let i = 1; i < hs.length; i++) if (hs[i].l - hs[i - 1].l > 1) skips.push(`${hs[i - 1].l}->${hs[i].l}`);

  const imgs = [...doc.querySelectorAll("img")].filter((i) => i.getBoundingClientRect().width > 0);
  const ctrls = [...doc.querySelectorAll("a,button,summary,input")];
  const samples = [...doc.querySelectorAll("p,li,span,a,b,small,figcaption,summary,h1,h2,h3")]
    .filter((el) => el.children.length === 0 && (el.textContent || "").trim().length > 2)
    .filter((el) => el.getBoundingClientRect().width > 0 && !el.closest("[aria-hidden=true]"))
    .slice(0, 300);

  const fails = samples
    .map((el) => {
      const st = getComputedStyle(el);
      const fg = parse(st.color);
      if (!fg) return null;
      const size = parseFloat(st.fontSize);
      const weight = Number(st.fontWeight) || 400;
      const bg = bgOf(el);
      if (!bg) return null;
      const r = ratio(fg, bg);
      const need = size >= 24 || (size >= 18.66 && weight >= 700) ? 3 : 4.5;
      return r < need ? { r: Math.round(r * 100) / 100, size, text: el.textContent.trim().slice(0, 30) } : null;
    })
    .filter(Boolean);

  return {
    lang: de.getAttribute("lang"),
    h1: hs.filter((h) => h.l === 1).length,
    skips,
    images: { total: imgs.length, missingAlt: imgs.filter((i) => !i.hasAttribute("alt")).length },
    contrast: { sampled: samples.length, failures: fails.length, worst: fails.sort((a, b) => a.r - b.r).slice(0, 5) },
    tap: {
      total: ctrls.length,
      under24: ctrls.filter((c) => {
        const r = c.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && (r.height < 24 || r.width < 24);
      }).length,
    },
    overflow: de.scrollWidth > innerWidth + 1,
    scrollWidth: de.scrollWidth,
  };
}
