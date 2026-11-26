/* Storybook nature sets.
   One shared book, cast and timing; each set supplies its own world art.
   All shapes are inline SVG so the theme palette can tint them through CSS
   variables. Particle fields are HTML so the renderer can animate them from
   the timeline instead of wall-clock CSS animations. */

const WORLD_SETS = [
  'garden', 'forest', 'beach', 'desert', 'snow',
  'jungle', 'savanna', 'autumn', 'cherry', 'lavender',
  'bamboo', 'market',
];

const art = (inner) => `
<svg class="world-art" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">${inner}</svg>`;

function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function fallField(kind, count, seed, speedMin, speedMax) {
  const r = rng(seed);
  let items = '';
  for (let i = 0; i < count; i += 1) {
    const left = 14 + r() * 1052;
    const size = kind === 'snow' ? 9 + r() * 16 : 12 + r() * 13;
    const speed = speedMin + r() * (speedMax - speedMin);
    const sway = 12 + r() * 34;
    const phase = r() * 1980;
    items += `<i class="fall-particle ${kind}" data-speed="${speed.toFixed(1)}" data-sway="${sway.toFixed(1)}" data-phase="${phase.toFixed(1)}" style="left:${left.toFixed(1)}px;width:${size.toFixed(1)}px;height:${size.toFixed(1)}px"></i>`;
  }
  return `<div class="world-particles ${kind}-field">${items}</div>`;
}

function glowField(count, seed, top0, top1) {
  const r = rng(seed);
  let items = '';
  for (let i = 0; i < count; i += 1) {
    const left = 40 + r() * 1000;
    const top = top0 + r() * (top1 - top0);
    const size = 7 + r() * 9;
    items += `<i class="glow-particle" data-phase="${(r() * 6.28).toFixed(2)}" style="left:${left.toFixed(1)}px;top:${top.toFixed(1)}px;width:${size.toFixed(1)}px;height:${size.toFixed(1)}px"></i>`;
  }
  return `<div class="world-particles firefly-field">${items}</div>`;
}

const broadTree = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-24 0C-18-110-12-206-6-302h36C26-200 22-100 32 0Z" fill="var(--trunk)" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M4-266c-16-32-46-56-84-68M12-292c22-38 56-58 96-68" fill="none" stroke="var(--trunk)" stroke-width="10" stroke-linecap="round"/>
  <ellipse cx="-96" cy="-332" rx="94" ry="68" fill="var(--leaf-b)"/>
  <ellipse cx="82" cy="-344" rx="98" ry="72" fill="var(--leaf-a)"/>
  <ellipse cx="-8" cy="-412" rx="110" ry="84" fill="var(--leaf-a)"/>
  <ellipse cx="-124" cy="-392" rx="76" ry="58" fill="var(--leaf-c)"/>
  <ellipse cx="116" cy="-410" rx="74" ry="56" fill="var(--leaf-b)"/>
</g>`;

const pine = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0v-330" stroke="var(--trunk)" stroke-width="18" stroke-linecap="round"/>
  <path d="M0-210L-88-60H88z" fill="var(--leaf-c)" stroke="#3A2A1A" stroke-width="6" stroke-linejoin="round"/>
  <path d="M0-296L-70-152h140z" fill="var(--leaf-b)" stroke="#3A2A1A" stroke-width="6" stroke-linejoin="round"/>
  <path d="M0-378L-52-240h104z" fill="var(--leaf-a)" stroke="#3A2A1A" stroke-width="6" stroke-linejoin="round"/>
  <path d="M-52-378L0-430 52-378z" fill="#F7FBFF" opacity=".92"/>
  <path d="M-64-166l16-8 12 12 14-12 14 8" fill="none" stroke="#F7FBFF" stroke-width="7" stroke-linecap="round" opacity=".55"/>
</g>`;

const palm = (x, y, s, flip = 1) => `
<g transform="translate(${x} ${y}) scale(${s * flip} ${s})">
  <path d="M0 0C-10-120 4-238 26-330" fill="none" stroke="var(--trunk)" stroke-width="22" stroke-linecap="round"/>
  <path d="M26-330c-56-58-124-72-180-50M26-330c-4-78 26-140 86-172M26-330c58-62 132-76 194-52M26-330c-38 44-108 62-168 52M26-330c50 44 120 58 182 44" fill="none" stroke="var(--palm-a)" stroke-width="18" stroke-linecap="round"/>
  <circle cx="18" cy="-318" r="13" fill="#6B4A2A" stroke="#3A2A1A" stroke-width="4"/>
  <circle cx="40" cy="-312" r="11" fill="#6B4A2A" stroke="#3A2A1A" stroke-width="4"/>
</g>`;

const cactus = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <rect x="-30" y="-300" width="60" height="300" rx="30" fill="var(--cactus)" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M-30-210h-44a24 24 0 0 0-24 24v64a18 18 0 0 0 36 0v-52h32" fill="var(--cactus)" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M30-160h40a24 24 0 0 1 24 24v48a18 18 0 0 1-36 0v-36h-28" fill="var(--cactus)" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M-8-250v-24M8-268v-32" stroke="#3A2A1A" stroke-width="4" stroke-linecap="round"/>
  <circle cx="0" cy="-312" r="14" fill="var(--flower)" stroke="#3A2A1A" stroke-width="4"/>
</g>`;

const fern = (x, y, s, flip = 1) => `
<g transform="translate(${x} ${y}) scale(${s * flip} ${s})" fill="none" stroke="var(--fern)" stroke-width="9" stroke-linecap="round">
  <path d="M0 0C-20-60-58-112-112-142"/>
  <path d="M-22-48c-18-14-38-18-56-16M-46-84c-18-14-38-18-56-16M-74-116c-18-14-38-18-56-16"/>
  <path d="M0 0C16-70 50-124 104-156"/>
  <path d="M8-54c18-10 38-12 54-8M30-94c18-10 38-12 54-8M58-130c18-10 38-12 54-8"/>
</g>`;

const mushroom = (x, y, s, cap = '#E84A5F') => `
<g transform="translate(${x} ${y}) scale(${s})">
  <rect x="-9" y="-42" width="18" height="42" rx="7" fill="#F4E6D0" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-36-38c0-28 16-48 36-48s36 20 36 48z" fill="${cap}" stroke="#3A2A1A" stroke-width="4"/>
  <circle cx="-15" cy="-54" r="4.5" fill="#FFF6E8"/><circle cx="7" cy="-64" r="3.5" fill="#FFF6E8"/><circle cx="18" cy="-50" r="3" fill="#FFF6E8"/>
</g>`;

const rock = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-54 0c-10-26 10-48 38-50 32-2 58 16 60 40 2 10-8 10-10 10z" fill="var(--rock)" stroke="#3A2A1A" stroke-width="5"/>
  <path d="M-20-28c8-8 18-12 30-12" fill="none" stroke="#FFF6E8" stroke-width="4" opacity=".25"/>
</g>`;

const pumpkin = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <ellipse cx="0" cy="-30" rx="48" ry="32" fill="var(--pumpkin)" stroke="#3A2A1A" stroke-width="5"/>
  <path d="M0-62c-6-18 2-30 12-36" fill="none" stroke="#4E7A2F" stroke-width="7" stroke-linecap="round"/>
  <path d="M0-60c-28-10-42 8-44 24M0-60c28-10 42 8 44 24" fill="none" stroke="#3A2A1A" stroke-width="4" opacity=".5"/>
</g>`;

const tuft = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})" fill="none" stroke="var(--grass)" stroke-width="7" stroke-linecap="round">
  <path d="M0 0C-4-32-18-58-38-72"/><path d="M6 0C8-40 18-70 34-92"/><path d="M12 0C20-26 36-44 56-54"/>
</g>`;

const bush = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <ellipse cx="-34" cy="-30" rx="52" ry="38" fill="var(--leaf-c)" stroke="#3A2A1A" stroke-width="4"/>
  <ellipse cx="26" cy="-42" rx="46" ry="40" fill="var(--leaf-b)" stroke="#3A2A1A" stroke-width="4"/>
  <ellipse cx="-2" cy="-62" rx="38" ry="32" fill="var(--leaf-a)" stroke="#3A2A1A" stroke-width="4"/>
</g>`;

const log = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-96-24C-80-58 -20-68 42-58 86-51 110-30 104 0H-96z" fill="#6B4A32" stroke="#3A2A1A" stroke-width="5"/>
  <ellipse cx="102" cy="-12" rx="20" ry="26" fill="#9A6741" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M98-26c-10 0-16 8-16 16M104-8c-10 0-14 6-14 12" fill="none" stroke="#5A3A24" stroke-width="3"/>
  <path d="M-70-28c16-10 34-14 54-12" fill="none" stroke="#4A3222" stroke-width="4" stroke-linecap="round"/>
</g>`;

const acacia = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0C-10-112-4-204 14-286" fill="none" stroke="var(--trunk)" stroke-width="26" stroke-linecap="round"/>
  <path d="M4-90c-8-22-14-44-14-66M10-170c10-18 20-34 34-48" fill="none" stroke="var(--trunk)" stroke-width="7" stroke-linecap="round" opacity=".65"/>
  <path d="M12-278c-64-12-128-34-174-64M14-288c58-20 120-44 166-78M12-302c-24-44-36-88-30-132M14-300c24-24 44-50 58-82" fill="none" stroke="var(--trunk)" stroke-width="11" stroke-linecap="round"/>
  <path d="M-220-352C-216-378-192-396-162-400-154-416-126-424-100-418-84-430-52-434-26-424-6-436 26-432 46-420 66-430 98-426 116-412 140-416 164-400 174-380 182-366 178-352 162-344 148-334 126-330 108-336 92-326 66-322 48-330 30-322 2-320-14-330-36-320-66-324-84-336-104-328-134-332-150-342-176-334-202-340-212-348Z" fill="var(--leaf-b)" stroke="#3A2A1A" stroke-width="3" stroke-linejoin="round"/>
  <path d="M-170-382c14-18 42-28 72-28 20 0 38 4 50 12-14 12-38 16-64 16-22 6-44 4-58 0z" fill="var(--leaf-a)"/>
  <path d="M-40-406c18-14 46-18 72-10 20 6 34 16 42 28-16 8-38 10-62 4-22 4-40-6-52-22z" fill="var(--leaf-a)"/>
  <path d="M66-394c16-10 38-12 56-4 16 6 28 18 32 30-14 6-34 6-54 0-16 2-28-8-34-26z" fill="var(--leaf-a)"/>
  <path d="M-186-348c40 10 86 12 132 6 36 0 70-6 98-16-10 12-30 20-56 24-26 6-60 8-92 4-34 4-64-4-82-18z" fill="#6F7F2A" opacity=".35"/>
  <path d="M-150-388c26-6 52-6 78 0M-10-412c28-4 56-2 84 4M96-386c20-2 40 2 60 8" fill="none" stroke="#5F6F24" stroke-width="3" stroke-linecap="round" opacity=".45"/>
</g>`;

const savannaGrass = (x, y, s, flip = 1) => `
<g transform="translate(${x} ${y}) scale(${s * flip} ${s})" fill="none" stroke="var(--grass)" stroke-linecap="round">
  <path d="M-6 0C-16-34-30-58-48-74" stroke-width="6"/>
  <path d="M2 0C-2-46 2-86 0-120" stroke-width="7"/>
  <path d="M10 0C14-38 26-70 44-94" stroke-width="6"/>
  <path d="M18 0C30-26 46-46 66-56" stroke-width="5"/>
  <path d="M-20 0C-28-22-40-36-56-44" stroke-width="4" opacity=".8"/>
  <ellipse cx="0" cy="-124" rx="9" ry="17" fill="var(--grass)" stroke="none" opacity=".95"/>
  <ellipse cx="46" cy="-98" rx="7" ry="14" fill="var(--grass)" stroke="none" opacity=".85" transform="rotate(18 46 -98)"/>
  <ellipse cx="-50" cy="-76" rx="6" ry="12" fill="var(--grass)" stroke="none" opacity=".8" transform="rotate(-20 -50 -76)"/>
</g>`;

const savannaReeds = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})" fill="none" stroke="#5E7A2E" stroke-linecap="round">
  <path d="M0 0C-8-36-6-72 2-104" stroke-width="6"/>
  <path d="M12 0C10-30 18-58 30-82" stroke-width="5"/>
  <path d="M-12 0C-18-26-26-46-38-60" stroke-width="5"/>
  <ellipse cx="2" cy="-110" rx="7" ry="18" fill="#7E4A2A" stroke="none" transform="rotate(4 2 -110)"/>
  <ellipse cx="31" cy="-88" rx="6" ry="15" fill="#7E4A2A" stroke="none" transform="rotate(14 31 -88)"/>
  <ellipse cx="-40" cy="-64" rx="5" ry="13" fill="#7E4A2A" stroke="none" transform="rotate(-18 -40 -64)"/>
</g>`;

const termiteMound = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-44 0C-38-54-22-94 0-124 22-94 38-54 44 0z" fill="#A86A3A" stroke="#3A2A1A" stroke-width="5"/>
  <path d="M-20-18c-2-34 4-66 20-90M16-14c4-30 2-58-10-80" fill="none" stroke="#C98B53" stroke-width="4" stroke-linecap="round" opacity=".6"/>
  <path d="M-8-106c6-10 16-10 22 0" fill="none" stroke="#5A3A24" stroke-width="4" stroke-linecap="round"/>
</g>`;

const savannaFarTree = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})" fill="#8F6C36" opacity=".5">
  <path d="M0 0c-2-20 0-38 5-56h7c-4 18-4 38 0 56z"/>
  <path d="M-34-56c8-12 24-18 38-18s30 6 38 18c-14-5-26-7-38-7s-24 2-38 7z"/>
</g>`;

const savannaKopje = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-90 0c-8-28 12-54 44-64 30-10 66-2 84 18 14 16 10 34-8 46z" fill="#9A6F3A" opacity=".78"/>
  <path d="M-50-34c18-10 42-12 64-4" fill="none" stroke="#7E562C" stroke-width="4" opacity=".5" stroke-linecap="round"/>
</g>`;

const autumnTree = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-18 0C-14-96-10-182-16-270h36C20-182 24-96 32 0Z" fill="var(--trunk)" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M4-200c-34-36-76-56-120-62M8-244c40-38 86-58 136-56M0-286c-20-36-28-72-22-108M12-294c28-30 50-64 60-100" fill="none" stroke="var(--trunk)" stroke-width="11" stroke-linecap="round"/>
  <path d="M-206-248c-18-48 18-92 72-104 22-44 76-68 128-48 38-30 96-22 120 18 50 6 82 46 72 90 30 32 16 78-26 94-36 28-92 30-140 18-40 18-94 16-130-8-46 10-96-10-96-60z" fill="var(--leaf-b)" stroke="#3A2A1A" stroke-width="3" stroke-linejoin="round"/>
  <path d="M-156-292c28-30 74-40 112-24 26 12 40 32 40 56-30 14-70 14-104 2-26-8-42-20-48-34z" fill="var(--leaf-a)"/>
  <path d="M24-322c32-22 76-22 106 0 20 14 30 34 28 56-30 10-66 6-96-8-22-10-34-28-38-48z" fill="var(--leaf-c)"/>
  <path d="M-80-198c30-18 70-20 102-4 20 10 32 26 34 44-26 10-58 8-86-2-22-8-40-20-50-38z" fill="var(--leaf-a)" opacity=".85"/>
  <g fill="none" stroke="var(--leaf-c)" stroke-width="3" stroke-linecap="round" opacity=".5">
    <path d="M-170-270c26-14 54-16 82-6M-20-300c28-8 58-6 86 4M120-300c18-2 36 2 52 10"/>
  </g>
</g>`;

const autumnFarTree = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})" fill="#9A5A32" opacity=".5">
  <path d="M0 0c-2-20 0-38 5-56h7c-4 18-4 38 0 56z"/>
  <path d="M-34-56c8-12 24-18 38-18s30 6 38 18c-14-5-26-7-38-7s-24 2-38 7z"/>
</g>`;

const hayBale = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <circle cx="0" cy="-40" r="40" fill="#D9A64E" stroke="#3A2A1A" stroke-width="5"/>
  <circle cx="0" cy="-40" r="24" fill="none" stroke="#B87A30" stroke-width="4" opacity=".8"/>
  <circle cx="0" cy="-40" r="9" fill="none" stroke="#B87A30" stroke-width="3" opacity=".7"/>
  <path d="M-22-56c12-10 32-10 44 0" fill="none" stroke="#E8BE6A" stroke-width="4" stroke-linecap="round" opacity=".8"/>
</g>`;

const barn = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-62 0v-70h124v70z" fill="#A84E36" stroke="#3A2A1A" stroke-width="5"/>
  <path d="M-76-70L0-116l76 46z" fill="#6E2E22" stroke="#3A2A1A" stroke-width="5" stroke-linejoin="round"/>
  <rect x="-17" y="-48" width="34" height="48" fill="#5A2A20" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-46-54h18v18h-18zM28-54h18v18h-18z" fill="#F2C98E" stroke="#3A2A1A" stroke-width="3.5"/>
  <path d="M-6-104h12v14H-6z" fill="#D9A64E" stroke="#3A2A1A" stroke-width="3"/>
</g>`;

const fenceLine = (x0, x1, y, step = 120) => {
  let out = `<path d="M${x0} ${y}h${x1 - x0}M${x0} ${y + 24}h${x1 - x0}" stroke="#6E4A2E" stroke-width="8" fill="none" stroke-linecap="round" opacity=".8"/>`;
  for (let x = x0; x <= x1; x += step) {
    out += `<path d="M${x} ${y - 22}v52" stroke="#6E4A2E" stroke-width="10" stroke-linecap="round" opacity=".85"/>`;
  }
  return out;
};

const autumnGrass = (x, y, s, flip = 1) => `
<g transform="translate(${x} ${y}) scale(${s * flip} ${s})" fill="none" stroke="var(--grass)" stroke-linecap="round">
  <path d="M-6 0C-16-34-30-58-48-74" stroke-width="6"/>
  <path d="M2 0C-2-46 2-86 0-120" stroke-width="7"/>
  <path d="M10 0C14-38 26-70 44-94" stroke-width="6"/>
  <path d="M18 0C30-26 46-46 66-56" stroke-width="5"/>
  <ellipse cx="0" cy="-124" rx="8" ry="16" fill="var(--grass)" stroke="none" opacity=".95"/>
  <ellipse cx="46" cy="-98" rx="6" ry="13" fill="var(--grass)" stroke="none" opacity=".85" transform="rotate(18 46 -98)"/>
  <ellipse cx="-50" cy="-76" rx="5" ry="11" fill="var(--grass)" stroke="none" opacity=".8" transform="rotate(-20 -50 -76)"/>
</g>`;

const cherryTree = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-16 0C-12-80-8-150-14-220h32C22-150 26-80 34 0Z" fill="var(--trunk)" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M4-160c-30-34-66-52-104-58M8-200c34-34 72-52 114-50M0-236c-18-30-24-60-18-90M10-244c24-26 44-54 52-84" fill="none" stroke="var(--trunk)" stroke-width="10" stroke-linecap="round"/>
  <path d="M-176-200c-16-40 16-78 62-88 18-38 64-58 108-40 32-26 82-18 102 16 42 4 70 38 62 76 26 28 14 68-22 82-32 24-80 26-120 16-34 16-80 14-112-6-40 8-82-8-80-56z" fill="var(--leaf-b)" stroke="#3A2A1A" stroke-width="3" stroke-linejoin="round"/>
  <path d="M-132-238c24-26 64-34 96-20 22 10 34 28 34 48-26 12-60 12-90 2-22-8-36-18-40-30z" fill="var(--leaf-a)"/>
  <path d="M18-264c28-18 64-18 90 0 18 12 26 30 24 50-26 10-58 6-82-6-20-8-30-24-32-44z" fill="var(--leaf-c)"/>
  <path d="M-70-166c26-16 60-18 88-4 18 10 28 24 30 40-22 8-50 6-74-2-20-8-34-18-44-34z" fill="var(--leaf-a)" opacity=".8"/>
  <g fill="none" stroke="var(--leaf-c)" stroke-width="3" stroke-linecap="round" opacity=".45">
    <path d="M-146-224c24-12 50-14 76-6M-18-246c24-6 50-4 74 4M104-246c16-2 32 2 46 8"/>
  </g>
</g>`;

const cherryFarTree = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})" fill="#D989A2" opacity=".45">
  <path d="M0 0c-2-20 0-38 5-56h7c-4 18-4 38 0 56z"/>
  <path d="M-36-56c8-14 24-20 40-20s32 6 40 20c-14-6-28-8-40-8s-26 2-40 8z"/>
</g>`;

const cypress = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0C-24-58-22-150 0-230 22-150 24-58 0 0Z" fill="#3E6A4A" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M0-12V-210" stroke="#2E523A" stroke-width="4" opacity=".5"/>
  <path d="M-8-100c8 4 16 4 24 0M-6-150c7 3 14 3 21 0" fill="none" stroke="#2E523A" stroke-width="3" opacity=".4"/>
</g>`;

const lavenderField = () => {
  const rows = [
    { y: 1400, s: 0.16, n: 28, off: 0, op: 0.4 },
    { y: 1460, s: 0.22, n: 26, off: 16, op: 0.5 },
    { y: 1528, s: 0.3, n: 24, off: 24, op: 0.62 },
    { y: 1604, s: 0.4, n: 22, off: 8, op: 0.75 },
    { y: 1688, s: 0.52, n: 20, off: 34, op: 0.88 },
    { y: 1778, s: 0.68, n: 18, off: 0, op: 1 },
    { y: 1878, s: 0.9, n: 16, off: 26, op: 1 },
  ];
  let out = '';
  for (const row of rows) {
    for (let i = 0; i < row.n; i += 1) {
      const x = 18 + i * ((1080 - 36) / (row.n - 1)) + row.off;
      if (row.y > 1500 && Math.abs(x - 540) < 58) continue;
      out += `<g opacity="${row.op}">${lavender(x, row.y, row.s)}</g>`;
    }
  }
  return out;
};

const umbrella = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0v-230" stroke="#6B4A2A" stroke-width="11" stroke-linecap="round"/>
  <path d="M-150-226c20-84 82-126 144-126s124 42 144 126z" fill="var(--umbrella-a)" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M-74-224c6-48 30-86 62-108M74-224c-6-48-30-86-62-108M0-226v-124" fill="none" stroke="var(--umbrella-b)" stroke-width="16" opacity=".85"/>
</g>`;

const beachBall = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <circle r="38" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="5"/>
  <path d="M0-38A38 38 0 0 1 26 28L0 0Z" fill="#E84343"/>
  <path d="M0-38A38 38 0 0 0-26 28L0 0Z" fill="#1CB0F6"/>
  <path d="M-36 10A38 38 0 0 0 36 10L0 0Z" fill="#FFC800"/>
</g>`;

const starfish = (x, y, s) => `
<path transform="translate(${x} ${y}) scale(${s})" d="M0-32l10 22 24 3-17 17 4 24-21-11-21 11 4-24-17-17 24-3z" fill="#FF8C42" stroke="#3A2A1A" stroke-width="4" stroke-linejoin="round"/>`;

const shell = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-26 0C-26-30 26-30 26 0Z" fill="#FFD7C2" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-14-4v-16M0-6v-20M14-4v-16" stroke="#E8A58A" stroke-width="3"/>
</g>`;

const stoneLantern = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <rect x="-34" y="-24" width="68" height="24" rx="7" fill="#8B8B8B" stroke="#3A2A1A" stroke-width="5"/>
  <rect x="-12" y="-120" width="24" height="96" fill="#9B9B9B" stroke="#3A2A1A" stroke-width="5"/>
  <rect x="-38" y="-164" width="76" height="44" rx="9" fill="#9B9B9B" stroke="#3A2A1A" stroke-width="5"/>
  <path d="M-48-164L0-208 48-164z" fill="#7B7B7B" stroke="#3A2A1A" stroke-width="5"/>
  <rect x="-14" y="-150" width="28" height="18" rx="4" fill="#FFC800"/>
</g>`;

const snowman = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <circle cx="0" cy="-42" r="42" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="5"/>
  <circle cx="0" cy="-112" r="31" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="5"/>
  <circle cx="0" cy="-158" r="23" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="5"/>
  <circle cx="-8" cy="-162" r="3" fill="#2B2B2B"/><circle cx="8" cy="-162" r="3" fill="#2B2B2B"/>
  <path d="M0-154l15 6-15 6z" fill="#FF8C42" stroke="#3A2A1A" stroke-width="2"/>
  <path d="M-16-66l-22-16M16-66l22-16" stroke="#6B4A2A" stroke-width="4" stroke-linecap="round"/>
  <path d="M-18-186l18-19 18 19z" fill="#E84343" stroke="#3A2A1A" stroke-width="3"/>
</g>`;

const lampPost = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0v-250" stroke="#5A4A3A" stroke-width="13" stroke-linecap="round"/>
  <rect x="-34" y="-282" width="68" height="44" rx="8" fill="#5A4A3A" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-46-282L0-326 46-282z" fill="#6B5A48" stroke="#3A2A1A" stroke-width="4"/>
  <rect x="-19" y="-272" width="38" height="28" rx="5" fill="#FFE6A6" stroke="#3A2A1A" stroke-width="3"/>
  <circle cx="0" cy="-312" r="9" fill="#FFD93B" opacity=".9"/>
</g>`;

const pagoda = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <rect x="-52" y="-22" width="104" height="22" rx="7" fill="#8B8B8B" stroke="#3A2A1A" stroke-width="4"/>
  <rect x="-30" y="-78" width="60" height="56" fill="#A0A0A0" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-58-78L0-118 58-78z" fill="#7B7B7B" stroke="#3A2A1A" stroke-width="5"/>
  <rect x="-22" y="-158" width="44" height="80" fill="#A0A0A0" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-48-158L0-198 48-158z" fill="#7B7B7B" stroke="#3A2A1A" stroke-width="5"/>
  <rect x="-14" y="-238" width="28" height="40" fill="#A0A0A0" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-36-238L0-274 36-238z" fill="#7B7B7B" stroke="#3A2A1A" stroke-width="5"/>
</g>`;

const bigLeaf = (x, y, s, flip = 1) => `
<g transform="translate(${x} ${y}) scale(${s * flip} ${s})">
  <path d="M0 0C-46-22-78-82-62-156 10-140 48-74 36 0z" fill="var(--leaf-b)" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M-4-14C-22-56-30-98-22-138M10-20C2-60 6-104 20-140" fill="none" stroke="var(--leaf-c)" stroke-width="5" stroke-linecap="round"/>
</g>`;

const jungleFlower = (x, y, s, color) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0v-34" stroke="#3F8A4A" stroke-width="5" stroke-linecap="round"/>
  <g transform="translate(0 -52)">
    <ellipse cx="0" cy="-16" rx="9" ry="17" fill="${color}" stroke="#3A2A1A" stroke-width="3"/>
    <ellipse cx="0" cy="16" rx="9" ry="17" fill="${color}" stroke="#3A2A1A" stroke-width="3"/>
    <ellipse cx="-16" cy="0" rx="9" ry="17" fill="${color}" stroke="#3A2A1A" stroke-width="3"/>
    <ellipse cx="16" cy="0" rx="9" ry="17" fill="${color}" stroke="#3A2A1A" stroke-width="3"/>
    <circle cx="0" cy="0" r="8" fill="#FFD93B" stroke="#3A2A1A" stroke-width="3"/>
  </g>
</g>`;

const torii = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-138 0h34l14-250h-34zM104 0h34l-14-250h-34z" fill="#D94A3A" stroke="#3A2A1A" stroke-width="5"/>
  <rect x="-170" y="-292" width="340" height="30" rx="10" fill="#D94A3A" stroke="#3A2A1A" stroke-width="5"/>
  <rect x="-136" y="-238" width="272" height="20" rx="7" fill="#D94A3A" stroke="#3A2A1A" stroke-width="5"/>
</g>`;

const lavender = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0C-4-10-4-20-2-30M-8 0C-10-8-10-18-8-26M8 0C10-8 10-18 8-26" fill="none" stroke="#5E8A45" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="0" cy="-24" rx="14" ry="12" fill="#6E9A50"/>
  <ellipse cx="-6" cy="-32" rx="7" ry="16" fill="var(--lavender)"/>
  <ellipse cx="2" cy="-40" rx="8" ry="18" fill="var(--lavender)"/>
  <ellipse cx="10" cy="-32" rx="7" ry="15" fill="var(--lavender-2)"/>
  <ellipse cx="-14" cy="-26" rx="5" ry="12" fill="var(--lavender-2)"/>
  <ellipse cx="16" cy="-24" rx="5" ry="11" fill="var(--lavender)"/>
</g>`;

const windmill = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M-54 0L-34-210H34L54 0Z" fill="#F4E6D0" stroke="#3A2A1A" stroke-width="6"/>
  <path d="M-46-78H46M-41-142H41" stroke="#D8C4A8" stroke-width="4" opacity=".65"/>
  <path d="M-60-210L0-288 60-210Z" fill="#8A5A3B" stroke="#3A2A1A" stroke-width="6" stroke-linejoin="round"/>
  <rect x="-15" y="-62" width="30" height="62" rx="5" fill="#6B4A3A" stroke="#3A2A1A" stroke-width="4"/>
  <rect x="-11" y="-152" width="22" height="28" rx="4" fill="#FFE2A8" stroke="#3A2A1A" stroke-width="4"/>
  <path d="M0-180v-16" stroke="#6B4A3A" stroke-width="7"/>
  <g transform="translate(0 -198) rotate(45)">
    <g>
      <path d="M0 0V-98" stroke="#6B4A3A" stroke-width="7" stroke-linecap="round"/>
      <path d="M-11-98h22l-4 62h-14z" fill="#FFF6E8" stroke="#6B4A3A" stroke-width="4" stroke-linejoin="round"/>
      <path d="M-8-86h16M-7-72h14M-6-58h12" stroke="#6B4A3A" stroke-width="3" opacity=".7"/>
    </g>
    <g transform="rotate(90)">
      <path d="M0 0V-98" stroke="#6B4A3A" stroke-width="7" stroke-linecap="round"/>
      <path d="M-11-98h22l-4 62h-14z" fill="#FFF6E8" stroke="#6B4A3A" stroke-width="4" stroke-linejoin="round"/>
      <path d="M-8-86h16M-7-72h14M-6-58h12" stroke="#6B4A3A" stroke-width="3" opacity=".7"/>
    </g>
    <g transform="rotate(180)">
      <path d="M0 0V-98" stroke="#6B4A3A" stroke-width="7" stroke-linecap="round"/>
      <path d="M-11-98h22l-4 62h-14z" fill="#FFF6E8" stroke="#6B4A3A" stroke-width="4" stroke-linejoin="round"/>
      <path d="M-8-86h16M-7-72h14M-6-58h12" stroke="#6B4A3A" stroke-width="3" opacity=".7"/>
    </g>
    <g transform="rotate(270)">
      <path d="M0 0V-98" stroke="#6B4A3A" stroke-width="7" stroke-linecap="round"/>
      <path d="M-11-98h22l-4 62h-14z" fill="#FFF6E8" stroke="#6B4A3A" stroke-width="4" stroke-linejoin="round"/>
      <path d="M-8-86h16M-7-72h14M-6-58h12" stroke="#6B4A3A" stroke-width="3" opacity=".7"/>
    </g>
    <circle r="12" fill="#6B4A3A" stroke="#3A2A1A" stroke-width="4"/>
  </g>
</g>`;

const bamboo = (x, y, s) => `
<g transform="translate(${x} ${y}) scale(${s})">
  <path d="M0 0C-6-120-2-240 0-360" stroke="var(--bamboo)" stroke-width="18" stroke-linecap="round"/>
  <path d="M-7-90h14M-4-170h12M-2-250h12M0-330h10" stroke="#3A2A1A" stroke-width="4" opacity=".45"/>
  <path d="M0-240c-30-30-60-38-88-34M0-290c32-28 62-36 92-30M0-200c-28-20-50-24-74-22M0-330c24-20 48-26 70-22" fill="none" stroke="var(--leaf-a)" stroke-width="9" stroke-linecap="round"/>
  <path d="M-88-274c-22-10-34-24-38-42 18 2 32 14 38 42zM92-320c22-8 34-20 40-38-18 2-32 14-40 38zM-74-222c-20-8-32-20-36-36 18 2 30 14 36 36zM70-352c20-8 32-20 36-36-18 2-30 14-36 36z" fill="var(--leaf-b)" stroke="#3A2A1A" stroke-width="3"/>
</g>`;

const lavenderRows = () => {
  let out = '';
  for (let row = 0; row < 2; row += 1) {
    for (let i = 0; i < 14; i += 1) {
      const x = 18 + i * 78 + (row ? 24 : 0);
      const y = 1888 - row * 46;
      const s = 0.78 + ((i * 7) % 5) * 0.07;
      out += lavender(x, y, s);
    }
  }
  return out;
};

const WORLD_DECOR = {
  garden: '',

  forest: art(`
    <path d="M0 1150c150-16 250 8 380-4s250-18 380 0 220 12 320-2v144H0z" fill="#7EA868"/>
    <path d="M0 1236c180-20 300 10 470-6s300-18 610 6v690H0z" fill="var(--forest-ground)"/>
    <path d="M0 1456c180-24 320 14 500-8s300-16 580 8v470H0z" fill="var(--forest-ground-2)"/>
    <path d="M0 1706c180-20 340 14 540-6s300-12 540 8v220H0z" fill="var(--forest-ground-3)"/>
    <ellipse cx="540" cy="1300" rx="540" ry="84" fill="#E8F2D4" opacity=".16"/>
    <ellipse cx="540" cy="1450" rx="560" ry="90" fill="#E8F2D4" opacity=".10"/>
    <path d="M70 1150l190 0 160 770-190 0z" fill="#FFF6C7" opacity=".035"/>
    <path d="M670 1150l130 0 180 770-130 0z" fill="#FFF6C7" opacity=".025"/>
    <path d="M250 1920c50-90 140-130 180-200 30-50 30-90 50-130h90c-20 50-14 100-50 150-48 70-120 110-150 180z" fill="#B9905E" opacity=".32"/>
    <g opacity=".45">
      ${broadTree(318, 1650, 0.5)}
      ${broadTree(760, 1640, 0.46)}
    </g>
    <path d="M0 0h210l250 1300H0z" fill="#FFF6C7" opacity=".10"/>
    <path d="M1080 0H870L640 1300h440z" fill="#FFF6C7" opacity=".08"/>
    <path d="M0 0h120l180 920H0z" fill="#FFFDF6" opacity=".025"/>
    <ellipse cx="540" cy="1880" rx="430" ry="48" fill="#6B4A32" opacity=".24"/>
    <ellipse cx="220" cy="1740" rx="130" ry="28" fill="#FFF6C7" opacity=".08"/>
    <ellipse cx="860" cy="1600" rx="110" ry="22" fill="#FFF6C7" opacity=".06"/>
    ${broadTree(42, 1920, 1.28)}
    ${broadTree(1014, 1920, 1.22)}
    ${broadTree(246, 1860, 0.52)}
    ${broadTree(836, 1840, 0.46)}
    ${bush(120, 1920, 1.15)}
    ${bush(958, 1920, 1.05)}
    ${fern(152, 1888, 1.22, 1)}
    ${fern(930, 1904, 1.12, -1)}
    ${fern(390, 1710, 0.7, 1)}
    ${fern(694, 1690, 0.64, -1)}
    ${mushroom(352, 1818, 1.05, '#E84A5F')}
    ${mushroom(398, 1838, 0.76, '#FFC800')}
    ${mushroom(724, 1772, 0.92, '#E84A5F')}
    ${mushroom(790, 1800, 0.62, '#FFC800')}
    ${log(330, 1872, 0.9)}
    ${rock(824, 1862, 1.05)}
    ${rock(286, 1880, 0.78)}
    ${tuft(510, 1888, 0.9)}
    ${tuft(610, 1904, 0.72)}
    ${tuft(860, 1900, 0.8)}
  `) + glowField(28, 101, 1240, 1820),

  beach: art(`
    <defs>
      <linearGradient id="seaGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="var(--sea-deep)"/>
        <stop offset="1" stop-color="var(--sea)"/>
      </linearGradient>
    </defs>
    <rect x="0" y="1120" width="1080" height="420" fill="url(#seaGrad)"/>
    <g fill="none" stroke="#BFF4FF" stroke-linecap="round">
      <path d="M0 1260c120-10 220 8 340 0s260-12 400-2 220 8 340-2" stroke-width="8" opacity=".30"/>
      <path d="M0 1350c140-12 240 10 360 0s250-10 370 0 240 8 350-4" stroke-width="7" opacity=".24"/>
      <path d="M0 1430c130-8 230 8 350 0s250-8 380 0 230 6 350-2" stroke-width="6" opacity=".20"/>
    </g>
    <g stroke="#FFF1C9" stroke-linecap="round" opacity=".18">
      <path d="M792 1188v54M820 1208v42M850 1176v62M878 1226v30M906 1198v50" stroke-width="5"/>
    </g>
    <path d="M0 1468c94-22 168 20 262 8 94-12 154-36 252-24 98 12 156 34 254 22 68-8 122-24 172-18v104H0z" fill="var(--sea-foam)" opacity=".9"/>
    <path d="M0 1504c110-28 178 18 280 4 102-14 162-40 262-28 100 12 164 38 264 24 84-12 138-26 194-20" fill="none" stroke="#FFFDF6" stroke-width="8" opacity=".55" stroke-linecap="round"/>
    ${palm(28, 1920, 1.22, 1)}
    ${palm(1040, 1920, 1.16, -1)}
    ${umbrella(358, 1780, 0.72)}
    ${beachBall(404, 1860, 0.85)}
    ${starfish(738, 1834, 1.0)}
    ${shell(784, 1848, 0.9)}
    ${shell(292, 1842, 0.72)}
    ${rock(520, 1888, 0.7)}
  `),

  desert: art(`
    <path d="M0 1220c170-70 300 24 470-10s260-84 430-38 180 8 180 8v740H0z" fill="var(--dune-a)"/>
    <path d="M0 1460c190-80 330 30 510-12s250-72 390-34 180 22 180 22v484H0z" fill="var(--dune-b)"/>
    <path d="M0 1660c150-48 280 18 430-10s250-50 380-24 170 18 170 18v276H0z" fill="var(--dune-c)"/>
    <path d="M0 1320c170-52 320 18 500-10s270-62 580-18" fill="none" stroke="#FFE4B8" stroke-width="7" opacity=".55"/>
    <path d="M0 1580c170-44 300 16 460-8s270-46 620-14" fill="none" stroke="#FFD59A" stroke-width="6" opacity=".4"/>
    ${cactus(92, 1848, 0.92)}
    ${cactus(356, 1880, 0.8)}
    ${cactus(720, 1888, 0.62)}
    ${cactus(958, 1860, 0.78)}
    ${rock(828, 1868, 0.9)}
    ${rock(292, 1888, 0.72)}
    ${rock(610, 1878, 0.5)}
    ${tuft(520, 1888, 0.55)}
  `),

  snow: art(`
    <path d="M-80 1330L190 940l270 390z" fill="var(--snow-mountain)" opacity=".92"/>
    <path d="M300 1350L610 880l330 470z" fill="var(--snow-mountain)" opacity=".88"/>
    <path d="M760 1330L990 990l230 340z" fill="var(--snow-mountain)" opacity=".8"/>
    <path d="M190 940l-56 80 56-18 56 18z" fill="#F7FBFF" opacity=".92"/>
    <path d="M610 880l-64 92 64-20 64 20z" fill="#F7FBFF" opacity=".94"/>
    <path d="M990 990l-50 74 50-16 50 16z" fill="#F7FBFF" opacity=".88"/>
    <path d="M0 1380c160-60 280 20 430-6s240-44 370-16 180 16 280 8v554H0z" fill="var(--snow-ground)"/>
    <path d="M0 1600c150-56 290 20 450-8s270-42 390-16 180 14 240 10v334H0z" fill="#D7E9FA" opacity=".9"/>
    <path d="M0 1750c160-42 300 18 460-6s270-34 390-12 170 10 230 8v180H0z" fill="#C8DFF4" opacity=".85"/>
    <ellipse cx="240" cy="1770" rx="80" ry="12" fill="#AFCBE8" opacity=".45"/>
    <ellipse cx="760" cy="1710" rx="90" ry="14" fill="#AFCBE8" opacity=".35"/>
    ${pine(84, 1900, 1.03)}
    ${pine(986, 1900, 0.92)}
    ${pine(206, 1916, 0.58)}
    ${pine(868, 1912, 0.54)}
    ${pine(292, 1916, 0.42)}
    ${pine(784, 1918, 0.4)}
    ${snowman(366, 1846, 0.72)}
    ${lampPost(318, 1848, 0.8)}
    ${rock(828, 1878, 0.7)}
  `) + fallField('snow', 38, 505, 46, 96),

  jungle: art(`
    <path d="M404 1190h272l32 88-38 54-70 22-92-12-58-50z" fill="#2B5A3C"/>
    <path d="M404 1190h72l12 92-44 58-54-38-20-58z" fill="#3F7A4A"/>
    <path d="M676 1190h-70l-8 92 40 58 50-34 18-62z" fill="#3F7A4A"/>
    <path d="M438 1300l-10 120 44 30 22-130z" fill="#244A34" opacity=".9"/>
    <path d="M642 1300l12 120-44 30-20-130z" fill="#244A34" opacity=".9"/>
    <ellipse cx="488" cy="1520" rx="44" ry="24" fill="#3F7A4A" opacity=".85"/>
    <ellipse cx="650" cy="1660" rx="48" ry="26" fill="#3F7A4A" opacity=".8"/>
    <path d="M510 1190h96l-14 24h-70z" fill="#FFFDF6" opacity=".65"/>
    <defs>
      <clipPath id="jungleFallClip"><path d="M518 1190h80l-10 116-16 166 14 154-18 146h-78l16-150-8-154 12-162z"/></clipPath>
    </defs>
    <path d="M518 1190h80l-10 116-16 166 14 154-18 146h-78l16-150-8-154 12-162z" fill="var(--waterfall)"/>
    <path d="M530 1200h14l-4 118-12 160 12 150-12 140h-14l12-142-8-150 10-160z" fill="#FFFDF6" opacity=".55"/>
    <path d="M566 1200h10l-6 116-6 164 10 150-10 134h-12l10-136-6-152 8-160z" fill="#FFFDF6" opacity=".38"/>
    <path d="M548 1208h8l-4 108-8 156 8 150-8 148h-8l8-150-4-152 8-160z" fill="#FFFDF6" opacity=".25"/>
    <g clip-path="url(#jungleFallClip)" fill="none" stroke="#FFFDF6" stroke-linecap="round">
      <path class="waterfall-streak" data-speed="110" data-phase="0" data-travel="150" d="M530 1240v74" stroke-width="4" opacity=".42"/>
      <path class="waterfall-streak" data-speed="128" data-phase="42" data-travel="150" d="M544 1308v86" stroke-width="3" opacity=".36"/>
      <path class="waterfall-streak" data-speed="96" data-phase="84" data-travel="150" d="M558 1266v64" stroke-width="5" opacity=".40"/>
      <path class="waterfall-streak" data-speed="118" data-phase="24" data-travel="150" d="M572 1372v92" stroke-width="3" opacity=".34"/>
      <path class="waterfall-streak" data-speed="104" data-phase="66" data-travel="150" d="M584 1320v70" stroke-width="4" opacity=".38"/>
      <path class="waterfall-streak" data-speed="136" data-phase="12" data-travel="150" d="M536 1452v88" stroke-width="3" opacity=".32"/>
      <path class="waterfall-streak" data-speed="90" data-phase="54" data-travel="150" d="M562 1520v96" stroke-width="4" opacity=".36"/>
      <path class="waterfall-streak" data-speed="122" data-phase="96" data-travel="150" d="M578 1602v80" stroke-width="3" opacity=".30"/>
    </g>
    <ellipse class="waterfall-foam" data-pivot="552 1846" cx="552" cy="1846" rx="142" ry="30" fill="var(--waterfall-foam)" opacity=".84"/>
    <ellipse class="waterfall-foam" data-pivot="552 1840" cx="552" cy="1840" rx="96" ry="17" fill="#FFFDF6" opacity=".6"/>
    <ellipse class="waterfall-mist" cx="540" cy="1790" rx="360" ry="62" fill="#FFFDF6" opacity=".10"/>
    <ellipse class="waterfall-mist" cx="552" cy="1815" rx="210" ry="42" fill="#FFFDF6" opacity=".12"/>
    <ellipse cx="470" cy="1850" rx="54" ry="24" fill="#3F7A4A" opacity=".9"/>
    <ellipse cx="640" cy="1832" rx="46" ry="22" fill="#3F7A4A" opacity=".85"/>
    <path d="M40 1160c30 140 0 240 50 360M1040 1120c-20 160 10 260-40 380" fill="none" stroke="var(--fern)" stroke-width="12" stroke-linecap="round"/>
    <path d="M-40 1900c70-210 190-280 300-220 80-150 220-130 300 20 120-90 230-40 280 140v100H-40z" fill="var(--jungle-bank)"/>
    ${bigLeaf(258, 1878, 0.86, 1)}
    ${bigLeaf(834, 1878, 0.8, -1)}
    ${fern(120, 1908, 1.28, 1)}
    ${fern(960, 1908, 1.2, -1)}
    ${broadTree(10, 1920, 0.9)}
    ${broadTree(1068, 1920, 0.86)}
    ${jungleFlower(392, 1838, 0.9, '#FF6B9A')}
    ${jungleFlower(724, 1860, 0.8, '#FFC800')}
    ${mushroom(320, 1824, 0.88, '#FF8FA3')}
    ${mushroom(780, 1832, 0.82, '#FFC800')}
    ${rock(860, 1880, 0.9)}
    ${tuft(430, 1896, 0.8)}
  `) + glowField(26, 202, 1240, 1820),

  savanna: art(`
    <path d="M0 1156c150-16 250 8 380-4s250-18 380 0 220 12 320-2v142H0z" fill="#EFC47E"/>
    <path d="M0 1190c150-22 280 10 420-4s260-16 390 0 190 8 270-2v134H0z" fill="#DCA95E"/>
    ${savannaKopje(818, 1248, 0.95)}
    ${savannaFarTree(120, 1244, 0.95)}
    ${savannaFarTree(292, 1240, 0.7)}
    ${savannaFarTree(470, 1246, 0.62)}
    ${savannaFarTree(654, 1246, 0.82)}
    ${savannaFarTree(840, 1242, 0.68)}
    ${savannaFarTree(990, 1244, 0.86)}
    <path d="M0 1236c180-20 300 10 470-6s300-18 610 6v690H0z" fill="var(--savanna-ground)"/>
    <path d="M0 1456c180-24 320 14 500-8s300-16 580 8v470H0z" fill="var(--savanna-ground-2)"/>
    <path d="M0 1706c180-20 340 14 540-6s300-12 540 8v220H0z" fill="#A97434"/>
    <path d="M448 1236c-24 90 18 150 12 222-6 80-58 130-70 212-4 26-6 46-6 66h150c-2-56 24-116 58-162 38-52 44-102 30-166-14-58-34-108-28-172z" fill="#DCAE66" opacity=".3"/>
    <ellipse cx="540" cy="1690" rx="550" ry="230" fill="#E8C07C" opacity=".16"/>
    <g fill="none" stroke="#8A5A26" stroke-width="4" opacity=".13" stroke-linecap="round">
      <path d="M-20 1360c180-18 320 14 500-8s300-20 620 4"/>
      <path d="M-20 1530c160-14 320 20 520-4s300-22 600 6"/>
      <path d="M-20 1720c180-20 340 16 540-6s280-18 580 8"/>
    </g>
    ${acacia(70, 1782, 0.46)}
    ${acacia(990, 1770, 0.4)}
    ${savannaGrass(402, 1660, 0.58)}
    ${savannaGrass(664, 1628, 0.52, -1)}
    ${savannaGrass(1006, 1596, 0.46, -1)}
    ${savannaGrass(262, 1762, 0.78, -1)}
    ${savannaGrass(420, 1778, 0.7)}
    ${savannaGrass(604, 1748, 0.64, -1)}
    ${savannaGrass(736, 1770, 0.72)}
    ${savannaGrass(986, 1750, 0.68, -1)}
    ${savannaGrass(280, 1896, 1.18)}
    ${savannaGrass(388, 1904, 0.94, -1)}
    ${savannaGrass(536, 1900, 1.08)}
    ${savannaGrass(704, 1908, 0.96, -1)}
    ${savannaGrass(858, 1894, 1.14)}
    ${savannaGrass(966, 1902, 0.82, -1)}
    ${savannaGrass(186, 1908, 0.7, -1)}
    ${savannaReeds(448, 1860, 0.88)}
    ${savannaReeds(718, 1852, 0.8)}
    ${termiteMound(386, 1876, 0.62)}
    ${rock(322, 1878, 0.52)}
    ${rock(688, 1864, 0.64)}
    ${rock(1010, 1888, 0.46)}
  `),

  autumn: art(`
    <path d="M0 1154c150-18 250 8 380-4s250-18 380 0 220 12 320-2v144H0z" fill="#E8B96E"/>
    <path d="M0 1190c150-22 280 10 420-4s260-16 390 0 190 8 270-2v132H0z" fill="#D99A54"/>
    ${barn(818, 1248, 0.62)}
    ${autumnFarTree(120, 1244, 0.9)}
    ${autumnFarTree(292, 1240, 0.68)}
    ${autumnFarTree(470, 1246, 0.58)}
    ${autumnFarTree(654, 1246, 0.76)}
    ${autumnFarTree(986, 1242, 0.82)}
    <path d="M0 1236c180-20 300 10 470-6s300-18 610 6v690H0z" fill="var(--autumn-ground)"/>
    <path d="M0 1456c180-24 320 14 500-8s300-16 580 8v470H0z" fill="var(--autumn-ground-2)"/>
    <path d="M0 1706c180-20 340 14 540-6s300-12 540 8v220H0z" fill="#8E522B"/>
    <path d="M526 1236c-30 90 8 150 0 222-10 80-54 134-64 212-4 26-4 46-4 66h160c-4-58 20-118 52-168 34-52 40-102 24-162-16-60-36-110-30-170z" fill="#DDB277" opacity=".32"/>
    <ellipse cx="540" cy="1690" rx="560" ry="240" fill="#F2C98E" opacity=".15"/>
    <g fill="none" stroke="#7E4A26" stroke-width="4" opacity=".12" stroke-linecap="round">
      <path d="M-20 1360c180-18 320 14 500-8s300-20 620 4"/>
      <path d="M-20 1530c160-14 320 20 520-4s300-22 600 6"/>
      <path d="M-20 1720c180-20 340 16 540-6s280-18 580 8"/>
    </g>
    ${autumnTree(46, 1810, 0.86)}
    ${autumnTree(1032, 1810, 0.82)}
    ${autumnGrass(260, 1600, 0.55)}
    ${autumnGrass(640, 1580, 0.5, -1)}
    ${autumnGrass(990, 1590, 0.46, -1)}
    ${autumnGrass(236, 1760, 0.72, -1)}
    ${autumnGrass(398, 1772, 0.66)}
    ${autumnGrass(612, 1748, 0.6, -1)}
    ${autumnGrass(736, 1766, 0.68)}
    ${autumnGrass(966, 1748, 0.62, -1)}
    ${autumnGrass(280, 1898, 1.1)}
    ${autumnGrass(388, 1904, 0.9, -1)}
    ${autumnGrass(536, 1900, 1.0)}
    ${autumnGrass(704, 1908, 0.9, -1)}
    ${autumnGrass(858, 1894, 1.04)}
    ${autumnGrass(966, 1902, 0.78, -1)}
    ${autumnGrass(186, 1908, 0.66, -1)}
    ${savannaReeds(448, 1858, 0.82)}
    ${savannaReeds(716, 1852, 0.74)}
    ${hayBale(212, 1892, 0.86)}
    ${hayBale(930, 1884, 0.7)}
    ${pumpkin(326, 1880, 0.82)}
    ${pumpkin(378, 1872, 0.58)}
    ${pumpkin(756, 1878, 0.68)}
    ${pumpkin(700, 1890, 0.48)}
    ${mushroom(470, 1884, 0.58, '#D75A2B')}
    ${mushroom(876, 1862, 0.5, '#FFC800')}
    ${rock(542, 1892, 0.5)}
    ${rock(1012, 1888, 0.44)}
    <g fill="#C96A2E" opacity=".75">
      <path d="M338 1722c8-6 17-3 18 5 1 8-7 13-15 10-8-3-10-11-3-15z"/>
      <path d="M612 1664c7-5 15-2 16 5 1 7-6 11-13 9-7-2-9-10-3-14z"/>
      <path d="M792 1778c7-5 15-2 16 5 1 7-6 11-13 9-7-2-9-10-3-14z"/>
      <path d="M224 1690c6-4 13-2 14 4 1 6-5 10-12 8-6-2-8-8-2-12z"/>
    </g>
  `) + fallField('leaf', 32, 303, 34, 70),

  cherry: art(`
    <path d="M0 1154c150-18 250 8 380-4s250-18 380 0 220 12 320-2v144H0z" fill="#F7DDE2"/>
    <path d="M0 1190c150-22 280 10 420-4s260-16 390 0 190 8 270-2v132H0z" fill="#EFC3CE"/>
    ${cherryFarTree(110, 1244, 0.9)}
    ${cherryFarTree(286, 1240, 0.66)}
    ${cherryFarTree(472, 1246, 0.58)}
    ${cherryFarTree(664, 1242, 0.78)}
    ${cherryFarTree(846, 1244, 0.64)}
    ${cherryFarTree(1006, 1240, 0.84)}
    <path d="M0 1236c180-20 300 10 470-6s300-18 610 6v690H0z" fill="var(--cherry-ground)"/>
    <path d="M0 1456c180-24 320 14 500-8s300-16 580 8v470H0z" fill="var(--cherry-ground-2)"/>
    <path d="M0 1706c180-20 340 14 540-6s300-12 540 8v220H0z" fill="var(--cherry-ground-3)"/>
    <ellipse cx="540" cy="1688" rx="560" ry="240" fill="#E8F2D0" opacity=".22"/>
    <g fill="none" stroke="#5E7A48" stroke-width="4" opacity=".12" stroke-linecap="round">
      <path d="M-20 1360c180-18 320 14 500-8s300-20 620 4"/>
      <path d="M-20 1530c160-14 320 20 520-4s300-22 600 6"/>
      <path d="M-20 1720c180-20 340 16 540-6s280-18 580 8"/>
    </g>
    ${torii(520, 1745, 0.72)}
    ${cherryTree(64, 1812, 1.0)}
    ${cherryTree(1014, 1810, 0.96)}
    ${stoneLantern(354, 1852, 0.55)}
    ${autumnGrass(252, 1600, 0.54)}
    ${autumnGrass(652, 1580, 0.48, -1)}
    ${autumnGrass(986, 1592, 0.46, -1)}
    ${autumnGrass(232, 1764, 0.7, -1)}
    ${autumnGrass(398, 1776, 0.64)}
    ${autumnGrass(612, 1750, 0.58, -1)}
    ${autumnGrass(736, 1770, 0.66)}
    ${autumnGrass(968, 1750, 0.6, -1)}
    ${autumnGrass(272, 1898, 1.08)}
    ${autumnGrass(386, 1904, 0.88, -1)}
    ${autumnGrass(536, 1900, 0.98)}
    ${autumnGrass(704, 1908, 0.88, -1)}
    ${autumnGrass(858, 1894, 1.02)}
    ${autumnGrass(966, 1902, 0.76, -1)}
    ${autumnGrass(176, 1908, 0.64, -1)}
    ${rock(316, 1882, 0.52)}
    ${rock(742, 1868, 0.58)}
    ${rock(1008, 1888, 0.44)}
    <g fill="#F4B8C8" opacity=".9">
      <path d="M338 1722c8-6 17-3 18 5 1 8-7 13-15 10-8-3-10-11-3-15z"/>
      <path d="M612 1664c7-5 15-2 16 5 1 7-6 11-13 9-7-2-9-10-3-14z"/>
      <path d="M792 1778c7-5 15-2 16 5 1 7-6 11-13 9-7-2-9-10-3-14z"/>
      <path d="M224 1690c6-4 13-2 14 4 1 6-5 10-12 8-6-2-8-8-2-12z"/>
      <path d="M920 1802c6-4 13-1 13 5 1 6-5 9-11 7-6-2-8-8-2-12z"/>
    </g>
  `) + fallField('petal', 30, 404, 34, 62),

  lavender: art(`
    <path d="M0 1154c150-18 250 8 380-4s250-18 380 0 220 12 320-2v144H0z" fill="#E8D4F2"/>
    <path d="M0 1190c150-22 280 10 420-4s260-16 390 0 190 8 270-2v132H0z" fill="#D9BCE8"/>
    <g opacity=".45">
      ${cypress(180, 1244, 0.2)}
      ${cypress(408, 1240, 0.16)}
      ${cypress(770, 1246, 0.18)}
      ${cypress(968, 1242, 0.14)}
    </g>
    <path d="M0 1236c180-20 300 10 470-6s300-18 610 6v690H0z" fill="var(--lavender-hill)"/>
    <path d="M0 1456c180-24 320 14 500-8s300-16 580 8v470H0z" fill="var(--lavender-hill-2)"/>
    <path d="M0 1706c180-20 340 14 540-6s300-12 540 8v220H0z" fill="#8E70B4"/>
    <path d="M514 1236c-8 90 4 170 8 250 4 80 8 160 14 240h52c-2-80-2-160 4-240 6-80 12-160 4-250z" fill="#D9C7A8" opacity=".5"/>
    <ellipse cx="540" cy="1690" rx="560" ry="240" fill="#E8D4F2" opacity=".18"/>
    <g fill="none" stroke="#6E508E" stroke-width="4" opacity=".12" stroke-linecap="round">
      <path d="M-20 1360c180-18 320 14 500-8s300-20 620 4"/>
      <path d="M-20 1530c160-14 320 20 520-4s300-22 600 6"/>
      <path d="M-20 1720c180-20 340 16 540-6s280-18 580 8"/>
    </g>
    ${windmill(540, 1710, 0.66)}
    ${cypress(120, 1740, 0.75)}
    ${cypress(960, 1720, 0.7)}
    ${lavenderField()}
    ${lavender(44, 1912, 1.3)}
    ${lavender(122, 1908, 1.1)}
    ${lavender(946, 1910, 1.2)}
    ${lavender(1028, 1906, 1.0)}
    ${rock(312, 1886, 0.52)}
    ${rock(772, 1874, 0.56)}
    ${autumnGrass(236, 1902, 0.62, -1)}
    ${autumnGrass(676, 1898, 0.58)}
    ${autumnGrass(850, 1908, 0.55, -1)}
  `),

  bamboo: art(`
    <path d="M0 1154c150-18 250 8 380-4s250-18 380 0 220 12 320-2v144H0z" fill="#DCEBCF"/>
    <path d="M0 1190c150-22 280 10 420-4s260-16 390 0 190 8 270-2v132H0z" fill="#C9DEC0"/>
    <ellipse cx="540" cy="1280" rx="530" ry="82" fill="#F1F7EA" opacity=".35"/>
    <ellipse cx="540" cy="1420" rx="560" ry="92" fill="#F1F7EA" opacity=".22"/>
    <path d="M0 1236c180-20 300 10 470-6s300-18 610 6v690H0z" fill="var(--bamboo-ground)"/>
    <path d="M0 1456c180-24 320 14 500-8s300-16 580 8v470H0z" fill="#78945E"/>
    <path d="M0 1706c180-20 340 14 540-6s300-12 540 8v220H0z" fill="#5E7A4A"/>
    <ellipse cx="540" cy="1688" rx="560" ry="240" fill="#DCEBCF" opacity=".14"/>
    <g fill="none" stroke="#46603A" stroke-width="4" opacity=".12" stroke-linecap="round">
      <path d="M-20 1360c180-18 320 14 500-8s300-20 620 4"/>
      <path d="M-20 1530c160-14 320 20 520-4s300-22 600 6"/>
      <path d="M-20 1720c180-20 340 16 540-6s280-18 580 8"/>
    </g>
    <g fill="#B8B8A8" stroke="#6E6E5E" stroke-width="3" opacity=".85">
      <path d="M398 1868c22-8 50-4 62 6 8 8-4 16-28 18-26 2-48-4-40-16z"/>
      <path d="M492 1830c18-6 42-2 52 6 8 8-4 16-24 18-22 2-40-4-34-14z"/>
      <path d="M582 1878c20-6 44-2 56 6 8 8-6 16-30 18-24 2-44-4-34-14z"/>
    </g>
    ${pagoda(390, 1600, 0.4)}
    ${stoneLantern(760, 1660, 0.42)}
    <g opacity=".5">
      ${bamboo(80, 1600, 0.55)}
      ${bamboo(240, 1592, 0.48)}
      ${bamboo(400, 1600, 0.52)}
      ${bamboo(680, 1594, 0.56)}
      ${bamboo(840, 1600, 0.5)}
      ${bamboo(1000, 1592, 0.54)}
    </g>
    <g opacity=".78">
      ${bamboo(150, 1780, 0.8)}
      ${bamboo(330, 1788, 0.72)}
      ${bamboo(750, 1780, 0.76)}
      ${bamboo(930, 1788, 0.7)}
    </g>
    ${bamboo(40, 1910, 1.25)}
    ${bamboo(148, 1904, 1.0)}
    ${bamboo(980, 1908, 1.18)}
    ${bamboo(1030, 1900, 0.92)}
    ${fern(70, 1912, 0.9, 1)}
    ${fern(1030, 1912, 0.85, -1)}
    ${rock(360, 1884, 0.55)}
    ${rock(720, 1872, 0.6)}
    ${rock(972, 1888, 0.46)}
    ${tuft(472, 1892, 0.62)}
    ${tuft(620, 1900, 0.55)}
    ${tuft(560, 1872, 0.45)}
  `) + fallField('leaf', 24, 606, 26, 52),
};
