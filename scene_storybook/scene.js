(() => {
  'use strict';

  const T = window.__TIMELINE__;
  if (!T) { console.warn('storybook scene: no timeline injected'); return; }

  const $ = (id) => document.getElementById(id);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  const clamp01 = (v) => Math.max(0, Math.min(1, v));
  const seg = (t, a, b) => clamp01((t - a) / Math.max(b - a, 1e-6));
  const easeOutCubic = (x) => 1 - Math.pow(1 - x, 3);
  const easeOutBack = (x) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmtTime = (s) => { s = Math.max(0, s); const m = Math.floor(s / 60); return `${m}:${String(Math.floor(s % 60)).padStart(2, '0')}`; };
  const pad2 = (n) => String(n).padStart(2, '0');

  const theme = T.theme;
  const worlds = theme.worlds && theme.worlds.length ? theme.worlds : [theme.bg];
  const palette = theme.colors && theme.colors.length ? theme.colors : [theme.bg, theme.bg2];
  const cat = T.category;
  const stage = $('stage');
  const worldSet = (typeof WORLD_SETS !== 'undefined' && WORLD_SETS.includes(T.set))
    ? T.set
    : 'garden';
  const marketBulbs = $$('#market .bulb');
  const marketLanterns = $$('#market .lantern');
  const marketGlow = document.querySelector('.market-glow');
  let decorFall = [];
  let decorGlow = [];

  const CAST_SLOTS = ['left', 'pond', 'mid', 'right'];
  const DEFAULT_CAST = { left: 'bunny', pond: 'frog', mid: 'hedgehog', right: 'cat' };
  const ANIMAL_WIDTH = {
    bunny: 280, frog: 168, hedgehog: 170,
    cat: 260, duck: 182, panda: 270, penguin: 230,
    lion: 300, elephant: 340, giraffe: 300, zebra: 300, deer: 300,
    polar: 290, reindeer: 300, owl: 170, monkey: 230,
    camel: 310, deer: 270,
  };
  const SLOT_FALLBACK = { left: 1, pond: 0.55, mid: 0.68, right: 1 };
  const SLOT_WIDTH = {
    left: {
      bunny: 260, frog: 150, hedgehog: 140,
      cat: 246, duck: 160, panda: 252, penguin: 210,
      lion: 320, elephant: 330, giraffe: 300, zebra: 360, deer: 300,
      polar: 280, reindeer: 290, owl: 150, monkey: 220,
      camel: 310, deer: 260,
    },
    pond: {
      frog: 150, duck: 158, bunny: 155, cat: 150,
      panda: 150, penguin: 140, hedgehog: 125,
    },
    mid: {
      hedgehog: 122, penguin: 148, panda: 162, bunny: 165,
      cat: 155, duck: 130, frog: 130,
      owl: 150, monkey: 180, deer: 190, zebra: 330,
      lion: 220, elephant: 300, giraffe: 260, deer: 210, polar: 190,
      reindeer: 195, camel: 200,
    },
    right: {
      cat: 246, bunny: 266, penguin: 208,
      panda: 240, duck: 150, frog: 140, hedgehog: 130,
      lion: 315, elephant: 340, giraffe: 310, zebra: 370, deer: 300,
      polar: 290, reindeer: 300, owl: 150, monkey: 230,
      camel: 310, deer: 270,
    },
  };
  const ANIMAL_PHASE = {
    lion: 0.2, elephant: 1.1, giraffe: 2.0, zebra: 0.7,
    polar: 1.5, reindeer: 2.6, owl: 0.9, monkey: 1.8,
    camel: 2.3, deer: 0.5,
  };
  const cast = (T.cast && typeof T.cast === 'object' && !Array.isArray(T.cast))
    ? T.cast
    : DEFAULT_CAST;
  const critters = CAST_SLOTS.map((slot) => {
    const id = 'critter' + slot[0].toUpperCase() + slot.slice(1);
    return { slot, name: cast[slot] || DEFAULT_CAST[slot], el: $(id) };
  });

  function readable(hex) {
    const h = String(hex).replace('#', '');
    const r = parseInt(h.slice(0, 2), 16) / 255;
    const g = parseInt(h.slice(2, 4), 16) / 255;
    const b = parseInt(h.slice(4, 6), 16) / 255;
    return (0.299 * r + 0.587 * g + 0.114 * b) > 0.62;
  }

  function colorDistance(a, b) {
    const pa = String(a).replace('#', '');
    const pb = String(b).replace('#', '');
    const dr = (parseInt(pa.slice(0, 2), 16) - parseInt(pb.slice(0, 2), 16)) / 255;
    const dg = (parseInt(pa.slice(2, 4), 16) - parseInt(pb.slice(2, 4), 16)) / 255;
    const db = (parseInt(pa.slice(4, 6), 16) - parseInt(pb.slice(4, 6), 16)) / 255;
    return Math.sqrt(dr * dr + dg * dg + db * db) / Math.sqrt(3);
  }

  function accentFor(worldIndex, offset) {
    const world = worlds[((worldIndex % worlds.length) + worlds.length) % worlds.length];
    for (let k = 0; k < palette.length; k++) {
      const color = palette[(offset + k) % palette.length];
      if (colorDistance(color, world) >= 0.26) return color;
    }
    return theme.card;
  }

  function accent2For(accent, worldIndex) {
    const world = worlds[((worldIndex % worlds.length) + worlds.length) % worlds.length];
    for (let k = 0; k < palette.length; k++) {
      const color = palette[(k + 1) % palette.length];
      if (color.toLowerCase() === accent.toLowerCase()) continue;
      if (colorDistance(color, accent) >= 0.18 && colorDistance(color, world) >= 0.18) return color;
    }
    return theme.ink;
  }

  const tf = (el, x, y, s, r) => {
    el.style.transform = `translate(${x || 0}px, ${y || 0}px) scale(${s == null ? 1 : s}) rotate(${r || 0}deg)`;
  };
  const op = (el, o) => { el.style.opacity = String(o); };

  let accentNow = '';
  let accent2Now = '';
  let worldNow = -1;
  let switchT = -99;

  function setAccent(color, color2) {
    if (color !== accentNow) {
      accentNow = color;
      stage.style.setProperty('--accent', color);
      stage.style.setProperty('--hl-ink', readable(color) ? theme.ink : '#FFFDF6');
    }
    if (color2 !== accent2Now) {
      accent2Now = color2;
      stage.style.setProperty('--accent2', color2);
    }
  }

  function setWorld(index, t, transitionT) {
    const i = ((index % worlds.length) + worlds.length) % worlds.length;
    if (i === worldNow) return;
    if (worldNow >= 0) {
      stage.style.setProperty('--prevWorld', worlds[worldNow]);
      switchT = transitionT == null ? t : transitionT;
    }
    worldNow = i;
    stage.style.setProperty('--world', worlds[i]);
  }

  function renderWorldFade(t) {
    if (worldNow < 0) return;
    const fade = 1 - seg(t, switchT, switchT + 0.55);
    $('worldPrev').style.opacity = String(fade);
  }

  /* ------------------------------------------------------------ static text */

  function fitLine(el, maxSize, minSize, maxWidth) {
    if (!el) return;
    let size = maxSize;
    el.style.fontSize = size + 'px';
    el.style.whiteSpace = 'nowrap';
    let guard = 100;
    while (size > minSize && el.scrollWidth > maxWidth && guard-- > 0) {
      size -= 1;
      el.style.fontSize = size + 'px';
    }
  }

  function layoutMetaText() {
    const language = $('topLang');
    language.classList.remove('wrap');
    language.style.whiteSpace = 'nowrap';
    let langSize = 60;
    language.style.fontSize = langSize + 'px';
    let guard = 120;
    while (langSize > 34 && language.scrollWidth > 480 && guard-- > 0) {
      langSize -= 1;
      language.style.fontSize = langSize + 'px';
    }

    const category = document.querySelector('.top-category');
    const stacked = (cat.english.length + cat.native.length) > 30;
    category.classList.toggle('stacked', stacked);
    let size = stacked ? 21 : 27;
    category.style.fontSize = size + 'px';
    guard = 100;
    while (size > 16 && category.scrollWidth > 480 && guard-- > 0) {
      size -= 1;
      category.style.fontSize = size + 'px';
    }

    const introLength = cat.english.length + cat.native.length;
    $('introCategory').style.fontSize =
      (introLength <= 30 ? 25 : introLength <= 44 ? 23 : introLength <= 60 ? 21 : 19) + 'px';
    fitLine($('outroKicker'), 19, 11, 760);
  }

  function injectCritters() {
    for (const critter of critters) {
      if (!critter.el) continue;
      if (!ANIMALS[critter.name]) critter.name = DEFAULT_CAST[critter.slot];
      critter.el.dataset.animal = critter.name;
      critter.el.classList.add('critter', 'slot-' + critter.slot, 'is-' + critter.name);
      critter.el.innerHTML = ANIMALS[critter.name];
      const width = (SLOT_WIDTH[critter.slot] || {})[critter.name]
        || Math.round((ANIMAL_WIDTH[critter.name] || 240) * (SLOT_FALLBACK[critter.slot] || 1));
      critter.el.style.width = Math.round(width) + 'px';
    }
  }

  /* ------------------------------------------------------------- static setup */

  stage.style.setProperty('--card', theme.card);
  stage.style.setProperty('--ink', theme.ink);
  stage.classList.add('set-' + worldSet);
  const decor = $('worldDecor');
  if (decor) {
    decor.innerHTML = (typeof WORLD_DECOR !== 'undefined' && WORLD_DECOR[worldSet]) || '';
    decorFall = Array.from(decor.querySelectorAll('.fall-particle'));
    decorGlow = Array.from(decor.querySelectorAll('.glow-particle'));
  }
  injectAnimals(document);
  injectCritters();

  $$('[data-icon]').forEach((el) => { el.innerHTML = makeIcon(el.dataset.icon); });
  $('introVelo').innerHTML = MASCOT_SVG;
  $('phraseVelo').innerHTML = MASCOT_SVG;
  $('outroVelo').innerHTML = MASCOT_SVG;

  $('topLang').textContent = T.language.name.toUpperCase();
  $('topCatEn').textContent = cat.english;
  $('topCatVi').textContent = cat.native;
  $('introKicker').textContent = `A TINY ${T.language.name.toUpperCase()} STORY`;
  $('outroKicker').textContent = `THE END · ${cat.english.toUpperCase()}`;
  $('pageWatermark').innerHTML = makeIcon(cat.icon);
  $('introTitle').textContent = `${T.phrases.length} PHRASES`;
  $('introRibbon').textContent = `UNDER ${Math.ceil(T.duration / 10) * 10} SECONDS`;
  $('introCatIcon').innerHTML = makeIcon(cat.icon);
  $('introCatText').textContent = `${cat.english} · ${cat.native}`;
  $('natLabelText').textContent = T.language.native_label;
  $('translitLabel').textContent = T.language.translit_label;
  $('outroSub').textContent = `${T.phrases.length} new ${T.language.name} phrases`;
  $('outroXp').textContent = `+${T.xp} XP`;
  $('outroStreak').textContent = `${T.streak} day streak`;
  $('footBrand').textContent = T.brand;
  $('niceSticker').innerHTML = `${makeIcon('star')}<span>NICE!</span>${makeIcon('star')}`;

  if (window.__GALLERY_LABEL__) {
    const tag = $('galleryTag');
    tag.innerHTML = `<span>${esc(theme.name.toUpperCase())}</span><span class="g-swatches">${worlds.map((c) => `<i style="background:${c}"></i>`).join('')}</span>`;
    tag.style.display = 'flex';
  }

  $('outroList').innerHTML = T.phrases.map((p, i) =>
    `<div class="o-row">
       <span class="o-swatch" style="background:${palette[i % palette.length]}"></span>
       <span class="o-copy"><span class="o-en">${esc(p.english)}</span><span class="o-vi">${esc(p.native)}</span></span>
     </div>`
  ).join('');
  const oRows = Array.from(document.querySelectorAll('.o-row'));

  /* ------------------------------------------------------------- canvases */

  const dust = $('dust');
  const dctx = dust.getContext('2d');
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

  const dustData = (() => {
    const rnd = mulberry32(77123);
    const colors = palette.concat(['#FFFFFF', '#FFF6C8']);
    return Array.from({ length: 26 }, () => ({
      x: rnd() * 1080,
      y: rnd() * 1920,
      r: 2 + rnd() * 4.5,
      speed: 0.4 + rnd() * 0.9,
      amp: 12 + rnd() * 36,
      phase: rnd() * Math.PI * 2,
      color: colors[Math.floor(rnd() * colors.length)],
    }));
  })();

  const petalData = (() => {
    const rnd = mulberry32(99127);
    const colors = palette.concat(['#FFFFFF', '#FFB3C1']);
    return Array.from({ length: 16 }, () => ({
      x: rnd() * 1080,
      y: rnd() * 1920,
      r: 5 + rnd() * 7,
      speed: 0.35 + rnd() * 0.8,
      amp: 25 + rnd() * 55,
      phase: rnd() * Math.PI * 2,
      rot: rnd() * 360,
      color: colors[Math.floor(rnd() * colors.length)],
    }));
  })();

  function drawDust(t) {
    dctx.clearRect(0, 0, 1080, 1920);
    for (const p of dustData) {
      const y = (((p.y - t * p.speed * 18) % 2000) + 2000) % 2000 - 40;
      const x = p.x + Math.sin(t * 0.35 + p.phase) * p.amp;
      dctx.save();
      dctx.globalAlpha = 0.20 + 0.12 * Math.sin(t * 0.8 + p.phase);
      dctx.fillStyle = p.color;
      dctx.beginPath();
      dctx.arc(x, y, p.r, 0, 7);
      dctx.fill();
      dctx.restore();
    }
    for (const p of petalData) {
      const y = (((p.y + t * p.speed * 26) % 2000) + 2000) % 2000 - 40;
      const x = p.x + Math.sin(t * 0.45 + p.phase) * p.amp;
      dctx.save();
      dctx.globalAlpha = 0.48;
      dctx.translate(x, y);
      dctx.rotate((p.rot + t * 24) * Math.PI / 180);
      dctx.fillStyle = p.color;
      dctx.beginPath();
      dctx.ellipse(0, 0, p.r, p.r * 0.55, 0, 0, 7);
      dctx.fill();
      dctx.restore();
    }
  }

  const burstData = (T.fx || []).map((b, bi) => {
    const rnd = mulberry32(4400 + bi * 97);
    const colors = palette.concat(['#FFFFFF', '#FFFDF6']);
    const count = Math.round((b.count || 30) * (b.power || 1));
    const parts = [];
    for (let i = 0; i < count; i++) {
      const ang = -Math.PI / 2 + (rnd() - 0.5) * 2.4;
      const spd = 360 + rnd() * 840;
      parts.push({
        vx: Math.cos(ang) * spd + (rnd() - 0.5) * 160,
        vy: Math.sin(ang) * spd,
        w: 9 + rnd() * 14,
        h: 6 + rnd() * 10,
        rot: rnd() * Math.PI * 2,
        vr: (rnd() - 0.5) * 14,
        life: 1.05 + rnd() * 1.05,
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

  /* --------------------------------------------------------------- wording */

  let currentPhrase = -1;
  let enSpans = [];
  let viTiles = [];
  let enActive = -1;
  let viActive = -1;

  function layoutTiles(text, offset, wordList) {
    const box = $('natText');
    const tileWords = (Array.isArray(wordList) && wordList.length && wordList.every((w) => w && w.text))
      ? wordList.map((w) => w.text)
      : null;
    const words = tileWords || (T.language.char_tiles
      ? Array.from(String(text).replace(/\s+/g, '')).reduce((acc, ch) => {
          if (/[\p{P}\p{S}]/u.test(ch) && acc.length) acc[acc.length - 1] += ch;
          else acc.push(ch);
          return acc;
        }, [])
      : String(text).split(/\s+/).filter(Boolean));
    box.dir = T.language.rtl ? 'rtl' : 'ltr';
    box.classList.remove('lines');
    box.style.flexWrap = 'nowrap';
    box.innerHTML = words.map((w, i) => {
      const bg = palette[(i + offset) % palette.length];
      const fg = readable(bg) ? theme.ink : '#FFFDF6';
      return `<span class="tile"><span class="tile-bg" style="background:${bg};color:${fg}">${esc(w)}</span></span>`;
    }).join('');

    const tiles = Array.from(box.querySelectorAll('.tile'));
    const avail = box.clientWidth || 820;
    const natLen = text.length;
    const start = natLen <= 12 ? 120 : natLen <= 20 ? 112 : natLen <= 30 ? 104 : natLen <= 42 ? 92 : natLen <= 56 ? 82 : 74;
    const gap = 9;
    const MIN = 50;

    const widest = (rows) => Math.max(...rows.map((row) =>
      row.reduce((sum, el) => sum + el.offsetWidth, 0) + gap * Math.max(0, row.length - 1)));

    const split = (count) => {
      if (count === 1) return [tiles];
      let best = null;
      let bestW = Infinity;
      if (count === 2) {
        for (let i = 1; i < tiles.length; i++) {
          const rows = [tiles.slice(0, i), tiles.slice(i)];
          const w = widest(rows);
          if (w < bestW) { bestW = w; best = rows; }
        }
      } else {
        for (let i = 1; i < tiles.length - 1; i++) {
          for (let j = i + 1; j < tiles.length; j++) {
            const rows = [tiles.slice(0, i), tiles.slice(i, j), tiles.slice(j)];
            const w = widest(rows);
            if (w < bestW) { bestW = w; best = rows; }
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
      let size = start;
      while (size >= MIN) {
        box.style.fontSize = size + 'px';
        const rows = split(count);
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
    box.style.flexWrap = '';
    viTiles = Array.from(box.querySelectorAll('.tile'));
  }

  function fitPage() {
    const inner = $('pageInner');
    if (!inner) return;
    inner.style.transform = 'scale(1)';
    const cw = inner.clientWidth;
    const ch = inner.clientHeight;
    const sw = inner.scrollWidth;
    const sh = inner.scrollHeight;
    let scale = 1;
    if (sw > cw + 1 || sh > ch + 1) {
      const k = Math.min((cw - 2) / sw, (ch - 2) / sh, 0.96);
      scale = Math.max(0.64, k);
      inner.style.transform = `scale(${scale})`;
    }
    const pb = $('pageButterfly');
    if (pb) pb.style.display = scale < 0.9 ? 'none' : '';
  }

  function setPhrase(p) {
    if (!p || currentPhrase === p.index) return;
    currentPhrase = p.index;
    enActive = -1;
    viActive = -1;

    const words = p.english.split(/\s+/);
    $('enText').innerHTML = words.map((w) => `<span class="w"><span class="w-bg">${esc(w)}</span></span>`).join(' ');
    enSpans = Array.from($('enText').querySelectorAll('.w'));
    const len = p.english.length;
    $('enText').style.fontSize = (len <= 26 ? 96 : len <= 40 ? 88 : len <= 54 ? 80 : len <= 68 ? 64 : 58) + 'px';

    layoutTiles(p.native, p.index, p.vi_words);

    $('translitText').textContent = p.transliteration || '';
    const tlLen = (p.transliteration || '').length;
    $('translitText').style.fontSize = (tlLen <= 30 ? 52 : tlLen <= 44 ? 48 : tlLen <= 58 ? 44 : 40) + 'px';
    $('translit').style.display = p.transliteration ? 'block' : 'none';
    $('chapterLabel').textContent = `PAGE ${p.index + 1} / ${T.phrases.length}`;
    fitPage();
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
      bars[i].style.height = (on ? 7 + 15 * Math.abs(Math.sin(t * 7.5 + i * 1.25)) : 6).toFixed(1) + 'px';
    }
  }

  /* --------------------------------------------------------------- animals */

  function blinkAt(t, phase) {
    const p = (t + phase) % 4.6;
    if (p < 0.18) return Math.max(0.08, 1 - Math.sin((p / 0.18) * Math.PI) * 0.94);
    return 1;
  }

  function animVelo(wrap, t, opts) {
    if (!wrap) return;
    const o = opts || {};
    const phase = o.phase || 0;
    const wave = o.wave || 0;
    const jump = o.jump || 0;
    const svg = wrap.querySelector('.velo');
    if (!svg) return;
    const bob = svg.querySelector('.velo-bob');
    if (bob) bob.setAttribute('transform', `translate(0 ${Math.sin(t * 2.2 + phase) * 7 - jump * 42})`);
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
    const lookX = o.lookX || 0;
    const lookY = o.lookY || 0;
    svg.querySelectorAll('.velo-pupil').forEach((pupil) => {
      pupil.setAttribute('transform', `translate(${lookX} ${lookY})`);
    });
  }

  function animBunny(el, t, jump, wave) {
    if (!el) return;
    const svg = el.querySelector('.bunny-svg');
    if (!svg) return;
    const bob = svg.querySelector('.bunny-bob');
    if (bob) {
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.1) * 4 - jump * 24}) translate(100 238) scale(${1 - 0.03 * jump} ${1 + 0.045 * jump}) translate(-100 -238)`
      );
    }
    const head = svg.querySelector('.bunny-head');
    if (head) head.setAttribute('transform', `rotate(${Math.sin(t * 0.9) * 2.2} 100 150)`);
    const earL = svg.querySelector('.bunny-ear-l');
    const earR = svg.querySelector('.bunny-ear-r');
    if (earL) earL.setAttribute('transform', `rotate(${-10 + Math.sin(t * 2.8) * 4 + jump * 2} 78 118)`);
    if (earR) earR.setAttribute('transform', `rotate(${10 - Math.sin(t * 2.5) * 4 - jump * 2} 122 118)`);
    const paw = svg.querySelector('.bunny-paw');
    if (paw) paw.setAttribute('transform', `translate(0 ${-wave * 16}) rotate(${wave * 22} 156 182)`);
    const tail = svg.querySelector('.bunny-tail');
    if (tail) tail.setAttribute('transform', `translate(${Math.sin(t * 4.2) * 3} ${Math.cos(t * 4.2) * 3})`);
    const blink = blinkAt(t, 0.7);
    const eyeL = svg.querySelector('.bunny-eye-l');
    const eyeR = svg.querySelector('.bunny-eye-r');
    if (eyeL) eyeL.setAttribute('transform', `translate(76 106) scale(1 ${blink})`);
    if (eyeR) eyeR.setAttribute('transform', `translate(124 106) scale(1 ${blink})`);
  }

  function animFrog(el, t, jump) {
    if (!el) return;
    const svg = el.querySelector('.frog-svg');
    if (!svg) return;
    const bob = svg.querySelector('.frog-bob');
    if (bob) {
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.6 + 0.4) * 3 - jump * 32}) translate(90 126) scale(${1 - 0.03 * jump} ${1 + 0.05 * jump}) translate(-90 -126)`
      );
    }
    const head = svg.querySelector('.frog-head');
    if (head) head.setAttribute('transform', `rotate(${Math.sin(t * 1.2) * 1.8} 90 86)`);
    const throat = svg.querySelector('.frog-throat');
    if (throat) throat.setAttribute('transform', `translate(90 101) scale(1 ${1 + 0.18 * Math.abs(Math.sin(t * 2.4))}) translate(-90 -101)`);
    const blink = blinkAt(t, 1.4);
    const eyeL = svg.querySelector('.frog-eye-l');
    const eyeR = svg.querySelector('.frog-eye-r');
    if (eyeL) eyeL.setAttribute('transform', `translate(62 50) scale(1 ${blink})`);
    if (eyeR) eyeR.setAttribute('transform', `translate(118 50) scale(1 ${blink})`);
  }

  function animHedgehog(el, t, jump) {
    if (!el) return;
    const svg = el.querySelector('.hedgehog-svg');
    if (!svg) return;
    const bob = svg.querySelector('.hedgehog-bob');
    if (bob) {
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.2 + 2) * 3 - jump * 24}) translate(90 122) scale(${1 - 0.025 * jump} ${1 + 0.04 * jump}) translate(-90 -122)`
      );
    }
    const head = svg.querySelector('.hedgehog-head');
    if (head) head.setAttribute('transform', `rotate(${Math.sin(t * 1.6) * 3.4} 124 84)`);
    const nose = svg.querySelector('.hedgehog-head > path');
    if (nose) nose.setAttribute('transform', `translate(${Math.sin(t * 5.2) * 2} 0)`);
    const blink = blinkAt(t, 3.1);
    const eyeL = svg.querySelector('.hedgehog-eye-l');
    const eyeR = svg.querySelector('.hedgehog-eye-r');
    if (eyeL) eyeL.setAttribute('transform', `translate(116 76) scale(1 ${blink})`);
    if (eyeR) eyeR.setAttribute('transform', `translate(136 76) scale(1 ${blink})`);
  }

  function animCat(el, t, jump, wave) {
    if (!el) return;
    const svg = el.querySelector('.cat-svg');
    if (!svg) return;
    const bob = svg.querySelector('.cat-bob');
    if (bob) {
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.2 + 0.5) * 4 - jump * 26}) translate(110 240) scale(${1 - 0.03 * jump} ${1 + 0.045 * jump}) translate(-110 -240)`
      );
    }
    const head = svg.querySelector('.cat-head');
    if (head) head.setAttribute('transform', `rotate(${Math.sin(t * 1.0) * 2.1} 110 112)`);
    const tail = svg.querySelector('.cat-tail');
    if (tail) tail.setAttribute('transform', `rotate(${8 + Math.sin(t * 2.8) * 10} 178 198)`);
    const paw = svg.querySelector('.cat-paw');
    if (paw) paw.setAttribute('transform', `translate(0 ${-wave * 13}) rotate(${-wave * 26} 164 196)`);
    const blink = blinkAt(t, 0.3);
    const eyeL = svg.querySelector('.cat-eye-l');
    const eyeR = svg.querySelector('.cat-eye-r');
    if (eyeL) eyeL.setAttribute('transform', `translate(86 108) scale(1 ${blink})`);
    if (eyeR) eyeR.setAttribute('transform', `translate(134 108) scale(1 ${blink})`);
  }

  function animDuck(el, t, jump, wave) {
    if (!el) return;
    const svg = el.querySelector('.duck-svg');
    if (!svg) return;
    const bob = svg.querySelector('.duck-bob');
    if (bob) {
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.6 + 1.2) * 3 - jump * 24}) translate(100 170) scale(${1 - 0.03 * jump} ${1 + 0.05 * jump}) translate(-100 -170)`
      );
    }
    const head = svg.querySelector('.duck-head');
    if (head) head.setAttribute('transform', `rotate(${Math.sin(t * 1.3) * 2.6} 100 66)`);
    const wing = svg.querySelector('.duck-wing');
    if (wing) wing.setAttribute('transform', `rotate(${-8 + Math.sin(t * 2.4) * 5 - wave * 34} 66 118)`);
    const blink = blinkAt(t, 1.1);
    const eyeL = svg.querySelector('.duck-eye-l');
    const eyeR = svg.querySelector('.duck-eye-r');
    if (eyeL) eyeL.setAttribute('transform', `translate(84 58) scale(1 ${blink})`);
    if (eyeR) eyeR.setAttribute('transform', `translate(116 58) scale(1 ${blink})`);
  }

  function animPanda(el, t, jump, wave) {
    if (!el) return;
    const svg = el.querySelector('.panda-svg');
    if (!svg) return;
    const bob = svg.querySelector('.panda-bob');
    if (bob) {
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.1 + 2.4) * 3.5 - jump * 25}) translate(110 240) scale(${1 - 0.03 * jump} ${1 + 0.045 * jump}) translate(-110 -240)`
      );
    }
    const head = svg.querySelector('.panda-head');
    if (head) head.setAttribute('transform', `rotate(${Math.sin(t * 1.1 + 1) * 2.4} 110 112)`);
    const paw = svg.querySelector('.panda-paw');
    if (paw) paw.setAttribute('transform', `translate(0 ${-wave * 18}) rotate(${-wave * 34} 158 180)`);
    const blink = blinkAt(t, 2.6);
    const eyeL = svg.querySelector('.panda-eye-l');
    const eyeR = svg.querySelector('.panda-eye-r');
    if (eyeL) eyeL.setAttribute('transform', `translate(88 107) scale(1 ${blink})`);
    if (eyeR) eyeR.setAttribute('transform', `translate(132 107) scale(1 ${blink})`);
  }

  function animPenguin(el, t, jump, wave) {
    if (!el) return;
    const svg = el.querySelector('.penguin-svg');
    if (!svg) return;
    const bob = svg.querySelector('.penguin-bob');
    if (bob) {
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.4 + 0.8) * 3.5 - jump * 24}) rotate(${Math.sin(t * 1.8) * 2} 100 248) translate(100 248) scale(${1 - 0.03 * jump} ${1 + 0.045 * jump}) translate(-100 -248)`
      );
    }
    const head = svg.querySelector('.penguin-head');
    if (head) head.setAttribute('transform', `rotate(${Math.sin(t * 1.2 + 0.4) * 2.2} 100 74)`);
    const flipper = svg.querySelector('.penguin-flipper');
    if (flipper) flipper.setAttribute('transform', `rotate(${Math.sin(t * 3.1) * 6 + wave * 24} 162 168)`);
    const blink = blinkAt(t, 1.9);
    const eyeL = svg.querySelector('.penguin-eye-l');
    const eyeR = svg.querySelector('.penguin-eye-r');
    if (eyeL) eyeL.setAttribute('transform', `translate(84 79) scale(1 ${blink})`);
    if (eyeR) eyeR.setAttribute('transform', `translate(116 79) scale(1 ${blink})`);
  }

  function animNewCritter(el, t, jump, wave, phase) {
    if (!el) return;
    const svg = el.querySelector('svg');
    if (!svg) return;
    const pivot = (node, fallback) => (node && node.dataset.pivot ? node.dataset.pivot : fallback).split(/\s+/).map(Number);
    const bob = svg.querySelector('.critter-bob');
    if (bob) {
      const p = pivot(bob, '100 240');
      bob.setAttribute(
        'transform',
        `translate(0 ${Math.sin(t * 2.2 + phase) * 4 - jump * 26}) translate(${p[0]} ${p[1]}) scale(${1 - 0.03 * jump} ${1 + 0.045 * jump}) translate(${-p[0]} ${-p[1]})`
      );
    }
    const head = svg.querySelector('.critter-head');
    if (head) {
      const p = pivot(head, '100 110');
      head.setAttribute('transform', `rotate(${(Math.sin(t * 0.9 + phase) * 2.2).toFixed(2)} ${p[0]} ${p[1]})`);
    }
    const tail = svg.querySelector('.critter-tail');
    if (tail) {
      const p = pivot(tail, '170 200');
      tail.setAttribute('transform', `rotate(${(Math.sin(t * 2.5 + phase) * 8).toFixed(2)} ${p[0]} ${p[1]})`);
    }
    const ears = svg.querySelectorAll('.critter-ear');
    ears.forEach((ear, i) => {
      const p = pivot(ear, '100 80');
      const dir = i % 2 ? 1 : -1;
      ear.setAttribute(
        'transform',
        `rotate(${(Math.sin(t * 1.9 + phase + i * 0.9) * 3 * dir).toFixed(2)} ${p[0]} ${p[1]})`
      );
    });
    const paw = svg.querySelector('.critter-paw');
    if (paw) {
      const p = pivot(paw, '160 190');
      paw.setAttribute('transform', `rotate(${(-wave * 20).toFixed(2)} ${p[0]} ${p[1]})`);
    }
    const blink = blinkAt(t, phase + 0.3);
    for (const side of ['l', 'r']) {
      const eye = svg.querySelector('.critter-eye-' + side);
      if (!eye) continue;
      const p = pivot(eye, '90 105');
      eye.setAttribute('transform', `translate(${p[0]} ${p[1]}) scale(1 ${blink}) translate(${-p[0]} ${-p[1]})`);
    }
  }

  function animCritter(el, name, t, jump, wave) {
    switch (name) {
      case 'frog': animFrog(el, t, jump); break;
      case 'hedgehog': animHedgehog(el, t, jump); break;
      case 'cat': animCat(el, t, jump, wave); break;
      case 'duck': animDuck(el, t, jump, wave); break;
      case 'panda': animPanda(el, t, jump, wave); break;
      case 'penguin': animPenguin(el, t, jump, wave); break;
      case 'lion':
      case 'elephant':
      case 'giraffe':
      case 'zebra':
      case 'polar':
      case 'reindeer':
      case 'owl':
      case 'monkey':
      case 'camel':
      case 'deer':
        animNewCritter(el, t, jump, wave, ANIMAL_PHASE[name] || 0);
        break;
      default: animBunny(el, t, jump, wave); break;
    }
  }

  const butterflyEls = ['bfly1', 'bfly2', 'bfly3'].map((id) => $(id)).filter(Boolean);
  const butterflyBase = butterflyEls.map((el, i) => ({
    x: el.offsetLeft,
    y: el.offsetTop,
    phase: i * 1.9 + 0.7,
    amp: 28 + i * 8,
  }));

  function animButterflies(t) {
    butterflyEls.forEach((el, i) => {
      const b = butterflyBase[i];
      const x = Math.sin(t * 0.55 + b.phase) * (b.amp + 18);
      const y = Math.sin(t * 0.9 + b.phase * 1.3) * (b.amp + 22);
      el.style.transform = `translate(${x}px, ${y}px) rotate(${Math.sin(t * 0.7 + b.phase) * 12}deg)`;
      const flap = 0.48 + 0.52 * Math.abs(Math.sin(t * 8 + b.phase));
      const wingL = el.querySelector('.bfly-wing-l');
      const wingR = el.querySelector('.bfly-wing-r');
      if (wingL) wingL.setAttribute('transform', `translate(60 55) scale(${flap} 1) translate(-60 -55)`);
      if (wingR) wingR.setAttribute('transform', `translate(60 55) scale(${flap} 1) translate(-60 -55)`);
    });
  }

  const pageButterfly = $('pageButterfly');
  function animPageButterfly(t, phrase, u) {
    if (!pageButterfly) return;
    if (!phrase) {
      pageButterfly.style.opacity = '0';
      return;
    }
    const inStart = phrase.nat_reveal - 0.25;
    const inP = easeOutCubic(seg(t, inStart, inStart + 0.72));
    const outStart = phrase.vi_repeat_end + 0.35;
    const outP = seg(t, outStart, outStart + 0.55);
    const opacity = (t < inStart ? 0 : 1) * (1 - outP);
    const x = (1 - inP) * 170 + Math.sin(t * 0.7 + 1.2) * 10 + outP * 190;
    const y = (1 - inP) * -92 + Math.sin(t * 1.05 + 0.4) * 9 - outP * 110;
    pageButterfly.style.opacity = String(Math.max(0, opacity));
    pageButterfly.style.transform = `translate(${x}px, ${y}px) rotate(${Math.sin(t * 0.9) * 7}deg)`;
    const flap = 0.52 + 0.48 * Math.abs(Math.sin(t * 7 + 0.6));
    const wingL = pageButterfly.querySelector('.bfly-wing-l');
    const wingR = pageButterfly.querySelector('.bfly-wing-r');
    if (wingL) wingL.setAttribute('transform', `translate(60 55) scale(${flap} 1) translate(-60 -55)`);
    if (wingR) wingR.setAttribute('transform', `translate(60 55) scale(${flap} 1) translate(-60 -55)`);
  }

  const flowerEls = ['flower1', 'flower2', 'flower3', 'flower4'].map((id) => $(id)).filter(Boolean);
  function animFlowers(t) {
    flowerEls.forEach((el, i) => {
      el.style.transform = `rotate(${Math.sin(t * 1.15 + i * 1.4) * 3}deg)`;
    });
  }

  const grassEls = $$('.grass');
  function animGrass(t) {
    grassEls.forEach((el, i) => {
      el.style.transform = `rotate(${Math.sin(t * 1.4 + i * 1.1) * 2}deg)`;
    });
  }

  const birdEls = ['skyBird1', 'skyBird2', 'skyBird3'].map((id) => $(id)).filter(Boolean);
  const birdBase = [
    { y: 300, speed: 60, phase: 0.0, scale: 1.0 },
    { y: 430, speed: 44, phase: 2.4, scale: 0.8 },
    { y: 230, speed: 36, phase: 4.1, scale: 0.65 },
  ];

  function animBirds(t) {
    birdEls.forEach((el, i) => {
      const b = birdBase[i];
      const x = ((t * b.speed + i * 420) % 1440) - 180;
      const y = b.y + Math.sin(t * 0.7 + b.phase) * 34;
      el.style.transform = `translate(${x}px, ${y}px) scale(${b.scale}) rotate(${Math.sin(t * 0.8 + b.phase) * 6}deg)`;
      const wing = el.querySelector('.bird-wing');
      if (wing) wing.setAttribute('transform', `rotate(${Math.sin(t * 11 + b.phase) * 24} 42 36)`);
    });
  }

  function animMarket(t) {
    marketBulbs.forEach((bulb, i) => {
      const glow = 0.52 + 0.48 * Math.abs(Math.sin(t * 2.2 + i * 0.85));
      bulb.style.opacity = glow.toFixed(2);
      bulb.setAttribute('r', (12 + 3 * glow).toFixed(1));
    });
    marketLanterns.forEach((lantern, i) => {
      const sway = Math.sin(t * 1.5 + i * 1.8);
      lantern.style.transform = `rotate(${(sway * 2.4).toFixed(2)}deg)`;
      const lamp = lantern.querySelector('span');
      if (lamp) lamp.style.filter = `brightness(${(0.96 + 0.08 * Math.sin(t * 2.1 + i)).toFixed(3)})`;
    });
    if (marketGlow) marketGlow.style.opacity = String(0.82 + 0.18 * Math.sin(t * 1.1));
  }

  let waterfallStreaks = null;
  let waterfallFoam = null;
  let waterfallMist = null;
  function animWaterfall(t) {
    if (!waterfallStreaks) {
      waterfallStreaks = $$('.waterfall-streak');
      waterfallFoam = $$('.waterfall-foam');
      waterfallMist = $$('.waterfall-mist');
    }
    waterfallStreaks.forEach((el) => {
      const speed = parseFloat(el.dataset.speed || '100');
      const phase = parseFloat(el.dataset.phase || '0');
      const travel = parseFloat(el.dataset.travel || '150');
      const y = (t * speed + phase) % travel;
      el.setAttribute('transform', `translate(0 ${y.toFixed(2)})`);
    });
    waterfallFoam.forEach((el, i) => {
      const p = (el.dataset.pivot || '552 1840').split(/\s+/).map(Number);
      const s = 1 + Math.sin(t * 2.2 + i * 1.7) * 0.05;
      el.setAttribute('transform', `translate(${p[0]} ${p[1]}) scale(${s}) translate(${-p[0]} ${-p[1]})`);
      const base = i === 0 ? 0.84 : 0.60;
      el.setAttribute('opacity', (base + 0.06 * Math.sin(t * 2.4 + i)).toFixed(3));
    });
    waterfallMist.forEach((el, i) => {
      const base = i === 0 ? 0.10 : 0.12;
      el.setAttribute('opacity', (base + 0.04 * Math.sin(t * 1.4 + i * 1.2)).toFixed(3));
    });
  }

  function animDecor(t) {
    decorFall.forEach((el, i) => {
      const speed = parseFloat(el.dataset.speed || '50');
      const sway = parseFloat(el.dataset.sway || '20');
      const phase = parseFloat(el.dataset.phase || '0');
      const y = ((t * speed + phase) % 1980) - 50;
      const x = Math.sin(t * 0.8 + i * 1.3) * sway;
      el.style.translate = `${x.toFixed(1)}px ${y.toFixed(1)}px`;
    });
    decorGlow.forEach((el, i) => {
      const phase = parseFloat(el.dataset.phase || '0');
      const glow = 0.35 + 0.65 * Math.abs(Math.sin(t * 1.8 + phase));
      el.style.opacity = glow.toFixed(2);
      el.style.translate = `${(Math.sin(t * 0.7 + phase) * 16).toFixed(1)}px ${(Math.cos(t * 0.9 + phase) * 12).toFixed(1)}px`;
    });
  }

  function renderSky(t) {
    const rays = document.querySelector('.sun-rays');
    if (rays) rays.style.transform = `rotate(${(t * 4) % 360}deg)`;
    const core = document.querySelector('.sun-core');
    if (core) core.style.transform = `scale(${1 + 0.02 * Math.sin(t * 1.8)})`;
    $('cloud1').style.transform = `translate(${Math.sin(t * 0.08) * 26}px, ${Math.sin(t * 0.12 + 1) * 10}px)`;
    $('cloud2').style.transform = `translate(${Math.sin(t * 0.07 + 2) * 34}px, ${Math.cos(t * 0.1 + 2) * 12}px)`;
    $('cloud3').style.transform = `translate(${Math.cos(t * 0.06 + 1) * 22}px, ${Math.sin(t * 0.09 + 3) * 9}px)`;
    const balloon = $('balloon');
    if (balloon) balloon.style.transform = `translate(${Math.sin(t * 0.12) * 20}px, ${Math.sin(t * 0.45 + 1) * 10}px) rotate(${Math.sin(t * 0.25) * 2.6}deg)`;
    animBirds(t);
    if (worldSet === 'market') animMarket(t);
    if (worldSet !== 'garden') animDecor(t);
    renderWorldFade(t);
  }

  function renderGarden(t, scene) {
    const at = (centre, width) => Math.max(0, 1 - Math.abs(t - centre) / width);
    const jumps = { left: 0, pond: 0, mid: 0, right: 0 };
    const waves = { left: 0, pond: 0, mid: 0, right: 0 };

    if (scene.type === 'phrase') {
      const p = scene.phrase;
      jumps.left = at(p.nat_reveal + 0.2, 0.32) + at(p.vi_repeat_end + 0.1, 0.32);
      jumps.pond = at(p.nat_reveal + 0.3, 0.32);
      jumps.right = at(p.vi_repeat_start + 0.05, 0.32);
      jumps.mid = at(p.vi_repeat_start + 0.15, 0.32);
      waves.left = clamp01(
        Math.max(0, 1 - Math.abs(t - (p.start + 0.8)) / 0.55)
        + 0.8 * Math.max(0, 1 - Math.abs(t - (p.vi_repeat_start + 0.35)) / 0.5)
      );
      waves.right = 0.35 * Math.max(0, 1 - Math.abs(t - (p.vi_repeat_start + 0.2)) / 0.6);
    } else if (scene.type === 'intro') {
      jumps.left = 0.8 * at(1.7, 0.4);
      jumps.pond = 0.7 * at(1.35, 0.4);
      jumps.mid = 0.6 * at(2.2, 0.4);
      jumps.right = 0.8 * at(2.0, 0.4);
    } else if (scene.type === 'outro') {
      const o = t - T.outro.start;
      jumps.left = 0.7 * Math.max(0, Math.sin(o * 4.1));
      jumps.pond = 0.6 * Math.max(0, Math.sin(o * 3.8 + 2));
      jumps.mid = 0.5 * Math.max(0, Math.sin(o * 3.2 + 0.5));
      jumps.right = 0.7 * Math.max(0, Math.sin(o * 3.4 + 1));
      waves.left = 0.7;
      waves.right = 0.4;
    }

    critters.forEach((critter) => {
      animCritter(critter.el, critter.name, t, jumps[critter.slot], waves[critter.slot]);
    });
    animPageButterfly(t, scene.type === 'phrase' ? scene.phrase : null, scene.type === 'phrase' ? t - scene.phrase.start : 0);
    if (worldSet === 'garden') {
      animButterflies(t);
      animFlowers(t);
      animGrass(t);
    }
    if (worldSet === 'jungle') animWaterfall(t);

    if (scene.type === 'outro') {
      const o = t - T.outro.start;
      critters.forEach((critter, i) => {
        if (!critter.el) return;
        const sway = Math.sin(o * 3.2 + i * 1.35);
        const bounce = Math.sin(o * 4.2 + i * 1.35);
        critter.el.style.transform = `translate(${sway * 11}px, ${-Math.abs(bounce) * 7}px) rotate(${sway * 2.4}deg)`;
      });
      const lily = $('lilyPad');
      if (lily) lily.style.transform = `translateY(${Math.sin(o * 2.1) * 3}px) rotate(${Math.sin(o * 1.6) * 1.5}deg)`;
    } else {
      critters.forEach((critter) => {
        if (critter.el) critter.el.style.transform = '';
      });
      const lily = $('lilyPad');
      if (lily) lily.style.transform = '';
    }
  }

  /* ------------------------------------------------------------------ intro */

  function renderIntro(t) {
    setWorld(0, t, 0);
    const a = accentFor(0, 0);
    setAccent(a, accent2For(a, 0));

    const c = seg(t, 0.02, 0.5);
    const ce = easeOutBack(c);
    $('introCard').style.transform = `translateY(${(1 - ce) * 180}px) scale(${0.92 + 0.08 * easeOutCubic(c)}) rotate(${-2 - 4 * (1 - c)}deg)`;
    op($('introCard'), clamp01(c * 1.8));

    const k = seg(t, 0.15, 0.5);
    tf($('introTitle'), 0, (1 - easeOutCubic(k)) * 30, 1, 0);
    op($('introTitle'), clamp01(k * 1.6));

    const r = seg(t, 0.45, 0.8);
    tf($('introRibbon'), 0, (1 - easeOutBack(r)) * 30, r > 0 ? easeOutBack(r) : 0.001, 1.5);
    op($('introRibbon'), clamp01(r * 1.7));

    const m = seg(t, 0.65, 0.95);
    tf($('introCategory'), 0, (1 - easeOutBack(m)) * 26, m > 0 ? easeOutBack(m) : 0.001, 0);
    op($('introCategory'), clamp01(m * 1.7));

    const n = seg(t, 0.8, 1.1);
    op($('introNote'), clamp01(n * 1.6));

    const mi = seg(t, 0.25, 1.25);
    const me = easeOutCubic(mi);
    $('introVelo').style.transform = `translate(${(1 - me) * 460}px, ${(1 - easeOutBack(mi)) * -180}px) scale(${0.78 + 0.22 * me}) rotate(${(1 - mi) * 12}deg)`;
    op($('introVelo'), clamp01(mi * 1.7));
    animVelo($('introVelo'), t, { phase: 0.4, wave: mi >= 1 ? 0.8 : 0, jump: Math.max(0, 1 - Math.abs(t - 1.7) / 0.3) });
  }

  /* ----------------------------------------------------------------- phrase */

  function renderPhrase(p, t) {
    const u = t - p.start;
    const worldIndex = p.index + 1;
    setWorld(worldIndex, t, p.start);
    const accent = accentFor(worldIndex, p.index);
    setAccent(accent, accent2For(accent, worldIndex));

    const bp = seg(u, 0.02, 0.52);
    const be = easeOutBack(bp);
    const book = $('book');
    book.style.transform = `perspective(1200px) rotateY(${(1 - easeOutCubic(bp)) * -7}deg) translateY(${(1 - be) * 200}px) rotate(${-1 - 3 * (1 - bp)}deg) scale(${0.93 + 0.07 * easeOutCubic(bp)})`;
    op(book, clamp01(bp * 1.8));

    const a = seg(u, 0.05, 0.45);
    tf($('enText'), 0, (1 - easeOutCubic(a)) * 26, 1, 0);
    op($('enText'), clamp01(a * 1.8));

    const nr = p.nat_reveal;
    const n = seg(t, nr, nr + 0.55);
    for (let i = 0; i < viTiles.length; i++) {
      const s = seg(t, nr + 0.03 + i * 0.05, nr + 0.42 + i * 0.05);
      tf(viTiles[i], 0, (1 - easeOutBack(s)) * 46, 1, ((i % 2 ? 1 : -1) * 5) * (1 - s));
      op(viTiles[i], clamp01(s * 2));
    }

    const listenOpacity = 1 - seg(t, nr - 0.22, nr + 0.14);
    $('listenPanel').style.opacity = String(listenOpacity);
    $('listenPanel').style.display = listenOpacity > 0.005 ? 'flex' : 'none';
    op($('natBlock'), seg(t, nr - 0.08, nr + 0.24));
    if (listenOpacity > 0.005) {
      const bars = $('listenBars').children;
      for (let i = 0; i < bars.length; i++) {
        bars[i].style.height = (10 + 38 * Math.abs(Math.sin(t * 6 + i * 0.9))).toFixed(1) + 'px';
      }
      const ring = $('listenPanel').querySelector('.listen-ring');
      if (ring) ring.style.transform = `scale(${1 + 0.035 * Math.sin(t * 3.1)})`;
      const notes = $('listenNotes').children;
      for (let i = 0; i < notes.length; i++) {
        notes[i].style.transform = `translateY(${Math.sin(t * 2 + i * 1.7) * 9}px) rotate(${Math.sin(t * 1.6 + i) * 8}deg)`;
      }
      const lbird = $('listenBird');
      if (lbird) {
        lbird.style.transform = `translateY(${Math.sin(t * 2.4) * 3}px) rotate(${Math.sin(t * 1.1) * 3}deg)`;
        const wing = lbird.querySelector('.bird-wing');
        if (wing) wing.setAttribute('transform', `rotate(${Math.sin(t * 10) * 18} 42 36)`);
      }
    }

    enActive = setActive(enSpans, wordIndex(p.en_words, t), enActive);
    let viIdx = wordIndex(p.vi_words, t);
    if (viIdx < 0 && p.vi_words_repeat) viIdx = wordIndex(p.vi_words_repeat, t);
    viActive = setActive(viTiles, viIdx, viActive);

    const enPlaying = t >= p.en_start - 0.05 && t <= p.en_end + 0.05;
    $('enEq').style.opacity = enPlaying ? '1' : '.3';
    animateEq($('enEq'), t, enPlaying);
    const viPlaying =
      (t >= p.vi_start - 0.05 && t <= p.vi_end + 0.05) ||
      (t >= p.vi_repeat_start - 0.05 && t <= p.vi_repeat_end + 0.05);
    $('natEq').style.opacity = viPlaying ? '1' : '.3';
    animateEq($('natEq'), t, viPlaying);

    const tr = p.transliteration ? seg(t, nr + 0.28, nr + 0.72) : 0;
    tf($('translit'), 0, (1 - easeOutCubic(tr)) * 26, 1, 0);
    op($('translit'), tr);

    const rpStart = nr + 0.3;
    const rp = seg(t, rpStart, rpStart + 0.45);
    tf($('echoPill'), 0, 0, rp > 0 ? easeOutBack(rp) : 0.001, 0);
    op($('echoRow'), clamp01(rp * 2));

    const echoBird = $('echoBird');
    if (echoBird) {
      echoBird.style.transform = `translateY(${Math.sin(t * 2.6) * 2.5}px) rotate(${Math.sin(t * 1.2) * 2}deg)`;
      const wing = echoBird.querySelector('.bird-wing');
      if (wing) wing.setAttribute('transform', `rotate(${Math.sin(t * 11) * 20} 42 36)`);
    }

    const echoSpan = Math.max(0.4, p.vi_repeat_end - p.vi_repeat_start);
    const echoProgress = t < p.vi_repeat_start ? 0 : clamp01((t - p.vi_repeat_start) / echoSpan);
    $('ringFill').style.strokeDashoffset = String(163.36 * (1 - echoProgress));

    const mv = seg(u, 0.06, 0.62);
    const fly = 1 - easeOutCubic(mv);
    $('phraseVelo').style.transform = `translate(${fly * 190}px, ${(1 - easeOutBack(mv)) * 40 - Math.sin(Math.PI * mv) * 92}px) scale(${0.88 + 0.12 * easeOutCubic(mv)}) rotate(${fly * 10}deg)`;
    op($('phraseVelo'), clamp01(mv * 1.8));

    const jumpNative = Math.max(0, 1 - Math.abs(t - (nr + 0.18)) / 0.32);
    const jumpEcho = Math.max(0, 1 - Math.abs(t - (p.vi_repeat_end + 0.1)) / 0.32);
    const echoWave = t >= p.vi_repeat_start - 0.2 && t <= p.vi_repeat_end + 0.15
      ? 0.5 + 0.25 * Math.sin(t * 8)
      : 0.18;
    const wave = mv < 0.999 ? 1 : echoWave;
    animVelo($('phraseVelo'), t, {
      phase: 1.7,
      wave,
      jump: Math.max(jumpNative, jumpEcho),
      lookX: t >= p.vi_repeat_start - 0.2 ? -1.8 : -2.8,
      lookY: t >= nr ? 2.4 : 1.0,
    });

    const niceStart = p.vi_repeat_end + 0.05;
    const niceP = seg(t, niceStart, niceStart + 0.9);
    const niceShow = t >= niceStart
      ? Math.min(1, niceP * 8) * (1 - seg(niceP, 0.55, 1))
      : 0;
    const niceScale = 0.6 + 0.4 * easeOutBack(clamp01(niceP * 3));
    $('niceSticker').style.opacity = String(Math.max(0, niceShow));
    $('niceSticker').style.transform = `translateX(-50%) translateY(${(1 - niceP) * 17}px) rotate(-7deg) scale(${niceScale})`;

    let bubble = 'LISTEN...';
    let bubbleStart = p.start;
    if (t >= nr) { bubble = 'YOU GOT THIS!'; bubbleStart = nr; }
    if (t >= p.vi_repeat_start - 0.2) { bubble = 'SAY IT!'; bubbleStart = p.vi_repeat_start - 0.2; }
    if (t >= p.vi_repeat_end) { bubble = 'PERFECT!'; bubbleStart = p.vi_repeat_end; }
    if ($('bubble').textContent !== bubble) $('bubble').textContent = bubble;
    const bubbleP = seg(t, bubbleStart, bubbleStart + 0.26);
    const bubbleCut = t >= niceStart ? 1 - clamp01((t - niceStart) / 0.12) : 1;
    tf($('bubble'), 0, 0, 0.75 + 0.25 * easeOutBack(bubbleP), -1.5);
    op($('bubble'), clamp01(bubbleP * 2) * clamp01(mv * 1.8) * bubbleCut);
  }

  /* ------------------------------------------------------------------ outro */

  function renderOutro(t) {
    setWorld(0, t, T.outro.start);
    const a = accentFor(0, 1);
    setAccent(a, accent2For(a, 0));

    const o = t - T.outro.start;
    const c = seg(o, 0.02, 0.55);
    const ce = easeOutBack(c);
    $('outroCard').style.transform = `translateY(${(1 - ce) * 210}px) scale(${0.93 + 0.07 * easeOutCubic(c)}) rotate(${-1.4 - 3 * (1 - c)}deg)`;
    op($('outroCard'), clamp01(c * 1.8));

    const ti = seg(o, 0.25, 0.62);
    tf($('outroTitle'), 0, (1 - easeOutCubic(ti)) * 24, 1, 0);
    op($('outroTitle'), ti);

    const sub = seg(o, 0.38, 0.72);
    op($('outroSub'), sub);

    oRows.forEach((row, i) => {
      const p = seg(o, 0.5 + i * 0.1, 0.78 + i * 0.1);
      tf(row, 0, (1 - easeOutBack(p)) * 28, 1, 0);
      op(row, clamp01(p * 1.8));
    });

    const st = seg(o, 1.5, 1.85);
    tf($('outroStats'), 0, (1 - easeOutBack(st)) * 22, st > 0 ? easeOutBack(st) : 0.001, 0);
    op($('outroStats'), clamp01(st * 1.7));

    const ct = seg(o, 1.85, 2.25);
    const pulse = ct >= 1 ? 1 + 0.025 * Math.sin((o - 1.85) * 4.6) : 1;
    tf($('outroCta'), 0, (1 - easeOutBack(ct)) * 30, (ct > 0 ? easeOutBack(ct) : 0.001) * pulse, 0);
    op($('outroCta'), clamp01(ct * 1.6));

    const mv = seg(o, 0.15, 0.7);
    tf($('outroVelo'), 0, (1 - easeOutBack(mv)) * 70, 0.8 + 0.2 * easeOutCubic(mv), 0);
    op($('outroVelo'), clamp01(mv * 1.7));
    animVelo($('outroVelo'), t, {
      phase: 2.3,
      wave: mv >= 1 ? 0.85 : 0,
      jump: 0.55 * Math.max(0, Math.sin(o * 4.2)),
    });

    const ob = seg(o, 0.9, 1.25);
    tf($('outroBubble'), 0, 0, 0.7 + 0.3 * easeOutBack(ob), 2);
    op($('outroBubble'), clamp01(ob * 1.8));
  }

  /* -------------------------------------------------------------------- HUD */

  function applyCamera(t, scene) {
    const el = $('scenes');
    if (!el) return;
    let scale = 1;
    let x = 0;
    let y = 0;
    if (scene.type === 'intro') {
      const p = easeOutCubic(clamp01(t / Math.max(1, T.intro.end)));
      scale = 1.034 - 0.03 * p;
      y = 8 * (1 - p);
    } else if (scene.type === 'phrase') {
      const p = scene.phrase;
      const u = t - p.start;
      const e = easeOutCubic(clamp01(u / 3.0));
      scale = 1 + 0.036 * e;
      y = -11 * e;
      x = Math.sin(t * 0.35) * 4;
    } else {
      const o = t - T.outro.start;
      const e = easeOutCubic(clamp01(o / 4.5));
      scale = 1.02 + 0.016 * e;
      y = -7 * e;
    }
    el.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
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
    let scene;
    if (t < T.intro.end) {
      showScene('intro');
      renderIntro(t);
      scene = { type: 'intro' };
    } else if (t < T.outro.start) {
      const p = phraseAt(t);
      showScene('phrase');
      setPhrase(p);
      renderPhrase(p, t);
      scene = { type: 'phrase', phrase: p };
    } else {
      showScene('outro');
      renderOutro(t);
      scene = { type: 'outro' };
    }
    applyCamera(t, scene);
    renderSky(t);
    renderGarden(t, scene);
    drawDust(t);
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
    try {
      layoutMetaText();
      seek(0);
    } catch (e) { console.error(e); }
    window.sceneReady = true;
    if (window.__AUDIO_SRC__) setupPreview(window.__AUDIO_SRC__);
  };

  const specs = ['1000 86px Nunito', '1000 126px Nunito', '900 46px Nunito', '800 22px Nunito', '900 30px Nunito'];
  Promise.all(specs.map((s) => document.fonts.load(s).catch(() => null)))
    .then(() => document.fonts.ready)
    .then(ready)
    .catch(ready);
})();
