/* Storybook cast - cute inline SVGs. Colours are CSS variables so the scene
   can tint them from the active theme. */

/* Alternating outer/inner points give a flat mane a clean fur edge without
   stacking dozens of outlined circles. */
function manePath(cx, cy, outer, inner, points = 16) {
  let d = '';
  for (let i = 0; i < points * 2; i += 1) {
    const a = -Math.PI / 2 + (i * Math.PI) / points;
    const r = i % 2 ? inner : outer;
    const x = cx + Math.cos(a) * r;
    const y = cy + Math.sin(a) * r;
    d += `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`;
  }
  return `${d}Z`;
}

const ANIMALS = {
  bunny: `
<svg class="animal-svg bunny-svg" viewBox="0 0 200 260" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="100" cy="248" rx="62" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="bunny-bob">
    <g class="bunny-tail"><circle cx="160" cy="208" r="15" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="4"/></g>
    <ellipse cx="100" cy="184" rx="62" ry="64" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="5"/>
    <ellipse cx="100" cy="196" rx="38" ry="42" fill="#FFFFFF"/>
    <ellipse cx="44" cy="182" rx="17" ry="12" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="4"/>
    <g class="bunny-paw">
      <ellipse cx="156" cy="182" rx="17" ry="12" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="4"/>
    </g>
    <g class="bunny-head">
      <g class="bunny-ear-l" transform="rotate(-10 78 118)">
        <ellipse cx="78" cy="66" rx="21" ry="56" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="5"/>
        <ellipse cx="78" cy="70" rx="10" ry="39" fill="#FFB3C1"/>
      </g>
      <g class="bunny-ear-r" transform="rotate(10 122 118)">
        <ellipse cx="122" cy="66" rx="21" ry="56" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="5"/>
        <ellipse cx="122" cy="70" rx="10" ry="39" fill="#FFB3C1"/>
      </g>
      <ellipse cx="100" cy="114" rx="64" ry="58" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="5"/>
      <ellipse cx="56" cy="128" rx="13" ry="7" fill="#FF9FB3" opacity=".7"/>
      <ellipse cx="144" cy="128" rx="13" ry="7" fill="#FF9FB3" opacity=".7"/>
      <g class="bunny-eye-l" transform="translate(76 106)">
        <circle r="9.5" fill="#2B2B2B"/>
        <circle cx="-3" cy="-3" r="3.4" fill="#FFFFFF"/>
      </g>
      <g class="bunny-eye-r" transform="translate(124 106)">
        <circle r="9.5" fill="#2B2B2B"/>
        <circle cx="-3" cy="-3" r="3.4" fill="#FFFFFF"/>
      </g>
      <path d="M100 124l8 7-8 6-8-6 8-7z" fill="#FF8FA3" stroke="#3A2A1A" stroke-width="2.5"/>
      <path d="M100 137v5M100 142c-4 6-10 6-13 2M100 142c4 6 10 6 13 2" fill="none" stroke="#3A2A1A" stroke-width="3" stroke-linecap="round"/>
    </g>
    <ellipse cx="70" cy="240" rx="23" ry="12" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="130" cy="240" rx="23" ry="12" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="4"/>
  </g>
</svg>`,

  frog: `
<svg class="animal-svg frog-svg" viewBox="0 0 180 140" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="90" cy="132" rx="54" ry="8" fill="#2A2A2A" opacity=".10"/>
  <g class="frog-bob">
    <path d="M44 104c-18-4-28-16-24-28 5 0 12 4 18 12 4-10 12-14 20-10 8 4 10 14 4 24z" fill="#5E8A32" stroke="#3E5A22" stroke-width="4.5" stroke-linejoin="round"/>
    <path d="M136 104c18-4 28-16 24-28-5 0-12 4-18 12-4-10-12-14-20-10-8 4-10 14-4 24z" fill="#5E8A32" stroke="#3E5A22" stroke-width="4.5" stroke-linejoin="round"/>
    <ellipse cx="90" cy="89" rx="58" ry="37" fill="#6F9A3A" stroke="#3E5A22" stroke-width="5"/>
    <path d="M54 80c8-14 64-14 72 0 6 10 2 22-8 28-14 8-42 8-56 0-10-6-14-18-8-28z" fill="#E9E2A8"/>
    <circle cx="58" cy="96" r="4" fill="#4E6E26" opacity=".7"/>
    <circle cx="74" cy="108" r="3.2" fill="#4E6E26" opacity=".65"/>
    <circle cx="124" cy="100" r="3.8" fill="#4E6E26" opacity=".7"/>
    <circle cx="108" cy="70" r="3.4" fill="#4E6E26" opacity=".55"/>
    <g class="frog-head">
      <g class="frog-eye-l" transform="translate(62 50)">
        <circle r="22" fill="#FFF3D6" stroke="#3E5A22" stroke-width="4.5"/>
        <circle cx="2" cy="1" r="10.5" fill="#E0B54A"/>
        <ellipse cx="2" cy="1" rx="5.5" ry="3" fill="#241C14"/>
        <circle cx="-1" cy="-2" r="2" fill="#FFFFFF" opacity=".9"/>
        <path d="M-17-7c5-7 29-7 34 0" fill="none" stroke="#3E5A22" stroke-width="3" stroke-linecap="round"/>
      </g>
      <g class="frog-eye-r" transform="translate(118 50)">
        <circle r="22" fill="#FFF3D6" stroke="#3E5A22" stroke-width="4.5"/>
        <circle cx="-2" cy="1" r="10.5" fill="#E0B54A"/>
        <ellipse cx="-2" cy="1" rx="5.5" ry="3" fill="#241C14"/>
        <circle cx="-5" cy="-2" r="2" fill="#FFFFFF" opacity=".9"/>
        <path d="M-17-7c5-7 29-7 34 0" fill="none" stroke="#3E5A22" stroke-width="3" stroke-linecap="round"/>
      </g>
      <circle cx="74" cy="84" r="1.8" fill="#3E5A22"/>
      <circle cx="106" cy="84" r="1.8" fill="#3E5A22"/>
      <path d="M72 92c10 9 26 9 36 0" fill="none" stroke="#3E5A22" stroke-width="4" stroke-linecap="round"/>
      <ellipse class="frog-throat" cx="90" cy="104" rx="17" ry="9" fill="#B7D47A"/>
    </g>
    <path d="M46 116c-10 0-16 5-16 10h32c0-5-6-10-16-10z" fill="#6F9A3A" stroke="#3E5A22" stroke-width="3.5"/>
    <path d="M134 116c10 0 16 5 16 10h-32c0-5 6-10 16-10z" fill="#6F9A3A" stroke="#3E5A22" stroke-width="3.5"/>
  </g>
</svg>`,

  hedgehog: `
<svg class="animal-svg hedgehog-svg" viewBox="0 0 180 130" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="90" cy="122" rx="58" ry="8" fill="#2A2A2A" opacity=".10"/>
  <g class="hedgehog-bob">
    <g class="hedgehog-spikes">
      <path d="M38 78L22 40 52 58z" fill="#7A4B2A" stroke="#3A2A1A" stroke-width="3"/>
      <path d="M54 66L48 26 78 52z" fill="#8A5A3B" stroke="#3A2A1A" stroke-width="3"/>
      <path d="M76 58L82 20 104 52z" fill="#7A4B2A" stroke="#3A2A1A" stroke-width="3"/>
      <path d="M98 56L116 30 122 64z" fill="#8A5A3B" stroke="#3A2A1A" stroke-width="3"/>
      <path d="M30 94L12 70 34 64z" fill="#8A5A3B" stroke="#3A2A1A" stroke-width="3"/>
    </g>
    <ellipse cx="86" cy="84" rx="58" ry="36" fill="#A66A3F" stroke="#3A2A1A" stroke-width="5"/>
    <g class="hedgehog-head">
      <ellipse cx="124" cy="84" rx="34" ry="28" fill="#FFE8C7" stroke="#3A2A1A" stroke-width="4"/>
      <path d="M154 82l10 5-10 6z" fill="#3A2A1A"/>
      <g class="hedgehog-eye-l" transform="translate(116 76)">
        <circle r="5.5" fill="#2B2B2B"/>
        <circle cx="-2" cy="-2" r="2" fill="#FFFFFF"/>
      </g>
      <g class="hedgehog-eye-r" transform="translate(136 76)">
        <circle r="5.5" fill="#2B2B2B"/>
        <circle cx="-2" cy="-2" r="2" fill="#FFFFFF"/>
      </g>
      <circle cx="90" cy="62" r="8" fill="#FF4B4B" stroke="#3A2A1A" stroke-width="3"/>
      <path d="M90 54c2-6 8-8 12-8-2 6-6 9-12 8z" fill="#6FBE63" stroke="#3A2A1A" stroke-width="2.5"/>
    </g>
    <ellipse cx="66" cy="116" rx="18" ry="8" fill="#A66A3F" stroke="#3A2A1A" stroke-width="3.5"/>
    <ellipse cx="116" cy="116" rx="18" ry="8" fill="#A66A3F" stroke="#3A2A1A" stroke-width="3.5"/>
  </g>
</svg>`,

  cat: `
<svg class="animal-svg cat-svg" viewBox="0 0 220 250" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="110" cy="240" rx="66" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="cat-bob">
    <g class="cat-tail" transform="rotate(8 178 198)">
      <path d="M176 208c26 4 42-10 44-30 2-18-10-30-22-30 8 10 8 22 0 30-10 10-24 8-32 2z" fill="#FFA94D" stroke="#3A2A1A" stroke-width="5" stroke-linejoin="round"/>
      <path d="M198 148c-4 8-4 17 2 23 1-9 3-17 8-23z" fill="#FFF6E8"/>
    </g>
    <ellipse cx="110" cy="188" rx="60" ry="52" fill="#FFA94D" stroke="#3A2A1A" stroke-width="5"/>
    <ellipse cx="110" cy="200" rx="35" ry="33" fill="#FFF6E8"/>
    <ellipse cx="56" cy="196" rx="17" ry="12" fill="#FFA94D" stroke="#3A2A1A" stroke-width="4"/>
    <g class="cat-paw">
      <ellipse cx="164" cy="196" rx="17" ry="12" fill="#FFA94D" stroke="#3A2A1A" stroke-width="4"/>
    </g>
    <g class="cat-head">
      <g class="cat-ear-l">
        <path d="M54 84L42 34l50 24z" fill="#FFA94D" stroke="#3A2A1A" stroke-width="5" stroke-linejoin="round"/>
        <path d="M58 72l-6-24 24 12z" fill="#FFB3C1"/>
      </g>
      <g class="cat-ear-r">
        <path d="M166 84l12-50-50 24z" fill="#FFA94D" stroke="#3A2A1A" stroke-width="5" stroke-linejoin="round"/>
        <path d="M162 72l6-24-24 12z" fill="#FFB3C1"/>
      </g>
      <ellipse cx="110" cy="112" rx="62" ry="54" fill="#FFA94D" stroke="#3A2A1A" stroke-width="5"/>
      <path d="M84 66l6 16M110 62v18M136 66l-6 16" fill="none" stroke="#E07B23" stroke-width="6" stroke-linecap="round"/>
      <ellipse cx="62" cy="130" rx="13" ry="8" fill="#FF9FB3" opacity=".65"/>
      <ellipse cx="158" cy="130" rx="13" ry="8" fill="#FF9FB3" opacity=".65"/>
      <g class="cat-eye-l" transform="translate(86 108)">
        <circle r="9.5" fill="#2B2B2B"/>
        <circle cx="-3" cy="-3" r="3.4" fill="#FFFFFF"/>
      </g>
      <g class="cat-eye-r" transform="translate(134 108)">
        <circle r="9.5" fill="#2B2B2B"/>
        <circle cx="-3" cy="-3" r="3.4" fill="#FFFFFF"/>
      </g>
      <path d="M110 124l8 6-8 6-8-6z" fill="#FF8FA3" stroke="#3A2A1A" stroke-width="2.5"/>
      <path d="M110 136v4M110 140c-4 6-10 6-13 2M110 140c4 6 10 6 13 2" fill="none" stroke="#3A2A1A" stroke-width="3" stroke-linecap="round"/>
      <path d="M56 116l-26-6M56 126l-28 4M164 116l26-6M164 126l28 4" fill="none" stroke="#3A2A1A" stroke-width="2.5" stroke-linecap="round" opacity=".75"/>
    </g>
    <ellipse cx="78" cy="236" rx="24" ry="12" fill="#FFA94D" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="142" cy="236" rx="24" ry="12" fill="#FFA94D" stroke="#3A2A1A" stroke-width="4"/>
  </g>
</svg>`,

  duck: `
<svg class="animal-svg duck-svg" viewBox="0 0 200 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="100" cy="170" rx="64" ry="9" fill="#2A2A2A" opacity=".10"/>
  <g class="duck-bob">
    <ellipse cx="56" cy="120" rx="24" ry="17" fill="#8A5A3A" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="144" cy="120" rx="24" ry="17" fill="#8A5A3A" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="100" cy="116" rx="60" ry="45" fill="#B08A5E" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M62 118c10-16 66-16 76 0 8 12 2 26-10 32-16 8-42 8-56 0-12-6-18-20-10-32z" fill="#E8D2B0"/>
    <path d="M74 104c8-14 44-14 52 0 5 9-2 18-12 22-10 4-22 4-30 0-10-4-15-13-10-22z" fill="#7A4A2E"/>
    <g class="duck-head">
      <circle cx="100" cy="66" r="40" fill="#2E6B3A" stroke="#3A2A1A" stroke-width="5"/>
      <path d="M80 96c12 6 28 6 40 0" fill="none" stroke="#FFF6E8" stroke-width="7" stroke-linecap="round"/>
      <ellipse cx="100" cy="84" rx="19" ry="10" fill="#F08A24" stroke="#3A2A1A" stroke-width="3.5"/>
      <path d="M88 80h24" fill="none" stroke="#3A2A1A" stroke-width="2.5" stroke-linecap="round"/>
      <g class="duck-eye-l" transform="translate(84 58)">
        <circle r="7.5" fill="#2B2118"/>
        <circle cx="-2.6" cy="-2.6" r="2.8" fill="#FFFFFF"/>
        <path d="M-9-7c5-4 12-4 17 0" fill="none" stroke="#1E4A2A" stroke-width="2.6" stroke-linecap="round"/>
      </g>
      <g class="duck-eye-r" transform="translate(116 58)">
        <circle r="7.5" fill="#2B2118"/>
        <circle cx="-2.6" cy="-2.6" r="2.8" fill="#FFFFFF"/>
        <path d="M-9-7c5-4 12-4 17 0" fill="none" stroke="#1E4A2A" stroke-width="2.6" stroke-linecap="round"/>
      </g>
    </g>
    <g class="duck-wing" transform="rotate(-8 66 118)">
      <path d="M48 108c-14 4-20 18-12 30 12 6 28 0 36-12-10-2-18-8-24-18z" fill="#7A4A2E" stroke="#3A2A1A" stroke-width="4" stroke-linejoin="round"/>
      <path d="M56 120c6 3 13 1 18-4" fill="none" stroke="#2E6FA8" stroke-width="6" stroke-linecap="round"/>
    </g>
    <path d="M72 158c-2 6-8 10-16 10 4-6 8-9 16-10zM128 158c2 6 8 10 16 10-4-6-8-9-16-10z" fill="#F08A24" stroke="#3A2A1A" stroke-width="3.5" stroke-linejoin="round"/>
  </g>
</svg>`,

  panda: `
<svg class="animal-svg panda-svg" viewBox="0 0 220 250" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="110" cy="240" rx="68" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="panda-bob">
    <ellipse cx="64" cy="186" rx="20" ry="32" transform="rotate(18 64 186)" fill="#2B2B2B" stroke="#1A1A1A" stroke-width="4"/>
    <ellipse cx="110" cy="190" rx="60" ry="50" fill="#FFFDF6" stroke="#2B2B2B" stroke-width="5"/>
    <ellipse cx="110" cy="198" rx="38" ry="34" fill="#FFFFFF"/>
    <g class="panda-paw">
      <ellipse cx="158" cy="180" rx="18" ry="30" transform="rotate(-24 158 180)" fill="#2B2B2B" stroke="#1A1A1A" stroke-width="4"/>
    </g>
    <g class="panda-head">
      <circle cx="58" cy="58" r="24" fill="#2B2B2B" stroke="#1A1A1A" stroke-width="4"/>
      <circle cx="162" cy="58" r="24" fill="#2B2B2B" stroke="#1A1A1A" stroke-width="4"/>
      <circle cx="110" cy="112" r="64" fill="#FFFDF6" stroke="#2B2B2B" stroke-width="5"/>
      <ellipse cx="86" cy="108" rx="20" ry="25" transform="rotate(-16 86 108)" fill="#2B2B2B"/>
      <ellipse cx="134" cy="108" rx="20" ry="25" transform="rotate(16 134 108)" fill="#2B2B2B"/>
      <g class="panda-eye-l" transform="translate(88 107)">
        <circle r="7" fill="#FFFFFF"/>
        <circle cx="1" cy="1" r="4.5" fill="#2B2B2B"/>
        <circle cx="-1" cy="-2" r="1.6" fill="#FFFFFF"/>
      </g>
      <g class="panda-eye-r" transform="translate(132 107)">
        <circle r="7" fill="#FFFFFF"/>
        <circle cx="-1" cy="1" r="4.5" fill="#2B2B2B"/>
        <circle cx="-3" cy="-2" r="1.6" fill="#FFFFFF"/>
      </g>
      <ellipse cx="110" cy="129" rx="10" ry="7" fill="#2B2B2B"/>
      <path d="M110 136v4M110 140c-4 6-10 6-13 2M110 140c4 6 10 6 13 2" fill="none" stroke="#2B2B2B" stroke-width="3" stroke-linecap="round"/>
      <ellipse cx="68" cy="132" rx="12" ry="7" fill="#FFB3C1" opacity=".55"/>
      <ellipse cx="152" cy="132" rx="12" ry="7" fill="#FFB3C1" opacity=".55"/>
    </g>
    <ellipse cx="78" cy="236" rx="24" ry="12" fill="#2B2B2B" stroke="#1A1A1A" stroke-width="4"/>
    <ellipse cx="142" cy="236" rx="24" ry="12" fill="#2B2B2B" stroke="#1A1A1A" stroke-width="4"/>
  </g>
</svg>`,

  penguin: `
<svg class="animal-svg penguin-svg" viewBox="0 0 200 260" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="100" cy="248" rx="62" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="penguin-bob">
    <ellipse cx="38" cy="168" rx="18" ry="42" transform="rotate(22 38 168)" fill="#243B6B" stroke="#16264A" stroke-width="4"/>
    <ellipse cx="100" cy="160" rx="58" ry="78" fill="#243B6B" stroke="#16264A" stroke-width="5"/>
    <ellipse cx="100" cy="172" rx="38" ry="58" fill="#FFFDF6"/>
    <g class="penguin-flipper">
      <ellipse cx="162" cy="168" rx="18" ry="42" transform="rotate(-22 162 168)" fill="#243B6B" stroke="#16264A" stroke-width="4"/>
    </g>
    <g class="penguin-head">
      <circle cx="100" cy="74" r="50" fill="#243B6B" stroke="#16264A" stroke-width="5"/>
      <ellipse cx="82" cy="78" rx="18" ry="21" fill="#FFFDF6"/>
      <ellipse cx="118" cy="78" rx="18" ry="21" fill="#FFFDF6"/>
      <g class="penguin-eye-l" transform="translate(84 79)">
        <circle r="6.5" fill="#2B2B2B"/>
        <circle cx="-2" cy="-2" r="2.3" fill="#FFFFFF"/>
      </g>
      <g class="penguin-eye-r" transform="translate(116 79)">
        <circle r="6.5" fill="#2B2B2B"/>
        <circle cx="-2" cy="-2" r="2.3" fill="#FFFFFF"/>
      </g>
      <path d="M100 88l18 10-18 11-18-11z" fill="#FF9F1C" stroke="#3A2A1A" stroke-width="3.5" stroke-linejoin="round"/>
      <ellipse cx="62" cy="96" rx="10" ry="6" fill="#FF9FB3" opacity=".55"/>
      <ellipse cx="138" cy="96" rx="10" ry="6" fill="#FF9FB3" opacity=".55"/>
    </g>
    <ellipse cx="76" cy="244" rx="20" ry="8" fill="#FF9F1C" stroke="#3A2A1A" stroke-width="3.5"/>
    <ellipse cx="124" cy="244" rx="20" ry="8" fill="#FF9F1C" stroke="#3A2A1A" stroke-width="3.5"/>
  </g>
</svg>`,

  lion: `
<svg class="animal-svg lion-svg" viewBox="0 0 260 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="130" cy="288" rx="86" ry="12" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="130 290">
    <g class="critter-tail" data-pivot="188 250">
      <path d="M188 252c40 18 62 2 58-26-3-20-19-30-33-24" fill="none" stroke="#D08A2E" stroke-width="14" stroke-linecap="round"/>
      <path d="M237 214c10-2 16 4 14 12-2 7-10 10-16 6 5-4 6-10 2-16z" fill="#7A3E1C" stroke="#3A2A1E" stroke-width="3.5" stroke-linejoin="round"/>
    </g>
    <ellipse cx="82" cy="258" rx="40" ry="34" fill="#D08A2E" stroke="#3A2A1E" stroke-width="5"/>
    <ellipse cx="178" cy="258" rx="40" ry="34" fill="#D08A2E" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M70 198c0-34 26-58 60-58s60 24 60 58v28c0 32-26 48-60 48s-60-16-60-48z" fill="#E3A33C" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M106 174c6-8 42-8 48 0 6 30 2 54-4 68-4 10-12 16-20 16s-16-6-20-16c-6-14-10-38-4-68z" fill="#F0C579" stroke="#C9782E" stroke-width="2.5"/>
    <path d="M120 198c-2 14 0 26 4 36M140 198c2 14 0 26-4 36" fill="none" stroke="#D9A868" stroke-width="3" stroke-linecap="round" opacity=".7"/>
    <path d="M96 218c-4 24 0 46 10 58 8 10 22 8 26-2 4-12 2-32-4-56z" fill="#E3A33C" stroke="#3A2A1E" stroke-width="5"/>
    <g class="critter-paw" data-pivot="176 212">
      <path d="M164 218c6-4 14 0 16 10 4 22 6 42 2 52-4 12-18 14-24 4-4-8-4-26 0-46z" fill="#E3A33C" stroke="#3A2A1E" stroke-width="5"/>
      <ellipse cx="174" cy="278" rx="16" ry="10" fill="#F6D89A" stroke="#3A2A1E" stroke-width="4"/>
      <path d="M166 274v6M174 272v8M182 274v6" stroke="#3A2A1E" stroke-width="2.4" stroke-linecap="round"/>
    </g>
    <ellipse cx="100" cy="278" rx="16" ry="10" fill="#F6D89A" stroke="#3A2A1E" stroke-width="4"/>
    <path d="M92 274v6M100 272v8M108 274v6" stroke="#3A2A1E" stroke-width="2.4" stroke-linecap="round"/>
    <g class="critter-head" data-pivot="130 168">
      <path d="${manePath(130, 110, 80, 73, 16)}" fill="#9E4F20" stroke="#3A2A1E" stroke-width="5" stroke-linejoin="round"/>
      <path d="${manePath(130, 110, 63, 58, 16)}" fill="#BE6A28"/>
      <g class="critter-ear" data-pivot="88 78">
        <ellipse cx="76" cy="68" rx="14" ry="15" fill="#E3A33C" stroke="#3A2A1E" stroke-width="5"/>
        <ellipse cx="78" cy="70" rx="6.5" ry="7.5" fill="#C9782E"/>
      </g>
      <g class="critter-ear" data-pivot="172 78">
        <ellipse cx="184" cy="68" rx="14" ry="15" fill="#E3A33C" stroke="#3A2A1E" stroke-width="5"/>
        <ellipse cx="182" cy="70" rx="6.5" ry="7.5" fill="#C9782E"/>
      </g>
      <circle cx="130" cy="112" r="50" fill="#EFB74F" stroke="#3A2A1E" stroke-width="5"/>
      <ellipse cx="130" cy="141" rx="29" ry="18" fill="#F8DCA6"/>
      <g class="critter-eye-l" data-pivot="111 106">
        <ellipse cx="111" cy="106" rx="7" ry="8" fill="#2B2118"/>
        <circle cx="108.5" cy="103.5" r="2.4" fill="#FFF8E8"/>
      </g>
      <g class="critter-eye-r" data-pivot="149 106">
        <ellipse cx="149" cy="106" rx="7" ry="8" fill="#2B2118"/>
        <circle cx="146.5" cy="103.5" r="2.4" fill="#FFF8E8"/>
      </g>
      <path d="M101 94c6-4 14-4 19 1M159 94c-6-4-14-4-19 1" fill="none" stroke="#6B3A22" stroke-width="3.4" stroke-linecap="round"/>
      <path d="M119 125h22c3 0 5 3 3 5l-11 8c-1 1-3 1-4 0l-11-8c-2-2 0-5 3-5z" fill="#5E3320" stroke="#3A2A1E" stroke-width="3" stroke-linejoin="round"/>
      <path d="M130 138v5M130 143c-4 6-10 7-14 2M130 143c4 6 10 7 14 2" fill="none" stroke="#3A2A1E" stroke-width="3" stroke-linecap="round"/>
      <circle cx="110" cy="139" r="1.7" fill="#7A3E1C" opacity=".55"/>
      <circle cx="116" cy="145" r="1.5" fill="#7A3E1C" opacity=".5"/>
      <circle cx="150" cy="139" r="1.7" fill="#7A3E1C" opacity=".55"/>
      <circle cx="144" cy="145" r="1.5" fill="#7A3E1C" opacity=".5"/>
    </g>
  </g>
</svg>`,

  elephant: `
<svg class="animal-svg elephant-svg" viewBox="0 0 340 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="170" cy="288" rx="106" ry="12" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="170 290">
    <g class="critter-tail" data-pivot="266 216">
      <path d="M266 216c8 8 10 18 6 28" fill="none" stroke="#66737E" stroke-width="8" stroke-linecap="round"/>
      <path d="M272 244c5 0 8 4 6 8-2 4-7 4-9 0z" fill="#4B5762" stroke="#3A2A1E" stroke-width="2.5" stroke-linejoin="round"/>
    </g>
    <g>
      <path d="M100 206h34v60c0 12-8 18-17 18s-17-6-17-18z" fill="#8C9AA6" stroke="#3A2A1E" stroke-width="5"/>
      <path d="M140 206h34v60c0 12-8 18-17 18s-17-6-17-18z" fill="#8C9AA6" stroke="#3A2A1E" stroke-width="5"/>
      <path d="M174 206h34v60c0 12-8 18-17 18s-17-6-17-18z" fill="#8C9AA6" stroke="#3A2A1E" stroke-width="5"/>
      <path d="M214 206h34v60c0 12-8 18-17 18s-17-6-17-18z" fill="#8C9AA6" stroke="#3A2A1E" stroke-width="5"/>
    </g>
    <ellipse cx="170" cy="198" rx="96" ry="66" fill="#94A2AE" stroke="#3A2A1E" stroke-width="5"/>
    <ellipse cx="170" cy="222" rx="62" ry="40" fill="#B7C1C7"/>
    <path d="M110 278h8M124 278h8M150 278h8M164 278h8M184 278h8M198 278h8M224 278h8M238 278h8" stroke="#E8DCC4" stroke-width="4.5" stroke-linecap="round"/>
    <g class="critter-head" data-pivot="170 138">
      <g class="critter-ear" data-pivot="112 92">
        <ellipse cx="82" cy="112" rx="50" ry="60" fill="#7E8C99" stroke="#3A2A1E" stroke-width="5"/>
        <ellipse cx="90" cy="116" rx="31" ry="42" fill="#C0A6A0" opacity=".72"/>
      </g>
      <g class="critter-ear" data-pivot="228 92">
        <ellipse cx="258" cy="112" rx="50" ry="60" fill="#7E8C99" stroke="#3A2A1E" stroke-width="5"/>
        <ellipse cx="250" cy="116" rx="31" ry="42" fill="#C0A6A0" opacity=".72"/>
      </g>
      <ellipse cx="170" cy="112" rx="64" ry="56" fill="#94A2AE" stroke="#3A2A1E" stroke-width="5"/>
      <ellipse cx="170" cy="94" rx="44" ry="30" fill="#A7B3BD" opacity=".50"/>
      <g class="critter-eye-l" data-pivot="146 104">
        <ellipse cx="146" cy="104" rx="6.6" ry="7.6" fill="#2B2118"/>
        <circle cx="143.8" cy="101.8" r="2.3" fill="#FFF8E8"/>
      </g>
      <g class="critter-eye-r" data-pivot="194 104">
        <ellipse cx="194" cy="104" rx="6.6" ry="7.6" fill="#2B2118"/>
        <circle cx="191.8" cy="101.8" r="2.3" fill="#FFF8E8"/>
      </g>
      <path d="M138 96c5-4 12-4 17 1M202 96c-5-4-12-4-17 1" fill="none" stroke="#3A2A1E" stroke-width="3" stroke-linecap="round"/>
      <path d="M140 143c-10 14-11 27-3 35" fill="none" stroke="#3A2A1E" stroke-width="17" stroke-linecap="round"/>
      <path d="M140 143c-10 14-11 27-3 35" fill="none" stroke="#FFF3D6" stroke-width="10" stroke-linecap="round"/>
      <path d="M200 143c10 14 11 27 3 35" fill="none" stroke="#3A2A1E" stroke-width="17" stroke-linecap="round"/>
      <path d="M200 143c10 14 11 27 3 35" fill="none" stroke="#FFF3D6" stroke-width="10" stroke-linecap="round"/>
      <g class="critter-paw" data-pivot="170 140">
        <path d="M170 136c-2 30 6 56 22 72 12 10 28 10 30-2" fill="none" stroke="#3A2A1E" stroke-width="36" stroke-linecap="round"/>
        <path d="M170 136c-2 30 6 56 22 72 12 10 28 10 30-2" fill="none" stroke="#8C9AA6" stroke-width="27" stroke-linecap="round"/>
        <path d="M162 168h17M164 190h19M173 210h19M186 228h17" stroke="#6E7C88" stroke-width="3" stroke-linecap="round" opacity=".55"/>
      </g>
      <circle cx="131" cy="135" r="2" fill="#5E6B76" opacity=".45"/>
      <circle cx="209" cy="135" r="2" fill="#5E6B76" opacity=".45"/>
    </g>
  </g>
</svg>`,

  giraffe: `
<svg class="animal-svg giraffe-svg" viewBox="20 40 240 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="140" cy="428" rx="94" ry="11" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="140 430">
    <g class="critter-tail" data-pivot="232 316">
      <path d="M232 318c24 14 24 40 4 52" fill="none" stroke="#C98A3E" stroke-width="9" stroke-linecap="round"/>
      <path d="M236 366c1 10-5 17-13 15 5-5 7-11 5-17z" fill="#8A4A22" stroke="#3A2A1E" stroke-width="3" stroke-linejoin="round"/>
    </g>
    <path d="M114 320h22v94c0 10-5 14-11 14s-11-4-11-14z" fill="#C98A3E" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M198 336h22v70c0 10-5 14-11 14s-11-4-11-14z" fill="#C98A3E" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M114 414h22v9c0 4-5 6-11 6s-11-2-11-6zM198 406h22v9c0 4-5 6-11 6s-11-2-11-6z" fill="#4E321E"/>
    <path d="M84 320h24v94c0 10-5 14-12 14s-12-4-12-14z" fill="#D99A4E" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M170 336h24v70c0 10-5 14-12 14s-12-4-12-14z" fill="#D99A4E" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M84 414h24v9c0 4-5 6-12 6s-12-2-12-6zM170 406h24v9c0 4-5 6-12 6s-12-2-12-6z" fill="#5A3A22" stroke="#3A2A1E" stroke-width="3"/>
    <path d="M88 332C78 282 72 220 74 154l40 6c-2 64 6 124 22 172z" fill="#D99A4E" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M110 152c8 54 14 112 20 176l14-4c-8-64-14-122-20-176z" fill="#A65B22"/>
    <path d="M62 318c2-28 30-46 70-50 34-4 64 8 82 28 14 16 20 34 12 46-8 14-32 22-60 22-36 4-70-4-90-16-10-6-14-16-14-30z" fill="#D99A4E" stroke="#3A2A1E" stroke-width="5"/>
    <path d="M84 344c30 10 70 12 106 6 18-2 30-6 40-12" fill="none" stroke="#B8732E" stroke-width="6" stroke-linecap="round" opacity=".35"/>
    <g fill="#A65B22">
      <path d="M100 288l20-6 12 12-4 16-20 4-10-12z"/>
      <path d="M142 280l22-4 10 12-6 16-20 2-10-12z"/>
      <path d="M190 296l20-4 10 12-4 14-18 2-10-10z"/>
      <path d="M112 328l20-4 10 10-4 14-18 2-10-10z"/>
      <path d="M154 324l20-2 10 10-4 14-18 2-10-12z"/>
      <path d="M196 328l16-2 8 10-2 12-14 2-8-10z"/>
      <path d="M84 192l14-4 8 10-4 12-14 2-6-10z"/>
      <path d="M88 228l14-2 8 10-4 12-14 2-6-12z"/>
      <path d="M92 262l12-2 8 8-4 12-12 2-6-10z"/>
    </g>
    <g class="critter-head" data-pivot="100 160">
      <path d="M78 116V86M104 112V82" stroke="#3A2A1E" stroke-width="13" stroke-linecap="round"/>
      <path d="M78 116V86M104 112V82" stroke="#D99A4E" stroke-width="7" stroke-linecap="round"/>
      <circle cx="76" cy="82" r="9" fill="#A65B22" stroke="#3A2A1E" stroke-width="4"/>
      <circle cx="106" cy="78" r="9" fill="#A65B22" stroke="#3A2A1E" stroke-width="4"/>
      <g class="critter-ear" data-pivot="108 112">
        <ellipse cx="120" cy="108" rx="19" ry="10" transform="rotate(22 120 108)" fill="#D99A4E" stroke="#3A2A1E" stroke-width="4.5"/>
        <ellipse cx="122" cy="109" rx="10" ry="5" transform="rotate(22 122 109)" fill="#C97A2A"/>
      </g>
      <g class="critter-ear" data-pivot="62 112">
        <ellipse cx="50" cy="108" rx="19" ry="10" transform="rotate(-22 50 108)" fill="#D99A4E" stroke="#3A2A1E" stroke-width="4.5"/>
        <ellipse cx="48" cy="109" rx="10" ry="5" transform="rotate(-22 48 109)" fill="#C97A2A"/>
      </g>
      <path d="M82 96c22-4 38 6 40 26 2 20-12 34-34 34-20 0-34-12-34-30 0-16 12-26 28-30z" fill="#D99A4E" stroke="#3A2A1E" stroke-width="5"/>
      <ellipse cx="54" cy="144" rx="25" ry="17" fill="#F6D9A6" stroke="#3A2A1E" stroke-width="4.5"/>
      <g class="critter-eye-l" data-pivot="72 126">
        <ellipse cx="72" cy="126" rx="6.4" ry="7.2" fill="#2B2118"/>
        <circle cx="70" cy="123.8" r="2.2" fill="#FFF8E8"/>
      </g>
      <g class="critter-eye-r" data-pivot="92 120">
        <ellipse cx="92" cy="120" rx="5.4" ry="6.2" fill="#2B2118"/>
        <circle cx="90" cy="118" r="1.9" fill="#FFF8E8"/>
      </g>
      <path d="M64 116c5-4 12-3 16 1M98 112c-5-4-11-3-15 1" fill="none" stroke="#8A4A22" stroke-width="3" stroke-linecap="round"/>
      <circle cx="44" cy="146" r="2" fill="#8A4A22"/>
      <circle cx="56" cy="147" r="2" fill="#8A4A22"/>
      <path d="M48 152c4 4 9 4 12 0" fill="none" stroke="#3A2A1E" stroke-width="2.8" stroke-linecap="round"/>
      <path d="M82 134c6-4 12-2 13 4 1 6-5 10-11 8-6-2-8-8-2-12z" fill="#A65B22" opacity=".9"/>
    </g>
  </g>
</svg>`,

  zebra: `
<svg class="animal-svg zebra-svg" viewBox="0 0 280 310" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <clipPath id="zebraBodyClip"><path d="M62 200c0-30 32-50 84-50 54 0 88 18 94 46 6 22-10 40-42 46-42 8-94 2-120-14-10-6-16-16-16-28z"/></clipPath>
    <clipPath id="zebraHeadClip"><ellipse cx="92" cy="108" rx="38" ry="30"/></clipPath>
    <clipPath id="zebraNeckClip"><path d="M112 205C100 172 94 142 96 116l42 4c-2 30 6 60 18 88z"/></clipPath>
  </defs>
  <ellipse class="ground-shadow" cx="140" cy="298" rx="90" ry="11" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="140 300">
    <g class="critter-tail" data-pivot="238 190">
      <path d="M238 192c20 14 18 38-2 48" fill="none" stroke="#3B2A1E" stroke-width="7" stroke-linecap="round"/>
      <path d="M236 240c2 8-2 14-9 14 3-5 3-10 0-15z" fill="#3B2A1E"/>
    </g>
    <path d="M128 225h22v62c0 10-5 14-11 14s-11-4-11-14z" fill="#DED5C0" stroke="#3B2A1E" stroke-width="5"/>
    <path d="M204 225h22v62c0 10-5 14-11 14s-11-4-11-14z" fill="#DED5C0" stroke="#3B2A1E" stroke-width="5"/>
    <path d="M128 284h22v10c0 4-5 6-11 6s-11-2-11-6zM204 284h22v10c0 4-5 6-11 6s-11-2-11-6z" fill="#3B2A1E"/>
    <path d="M92 225h24v62c0 10-5 14-12 14s-12-4-12-14z" fill="#F4ECD8" stroke="#3B2A1E" stroke-width="5"/>
    <path d="M168 225h24v62c0 10-5 14-12 14s-12-4-12-14z" fill="#F4ECD8" stroke="#3B2A1E" stroke-width="5"/>
    <path d="M92 284h24v10c0 4-5 6-12 6s-12-2-12-6zM168 284h24v10c0 4-5 6-12 6s-12-2-12-6z" fill="#3B2A1E"/>
    <path d="M112 205C100 172 94 142 96 116l42 4c-2 30 6 60 18 88z" fill="#F4ECD8" stroke="#3B2A1E" stroke-width="5"/>
    <g clip-path="url(#zebraNeckClip)" stroke="#3B2A1E" stroke-width="9" stroke-linecap="round" fill="none">
      <path d="M104 128v74M116 124v80M128 122v80M140 126v76"/>
    </g>
    <path d="M134 118c14 34 16 70 8 106" fill="none" stroke="#3B2A1E" stroke-width="14" stroke-linecap="round"/>
    <g fill="#3B2A1E">
      <path d="M132 124l14-10 2 16z"/>
      <path d="M138 150l16-10 0 16z"/>
      <path d="M144 176l16-8-2 16z"/>
      <path d="M148 202l14-6-2 14z"/>
    </g>
    <path d="M62 200c0-30 32-50 84-50 54 0 88 18 94 46 6 22-10 40-42 46-42 8-94 2-120-14-10-6-16-16-16-28z" fill="#F4ECD8" stroke="#3B2A1E" stroke-width="5"/>
    <g clip-path="url(#zebraBodyClip)" stroke="#3B2A1E" stroke-width="14" stroke-linecap="round" fill="none">
      <path d="M82 170c10 22 14 46 10 70"/>
      <path d="M110 158c8 28 10 58 4 86"/>
      <path d="M140 152c4 30 4 62 0 92"/>
      <path d="M170 156c-4 28-2 58 6 84"/>
      <path d="M200 166c-10 22-14 44-10 68"/>
      <path d="M226 186c-12 16-16 34-12 50"/>
    </g>
    <path d="M92 270h20M128 270h18M172 270h18M204 270h18" stroke="#3B2A1E" stroke-width="8" stroke-linecap="round"/>
    <g class="critter-head" data-pivot="118 130">
      <g class="critter-ear" data-pivot="120 92">
        <ellipse cx="128" cy="86" rx="14" ry="23" transform="rotate(20 128 86)" fill="#F4ECD8" stroke="#3B2A1E" stroke-width="5"/>
        <ellipse cx="130" cy="88" rx="7" ry="12" transform="rotate(20 130 88)" fill="#D8D0BE"/>
      </g>
      <g class="critter-ear" data-pivot="62 92">
        <ellipse cx="54" cy="86" rx="14" ry="23" transform="rotate(-20 54 86)" fill="#F4ECD8" stroke="#3B2A1E" stroke-width="5"/>
        <ellipse cx="52" cy="88" rx="7" ry="12" transform="rotate(-20 52 88)" fill="#D8D0BE"/>
      </g>
      <ellipse cx="92" cy="108" rx="38" ry="30" fill="#F4ECD8" stroke="#3B2A1E" stroke-width="5"/>
      <g clip-path="url(#zebraHeadClip)" stroke="#3B2A1E" stroke-width="10" stroke-linecap="round" fill="none">
        <path d="M68 84l14 22M92 80l8 24M114 84l-4 22M62 112l20 4M112 112l16-2"/>
      </g>
      <ellipse cx="58" cy="124" rx="24" ry="16" fill="#D8D0BE" stroke="#3B2A1E" stroke-width="4.5"/>
      <g class="critter-eye-l" data-pivot="78 104">
        <ellipse cx="78" cy="104" rx="6.4" ry="7.2" fill="#2B2118"/>
        <circle cx="76" cy="101.8" r="2.2" fill="#FFF8E8"/>
      </g>
      <g class="critter-eye-r" data-pivot="100 100">
        <ellipse cx="100" cy="100" rx="5.4" ry="6.2" fill="#2B2118"/>
        <circle cx="98" cy="98" r="1.9" fill="#FFF8E8"/>
      </g>
      <path d="M70 94c5-4 12-3 16 1M104 92c-5-4-11-3-15 1" fill="none" stroke="#3B2A1E" stroke-width="3" stroke-linecap="round"/>
      <circle cx="48" cy="126" r="2" fill="#3B2A1E"/>
      <circle cx="60" cy="127" r="2" fill="#3B2A1E"/>
      <path d="M52 132c4 4 9 4 12 0" fill="none" stroke="#3B2A1E" stroke-width="2.8" stroke-linecap="round"/>
    </g>
  </g>
</svg>`,

  polar: `
<svg class="animal-svg polar-svg" viewBox="0 0 230 260" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="115" cy="248" rx="74" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="115 248">
    <ellipse cx="115" cy="194" rx="66" ry="56" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="5"/>
    <ellipse cx="115" cy="206" rx="38" ry="38" fill="#FFFFFF"/>
    <ellipse cx="56" cy="204" rx="19" ry="13" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="4"/>
    <g class="critter-paw" data-pivot="174 204"><ellipse cx="174" cy="204" rx="19" ry="13" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="4"/></g>
    <g class="critter-head" data-pivot="115 110">
      <circle cx="68" cy="64" r="20" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="4"/>
      <circle cx="162" cy="64" r="20" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="4"/>
      <ellipse cx="115" cy="112" rx="62" ry="54" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="5"/>
      <ellipse cx="115" cy="132" rx="32" ry="23" fill="#FFFFFF"/>
      <g class="critter-eye-l" data-pivot="92 104"><circle cx="92" cy="104" r="8" fill="#2B2B2B"/><circle cx="89" cy="101" r="2.8" fill="#FFF"/></g>
      <g class="critter-eye-r" data-pivot="138 104"><circle cx="138" cy="104" r="8" fill="#2B2B2B"/><circle cx="135" cy="101" r="2.8" fill="#FFF"/></g>
      <ellipse cx="115" cy="124" rx="9" ry="6" fill="#2B2B2B"/>
      <path d="M115 130v4M115 134c-4 5-9 5-12 1M115 134c4 5 9 5 12 1" fill="none" stroke="#3A2A1A" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M78 158c24 10 50 10 74 0" fill="none" stroke="var(--accent)" stroke-width="14" stroke-linecap="round"/>
    </g>
    <ellipse cx="86" cy="244" rx="22" ry="10" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="144" cy="244" rx="22" ry="10" fill="#F7FBFF" stroke="#3A2A1A" stroke-width="4"/>
  </g>
</svg>`,

  reindeer: `
<svg class="animal-svg reindeer-svg" viewBox="0 0 240 280" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="120" cy="268" rx="74" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="120 268">
    <g class="critter-tail" data-pivot="186 210"><ellipse cx="188" cy="208" rx="14" ry="18" fill="#B07A4A" stroke="#3A2A1A" stroke-width="4"/></g>
    <ellipse cx="120" cy="204" rx="64" ry="52" fill="#B07A4A" stroke="#3A2A1A" stroke-width="5"/>
    <ellipse cx="120" cy="216" rx="38" ry="32" fill="#F4E6D0"/>
    <g class="critter-head" data-pivot="120 108">
      <path d="M92 82c-18-34-34-46-48-40-10 4-4 18 6 26-16-6-24 8-12 18 14 12 34 12 54 8zM148 82c18-34 34-46 48-40 10 4 4 18-6 26 16-6 24 8 12 18-14 12-34 12-54 8z" fill="#8A5A32" stroke="#3A2A1A" stroke-width="4" stroke-linejoin="round"/>
      <ellipse cx="120" cy="104" rx="54" ry="44" fill="#B07A4A" stroke="#3A2A1A" stroke-width="5"/>
      <ellipse cx="82" cy="78" rx="16" ry="10" transform="rotate(-20 82 78)" fill="#B07A4A" stroke="#3A2A1A" stroke-width="4"/>
      <ellipse cx="158" cy="78" rx="16" ry="10" transform="rotate(20 158 78)" fill="#B07A4A" stroke="#3A2A1A" stroke-width="4"/>
      <ellipse cx="120" cy="126" rx="26" ry="19" fill="#F4E6D0"/>
      <g class="critter-eye-l" data-pivot="100 100"><circle cx="100" cy="100" r="7" fill="#2B2B2B"/><circle cx="97" cy="97" r="2.5" fill="#FFF"/></g>
      <g class="critter-eye-r" data-pivot="140 100"><circle cx="140" cy="100" r="7" fill="#2B2B2B"/><circle cx="137" cy="97" r="2.5" fill="#FFF"/></g>
      <ellipse cx="120" cy="120" rx="8" ry="6" fill="#3A2A1A"/>
      <circle cx="94" cy="132" r="5" fill="#E84A5F" opacity=".6"/><circle cx="146" cy="132" r="5" fill="#E84A5F" opacity=".6"/>
    </g>
    <ellipse cx="86" cy="264" rx="22" ry="10" fill="#B07A4A" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="154" cy="264" rx="22" ry="10" fill="#B07A4A" stroke="#3A2A1A" stroke-width="4"/>
  </g>
</svg>`,

  owl: `
<svg class="animal-svg owl-svg" viewBox="0 0 180 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="90" cy="190" rx="50" ry="8" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="90 190">
    <ellipse cx="90" cy="130" rx="54" ry="60" fill="#A86A3F" stroke="#3A2A1A" stroke-width="5"/>
    <ellipse cx="90" cy="146" rx="34" ry="40" fill="#E8C79A"/>
    <g class="critter-paw" data-pivot="40 120"><ellipse cx="40" cy="120" rx="18" ry="44" fill="#8A5A32" stroke="#3A2A1A" stroke-width="4"/></g>
    <g class="critter-head" data-pivot="90 72">
      <path d="M58 36l-8-24 28 14zM122 36l8-24-28 14z" fill="#8A5A32" stroke="#3A2A1A" stroke-width="4" stroke-linejoin="round"/>
      <circle cx="90" cy="70" r="52" fill="#A86A3F" stroke="#3A2A1A" stroke-width="5"/>
      <circle cx="66" cy="66" r="22" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="4"/>
      <circle cx="114" cy="66" r="22" fill="#FFF6E8" stroke="#3A2A1A" stroke-width="4"/>
      <g class="critter-eye-l" data-pivot="66 66"><circle cx="66" cy="66" r="10" fill="#2B2B2B"/><circle cx="62" cy="62" r="3.5" fill="#FFF"/></g>
      <g class="critter-eye-r" data-pivot="114 66"><circle cx="114" cy="66" r="10" fill="#2B2B2B"/><circle cx="110" cy="62" r="3.5" fill="#FFF"/></g>
      <path d="M90 78l12 10-12 8-12-8z" fill="#FF9600" stroke="#3A2A1A" stroke-width="3"/>
    </g>
    <ellipse cx="66" cy="188" rx="14" ry="6" fill="#FF9600" stroke="#3A2A1A" stroke-width="3"/>
    <ellipse cx="114" cy="188" rx="14" ry="6" fill="#FF9600" stroke="#3A2A1A" stroke-width="3"/>
  </g>
</svg>`,

  monkey: `
<svg class="animal-svg monkey-svg" viewBox="0 0 210 250" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="105" cy="240" rx="62" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="105 240">
    <g class="critter-tail" data-pivot="168 208"><path d="M166 202c30 6 38 30 20 44-8 6-18 2-14-6 12 0 14-12 6-22-6-6-12-8-12-8z" fill="#9A623A" stroke="#3A2A1A" stroke-width="4"/></g>
    <ellipse cx="105" cy="190" rx="56" ry="48" fill="#9A623A" stroke="#3A2A1A" stroke-width="5"/>
    <ellipse cx="105" cy="202" rx="34" ry="30" fill="#E8C79A"/>
    <ellipse cx="55" cy="94" rx="20" ry="24" fill="#9A623A" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="155" cy="94" rx="20" ry="24" fill="#9A623A" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="55" cy="94" rx="11" ry="14" fill="#E8C79A"/>
    <ellipse cx="155" cy="94" rx="11" ry="14" fill="#E8C79A"/>
    <g class="critter-head" data-pivot="105 110">
      <circle cx="105" cy="110" r="54" fill="#9A623A" stroke="#3A2A1A" stroke-width="5"/>
      <ellipse cx="105" cy="124" rx="38" ry="34" fill="#E8C79A"/>
      <g class="critter-eye-l" data-pivot="88 102"><circle cx="88" cy="102" r="7" fill="#2B2B2B"/><circle cx="85" cy="99" r="2.5" fill="#FFF"/></g>
      <g class="critter-eye-r" data-pivot="122 102"><circle cx="122" cy="102" r="7" fill="#2B2B2B"/><circle cx="119" cy="99" r="2.5" fill="#FFF"/></g>
      <circle cx="98" cy="120" r="3" fill="#3A2A1A"/><circle cx="112" cy="120" r="3" fill="#3A2A1A"/>
      <path d="M105 126v5M105 131c-5 5-10 4-13 0M105 131c5 5 10 4 13 0" fill="none" stroke="#3A2A1A" stroke-width="2.6" stroke-linecap="round"/>
    </g>
    <ellipse cx="78" cy="236" rx="20" ry="10" fill="#9A623A" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="132" cy="236" rx="20" ry="10" fill="#9A623A" stroke="#3A2A1A" stroke-width="4"/>
  </g>
</svg>`,

  camel: `
<svg class="animal-svg camel-svg" viewBox="0 0 290 260" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="145" cy="250" rx="92" ry="10" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="145 250">
    <g class="critter-tail" data-pivot="232 190"><path d="M232 184c16 4 20 18 10 28-4 4-10 2-8-4 6-4 6-12-2-16z" fill="#D9A45E" stroke="#3A2A1A" stroke-width="4"/></g>
    <ellipse cx="140" cy="196" rx="80" ry="46" fill="#D9A45E" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M96 178c6-34 30-48 50-48 24 0 44 18 46 48z" fill="#E8B96A" stroke="#3A2A1A" stroke-width="5"/>
    <g class="critter-head" data-pivot="226 92">
      <path d="M188 186c6-42 18-78 38-98l18 10c-14 28-18 56-12 88z" fill="#D9A45E" stroke="#3A2A1A" stroke-width="5"/>
      <ellipse cx="238" cy="78" rx="34" ry="28" fill="#E8B96A" stroke="#3A2A1A" stroke-width="5"/>
      <path d="M210 62l-18-18 28-2zM260 56l18-16-4 26z" fill="#D9A45E" stroke="#3A2A1A" stroke-width="4"/>
      <ellipse cx="258" cy="84" rx="18" ry="13" fill="#F4D8A8"/>
      <g class="critter-eye-l" data-pivot="228 72"><circle cx="228" cy="72" r="6" fill="#2B2B2B"/><circle cx="226" cy="70" r="2" fill="#FFF"/></g>
      <g class="critter-eye-r" data-pivot="248 72"><circle cx="248" cy="72" r="6" fill="#2B2B2B"/><circle cx="246" cy="70" r="2" fill="#FFF"/></g>
      <path d="M252 88l6 2-6 3z" fill="#3A2A1A"/>
    </g>
    <ellipse cx="90" cy="244" rx="18" ry="10" fill="#D9A45E" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="142" cy="244" rx="18" ry="10" fill="#D9A45E" stroke="#3A2A1A" stroke-width="4"/>
    <ellipse cx="194" cy="244" rx="18" ry="10" fill="#D9A45E" stroke="#3A2A1A" stroke-width="4"/>
  </g>
</svg>`,

  deer: `
<svg class="animal-svg deer-svg" viewBox="0 0 300 380" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse class="ground-shadow" cx="155" cy="370" rx="92" ry="11" fill="#2A2A2A" opacity=".10"/>
  <g class="critter-bob" data-pivot="160 372">
    <g class="critter-tail" data-pivot="242 235">
      <path d="M242 235c16 4 20 18 8 28-5 4-12 2-10-4 5-3 6-11 0-15z" fill="#E8CFA8" stroke="#3A2A1A" stroke-width="4" stroke-linejoin="round"/>
    </g>
    <path d="M126 255h20v106c0 8-4 11-10 11s-10-3-10-11z" fill="#8A5430" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M210 255h20v106c0 8-4 11-10 11s-10-3-10-11z" fill="#8A5430" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M126 354h20v9c0 4-4 6-10 6s-10-2-10-6zM210 354h20v9c0 4-4 6-10 6s-10-2-10-6z" fill="#4E321E"/>
    <path d="M92 255h22v108c0 8-5 11-11 11s-11-3-11-11z" fill="#A8683C" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M178 255h22v108c0 8-5 11-11 11s-11-3-11-11z" fill="#A8683C" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M92 354h22v9c0 4-5 6-11 6s-11-2-11-6zM178 354h22v9c0 4-5 6-11 6s-11-2-11-6z" fill="#4E321E"/>
    <path d="M104 250C94 214 88 182 88 148l46 4c2 34 10 66 24 102z" fill="#A8683C" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M60 252c0-36 32-60 84-62 50-2 88 20 96 52 6 26-12 46-46 52-40 8-90 2-116-12-10-6-18-18-18-30z" fill="#A8683C" stroke="#3A2A1A" stroke-width="5"/>
    <path d="M94 258c26 10 60 12 94 4 18-4 30-10 38-16-4 14-20 24-44 28-34 6-70 2-88-16z" fill="#E8CFA8" opacity=".8"/>
    <path d="M106 214c6-24 18-40 32-46l8 26c-12 8-22 22-28 38z" fill="#E8CFA8" opacity=".55"/>
    <g class="critter-head" data-pivot="112 168">
      <g fill="none" stroke="#5A3A22" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">
        <path d="M96 112C82 78 64 50 42 34"/>
        <path d="M88 100c-16-4-30-14-40-28"/>
        <path d="M76 78c-16 0-30-8-40-20"/>
        <path d="M60 56c-10-2-20-10-26-20"/>
        <path d="M46 36c-8-8-12-16-12-26"/>
        <path d="M50 40c8-10 12-22 10-34"/>
        <path d="M116 108C128 76 144 48 166 30" stroke="#7A4A28" stroke-width="8"/>
        <path d="M124 96c14-4 26-12 34-24" stroke="#7A4A28" stroke-width="7"/>
        <path d="M140 72c14 0 26-8 34-18" stroke="#7A4A28" stroke-width="7"/>
      </g>
      <g class="critter-ear" data-pivot="118 118">
        <ellipse cx="128" cy="112" rx="18" ry="10" transform="rotate(26 128 112)" fill="#A8683C" stroke="#3A2A1A" stroke-width="4.5"/>
        <ellipse cx="130" cy="113" rx="9" ry="5" transform="rotate(26 130 113)" fill="#E8CFA8"/>
      </g>
      <g class="critter-ear" data-pivot="76 122">
        <ellipse cx="66" cy="116" rx="18" ry="10" transform="rotate(-26 66 116)" fill="#A8683C" stroke="#3A2A1A" stroke-width="4.5"/>
        <ellipse cx="64" cy="117" rx="9" ry="5" transform="rotate(-26 64 117)" fill="#E8CFA8"/>
      </g>
      <path d="M96 106c20-2 34 8 36 24 2 18-10 30-28 30-16 0-28-10-30-24-2-14 8-26 22-30z" fill="#A8683C" stroke="#3A2A1A" stroke-width="5"/>
      <ellipse cx="62" cy="146" rx="23" ry="15" fill="#E8CFA8" stroke="#3A2A1A" stroke-width="4.5"/>
      <ellipse cx="45" cy="140" rx="6.5" ry="4.5" fill="#3A2A1E"/>
      <g class="critter-eye-l" data-pivot="84 128">
        <ellipse cx="84" cy="128" rx="6.4" ry="7.2" fill="#2B2118"/>
        <circle cx="82" cy="125.8" r="2.2" fill="#FFF8E8"/>
      </g>
      <g class="critter-eye-r" data-pivot="106 122">
        <ellipse cx="106" cy="122" rx="5.4" ry="6.2" fill="#2B2118"/>
        <circle cx="104" cy="120" r="1.9" fill="#FFF8E8"/>
      </g>
      <path d="M76 118c5-4 12-3 16 1M112 112c-5-4-11-3-15 1" fill="none" stroke="#6A4022" stroke-width="3" stroke-linecap="round"/>
      <circle cx="44" cy="142" r="2.2" fill="#3A2A1A"/>
      <circle cx="58" cy="148" r="2.2" fill="#3A2A1A"/>
      <path d="M46 151c5 4 10 4 14 0" fill="none" stroke="#3A2A1A" stroke-width="2.8" stroke-linecap="round"/>
      <path d="M96 140c7-4 14-1 15 6 1 7-6 11-13 8-7-3-9-10-2-14z" fill="#8A5430" opacity=".7"/>
    </g>
  </g>
</svg>`,

  butterfly: `
<svg class="animal-svg butterfly-svg" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <g class="bfly-wing-l">
    <path d="M56 48C32 8 4 10 8 36c3 20 24 28 44 24z" fill="var(--bfly-a, #FFC800)" stroke="#3A2A1A" stroke-width="3.5" stroke-linejoin="round"/>
    <path d="M56 54c-20 2-36 14-34 30 2 14 22 12 36-8z" fill="var(--bfly-b, #FF8FA3)" stroke="#3A2A1A" stroke-width="3.5" stroke-linejoin="round"/>
    <circle cx="28" cy="32" r="5" fill="#FFF6E8" opacity=".9"/>
    <circle cx="32" cy="72" r="4" fill="#FFF6E8" opacity=".85"/>
  </g>
  <g class="bfly-wing-r">
    <path d="M64 48C88 8 116 10 112 36c-3 20-24 28-44 24z" fill="var(--bfly-a, #FFC800)" stroke="#3A2A1A" stroke-width="3.5" stroke-linejoin="round"/>
    <path d="M64 54c20 2 36 14 34 30-2 14-22 12-36-8z" fill="var(--bfly-b, #FF8FA3)" stroke="#3A2A1A" stroke-width="3.5" stroke-linejoin="round"/>
    <circle cx="92" cy="32" r="5" fill="#FFF6E8" opacity=".9"/>
    <circle cx="88" cy="72" r="4" fill="#FFF6E8" opacity=".85"/>
  </g>
  <ellipse cx="60" cy="58" rx="6" ry="24" fill="#3A2A1A"/>
  <path d="M58 34c-4-10-12-14-18-14M62 34c4-10 12-14 18-14" fill="none" stroke="#3A2A1A" stroke-width="3" stroke-linecap="round"/>
</svg>`,

  bird: `
<svg class="animal-svg bird-svg" viewBox="0 0 100 70" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <g class="bird-bob">
    <path d="M20 44l-14 8 12-18z" fill="var(--bird-wing, #0E8CC7)" stroke="#3A2A1A" stroke-width="3" stroke-linejoin="round"/>
    <ellipse cx="48" cy="40" rx="26" ry="18" fill="var(--bird-body, #1CB0F6)" stroke="#3A2A1A" stroke-width="3.5"/>
    <circle cx="68" cy="30" r="14" fill="var(--bird-body, #1CB0F6)" stroke="#3A2A1A" stroke-width="3.5"/>
    <path d="M81 28l14 6-14 6z" fill="#FF9600" stroke="#3A2A1A" stroke-width="3" stroke-linejoin="round"/>
    <circle cx="72" cy="26" r="3" fill="#2B2B2B"/>
    <path class="bird-wing" d="M42 34c-8-10-20-8-24 2 8 6 18 8 28 4z" fill="var(--bird-wing, #0E8CC7)" stroke="#3A2A1A" stroke-width="3" stroke-linejoin="round"/>
    <path d="M26 54c-8 0-14 4-16 10 8 2 16 0 22-6z" fill="var(--bird-wing, #0E8CC7)" stroke="#3A2A1A" stroke-width="3" stroke-linejoin="round"/>
  </g>
</svg>`,

  balloon: `
<svg class="animal-svg balloon-svg" viewBox="0 0 120 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M60 5C30 5 7 30 7 63c0 34 30 51 53 73 23-22 53-39 53-73C113 30 90 5 60 5z" fill="var(--balloon-a, #FF6B35)" stroke="#3A2A1A" stroke-width="4" stroke-linejoin="round"/>
  <path d="M60 5C48 23 42 43 42 65c0 27 8 50 18 71 10-21 18-44 18-71C78 43 72 23 60 5z" fill="var(--balloon-b, #FFC800)" opacity=".9"/>
  <path d="M60 5C48 23 42 43 42 65c0 27 8 50 18 71M60 5c12 18 18 38 18 60 0 27-8 50-18 71" fill="none" stroke="rgba(255,255,255,.5)" stroke-width="5" stroke-linecap="round"/>
  <path d="M24 100c9 8 22 15 36 20M96 100c-9 8-22 15-36 20" fill="none" stroke="rgba(0,0,0,.12)" stroke-width="4" stroke-linecap="round"/>
  <path d="M42 137l-7 20M78 137l7 20" fill="none" stroke="#3A2A1A" stroke-width="4" stroke-linecap="round"/>
  <rect x="37" y="156" width="46" height="22" rx="6" fill="#A66A3F" stroke="#3A2A1A" stroke-width="3.5"/>
  <path d="M37 164h46" fill="none" stroke="#3A2A1A" stroke-width="3"/>
</svg>`,

  flower: `
<svg class="animal-svg flower-svg" viewBox="0 0 120 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M60 172c-2-38 2-72 0-104" fill="none" stroke="#3E8A3A" stroke-width="7" stroke-linecap="round"/>
  <path d="M60 138c-16-2-28-10-32-24 16-2 28 6 32 24z" fill="#4E9E45" stroke="#2F6E2F" stroke-width="3"/>
  <path d="M60 118c16-2 26-10 30-22-15-2-26 6-30 22z" fill="#6FBE63" stroke="#2F6E2F" stroke-width="3"/>
  <g class="flower-head">
    <ellipse cx="60" cy="30" rx="14" ry="24" fill="var(--flower, #FFC800)" stroke="#3A2A1A" stroke-width="3.5"/>
    <ellipse cx="60" cy="72" rx="14" ry="24" fill="var(--flower, #FFC800)" stroke="#3A2A1A" stroke-width="3.5"/>
    <ellipse cx="38" cy="42" rx="14" ry="24" transform="rotate(-60 38 42)" fill="var(--flower, #FFC800)" stroke="#3A2A1A" stroke-width="3.5"/>
    <ellipse cx="82" cy="42" rx="14" ry="24" transform="rotate(60 82 42)" fill="var(--flower, #FFC800)" stroke="#3A2A1A" stroke-width="3.5"/>
    <ellipse cx="38" cy="62" rx="14" ry="24" transform="rotate(60 38 62)" fill="var(--flower, #FFC800)" stroke="#3A2A1A" stroke-width="3.5"/>
    <ellipse cx="82" cy="62" rx="14" ry="24" transform="rotate(-60 82 62)" fill="var(--flower, #FFC800)" stroke="#3A2A1A" stroke-width="3.5"/>
    <circle cx="60" cy="52" r="14" fill="#FFD93B" stroke="#3A2A1A" stroke-width="3.5"/>
  </g>
</svg>`,

  grass: `
<svg class="grass-svg" viewBox="0 0 100 70" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M50 68C48 44 42 28 30 18c2 20 8 34 20 50z" fill="#4E9E45"/>
  <path d="M52 68c2-24 8-40 20-50-2 20-8 34-20 50z" fill="#6FBE63"/>
  <path d="M50 68C50 42 54 24 60 8c0 22-2 38-10 60z" fill="#3E8A3A"/>
</svg>`,
};

function injectAnimals(root = document) {
  root.querySelectorAll('[data-animal]').forEach((el) => {
    const name = el.dataset.animal;
    if (ANIMALS[name]) el.innerHTML = ANIMALS[name];
  });
}
