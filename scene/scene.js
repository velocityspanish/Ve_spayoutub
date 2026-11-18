(() => {
  'use strict';

  const T = window.__TIMELINE__;
  if (!T) { console.warn('scene.js: no timeline injected'); return; }

  const $ = (id) => document.getElementById(id);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  const clamp01 = (v) => Math.max(0, Math.min(1, v));
  const seg = (t, a, b) => clamp01((t - a) / Math.max(b - a, 1e-6));
  const easeOutCubic = (x) => 1 - Math.pow(1 - x, 3);
  const easeOutBack = (x) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmtTime = (s) => { s = Math.max(0, s); const m = Math.floor(s / 60); return `${m}:${String(Math.floor(s % 60)).padStart(2, '0')}`; };

  const stage = $('stage');
  const cat = T.category;

  const tf = (el, x, y, s, r) => {
    el.style.transform = `translate(${x || 0}px, ${y || 0}px) scale(${s == null ? 1 : s}) rotate(${r || 0}deg)`;
  };
  const op = (el, o) => { el.style.opacity = String(o); };

  /* ------------------------------------------------------------- static setup */

  document.documentElement.style.setProperty('--accent', cat.accent);

  $$('[data-icon]').forEach((el) => { el.innerHTML = makeIcon(el.dataset.icon); });
  $$('.mascot').forEach((el) => { el.innerHTML = MASCOT_SVG; });

  $('catText').textContent = `${cat.english} · ${cat.native}`;
  $('catIco').innerHTML = makeIcon(cat.icon);
  $('lessonIcon').innerHTML = makeIcon(cat.icon);
  $('lessonTitle').textContent = cat.english;
  $('lessonSub').textContent = `${cat.native} · ${T.phrases.length} phrases`;
  $('natLabelText').textContent = T.language.native_label;
  $('translitLabel').textContent = T.language.translit_label;
  $('logoLang').textContent = T.brand_bottom || T.language.name.toUpperCase();
  $('tagline').innerHTML = `Learn ${esc(T.language.name)} <b>in 60 seconds</b> a day`;
  $('streakVal').textContent = T.streak;
  $('outroStreak').textContent = `${T.streak} day streak`;
  $('outroXp').textContent = `+${T.xp} XP`;
  $('outroSub').textContent = `${T.phrases.length} new ${T.language.name} phrases`;
  $('footBrand').textContent = T.brand;
  $('footHandle').textContent = T.handle;

  const logoWord = $('logoWord');
  logoWord.innerHTML = T.brand_top.split('').map((c) => `<span>${c}</span>`).join('');
  const letters = Array.from(logoWord.querySelectorAll('span'));

  const dotsEl = $('dots');
  dotsEl.innerHTML = T.phrases.map(() => '<span class="dot"></span>').join('');
  const dotEls = Array.from(dotsEl.children);

  $('outroPhrases').innerHTML = T.phrases.map((p) =>
    `<div class="o-row"><span class="o-check">${makeIcon('check')}</span><span class="o-text">${esc(p.english)}</span></div>`
  ).join('');
  const oRows = Array.from(document.querySelectorAll('.o-row'));

  /* ------------------------------------------------------------- mascot anim */

  function blinkAt(t, phase) {
    const p = (t + phase) % 4.6;
    if (p < 0.18) return Math.max(0.08, 1 - Math.sin((p / 0.18) * Math.PI) * 0.94);
    return 1;
  }

  function animMascot(wrap, t, opts) {
    if (!wrap) return;
    const o = opts || {};
    const phase = o.phase || 0;
    const wave = o.wave || 0;
    const jump = o.jump || 0;
    const svg = wrap.querySelector('.velo');
    if (!svg) return;
    const bob = svg.querySelector('.velo-bob');
    if (bob) bob.setAttribute('transform', `translate(0 ${Math.sin(t * 2.2 + phase) * 7 - jump * 44})`);
    const tilt = svg.querySelector('.velo-tilt');
    if (tilt) tilt.setAttribute('transform', `rotate(${Math.sin(t * 1.4 + phase) * 2.2} 120 150)`);
    const blink = blinkAt(t, phase);
    for (const side of ['l', 'r']) {
      const eye = svg.querySelector('.velo-eye-' + side);
      if (!eye) continue;
      const cx = side === 'l' ? 86 : 154;
      eye.setAttribute('transform', `translate(${cx} 114) scale(1 ${blink})`);
    }
    const wl = 8 + Math.sin(t * 3.1 + phase) * 6 + wave * (26 + 22 * Math.sin(t * 13));
    const wr = 8 + Math.sin(t * 2.7 + phase + 1) * 6 + wave * (16 + 16 * Math.sin(t * 12 + 1));
    const wingL = svg.querySelector('.velo-wing-l');
    if (wingL) wingL.setAttribute('transform', `rotate(${-wl} 66 112)`);
    const wingR = svg.querySelector('.velo-wing-r');
    if (wingR) wingR.setAttribute('transform', `rotate(${wr} 174 112)`);
  }

  /* --------------------------------------------------------------- background */

  const blobs = $$('.blob');
  function renderBg(t) {
    const s0 = 1 + 0.05 * Math.sin(t * 0.32);
    const s1 = 1 + 0.06 * Math.sin(t * 0.27 + 2);
    const s2 = 1 + 0.05 * Math.sin(t * 0.29 + 4);
    const s3 = 1 + 0.06 * Math.sin(t * 0.24 + 1);
    blobs[0].style.transform = `translate(${Math.sin(t * 0.21) * 42}px, ${Math.cos(t * 0.17) * 30}px) scale(${s0})`;
    blobs[1].style.transform = `translate(${Math.sin(t * 0.19 + 2) * 36}px, ${Math.cos(t * 0.23) * 34}px) scale(${s1})`;
    blobs[2].style.transform = `translate(${Math.cos(t * 0.2 + 1) * 34}px, ${Math.sin(t * 0.18) * 30}px) scale(${s2})`;
    blobs[3].style.transform = `translate(${Math.cos(t * 0.17 + 3) * 30}px, ${Math.sin(t * 0.21) * 36}px) scale(${s3})`;
  }

  const fx = $('fx');
  const fctx = fx.getContext('2d');
  const fxTop = $('fxTop');
  const tctx = fxTop.getContext('2d');

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function drawStar(ctx, cx, cy, r, points) {
    ctx.beginPath();
    for (let i = 0; i < points * 2; i++) {
      const a = -Math.PI / 2 + (i * Math.PI) / points;
      const rr = i % 2 ? r * 0.45 : r;
      const x = cx + Math.cos(a) * rr;
      const y = cy + Math.sin(a) * rr;
      if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y);
    }
    ctx.closePath();
  }

  const ambient = (() => {
    const rnd = mulberry32(2024);
    const kinds = ['circle', 'rect', 'plus', 'star', 'ring'];
    const colors = ['#58CC02', '#1CB0F6', '#FFC800', '#CE82FF', '#FF9600'];
    return Array.from({ length: 16 }, () => ({
      x: rnd() * 1080,
      y: rnd() * 1920,
      size: 12 + rnd() * 22,
      speed: 0.4 + rnd() * 0.8,
      amp: 18 + rnd() * 50,
      phase: rnd() * Math.PI * 2,
      kind: kinds[Math.floor(rnd() * kinds.length)],
      rot: rnd() * 360,
      color: colors[Math.floor(rnd() * colors.length)],
    }));
  })();

  function drawAmbient(t) {
    fctx.clearRect(0, 0, 1080, 1920);
    for (const s of ambient) {
      const y = (((s.y - t * s.speed * 26) % 2000) + 2000) % 2000 - 40;
      const x = s.x + Math.sin(t * 0.5 + s.phase) * s.amp;
      fctx.save();
      fctx.globalAlpha = 0.13;
      fctx.translate(x, y);
      fctx.rotate(((s.rot + t * 9) % 360) * Math.PI / 180);
      fctx.fillStyle = s.color;
      fctx.strokeStyle = s.color;
      fctx.lineWidth = 5;
      if (s.kind === 'circle') {
        fctx.beginPath(); fctx.arc(0, 0, s.size / 2, 0, 7); fctx.fill();
      } else if (s.kind === 'rect') {
        fctx.beginPath(); fctx.roundRect(-s.size / 2, -s.size / 2, s.size, s.size, s.size * 0.3); fctx.fill();
      } else if (s.kind === 'plus') {
        fctx.fillRect(-s.size / 2, -s.size * 0.14, s.size, s.size * 0.28);
        fctx.fillRect(-s.size * 0.14, -s.size / 2, s.size * 0.28, s.size);
      } else if (s.kind === 'ring') {
        fctx.beginPath(); fctx.arc(0, 0, s.size / 2, 0, 7); fctx.stroke();
      } else {
        drawStar(fctx, 0, 0, s.size * 0.55, 5); fctx.fill();
      }
      fctx.restore();
    }
  }

  const burstData = (T.fx || []).map((b, bi) => {
    const rnd = mulberry32(1000 + bi * 97);
    const colors = ['#58CC02', '#1CB0F6', '#FFC800', '#FF4B4B', '#CE82FF', '#FF9600', '#FFFFFF', '#8FE63D'];
    const count = Math.round((b.count || 34) * (b.power || 1));
    const parts = [];
    for (let i = 0; i < count; i++) {
      const ang = -Math.PI / 2 + (rnd() - 0.5) * 2.4;
      const spd = 340 + rnd() * 820;
      parts.push({
        vx: Math.cos(ang) * spd + (rnd() - 0.5) * 160,
        vy: Math.sin(ang) * spd,
        w: 8 + rnd() * 14,
        h: 6 + rnd() * 10,
        rot: rnd() * Math.PI * 2,
        vr: (rnd() - 0.5) * 14,
        life: 1.1 + rnd() * 1.1,
        color: colors[Math.floor(rnd() * colors.length)],
        round: rnd() > 0.62,
        star: rnd() > 0.86,
      });
    }
    return { t: b.t, x: b.x, y: b.y, parts };
  });

  const GRAVITY = 1450;
  function drawTopFx(t) {
    tctx.clearRect(0, 0, 1080, 1920);
    for (const b of burstData) {
      const dt = t - b.t;
      if (dt < 0 || dt > 2.6) continue;
      for (const p of b.parts) {
        if (dt > p.life) continue;
        const x = b.x + p.vx * dt;
        const y = b.y + p.vy * dt + 0.5 * GRAVITY * dt * dt;
        if (y > 2010) continue;
        const alpha = 1 - clamp01((dt - p.life * 0.5) / (p.life * 0.5));
        tctx.save();
        tctx.globalAlpha = Math.max(0, alpha);
        tctx.translate(x, y);
        tctx.rotate(p.rot + p.vr * dt);
        tctx.fillStyle = p.color;
        if (p.star) { drawStar(tctx, 0, 0, p.w * 0.9, 5); tctx.fill(); }
        else if (p.round) { tctx.beginPath(); tctx.arc(0, 0, p.w * 0.42, 0, 7); tctx.fill(); }
        else { tctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); }
        tctx.restore();
      }
    }
  }

  /* -------------------------------------------------------------- phrases */

  let currentPhrase = -1;
  let enSpans = [];
  let viTiles = [];
  let viTileRanges = [];
  let enActive = -1;
  let viActive = -1;
  let stackHeights = { conn: 0, nat: 0, translit: 0, repeat: 0 };

  const flowHeight = (el) => {
    if (!el || el.offsetHeight === 0) return 0;
    const cs = getComputedStyle(el);
    return el.offsetHeight + (parseFloat(cs.marginTop) || 0) + (parseFloat(cs.marginBottom) || 0);
  };

  let WORD_SEGMENTER = null;
  try {
    if (typeof Intl !== 'undefined' && Intl.Segmenter) {
      WORD_SEGMENTER = new Intl.Segmenter(undefined, { granularity: 'word' });
    }
  } catch (e) {
    WORD_SEGMENTER = null;
  }

  const clusterCount = (text) => Array.from(String(text).replace(/\s+/g, '')).length;
  const KANA_RE = /^[\p{Script=Hiragana}\p{Script=Katakana}ー]$/u;

  // CJK scripts run words together, so group characters into word containers;
  // punctuation stays with the word in front of it.
  function wordUnits(text) {
    const plain = String(text);
    if (!T.language.char_tiles) {
      return plain.split(/\s+/).filter(Boolean).map((w) => ({ text: w, start: 0, end: 0 }));
    }
    if (!WORD_SEGMENTER) {
      return [{ text: plain.replace(/\s+/g, ''), start: 0, end: clusterCount(plain) }];
    }
    const units = [];
    let cursor = 0;
    for (const part of WORD_SEGMENTER.segment(plain)) {
      const seg = part.segment;
      if (!seg || !seg.trim()) continue;
      const width = clusterCount(seg);
      if (units.length && part.isWordLike === false) {
        // Merged punctuation is timed with the word before it, so it adds no cluster index.
        units[units.length - 1].text += seg;
        continue;
      }
      // Japanese particles are timed, but they read better attached to the word before them.
      if (units.length && width === 1 && KANA_RE.test(seg)) {
        units[units.length - 1].text += seg;
        units[units.length - 1].end += width;
      } else {
        units.push({ text: seg, start: cursor, end: cursor + width });
      }
      cursor += width;
    }
    if (!units.length) {
      const clean = plain.replace(/\s+/g, '');
      units.push({ text: clean, start: 0, end: clusterCount(clean) });
    }
    return units;
  }

  function layoutTiles(text) {
    const box = $('natText');
    const units = wordUnits(text);
    const words = units.map((u) => u.text);
    box.dir = T.language.rtl ? 'rtl' : 'ltr';
    box.classList.remove('lines');
    box.style.flexWrap = 'nowrap';
    box.innerHTML = words.map((w) => `<span class="tile"><span class="tile-bg">${esc(w)}</span></span>`).join('');
    const tiles = Array.from(box.querySelectorAll('.tile'));
    const avail = box.clientWidth;
    const natLen = text.length;
    const start = natLen <= 12 ? 104 : natLen <= 20 ? 96 : natLen <= 30 ? 88 : natLen <= 44 ? 80 : natLen <= 60 ? 72 : 64;
    const gap = 6;
    const MIN = 38;

    const lineWidths = (rows) =>
      rows.map((row) => row.reduce((sum, el) => sum + el.offsetWidth, 0) + gap * Math.max(0, row.length - 1));
    const widest = (rows) => Math.max(...lineWidths(rows));

    const split = (count) => {
      if (count === 1) return [tiles];
      let best = null;
      let bestW = Infinity;
      if (count === 2) {
        for (let i = 1; i < tiles.length; i++) {
          const rows = [tiles.slice(0, i), tiles.slice(i)];
          const w = widest(rows);
          if (w < bestW) {
            bestW = w;
            best = rows;
          }
        }
      } else {
        for (let i = 1; i < tiles.length - 1; i++) {
          for (let j = i + 1; j < tiles.length; j++) {
            const rows = [tiles.slice(0, i), tiles.slice(i, j), tiles.slice(j)];
            const w = widest(rows);
            if (w < bestW) {
              bestW = w;
              best = rows;
            }
          }
        }
      }
      return best || [tiles];
    };

    const build = (rows) => {
      box.innerHTML = '';
      if (rows.length === 1) {
        box.classList.remove('lines');
        rows[0].forEach((t) => box.appendChild(t));
      } else {
        box.classList.add('lines');
        for (const row of rows) {
          const line = document.createElement('div');
          line.className = 'tile-line';
          row.forEach((t) => line.appendChild(t));
          box.appendChild(line);
        }
      }
    };

    let fitted = false;
    for (const count of [1, 2, 3]) {
      if (tiles.length < count) break;
      box.style.fontSize = start + 'px';
      let rows = split(count);
      let size = start;
      const w0 = widest(rows);
      if (w0 > avail && avail > 0) {
        size = Math.max(MIN, Math.floor(start * (avail / w0) * 0.98));
      }
      while (size >= MIN) {
        box.style.fontSize = size + 'px';
        rows = split(count);
        if (widest(rows) <= avail + 0.5) {
          build(rows);
          fitted = true;
          break;
        }
        size -= 2;
      }
      if (fitted) break;
    }

    if (!fitted) {
      box.style.fontSize = MIN + 'px';
      build(split(3));
    }

    viTiles = Array.from(box.querySelectorAll('.tile'));
    viTileRanges = units.map((u) => ({ start: u.start, end: u.end }));
  }

  function setPhrase(p) {
    if (!p || currentPhrase === p.index) return;
    currentPhrase = p.index;
    enActive = -1;
    viActive = -1;

    const enWords = p.english.split(/\s+/);
    $('enText').innerHTML = enWords.map((w) => `<span class="w"><span class="w-bg">${esc(w)}</span></span>`).join(' ');
    enSpans = Array.from($('enText').querySelectorAll('.w'));
    const enLen = p.english.length;
    $('enText').style.fontSize = (enLen <= 26 ? 78 : enLen <= 42 ? 70 : enLen <= 62 ? 62 : 56) + 'px';

    layoutTiles(p.native);

    $('translitText').textContent = p.transliteration || '';
    $('translit').style.display = p.transliteration ? 'flex' : 'none';
    $('phraseCounter').textContent = `PHRASE ${p.index + 1} OF ${T.phrases.length}`;

    stackHeights = {
      conn: flowHeight($('connector')),
      nat: flowHeight($('natCard')),
      translit: flowHeight($('translit')),
      repeat: flowHeight($('repeatPill')),
    };
  }

  function wordIndex(words, t) {
    if (!words || !words.length) return -1;
    let idx = -1;
    for (let i = words.length - 1; i >= 0; i--) {
      if (t >= words[i].t0) { idx = i; break; }
    }
    if (idx < 0) return -1;
    const w = words[idx];
    const next = words[idx + 1];
    const end = next ? Math.min(w.t1 + 0.25, next.t0 + 0.1) : w.t1 + 0.35;
    return t <= end ? idx : -1;
  }

  function setActive(spans, idx, prev) {
    if (idx === prev) return prev;
    if (prev >= 0 && spans[prev]) spans[prev].classList.remove('on');
    if (idx >= 0 && spans[idx]) spans[idx].classList.add('on');
    return idx;
  }

  function animateEq(el, t, on) {
    if (!el) return;
    const bars = el.children;
    for (let i = 0; i < bars.length; i++) {
      bars[i].style.height = (on ? 8 + 16 * Math.abs(Math.sin(t * 7.5 + i * 1.25)) : 6).toFixed(1) + 'px';
    }
  }

  /* ------------------------------------------------------------------ intro */

  function renderIntro(t) {
    const a = seg(t, 0.12, 0.7);
    tf($('logoBadge'), 0, (1 - easeOutBack(a)) * 40, Math.max(0.001, easeOutBack(a)), -16 * (1 - a));
    op($('logoBadge'), clamp01(a * 2));

    letters.forEach((sp, i) => {
      const p = seg(t, 0.42 + i * 0.045, 0.78 + i * 0.045);
      tf(sp, 0, (1 - easeOutCubic(p)) * 52, 1, 0);
      op(sp, p);
    });

    const lg = seg(t, 0.82, 1.18);
    tf($('logoLang'), 0, (1 - easeOutBack(lg)) * 26, lg > 0 ? easeOutBack(lg) : 0.001, 0);
    op($('logoLang'), clamp01(lg * 1.6));

    const tg = seg(t, 1.02, 1.4);
    tf($('tagline'), 0, (1 - easeOutCubic(tg)) * 22, 1, 0);
    op($('tagline'), tg);

    const mi = seg(t, 0.65, 1.8);
    const mx = (1 - easeOutCubic(mi)) * -520;
    const my = (1 - easeOutBack(mi)) * 160;
    tf($('introMascot'), mx, my, 0.9 + 0.1 * easeOutCubic(mi), (1 - easeOutCubic(mi)) * -18);
    op($('introMascot'), clamp01(mi * 2));
    animMascot($('introMascot'), t, { phase: 0.4, wave: mi >= 1 ? seg(t, 2.2, 2.7) : 0 });

    const lc = seg(t, 2.3, 2.9);
    tf($('lessonCard'), 0, (1 - easeOutBack(lc)) * 230, 1, 0);
    op($('lessonCard'), clamp01(lc * 1.6));
  }

  /* ----------------------------------------------------------------- phrase */

  function renderPhrase(p, t) {
    const u = t - p.start;

    const a = seg(u, 0, 0.5);
    tf($('enCard'), 0, (1 - easeOutBack(a)) * 140, 0.96 + 0.04 * easeOutCubic(a), 0);
    op($('enCard'), clamp01(a * 1.8));

    const c = seg(u, 0.2, 0.55);
    tf($('connector'), 0, 0, c > 0 ? easeOutBack(c) : 0.001, 0);
    op($('connector'), clamp01(c * 2));

    const nr = p.nat_reveal;
    const n = seg(t, nr, nr + 0.55);
    tf($('natCard'), 0, (1 - easeOutBack(n)) * 120, 0.8 + 0.2 * easeOutBack(n), (1 - easeOutCubic(n)) * -3);
    op($('natCard'), clamp01(n * 1.6));

    for (let i = 0; i < viTiles.length; i++) {
      const s = seg(t, nr + 0.06 + i * 0.045, nr + 0.46 + i * 0.045);
      tf(viTiles[i], 0, (1 - easeOutBack(s)) * 34, 1, 0);
      op(viTiles[i], clamp01(s * 2));
    }

    enActive = setActive(enSpans, wordIndex(p.en_words, t), enActive);
    let viIdx = wordIndex(p.vi_words, t);
    if (viIdx < 0 && p.vi_words_repeat) viIdx = wordIndex(p.vi_words_repeat, t);
    let tileIdx = viIdx;
    if (viIdx >= 0 && T.language.char_tiles) {
      tileIdx = viTileRanges.findIndex((r) => viIdx >= r.start && viIdx < r.end);
    }
    viActive = setActive(viTiles, tileIdx, viActive);

    const enPlaying = t >= p.en_start - 0.05 && t <= p.en_end + 0.05;
    $('enLabel').classList.toggle('playing', enPlaying);
    animateEq($('enEq'), t, enPlaying);

    const viPlaying =
      (t >= p.vi_start - 0.05 && t <= p.vi_end + 0.05) ||
      (t >= p.vi_repeat_start - 0.05 && t <= p.vi_repeat_end + 0.05);
    $('natLabel').classList.toggle('playing', viPlaying);
    animateEq($('natEq'), t, viPlaying);

    const tr = p.transliteration ? seg(t, nr + 0.3, nr + 0.75) : 0;
    tf($('translit'), 0, (1 - easeOutCubic(tr)) * 18, 1, 0);
    op($('translit'), tr);

    const rpStart = p.vi_repeat_start - 0.28;
    const rp = seg(t, rpStart, rpStart + 0.5);
    const rpPulse = rp >= 1 ? 1 + 0.025 * Math.sin((t - rpStart) * 4.5) : 1;
    tf($('repeatPill'), 0, (1 - easeOutBack(rp)) * 34, (rp > 0 ? easeOutBack(rp) : 0.001) * rpPulse, 0);
    op($('repeatPill'), clamp01(rp * 1.8));

    const smooth = (x) => x * x * (3 - 2 * x);
    const hidden =
      (1 - smooth(clamp01(c))) * stackHeights.conn +
      (1 - smooth(clamp01(n))) * stackHeights.nat +
      (1 - smooth(clamp01(tr))) * stackHeights.translit +
      (1 - smooth(clamp01(rp))) * stackHeights.repeat;
    $('phraseStack').style.transform = `translateY(${(hidden * 0.5).toFixed(1)}px)`;

    const pm = seg(t, nr, nr + 0.55);
    tf($('peekMascot'), 0, (1 - easeOutBack(pm)) * 90, 0.6 + 0.4 * easeOutBack(pm), 6 * (1 - easeOutCubic(pm)));
    op($('peekMascot'), clamp01(pm * 1.6));
    animMascot($('peekMascot'), t, {
      phase: 1.7,
      wave: pm >= 1 ? 0.65 + 0.35 * Math.sin(t * 1.8) : 0,
      jump: Math.max(0, 1 - Math.abs(t - nr - 0.12) / 0.22),
    });
  }

  /* ------------------------------------------------------------------ outro */

  function renderOutro(t) {
    const o = t - T.outro.start;
    const c = seg(o, 0, 0.6);
    tf($('outroCard'), 0, (1 - easeOutBack(c)) * 200, 0.93 + 0.07 * easeOutCubic(c), 0);
    op($('outroCard'), clamp01(c * 1.6));

    const b = seg(o, 0.15, 0.7);
    tf($('outroBadge'), 0, 0, b > 0 ? easeOutBack(b) : 0.001, 0);
    op($('outroBadge'), clamp01(b * 2));

    const ti = seg(o, 0.35, 0.8);
    tf($('outroTitle'), 0, (1 - easeOutCubic(ti)) * 24, 1, 0);
    op($('outroTitle'), ti);

    const sb = seg(o, 0.5, 0.95);
    tf($('outroSub'), 0, (1 - easeOutCubic(sb)) * 20, 1, 0);
    op($('outroSub'), sb);

    oRows.forEach((row, i) => {
      const a = seg(o, 0.55 + i * 0.08, 0.9 + i * 0.08);
      tf(row, 0, (1 - easeOutBack(a)) * 26, 1, 0);
      op(row, clamp01(a * 1.7));
    });

    const st = seg(o, 1.12, 1.47);
    tf($('outroStats'), 0, (1 - easeOutBack(st)) * 20, st > 0 ? easeOutBack(st) : 0.001, 0);
    op($('outroStats'), clamp01(st * 1.7));

    const ct = seg(o, 1.35, 1.75);
    const ctp = ct >= 1 ? 1 + 0.02 * Math.sin((o - 1.35) * 4.5) : 1;
    tf($('cta'), 0, (1 - easeOutBack(ct)) * 30, (ct > 0 ? easeOutBack(ct) : 0.001) * ctp, 0);
    op($('cta'), clamp01(ct * 1.6));

    const mc = seg(o, 0.2, 0.75);
    tf($('outroMascot'), 0, (1 - easeOutBack(mc)) * 70, 0.7 + 0.3 * easeOutBack(mc), 0);
    op($('outroMascot'), clamp01(mc * 1.5));
    animMascot($('outroMascot'), t, {
      phase: 2.3,
      wave: mc >= 1 ? 0.8 + 0.2 * Math.sin(t * 2.2) : 0,
      jump: 0.65 * Math.max(0, Math.sin(o * 4.2)),
    });
  }

  /* -------------------------------------------------------------------- HUD */

  function renderHud(t, scene) {
    const hud = $('hud');
    const foot = $('foot');
    const show = scene.type === 'intro' ? seg(t, T.intro.end - 0.45, T.intro.end - 0.05) : 1;
    hud.style.opacity = String(show);
    hud.style.transform = `translateY(${(1 - show) * -16}px)`;
    foot.style.opacity = String(scene.type === 'intro' ? seg(t, 2.5, 3.0) * 0.92 : 0.92);

    let pct = 0;
    let phrase = null;
    if (scene.type === 'phrase') {
      phrase = scene.phrase;
      const local = clamp01((t - phrase.start) / Math.max(0.6, phrase.nat_reveal + 0.5 - phrase.start));
      pct = (phrase.index + local) / T.phrases.length;
    } else if (scene.type === 'outro') {
      pct = 1;
    }

    $('progressFill').style.width = (pct * 100).toFixed(2) + '%';
    const knob = $('progressKnob');
    knob.style.left = (pct * 100).toFixed(2) + '%';
    knob.style.opacity = pct > 0.004 ? '1' : '0';

    $('xpVal').textContent = `${Math.round(pct * T.xp)} XP`;
    $('streakVal').textContent = T.streak;

    dotEls.forEach((d, i) => {
      const done = scene.type === 'outro' || (phrase && (i < phrase.index || (i === phrase.index && t > phrase.nat_reveal + 0.1)));
      const current = !!phrase && i === phrase.index && !done;
      d.classList.toggle('done', !!done);
      d.classList.toggle('current', current);
    });

    const pop = phrase ? Math.max(0, 1 - Math.abs(t - (phrase.nat_reveal + 0.1)) / 0.35) : 0;
    $('xpPill').style.transform = `scale(${1 + 0.09 * pop})`;
  }

  /* ------------------------------------------------------------------- seek */

  let activeScene = '';
  function showScene(name) {
    if (activeScene === name) return;
    activeScene = name;
    $('sceneIntro').classList.toggle('active', name === 'intro');
    $('scenePhrase').classList.toggle('active', name === 'phrase');
    $('sceneOutro').classList.toggle('active', name === 'outro');
  }

  function phraseAt(t) {
    for (const p of T.phrases) if (t >= p.start && t < p.end) return p;
    return T.phrases[T.phrases.length - 1];
  }

  function seek(t) {
    t = Math.max(0, Math.min(T.duration, t));
    if (t < T.intro.end) {
      showScene('intro');
      renderIntro(t);
      renderHud(t, { type: 'intro' });
    } else if (t < T.outro.start) {
      const p = phraseAt(t);
      showScene('phrase');
      setPhrase(p);
      renderPhrase(p, t);
      renderHud(t, { type: 'phrase', phrase: p });
    } else {
      showScene('outro');
      renderOutro(t);
      renderHud(t, { type: 'outro' });
    }
    renderBg(t);
    drawAmbient(t);
    drawTopFx(t);
    window.currentTime = t;
  }

  window.seek = seek;
  window.timeline = T;

  /* ---------------------------------------------------------------- preview */

  function setupPreview(src) {
    const audio = new Audio(src);
    audio.preload = 'auto';
    const bar = document.createElement('div');
    bar.id = 'previewBar';
    bar.innerHTML = `<button id="ppBtn">Play</button><input id="scrub" type="range" min="0" max="${T.duration}" step="0.01" value="0"><span class="ptime" id="ptime">0:00 / ${fmtTime(T.duration)}</span>`;
    document.body.appendChild(bar);
    const btn = bar.querySelector('#ppBtn');
    const scrub = bar.querySelector('#scrub');
    const tm = bar.querySelector('#ptime');
    function tick() {
      if (!audio.paused) {
        seek(audio.currentTime);
        scrub.value = String(audio.currentTime);
        tm.textContent = `${fmtTime(audio.currentTime)} / ${fmtTime(T.duration)}`;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    btn.onclick = () => {
      if (audio.paused) {
        audio.play().then(() => { btn.textContent = 'Pause'; }).catch(() => { btn.textContent = 'Tap again to play'; });
      } else {
        audio.pause();
        btn.textContent = 'Play';
      }
    };
    audio.onended = () => { btn.textContent = 'Replay'; };
    scrub.oninput = () => {
      const v = parseFloat(scrub.value);
      audio.currentTime = v;
      seek(v);
      tm.textContent = `${fmtTime(v)} / ${fmtTime(T.duration)}`;
    };
    document.addEventListener('keydown', (e) => {
      if (e.code === 'Space') { e.preventDefault(); btn.click(); }
    });
  }

  const ready = () => {
    try { seek(0); } catch (e) { console.error(e); }
    window.sceneReady = true;
    if (window.__AUDIO_SRC__) setupPreview(window.__AUDIO_SRC__);
  };

  const specs = ['900 70px Nunito', '1000 120px Nunito', '800 32px Nunito', 'italic 800 34px Nunito', '900 88px Nunito'];
  Promise.all(specs.map((s) => document.fonts.load(s).catch(() => null)))
    .then(() => document.fonts.ready)
    .then(ready)
    .catch(ready);
})();
