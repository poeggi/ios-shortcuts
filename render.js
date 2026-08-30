/* Shared rendering for every page. The index and each shortcut's own page
   build their card and action list from the same functions, so a shortcut
   added to shortcuts.json later looks exactly like the ones already there.
   A page one level down sets window.BASE before loading this file. */

const BASE = window.BASE || '';
const REPO = 'https://github.com/poeggi/ios-shortcuts/blob/main/';

const esc = s => String(s).replace(/[&<>"]/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* A value arrives as segments so that a variable reference is drawn as a
   token, the way the Shortcuts editor draws it, while a literal bracket in
   the text stays a literal bracket. */
const segs = list => (list || []).map(p =>
  p.t === 'var' ? `<span class="var">${esc(p.v)}</span>` : esc(p.v)).join('');

const dir = s => s.slug
  ? `${BASE}shortcuts/${encodeURIComponent(s.slug)}/${encodeURIComponent(s.slug)}` : '';

function header(s) {
  const base = dir(s);
  const icon = base
    ? `<img class="icon" src="${base}.png" alt="" onerror="this.remove()">` : '';
  const tags = (s.tags || []).map(t => `<span class="tag">${esc(t)}</span>`).join('');
  return `<div class="head">
      ${icon}<h2>${esc(s.name)}</h2>
      ${tags ? `<div class="tags">${tags}</div>` : ''}
    </div>`;
}

function buttons(s, extra) {
  const base = dir(s);
  const install = s.icloud
    ? `<a class="btn" href="${esc(s.icloud)}">Install</a>`
    : `<span class="btn pending">Not published yet</span>`;
  const mirror = base && s.mirror !== false
    ? `<a class="btn mirror" href="${base}.shortcut" download>Mirror</a>` : '';
  return `<div class="row">${install}${mirror}${extra || ''}</div>`;
}

/* The action list: one row per action, its name in bold, its input and any
   variables as tokens, its parameters underneath, control flow indented. */
function stepsHtml(items) {
  return (items || []).map(item => {
    const depth = `--d:${item.depth || 0}`;
    if (item.kind === 'case') {
      return `<div class="flow" style="${depth}">Case <b>${esc(item.name)}</b></div>`;
    }
    if (item.kind === 'end') {
      return `<div class="flow" style="${depth}">End ${esc(item.name)}</div>`;
    }
    const target = item.target
      ? ` <span class="of">of</span> ${segs(item.target)}` : '';
    const args = (item.params || []).map(p =>
      `<dt>${esc(p.label)}</dt><dd>${segs(p.value)}</dd>`).join('');
    return `<div class="step" style="${depth}">
        <span class="num">${item.n}</span><span class="act">${esc(item.name)}</span>${target}
        ${args ? `<dl class="args">${args}</dl>` : ''}
      </div>`;
  }).join('');
}

/* The whole detail page below the card, from the generated sequence.json. */
function detail(seq) {
  const rows = [
    ['Record', `<code>${esc(seq.record)}</code>`],
    ['Shared', esc(seq.shared)],
    ['Signing', esc(seq.signing)],
    ['Certificate expires', esc(seq.expires)],
    ['Runs as', esc((seq.types || []).join(', ') || 'Shortcut')],
    ['Accepts', `${(seq.inputs || []).length} share sheet content types`],
    ['Icon', `glyph ${esc(seq.glyph)}, ${esc(seq.color || 'unknown')}`],
    ['Archived', `plist ${seq.sizes.plist} B, signed ${seq.sizes.signed} B,`
      + ` icon ${seq.sizes.icon} B`],
  ].map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
  return `<div class="section">How it is built</div>
    <div class="steps">${stepsHtml(seq.steps)}</div>
    <div class="section">Published record</div>
    <div class="card"><dl class="facts">${rows}</dl></div>`;
}

/* Every shortcut page is the same page with a different slug. */
function mountDetail(slug) {
  fetch(BASE + 'shortcuts.json')
    .then(r => r.json())
    .then(data => {
      const entry = (data.shortcuts || []).find(s => s.slug === slug);
      if (!entry) throw new Error('unknown shortcut');
      const notes = entry.notes
        ? `<a class="link" href="${REPO}${esc(entry.notes)}">Notes</a>` : '';
      document.getElementById('top').innerHTML = `<div class="card">
        ${header(entry)}
        <p>${esc(entry.summary)}</p>
        ${buttons(entry, notes)}
      </div>`;
      return fetch('sequence.json').then(r => r.json());
    })
    .then(seq => { document.getElementById('body').innerHTML = detail(seq); })
    .catch(() => {
      document.getElementById('top').innerHTML = '<div class="card"><p>Could not load'
        + ' this shortcut. <a class="link" href="../../">Back to the list</a></p></div>';
    });
}
