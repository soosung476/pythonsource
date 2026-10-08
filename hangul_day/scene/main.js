'use strict';
/*
 * 제580돌 한글날 홍보 모션그래픽 — 1920×1080, 30초
 *
 * renderFrame(t)가 t초 시점의 화면을 캔버스에 그린다. 모든 움직임이 t만의 함수라서
 * 프레임을 어떤 순서로 그려도 결과가 같다(병렬 렌더링 가능).
 * 음악 96 BPM 기준: 1박 0.625초, 1마디 2.5초. 장면 전환은 마디 경계에 맞췄다.
 *
 *  0.0 –  5.0  천지인(ㆍㅡㅣ) → 모음 열 개
 *  5.0 – 10.0  소리 내는 모양을 본뜬 자음 다섯 → 가획
 * 10.0 – 15.0  자모가 모여 '한글' → 새벽빛 전환, 訓民正音
 * 15.0 – 20.0  11,172자의 글자 벽
 * 20.0 – 25.0  『훈민정음』 서문
 * 25.0 – 30.0  제580돌 한글날 타이틀
 */

const W = 1920, H = 1080, CX = W / 2, CY = H / 2;
const BEAT = 60 / 96, S8 = BEAT / 2, S16 = BEAT / 4;
const DURATION = 30;

const cv = document.getElementById('c');
const mainCtx = cv.getContext('2d');
let ctx = mainCtx; // 그리기 함수들이 쓰는 대상. 오프스크린 레이어에 그릴 때 잠시 바꾼다.
function withCtx(g, fn) { const prev = ctx; ctx = g; try { return fn(); } finally { ctx = prev; } }

// ---------------------------------------------------------------- 색
const COL = {
  night: '#12203a', nightEdge: '#03060d',
  paper: '#f3ecde',
  ink: '#221e1a',
  cream: '#f6efe2',
  red: '#f05a46', blue: '#5d95f2', yellow: '#f6bf47', gold: '#ffd47e',
  redInk: '#c63e2d', blueInk: '#2b5daf', yellowInk: '#d38f14',
};
// 천지인 삼태극 색: 하늘(ㆍ)=빨강, 땅(ㅡ)=파랑, 사람(ㅣ)=노랑. c=기본 획, n=새로 더한 획
const PAL_NIGHT = { h: COL.red, e: COL.blue, p: COL.yellow, c: COL.cream, n: COL.gold };
const PAL_PAPER = { h: COL.redInk, e: COL.blueInk, p: COL.yellowInk, c: COL.ink, n: COL.redInk };

// ---------------------------------------------------------------- 수학 · 이징
const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const lerp = (a, b, u) => a + (b - a) * u;
const P = (t, t0, d) => clamp((t - t0) / d);
const ease = {
  lin: u => u,
  inQ: u => u * u,
  outQ: u => 1 - (1 - u) * (1 - u),
  inOutQ: u => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2),
  inC: u => u * u * u,
  outC: u => 1 - Math.pow(1 - u, 3),
  inOutC: u => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2),
  outQuart: u => 1 - Math.pow(1 - u, 4),
  outQuint: u => 1 - Math.pow(1 - u, 5),
  outExpo: u => (u >= 1 ? 1 : 1 - Math.pow(2, -10 * u)),
  inOutExpo: u => (u <= 0 ? 0 : u >= 1 ? 1 : u < 0.5 ? Math.pow(2, 20 * u - 10) / 2 : (2 - Math.pow(2, -20 * u + 10)) / 2),
  outBack: u => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); },
};
const E = (t, t0, d, f = ease.outC) => f(P(t, t0, d));

function hash(a, b = 0, c = 0) {
  let h = (Math.imul(a | 0, 0x27d4eb2d) ^ Math.imul((b | 0) + 0x9e37, 0x165667b1) ^ Math.imul((c | 0) + 0x7f4a, 0x2c1b3c6d)) >>> 0;
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function mulberry32(seed) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const _rgb = new Map();
function rgb(h) {
  let v = _rgb.get(h);
  if (!v) { const n = parseInt(h.slice(1), 16); v = [(n >> 16) & 255, (n >> 8) & 255, n & 255]; _rgb.set(h, v); }
  return v;
}
const toHex = v => '#' + v.map(x => Math.round(clamp(x, 0, 255)).toString(16).padStart(2, '0')).join('');
function mix(a, b, u) {
  if (u <= 0) return a;
  if (u >= 1) return b;
  const A = rgb(a), B = rgb(b);
  return toHex([lerp(A[0], B[0], u), lerp(A[1], B[1], u), lerp(A[2], B[2], u)]);
}
function rgba(h, a) { const [r, g, b] = rgb(h); return `rgba(${r},${g},${b},${a})`; }

// ---------------------------------------------------------------- 지오메트릭 자모
// 100×100 칸 위의 획(폴리라인) 목록. 둥근 끝·둥근 꺾임으로 그린다.
// 'h' 획(하늘 점에서 나온 짧은 획)은 바깥쪽 끝에서 시작하게 정의해 점이 늘어나며 붙는 연출을 한다.
const S = (role, ...xy) => { const pts = []; for (let i = 0; i < xy.length; i += 2) pts.push([xy[i], xy[i + 1]]); return { pts, role }; };
const RING = (role, cx, cy, r) => {
  const pts = [];
  for (let i = 0; i <= 64; i++) { const a = -Math.PI / 2 + (i / 64) * Math.PI * 2; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); }
  return { pts, role };
};
const GHOST = (x, y) => ({ pts: [[x, y], [x, y]], role: 'n', d1: 0 });

const JAMO = {
  'ㅏ': [S('p', 40, 8, 40, 92), S('h', 76, 50, 40, 50)],
  'ㅑ': [S('p', 40, 8, 40, 92), S('h', 76, 36, 40, 36), S('h', 76, 64, 40, 64)],
  'ㅓ': [S('p', 60, 8, 60, 92), S('h', 24, 50, 60, 50)],
  'ㅕ': [S('p', 60, 8, 60, 92), S('h', 24, 36, 60, 36), S('h', 24, 64, 60, 64)],
  'ㅗ': [S('e', 8, 66, 92, 66), S('h', 50, 30, 50, 66)],
  'ㅛ': [S('e', 8, 66, 92, 66), S('h', 36, 30, 36, 66), S('h', 64, 30, 64, 66)],
  'ㅜ': [S('e', 8, 34, 92, 34), S('h', 50, 70, 50, 34)],
  'ㅠ': [S('e', 8, 34, 92, 34), S('h', 36, 70, 36, 34), S('h', 64, 70, 64, 34)],
  'ㅡ': [S('e', 8, 50, 92, 50)],
  'ㅣ': [S('p', 50, 8, 50, 92)],

  'ㄱ': [S('c', 18, 20, 80, 20, 80, 86)],
  'ㅋ': [S('c', 18, 20, 80, 20, 80, 86), S('n', 18, 53, 80, 53)],
  'ㄴ': [S('c', 20, 14, 20, 80, 84, 80)],
  'ㄷ': [S('c', 20, 20, 20, 80, 84, 80), S('n', 82, 20, 20, 20)],
  'ㅌ': [S('c', 20, 20, 20, 80, 84, 80), S('c', 82, 20, 20, 20), S('n', 78, 50, 20, 50)],
  'ㄹ': [S('c', 18, 16, 80, 16, 80, 48, 20, 48, 20, 84, 84, 84)],
  'ㅁ': [S('c', 20, 20, 20, 80), S('c', 80, 20, 80, 80), S('c', 20, 80, 80, 80), S('c', 20, 20, 80, 20)],
  'ㅂ': [S('c', 20, 44, 20, 82), S('c', 80, 44, 80, 82), S('c', 20, 82, 80, 82), S('c', 20, 44, 80, 44), S('n', 20, 44, 20, 12), S('n', 80, 44, 80, 12)],
  'ㅍ': [S('c', 36, 24, 36, 78), S('c', 64, 24, 64, 78), S('c', 14, 78, 86, 78), S('n', 14, 24, 86, 24), GHOST(36, 24), GHOST(64, 24)],
  'ㅅ': [S('c', 16, 86, 50, 18, 84, 86)],
  'ㅈ': [S('c', 18, 86, 50, 26, 82, 86), S('n', 16, 26, 84, 26)],
  'ㅊ': [S('c', 18, 88, 50, 34, 82, 88), S('c', 16, 34, 84, 34), S('n', 50, 34, 50, 8)],
  'ㅇ': [RING('c', 50, 50, 34)],
  'ㅎ': [RING('c', 50, 66, 20), S('n', 16, 30, 84, 30), S('n', 50, 30, 50, 6)],
};

function polyLen(pts) {
  let L = 0;
  for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return L;
}

// 폴리라인의 [d0, d1] 구간(길이 비율)만 그린다. 길이가 0이면 점으로 그린다.
function strokePartial(pts, d0, d1, lw) {
  if (lw <= 0.01) return;
  const n = pts.length, segL = [];
  let L = 0;
  for (let i = 1; i < n; i++) { const l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); segL.push(l); L += l; }
  if (L < 1e-3) {
    if (d1 > d0) { ctx.beginPath(); ctx.arc(pts[0][0], pts[0][1], lw / 2, 0, Math.PI * 2); ctx.fill(); }
    return;
  }
  const a = d0 * L, b = d1 * L;
  if (b - a < 1e-4) return;
  ctx.lineWidth = lw;
  ctx.beginPath();
  let acc = 0, started = false;
  for (let i = 1; i < n; i++) {
    const l = segL[i - 1], s0 = acc, s1 = acc + l;
    acc = s1;
    if (s1 < a || s0 > b || l === 0) continue;
    const p = pts[i - 1], q = pts[i];
    const ua = clamp((a - s0) / l), ub = clamp((b - s0) / l);
    if (!started) { ctx.moveTo(lerp(p[0], q[0], ua), lerp(p[1], q[1], ua)); started = true; }
    ctx.lineTo(lerp(p[0], q[0], ub), lerp(p[1], q[1], ub));
  }
  ctx.stroke();
}

function resample(pts, m) {
  const n = pts.length, cum = [0];
  for (let i = 1; i < n; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const L = cum[n - 1];
  if (L < 1e-6) return Array.from({ length: m }, () => [pts[0][0], pts[0][1]]);
  const out = [];
  let j = 1;
  for (let k = 0; k < m; k++) {
    const s = (L * k) / (m - 1);
    while (j < n - 1 && cum[j] < s) j++;
    const seg = cum[j] - cum[j - 1], u = seg > 0 ? (s - cum[j - 1]) / seg : 0;
    out.push([lerp(pts[j - 1][0], pts[j][0], u), lerp(pts[j - 1][1], pts[j][1], u)]);
  }
  return out;
}

// 자모 A → B 변형. 짝이 없는 획은 자기 경로를 따라 자라나거나(d1 0→1) 줄어든다.
const ghostOf = s => ({ pts: s.pts, role: s.role, d0: 0, d1: 0 });
function morph(A, B, u) {
  const n = Math.max(A.length, B.length), out = [];
  for (let i = 0; i < n; i++) {
    const a = A[i] || ghostOf(B[i]), b = B[i] || ghostOf(A[i]);
    let pa = a.pts, pb = b.pts;
    if (pa.length !== pb.length) { pa = resample(pa, 96); pb = resample(pb, 96); }
    out.push({
      pts: pa.map((p, k) => [lerp(p[0], pb[k][0], u), lerp(p[1], pb[k][1], u)]),
      ra: a.role, rb: b.role, u,
      d0: lerp(a.d0 ?? 0, b.d0 ?? 0, u), d1: lerp(a.d1 ?? 1, b.d1 ?? 1, u), w: lerp(a.w ?? 1, b.w ?? 1, u),
    });
  }
  return out;
}

const boxAt = (x, y, size) => ({ x: x - size / 2, y: y - size / 2, w: size, h: size });
const lerpBox = (a, b, u) => ({ x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u), w: lerp(a.w, b.w, u), h: lerp(a.h, b.h, u) });

function strokeColor(s, pal) {
  if (s.ra !== undefined) return mix(pal[s.ra], pal[s.rb], s.u);
  return pal[s.role];
}

// opt: pal, color(모든 획 단색), tint(색을 섞을 대상), tintU, alpha, glow(px), write(0..1 획순 쓰기)
function renderGlyph(strokes, box, lw, opt = {}) {
  const pal = opt.pal || PAL_NIGHT;
  let lens = null, tot = 0, acc = 0;
  if (opt.write !== undefined) {
    lens = strokes.map(s => Math.max(polyLen(s.pts), 14));
    tot = lens.reduce((a, b) => a + b, 0);
  }
  ctx.save();
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.globalAlpha = opt.alpha ?? 1;
  for (let i = 0; i < strokes.length; i++) {
    const s = strokes[i];
    const d0 = s.d0 ?? 0;
    let d1 = s.d1 ?? 1;
    if (lens) { d1 = Math.min(d1, clamp((opt.write * tot - acc) / lens[i])); acc += lens[i]; }
    if (d1 <= d0) continue;
    let col = opt.color || strokeColor(s, pal);
    if (opt.tint) col = mix(col, opt.tint, opt.tintU ?? 1);
    ctx.strokeStyle = col;
    ctx.fillStyle = col;
    if (opt.glow) { ctx.shadowColor = rgba(opt.glowColor || col, opt.glowA ?? 0.55); ctx.shadowBlur = opt.glow; }
    const pts = s.pts.map(p => [box.x + (p[0] / 100) * box.w, box.y + (p[1] / 100) * box.h]);
    strokePartial(pts, d0, d1, lw * (s.w ?? 1));
  }
  ctx.restore();
}

// ---------------------------------------------------------------- 텍스트
const SERIF = '"Serif KR"', SANS = '"Sans KR"';
const _cw = new Map();
function charW(font, ch) {
  const k = font + '|' + ch;
  let w = _cw.get(k);
  if (w === undefined) { ctx.font = font; w = ctx.measureText(ch).width; _cw.set(k, w); }
  return w;
}

// 글자 단위로 그린다. fx(i, n) → {a, dx, dy, s, blur, color}. 각 글자의 [x0, x1]을 돌려준다.
function drawText(str, x, y, o, fx) {
  const font = `${o.weight || 400} ${o.size}px ${o.family || SANS}`;
  const chars = [...str], sp = o.spacing || 0;
  const ws = chars.map(c => charW(font, c));
  const total = ws.reduce((a, b) => a + b, 0) + sp * (chars.length - 1);
  let cx = o.align === 'left' ? x : o.align === 'right' ? x - total : x - total / 2;
  const pos = [];
  ctx.save();
  ctx.font = font;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  for (let i = 0; i < chars.length; i++) {
    pos.push([cx, cx + ws[i]]);
    const f = fx ? fx(i, chars.length) || {} : {};
    const a = (o.alpha ?? 1) * (f.a ?? 1);
    if (a > 0.003 && chars[i] !== ' ') {
      ctx.globalAlpha = a;
      ctx.fillStyle = f.color || o.color || COL.ink;
      const blur = f.blur ?? o.blur ?? 0;
      ctx.filter = blur > 0.3 ? `blur(${blur.toFixed(2)}px)` : 'none';
      const s = f.s ?? 1;
      ctx.save();
      ctx.translate(cx + ws[i] / 2 + (f.dx || 0), y + (f.dy || 0));
      if (f.rot) ctx.rotate(f.rot);
      if (s !== 1) ctx.scale(s, s);
      ctx.fillText(chars[i], 0, 0);
      ctx.restore();
    }
    cx += ws[i] + sp;
  }
  ctx.restore();
  return { total, pos };
}

// 아래에서 떠오르며 선명해지는 글자 효과
const rise = (t, t0, stagger, dur = 0.5, dist = 16, blur = 8) => i => {
  const u = P(t, t0 + i * stagger, dur), e = ease.outC(u);
  return { a: ease.outQ(u), dy: (1 - e) * dist, blur: (1 - e) * blur };
};

// ---------------------------------------------------------------- 배경
let paper = null, wallLayer = null, wallCtx = null, titleLayer = null, titleCtx = null;

function makePaper() {
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const g = c.getContext('2d');
  const rnd = mulberry32(1446);
  g.fillStyle = COL.paper;
  g.fillRect(0, 0, W, H);
  for (let i = 0; i < 70; i++) {
    const x = rnd() * W, y = rnd() * H, r = 90 + rnd() * 300;
    const gr = g.createRadialGradient(x, y, 0, x, y, r);
    gr.addColorStop(0, rnd() < 0.55 ? 'rgba(150,115,70,0.014)' : 'rgba(255,255,250,0.035)');
    gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr;
    g.fillRect(x - r, y - r, r * 2, r * 2);
  }
  g.lineCap = 'round';
  for (let i = 0; i < 1600; i++) {
    const x = rnd() * W, y = rnd() * H, len = 8 + rnd() * 50, a = rnd() * Math.PI * 2, bend = (rnd() - 0.5) * 0.9;
    g.strokeStyle = rnd() < 0.6 ? `rgba(140,108,66,${0.035 + rnd() * 0.06})` : `rgba(255,255,252,${0.12 + rnd() * 0.16})`;
    g.lineWidth = 0.5 + rnd() * 1.2;
    g.beginPath();
    g.moveTo(x, y);
    g.quadraticCurveTo(x + Math.cos(a + bend) * len * 0.5, y + Math.sin(a + bend) * len * 0.5, x + Math.cos(a) * len, y + Math.sin(a) * len);
    g.stroke();
  }
  const id = g.getImageData(0, 0, W, H), d = id.data;
  for (let i = 0; i < d.length; i += 4) { const n = (rnd() - 0.5) * 6; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
  g.putImageData(id, 0, 0);
  return c;
}

const STARS = (() => {
  const rnd = mulberry32(9);
  return Array.from({ length: 170 }, () => ({
    x: rnd() * W, y: rnd() * H, v: 5 + rnd() * 18, r: 0.6 + rnd() * 1.8,
    a: 0.12 + rnd() * 0.45, f: 0.4 + rnd() * 1.8, ph: rnd() * 6.28,
  }));
})();
const BOKEH = (() => {
  const rnd = mulberry32(31);
  return Array.from({ length: 14 }, () => ({ x: rnd() * W, y: rnd() * H, r: 40 + rnd() * 110, a: 0.025 + rnd() * 0.04, v: 4 + rnd() * 8 }));
})();

function drawNight(t) {
  const g = ctx.createRadialGradient(CX, 470, 60, CX, 470, 1250);
  g.addColorStop(0, COL.night);
  g.addColorStop(1, COL.nightEdge);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  ctx.save();
  for (const b of BOKEH) {
    const y = ((b.y - b.v * t) % (H + 300) + H + 300) % (H + 300) - 150;
    const gr = ctx.createRadialGradient(b.x, y, 0, b.x, y, b.r);
    gr.addColorStop(0, `rgba(140,170,255,${b.a})`);
    gr.addColorStop(1, 'rgba(140,170,255,0)');
    ctx.fillStyle = gr;
    ctx.fillRect(b.x - b.r, y - b.r, b.r * 2, b.r * 2);
  }
  ctx.fillStyle = COL.cream;
  for (const s of STARS) {
    const y = ((s.y - s.v * t) % H + H) % H;
    ctx.globalAlpha = s.a * (0.55 + 0.45 * Math.sin(t * s.f * 2 + s.ph));
    ctx.beginPath();
    ctx.arc(s.x, y, s.r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

const DAWN = { t: 12.5, x: CX, y: 470 };
function background(t) {
  const R = dawnR(t);
  if (R < 1180) drawNight(t);
  if (R <= 0) return;
  if (R >= 1180) { ctx.drawImage(paper, 0, 0); return; }
  ctx.save();
  ctx.beginPath();
  ctx.arc(DAWN.x, DAWN.y, R, 0, Math.PI * 2);
  ctx.clip();
  ctx.drawImage(paper, 0, 0);
  ctx.restore();
  // 번져 나가는 빛의 테두리
  const k = 1 - R / 1180;
  ctx.save();
  ctx.strokeStyle = rgba(COL.gold, 0.55 * k);
  ctx.shadowColor = rgba(COL.gold, 0.9 * k);
  ctx.shadowBlur = 60;
  ctx.lineWidth = 26;
  ctx.beginPath();
  ctx.arc(DAWN.x, DAWN.y, R, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

// ---------------------------------------------------------------- 자막(밤 장면)
const CAPTIONS = [
  { s: '하늘 · 땅 · 사람을 본떠 모음을 만들고,', a: 3.0, b: 4.75 },
  { s: '소리 내는 모양을 본떠 자음을 만들었습니다', a: 5.35, b: 7.25 },
  { s: '소리가 세지면 획을 더했습니다', a: 7.75, b: 9.7 },
  { s: '자음과 모음이 모여 한 글자를 이룹니다', a: 10.85, b: 12.2 },
];
function captions(t) {
  for (const c of CAPTIONS) {
    if (t < c.a || t > c.b + 0.4) continue;
    const out = E(t, c.b, 0.32, ease.inQ);
    drawText(c.s, CX, 990, { size: 40, weight: 500, color: COL.cream, alpha: 0.94 * (1 - out), spacing: 1 }, rise(t, c.a, 0.016, 0.45, 14, 6));
  }
}

// ---------------------------------------------------------------- 1. 천지인
function sceneHeavenEarthHuman(t) {
  if (t > 2.95) return;
  const Y = 440, SZ = 230, LW = 30;
  const items = [
    { x: CX - 440, t0: BEAT, han: '天', ko: '하늘', col: COL.red },
    { x: CX, t0: BEAT * 2, han: '地', ko: '땅', col: COL.blue },
    { x: CX + 440, t0: BEAT * 3, han: '人', ko: '사람', col: COL.yellow },
  ];
  const exit = E(t, 2.4, 0.45, ease.inC);
  items.forEach((it, idx) => {
    if (t < it.t0) return;
    const u = P(t, it.t0, 0.55), e = ease.outC(u);
    const sc = lerp(1, 0.55, exit);
    const box = boxAt(it.x, Y, SZ * sc);
    // 파문
    const ru = P(t, it.t0, 1.2);
    if (ru < 1) {
      ctx.save();
      ctx.strokeStyle = rgba(it.col, 0.5 * (1 - ru));
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(it.x, Y, lerp(30, 230, ease.outC(ru)), 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
    let strokes;
    if (idx === 0) strokes = [{ pts: [[50, 50], [50, 50]], role: 'h', w: 1.6 * ease.outBack(clamp(u * 1.4)) }];
    else if (idx === 1) strokes = [{ pts: [[8, 50], [92, 50]], role: 'e', d0: 0.5 - 0.5 * e, d1: 0.5 + 0.5 * e }];
    else strokes = [{ pts: [[50, 8], [50, 92]], role: 'p', d0: 1 - e, d1: 1 }];
    renderGlyph(strokes, box, LW * sc, { alpha: 1 - exit, glow: 30 });

    const lu = P(t, it.t0 + 0.12, 0.5), la = ease.outQ(lu) * (1 - E(t, 2.2, 0.3, ease.inQ));
    const dy = (1 - ease.outC(lu)) * 16;
    drawText(it.han, it.x, 655, { family: SERIF, weight: 700, size: 64, color: it.col, alpha: la }, () => ({ dy }));
    drawText(it.ko, it.x, 712, { size: 30, weight: 500, color: COL.cream, alpha: la * 0.8, spacing: 8 }, () => ({ dy }));
  });
}

// ---------------------------------------------------------------- 1b. 모음 열 개
const VOWELS = ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ'];
const vowelT = i => 2.5 + i * S16;
function vowelBox(i, t) {
  const a = boxAt(CX + (i - 4.5) * 150, 470, 120);
  const b = boxAt(CX + (i - 4.5) * 92, 150, 66);
  return lerpBox(a, b, E(t, 4.85 + i * 0.02, 0.6, ease.inOutC));
}
const vowelLW = t => lerp(14, 7.5, E(t, 4.85, 0.6, ease.inOutC));
function vowelStrokes(i, t) {
  const ts = vowelT(i);
  return JAMO[VOWELS[i]].map(s => {
    if (s.role === 'h') {
      const pop = ease.outBack(P(t, ts + 0.16, 0.24));
      const st = ease.inOutC(P(t, ts + 0.3, 0.26));
      return { pts: s.pts, role: 'h', d0: 0, d1: pop > 0 ? Math.max(st, 1e-4) : 0, w: pop };
    }
    return { pts: s.pts, role: s.role, d0: 0, d1: ease.outC(P(t, ts, 0.32)) };
  });
}
function sceneVowels(t) {
  if (t < 2.5 || t > 10.6) return;
  for (let i = 0; i < VOWELS.length; i++) {
    if (t < vowelT(i)) continue;
    const flying = FLIGHTS.find(f => f.v === i);
    if (flying && t >= flying.t0) continue;
    const alpha = flying ? 1 : 1 - E(t, 9.95 + i * 0.015, 0.4, ease.inQ);
    renderGlyph(vowelStrokes(i, t), vowelBox(i, t), vowelLW(t), { alpha, glow: 14 });
  }
}

// ---------------------------------------------------------------- 2. 자음과 가획
const CONS = [
  { base: 'ㄱ', chain: ['ㅋ'], han: '牙', ko: '어금닛소리' },
  { base: 'ㄴ', chain: ['ㄷ', 'ㅌ'], han: '舌', ko: '혓소리' },
  { base: 'ㅁ', chain: ['ㅂ', 'ㅍ'], han: '脣', ko: '입술소리' },
  { base: 'ㅅ', chain: ['ㅈ', 'ㅊ'], han: '齒', ko: '잇소리' },
  { base: 'ㅇ', chain: ['ㅎ'], han: '喉', ko: '목소리' },
];
const colX = i => CX + (i - 2) * 270;
const consT = i => 5.0 + i * S8;
const row1Box = (i, t) => lerpBox(boxAt(colX(i), 460, 190), boxAt(colX(i), 355, 140), E(t, 7.3 + i * 0.03, 0.5, ease.inOutC));
const row2Box = i => boxAt(colX(i), 555, 140);
const row3Box = i => boxAt(colX(i), 755, 140);
const row2T = i => 7.5 + i * S16;
const row3T = i => 8.75 + (i - 1) * S16;
const consLW = box => 0.105 * box.w;

function connector(x, y0, y1, u, alpha) {
  if (u <= 0) return;
  ctx.save();
  ctx.strokeStyle = rgba(COL.cream, 0.28 * alpha);
  ctx.lineWidth = 2;
  ctx.setLineDash([2, 7]);
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(x, y0);
  ctx.lineTo(x, lerp(y0, y1, u));
  ctx.stroke();
  ctx.restore();
}

function sceneConsonants(t) {
  if (t < 5.0 || t > 10.8) return;
  const fadeOut = k => 1 - E(t, 9.95 + k * 0.02, 0.4, ease.inQ);
  CONS.forEach((c, i) => {
    const ts = consT(i);
    if (t < ts) return;
    // 1행: 기본 자음
    const fl1 = FLIGHTS.find(f => f.row === 1 && f.col === i);
    if (!(fl1 && t >= fl1.t0)) {
      const box = row1Box(i, t);
      renderGlyph(JAMO[c.base], box, consLW(box), { write: ease.inOutQ(P(t, ts, 0.6)), alpha: fl1 ? 1 : fadeOut(i), glow: 16 });
    }
    // 발음 기관 이름
    const lu = P(t, ts + 0.22, 0.5), la = ease.outQ(lu) * (1 - E(t, 7.1, 0.3, ease.inQ));
    if (la > 0) {
      const dy = (1 - ease.outC(lu)) * 14;
      drawText(c.han, colX(i), 640, { family: SERIF, weight: 700, size: 52, color: COL.gold, alpha: la }, () => ({ dy }));
      drawText(c.ko, colX(i), 692, { size: 28, weight: 500, color: COL.cream, alpha: la * 0.75, spacing: 4 }, () => ({ dy }));
    }
    // 2행: 획을 더한 자음
    const t2 = row2T(i);
    if (t >= t2) {
      const u = P(t, t2, 0.45);
      const fl2 = FLIGHTS.find(f => f.row === 2 && f.col === i);
      const a = fl2 ? 1 : fadeOut(5 + i);
      const r1 = row1Box(i, t);
      connector(colX(i), r1.y + r1.h + 6, row2Box(i).y - 6, ease.outC(u), fadeOut(10));
      if (!(fl2 && t >= fl2.t0)) {
        const box = lerpBox(r1, row2Box(i), ease.outC(u));
        renderGlyph(morph(JAMO[c.base], JAMO[c.chain[0]], ease.inOutC(u)), box, consLW(box), { alpha: a, glow: 16 });
      }
    }
    // 3행
    if (c.chain[1]) {
      const t3 = row3T(i);
      if (t >= t3) {
        const u = P(t, t3, 0.45);
        connector(colX(i), row2Box(i).y + 146, row3Box(i).y - 6, ease.outC(u), fadeOut(10));
        const box = lerpBox(row2Box(i), row3Box(i), ease.outC(u));
        renderGlyph(morph(JAMO[c.chain[0]], JAMO[c.chain[1]], ease.inOutC(u)), box, consLW(box), { alpha: fadeOut(10 + i), glow: 16 });
      }
    }
  });
}

// ---------------------------------------------------------------- 3. '한글'
const SYL = [boxAt(CX - 170, 470, 300), boxAt(CX + 170, 470, 300)];
const SLOT = {
  'ㅎ': [0, 2, 2, 56, 58], 'ㅏ': [0, 58, 0, 40, 62], 'ㄴ': [0, 10, 62, 80, 36],
  'ㄱ': [1, 12, 0, 74, 34], 'ㅡ': [1, 2, 35, 96, 20], 'ㄹ': [1, 16, 54, 68, 46],
};
function slotBox(j) {
  const [s, x, y, w, h] = SLOT[j], B = SYL[s];
  return { x: B.x + (x / 100) * B.w, y: B.y + (y / 100) * B.h, w: (w / 100) * B.w, h: (h / 100) * B.h };
}
const LOGO_LW = 22;
// 날아갈 자모: 어디서(행/열 또는 모음 번호) 출발하는지
const FLIGHTS = [
  { j: 'ㅎ', row: 2, col: 4, t0: 10.2 },
  { j: 'ㅏ', v: 0, t0: 10.27 },
  { j: 'ㄴ', row: 1, col: 1, t0: 10.34 },
  { j: 'ㄱ', row: 1, col: 0, t0: 10.41 },
  { j: 'ㅡ', v: 8, t0: 10.48 },
];
const FLIGHT_DUR = 0.78;

function flightFrom(f, t) {
  if (f.v !== undefined) return { box: vowelBox(f.v, t), lw: vowelLW(t), strokes: JAMO[f.j], pal: PAL_NIGHT };
  const box = f.row === 1 ? row1Box(f.col, t) : row2Box(f.col);
  return { box, lw: consLW(box), strokes: JAMO[f.j], pal: PAL_NIGHT };
}

function logoTransform(t) {
  // 착지할 때 살짝 튀고, 글자 벽으로 넘어갈 때 작아지며 화면 중앙으로 간다
  const bump = 1 + 0.035 * Math.sin(Math.PI * P(t, 11.27, 0.32));
  const z = E(t, 14.55, 1.5, ease.outC);
  const s = lerp(1, 1 / 3.2, z) * bump;
  const y = lerp(470, CY, z);
  return { s, y };
}

const dawnR = t => 1200 * E(t, DAWN.t - 0.05, 1.0, ease.inOutC);

function drawLogo(t, base, glow, alpha) {
  const { s, y } = logoTransform(t);
  ctx.save();
  ctx.translate(CX, y);
  ctx.scale(s, s);
  ctx.translate(-CX, -470);
  for (const f of FLIGHTS) {
    if (t < f.t0) continue;
    const u = ease.inOutC(P(t, f.t0, FLIGHT_DUR));
    const from = flightFrom(f, t);
    const box = lerpBox(from.box, slotBox(f.j), u);
    const lw = lerp(from.lw, LOGO_LW, u);
    renderGlyph(from.strokes, box, lw, { pal: PAL_NIGHT, tint: base, tintU: u, alpha, glow, glowColor: COL.gold, glowA: 0.6 });
  }
  // ㄹ은 제자리에서 써진다
  const rw = ease.inOutQ(P(t, 10.62, 0.62));
  if (rw > 0) renderGlyph(JAMO['ㄹ'], slotBox('ㄹ'), LOGO_LW, { color: base, write: rw, alpha, glow, glowColor: COL.gold, glowA: 0.6 });
  ctx.restore();
}

function sceneLogo(t) {
  if (t < 10.2 || t > 15.6) return;
  const glow = lerp(15, 54, E(t, 11.9, 0.6, ease.inQ));
  const alpha = 1 - E(t, 15.15, 0.4, ease.inQ);
  const R = dawnR(t);
  if (R <= 0) drawLogo(t, COL.cream, glow, alpha);
  else if (R >= 1180) drawLogo(t, COL.ink, 0, alpha);
  else {
    // 번지는 빛의 원을 경계로 바깥은 밤(크림색 글자), 안쪽은 종이(먹색 글자)
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, W, H);
    ctx.arc(DAWN.x, DAWN.y, R, 0, Math.PI * 2);
    ctx.clip('evenodd');
    drawLogo(t, COL.cream, glow, alpha);
    ctx.restore();
    ctx.save();
    ctx.beginPath();
    ctx.arc(DAWN.x, DAWN.y, R, 0, Math.PI * 2);
    ctx.clip();
    drawLogo(t, COL.ink, 0, alpha);
    ctx.restore();
  }

  // 訓民正音 · 백성을 가르치는 바른 소리
  if (t > 13.0 && t < 14.9) {
    const out = E(t, 14.3, 0.3, ease.inQ);
    drawText('訓民正音', CX, 740, { family: SERIF, weight: 700, size: 46, color: COL.redInk, spacing: 22, alpha: 1 - out }, rise(t, 13.12, 0.07, 0.5, 14, 8));
    drawText('백성을 가르치는 바른 소리', CX, 802, { size: 32, weight: 300, color: COL.ink, spacing: 3, alpha: 0.82 * (1 - out) }, rise(t, 13.4, 0.025, 0.5, 12, 6));
  }
}

// ---------------------------------------------------------------- 4. 11,172
const CELL = 66;
const WORDS = [
  { s: '사랑', c: -13, r: -6, col: COL.redInk },
  { s: '하늘', c: 8, r: -7, col: COL.blueInk },
  { s: '노래', c: -4, r: -7, col: COL.yellowInk },
  { s: '별빛', c: -14, r: 1, col: COL.ink },
  { s: '바다', c: -10, r: 6, col: COL.blueInk },
  { s: '꿈', c: 13, r: -3, col: COL.yellowInk },
  { s: '우리', c: 2, r: 7, col: COL.ink },
  { s: '마음', c: 10, r: 5, col: COL.redInk },
  { s: '이야기', c: -6, r: 7, col: COL.redInk },
  { s: '나무', c: 12, r: 1, col: COL.blueInk },
];
const WORD_CELLS = new Map();
WORDS.forEach((w, k) => [...w.s].forEach((ch, i) => WORD_CELLS.set(`${w.c + i},${w.r}`, { k, ch })));
const wordT = k => 18.12 + k * S16;

function wallChar(seed, t) {
  const rate = lerp(15, 1.3, E(t, 15.0, 3.4, ease.outQ)) * (0.6 + 0.8 * hash(seed, 3));
  const k = Math.floor((t + hash(seed, 5) * 3) * rate);
  return String.fromCharCode(0xac00 + Math.floor(hash(seed, k, 9) * 11172));
}

function sceneWall(t) {
  if (t < 14.5 || t > 20.7) return;
  const cam = lerp(3.2, 1, E(t, 14.55, 1.5, ease.outC));
  const g = wallCtx;
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.clearRect(0, 0, W, H);
  g.translate(CX, CY);
  g.scale(cam, cam);
  g.font = `400 40px ${SERIF}`;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  const lit = [COL.redInk, COL.blueInk, COL.yellowInk];
  for (let r = -9; r <= 9; r++) {
    for (let c = -15; c <= 15; c++) {
      const x = c * CELL, y = r * CELL;
      if (Math.abs(x * cam) > CX + 50 || Math.abs(y * cam) > CY + 50) continue;
      const seed = (c + 100) * 1000 + (r + 100);
      const wc = WORD_CELLS.get(`${c},${r}`);
      if (wc && t >= wordT(wc.k)) continue;
      const d = Math.hypot(x, y) / 1100;
      const appear = E(t, 14.6 + d * 0.75, 0.4, ease.outQ);
      const fall = P(t, 19.65 + hash(seed, 11) * 0.4, 0.6);
      let a = appear * (1 - fall) * (0.075 + 0.13 * hash(seed, 7));
      let col = COL.ink;
      const k2 = Math.floor(t * 2.6 + hash(seed, 13) * 10);
      if (hash(seed, k2, 17) > 0.968) { a = appear * (1 - fall) * 0.55; col = lit[Math.floor(hash(seed, k2, 19) * 3)]; }
      if (a < 0.004) continue;
      g.globalAlpha = a;
      g.fillStyle = col;
      g.fillText(wallChar(seed, t), x, y + ease.inC(fall) * 260);
    }
  }
  // 가운데는 비워서 숫자가 잘 보이게
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.globalAlpha = 1;
  g.globalCompositeOperation = 'destination-out';
  const clear = E(t, 14.7, 0.8, ease.outQ);
  const gr = g.createRadialGradient(CX, CY, 0, CX, CY, 640);
  gr.addColorStop(0, `rgba(0,0,0,${clear})`);
  gr.addColorStop(0.45, `rgba(0,0,0,${0.97 * clear})`);
  gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr;
  g.fillRect(0, 0, W, H);
  g.globalCompositeOperation = 'source-over';
  ctx.drawImage(wallLayer, 0, 0);

  // 단어들이 하나씩 제 색으로 떠오른다
  WORDS.forEach((w, k) => {
    const u = P(t, wordT(k), 0.35);
    if (u <= 0) return;
    const out = P(t, 19.75 + k * 0.03, 0.45);
    [...w.s].forEach((ch, i) => {
      const x = CX + (w.c + i) * CELL, y = CY + w.r * CELL;
      ctx.save();
      ctx.globalAlpha = ease.outQ(u) * (1 - out);
      ctx.translate(x, y + ease.inC(out) * 200);
      const s = lerp(1.6, 1, ease.outBack(u));
      ctx.scale(s, s);
      ctx.font = `700 46px ${SERIF}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = w.col;
      ctx.fillText(ch, 0, 0);
      ctx.restore();
    });
  });

  // 숫자
  const out = E(t, 19.7, 0.5, ease.inQ);
  const fx = (t0) => i => { const r = rise(t, t0, 0.025, 0.5, 14, 8)(i); r.blur += out * 10; return r; };
  drawText('스물네 개의 자모로', CX, CY - 150, { size: 44, weight: 500, color: COL.ink, alpha: 0.85 * (1 - out), spacing: 2 }, fx(15.35));
  drawCounter(t, out);
  drawText('개의 글자를 만들 수 있습니다', CX, CY + 172, { size: 44, weight: 500, color: COL.ink, alpha: 0.85 * (1 - out), spacing: 2 }, fx(16.95));
}

function drawCounter(t, out) {
  const appear = E(t, 15.45, 0.4, ease.outQ);
  if (appear <= 0) return;
  const v = Math.round(11172 * ease.outQuart(P(t, 15.5, 1.85)));
  const font = `900 220px ${SERIF}`;
  const dw = Math.max(...'0123456789'.split('').map(d => charW(font, d)));
  const cw = charW(font, ',');
  const slots = '11,172'.split('');
  const total = slots.reduce((a, ch) => a + (ch === ',' ? cw : dw), 0);
  const str = v.toLocaleString('en-US');
  const pulse = 1 + 0.06 * Math.sin(Math.PI * P(t, 17.5, 0.3));
  const done = E(t, 17.45, 0.25, ease.outQ);
  ctx.save();
  ctx.translate(CX, CY + 72);
  ctx.scale(pulse, pulse);
  ctx.font = font;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  ctx.globalAlpha = appear * (1 - out);
  ctx.filter = out > 0.01 ? `blur(${(out * 12).toFixed(2)}px)` : 'none';
  ctx.fillStyle = mix(COL.ink, COL.redInk, done);
  // 오른쪽 정렬된 고정폭 칸에 숫자를 채운다(세는 동안 자리가 흔들리지 않게)
  let x = total / 2;
  const chars = [...str];
  for (let i = chars.length - 1; i >= 0; i--) {
    const w = chars[i] === ',' ? cw : dw;
    x -= w;
    ctx.fillText(chars[i], x + w / 2, 0);
  }
  ctx.restore();
  // 밑줄
  const ul = E(t, 17.5, 0.45, ease.outC) * (1 - out);
  if (ul > 0) {
    ctx.save();
    ctx.strokeStyle = COL.redInk;
    ctx.lineWidth = 7;
    ctx.lineCap = 'round';
    ctx.globalAlpha = 1 - out;
    ctx.beginPath();
    ctx.moveTo(CX - 210 * ul, CY + 104);
    ctx.lineTo(CX + 210 * ul, CY + 104);
    ctx.stroke();
    ctx.restore();
  }
}

// ---------------------------------------------------------------- 5. 『훈민정음』 서문
const FRAME = { x: 300, y: 205, w: 1320, h: 670 };
function rectPts(x, y, w, h) { return [[x + w / 2, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y], [x + w / 2, y]]; }
function sceneQuote(t) {
  if (t < 19.9 || t > 25.3) return;
  const out = E(t, 24.5, 0.5, ease.inQ);
  const fp = E(t, 20.0, 1.0, ease.inOutC) * (1 - out);
  ctx.save();
  ctx.strokeStyle = rgba(COL.redInk, 0.6);
  ctx.lineCap = 'butt';
  ctx.lineJoin = 'miter';
  ctx.fillStyle = rgba(COL.redInk, 0.6);
  strokePartial(rectPts(FRAME.x, FRAME.y, FRAME.w, FRAME.h), 0, fp, 3.5);
  strokePartial(rectPts(FRAME.x + 14, FRAME.y + 14, FRAME.w - 28, FRAME.h - 28), 0, fp, 1.4);
  ctx.restore();

  const blurOut = out * 12;
  const fx = (t0, stagger) => i => { const r = rise(t, t0, stagger, 0.55, 18, 10)(i); r.blur += blurOut; return r; };
  drawText('“', CX, 400, { family: SERIF, weight: 900, size: 150, color: COL.redInk, alpha: 1 - out }, i => {
    const u = P(t, 20.3, 0.5);
    return { a: ease.outQ(u), s: lerp(0.6, 1, ease.outBack(u)), blur: blurOut };
  });
  const l1 = drawText('사람마다 하여금 쉬이 익혀', CX, 515, { family: SERIF, weight: 700, size: 70, color: COL.ink, alpha: 1 - out, spacing: 2 }, fx(20.5, 0.05));
  const l2 = drawText('날로 씀에 편안케 하고자 할 따름이니라', CX, 625, { family: SERIF, weight: 700, size: 70, color: COL.ink, alpha: 1 - out, spacing: 2 }, fx(21.05, 0.045));
  // 강조 밑줄: '쉬이', '편안케'
  const under = (pos, i0, i1, y, t0) => {
    const u = E(t, t0, 0.4, ease.outC) * (1 - out);
    if (u <= 0) return;
    const x0 = pos[i0][0] + 4, x1 = pos[i1][1] - 4;
    ctx.save();
    ctx.strokeStyle = COL.redInk;
    ctx.globalAlpha = 0.85;
    ctx.lineWidth = 8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x0, y);
    ctx.lineTo(lerp(x0, x1, u), y);
    ctx.stroke();
    ctx.restore();
  };
  under(l1.pos, 9, 10, 545, 22.5);
  under(l2.pos, 6, 8, 655, 22.8);
  drawText('― 『훈민정음』 서문, 1446', CX, 752, { size: 32, weight: 300, color: COL.ink, alpha: 0.75 * (1 - out), spacing: 3 }, fx(22.95, 0.02));
}

// ---------------------------------------------------------------- 6. 타이틀
const CONFETTI = (() => {
  const rnd = mulberry32(580);
  const kinds = ['dot', 'jamo', 'bar', 'ring', 'jamo', 'dot', 'bar', 'jamo'];
  const jamos = ['ㄱ', 'ㅎ', 'ㅏ', 'ㄴ', 'ㄹ', 'ㅗ', 'ㅁ', 'ㅜ', 'ㅂ', 'ㅓ'];
  const cols = [COL.redInk, COL.blueInk, COL.yellowInk, COL.ink];
  const n = 22, items = [];
  for (let k = 0; k < n; k++) {
    const a = -Math.PI / 2 + (k / n) * Math.PI * 2 + (rnd() - 0.5) * 0.12;
    const rx = 790 + (rnd() - 0.5) * 120, ry = 410 + (rnd() - 0.5) * 70;
    const kind = kinds[k % kinds.length];
    // 글자 영역(제580돌 ~ 문구)과 겹치면 바깥으로 밀어낸다
    let f = 1, x, y;
    do {
      x = clamp(CX + rx * f * Math.cos(a), 90, W - 90);
      y = clamp(CY + ry * f * Math.sin(a), 80, H - 80);
      f += 0.03;
    } while (x > CX - 660 && x < CX + 660 && y > 245 && y < 915 && f < 2);
    items.push({
      x, y,
      kind, col: cols[(k * 3) % cols.length], j: jamos[k % jamos.length],
      rot: kind === 'jamo' ? (rnd() - 0.5) * 0.5 : (rnd() - 0.5) * 2.2,
      size: kind === 'jamo' ? 74 + rnd() * 18 : 64 + rnd() * 26, ph: rnd() * 6.28, d: rnd() * 0.12,
    });
  }
  return items;
})();

function drawConfetti(t) {
  const O = { x: CX, y: 520 };
  CONFETTI.forEach(o => {
    const u = P(t, 25.0 + o.d, 1.25);
    if (u <= 0) return;
    const e = ease.outExpo(u);
    const x = lerp(O.x, o.x, e) + 7 * Math.sin(t * 0.9 + o.ph);
    const y = lerp(O.y, o.y, e) + 9 * Math.sin(t * 1.15 + o.ph * 1.7);
    const rot = o.rot + (1 - e) * 2.4 + 0.12 * Math.sin(t * 0.7 + o.ph);
    const s = lerp(0.2, 1, e);
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rot);
    ctx.scale(s, s);
    ctx.globalAlpha = clamp(u * 4) * 0.9;
    ctx.strokeStyle = o.col;
    ctx.fillStyle = o.col;
    ctx.lineCap = 'round';
    if (o.kind === 'dot') { ctx.beginPath(); ctx.arc(0, 0, o.size * 0.15, 0, Math.PI * 2); ctx.fill(); }
    else if (o.kind === 'bar') { ctx.lineWidth = 13; ctx.beginPath(); ctx.moveTo(-o.size * 0.4, 0); ctx.lineTo(o.size * 0.4, 0); ctx.stroke(); }
    else if (o.kind === 'ring') { ctx.lineWidth = 9; ctx.beginPath(); ctx.arc(0, 0, o.size * 0.26, 0, Math.PI * 2); ctx.stroke(); }
    else renderGlyph(JAMO[o.j], boxAt(0, 0, o.size), o.size * 0.12, { color: o.col, alpha: ctx.globalAlpha });
    ctx.restore();
  });
}

function drawSeal(x, y, size, t) {
  const u = P(t, 26.25, 0.2);
  if (u <= 0) return;
  const s = lerp(1.7, 1, ease.inQ(u)), a = clamp(u * 2.5);
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(-0.08);
  ctx.scale(s, s);
  ctx.globalAlpha = a * 0.93;
  ctx.fillStyle = COL.redInk;
  const r = 12, h = size / 2;
  ctx.beginPath();
  ctx.moveTo(-h + r, -h);
  ctx.arcTo(h, -h, h, h, r);
  ctx.arcTo(h, h, -h, h, r);
  ctx.arcTo(-h, h, -h, -h, r);
  ctx.arcTo(-h, -h, h, -h, r);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = COL.paper;
  ctx.font = `900 ${size * 0.4}px ${SERIF}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('한', 0, -size * 0.2);
  ctx.fillText('글', 0, size * 0.22);
  ctx.restore();
}

function sceneTitle(t) {
  if (t < 24.95) return;
  // 도장 찍힐 때의 작은 흔들림
  const sh = P(t, 26.25, 0.35);
  const shake = sh > 0 && sh < 1 ? 6 * (1 - sh) * Math.sin(sh * 38) : 0;
  const push = 1 + 0.025 * E(t, 25.0, 5.0, ease.outQ);
  ctx.save();
  ctx.translate(CX, CY + shake);
  ctx.scale(push, push);
  ctx.translate(-CX, -CY);
  drawConfetti(t);

  // 한글날 — 오프스크린에 그려 빛 줄기를 글자 모양 안에만 입힌다
  const g = titleCtx;
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.clearRect(0, 0, W, H);
  g.setTransform(ctx.getTransform());
  const title = withCtx(g, () => drawText('한글날', CX, 612, { family: SERIF, weight: 900, size: 250, color: COL.ink, spacing: 14 }, i => {
    const u = P(t, 25.12 + i * 0.12, 0.7), e = ease.outC(u);
    return { a: ease.outQ(u), s: lerp(1.35, 1, e), blur: (1 - e) * 18, dy: (1 - e) * 10 };
  }));
  const sw = P(t, 28.0, 0.95);
  if (sw > 0 && sw < 1) {
    g.save();
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.globalCompositeOperation = 'source-atop';
    const x = lerp(CX - 760, CX + 760, ease.inOutQ(sw));
    const gr = g.createLinearGradient(x - 170, 0, x + 170, 0);
    gr.addColorStop(0, 'rgba(232,170,60,0)');
    gr.addColorStop(0.5, 'rgba(240,180,70,0.75)');
    gr.addColorStop(1, 'rgba(232,170,60,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, W, H);
    g.restore();
  }
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.drawImage(titleLayer, 0, 0);
  ctx.restore();

  drawText('제580돌', CX, 330, { size: 54, weight: 700, color: COL.redInk, spacing: 6 }, rise(t, 25.55, 0.06, 0.55, 16, 8));
  drawSeal(CX + title.total / 2 + 92, 452, 112, t);

  // 날짜와 양옆 가는 선
  const dl = E(t, 26.6, 0.6, ease.outC);
  const dt = drawText('2026. 10. 9.', CX, 722, { size: 46, weight: 500, color: COL.ink, alpha: 0.88, spacing: 6 }, rise(t, 26.55, 0.03, 0.5, 14, 8));
  if (dl > 0) {
    ctx.save();
    ctx.strokeStyle = rgba(COL.ink, 0.45);
    ctx.lineWidth = 2;
    const hx = dt.total / 2 + 30;
    ctx.beginPath();
    ctx.moveTo(CX - hx, 706); ctx.lineTo(CX - hx - 110 * dl, 706);
    ctx.moveTo(CX + hx, 706); ctx.lineTo(CX + hx + 110 * dl, 706);
    ctx.stroke();
    ctx.restore();
  }
  drawText('백성을 위한 글자에서, 세계가 배우는 글자로', CX, 845, { family: SERIF, weight: 700, size: 42, color: COL.ink, alpha: 0.86, spacing: 2 }, rise(t, 27.05, 0.028, 0.55, 14, 8));
  ctx.restore();
}

// ---------------------------------------------------------------- 마무리
function overlays(t) {
  const night = 1 - E(t, DAWN.t, 0.9, ease.inOutQ);
  const vignette = (rgb, a) => {
    if (a <= 0) return;
    const g = ctx.createRadialGradient(CX, CY, 420, CX, CY, 1180);
    g.addColorStop(0, `rgba(${rgb},0)`);
    g.addColorStop(1, `rgba(${rgb},${a})`);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  };
  vignette('0,0,0', 0.5 * night);
  vignette('70,45,18', 0.2 * (1 - night));
  const black = Math.max(1 - P(t, 0, 0.55), P(t, 29.55, 0.45));
  if (black > 0) { ctx.fillStyle = `rgba(0,0,0,${black})`; ctx.fillRect(0, 0, W, H); }
}

function draw(t) {
  ctx = mainCtx;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  ctx.filter = 'none';
  background(t);
  sceneHeavenEarthHuman(t);
  sceneVowels(t);
  sceneConsonants(t);
  sceneLogo(t);
  sceneWall(t);
  sceneQuote(t);
  sceneTitle(t);
  captions(t);
  overlays(t);
}

// ---------------------------------------------------------------- 진입점
window.ready = (async () => {
  await Promise.all([...document.fonts].map(f => f.load()));
  await document.fonts.ready;
  paper = makePaper();
  wallLayer = document.createElement('canvas');
  wallLayer.width = W; wallLayer.height = H;
  wallCtx = wallLayer.getContext('2d');
  titleLayer = document.createElement('canvas');
  titleLayer.width = W; titleLayer.height = H;
  titleCtx = titleLayer.getContext('2d');
  return true;
})();

window.DURATION = DURATION;
window.renderFrame = t => { draw(t); return cv.toDataURL('image/png'); };
window.drawFrame = t => { draw(t); return true; };

// 브라우저 미리보기: index.html?play 또는 index.html#12.5
window.ready.then(() => {
  const q = location.search;
  if (q.includes('play')) {
    const start = performance.now();
    const loop = now => { draw(((now - start) / 1000) % DURATION); requestAnimationFrame(loop); };
    requestAnimationFrame(loop);
  } else if (location.hash) {
    draw(parseFloat(location.hash.slice(1)) || 0);
  }
});
