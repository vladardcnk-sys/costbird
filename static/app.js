/* ===== CANVAS BACKGROUND ===== */
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let W, H, pts = [];

function resize() {
  W = canvas.width = innerWidth;
  H = canvas.height = innerHeight;
  pts = [];
  const n = Math.floor(W * H / 18000);
  for (let i = 0; i < n; i++)
    pts.push({ x: Math.random()*W, y: Math.random()*H, vx: (Math.random()-.5)*.2, vy: (Math.random()-.5)*.2 });
}

function drawCanvas() {
  ctx.clearRect(0, 0, W, H);
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i];
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0 || p.x > W) p.vx *= -1;
    if (p.y < 0 || p.y > H) p.vy *= -1;
    ctx.beginPath(); ctx.arc(p.x, p.y, 1.5, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(124,58,237,.5)'; ctx.fill();
    for (let j = i+1; j < pts.length; j++) {
      const q = pts[j], d = Math.hypot(p.x-q.x, p.y-q.y);
      if (d < 120) {
        ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
        ctx.strokeStyle = `rgba(124,58,237,${.15*(1-d/120)})`; ctx.lineWidth=.5; ctx.stroke();
      }
    }
  }
  requestAnimationFrame(drawCanvas);
}

window.addEventListener('resize', resize);
resize(); drawCanvas();

/* ===== SCROLL REVEAL ===== */
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: .12 });
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));

/* ===== COUNTER ANIMATION ===== */
function countUp(el, target) {
  let v = 0, step = target / 50;
  const iv = setInterval(() => {
    v += step;
    if (v >= target) { el.textContent = target; clearInterval(iv); }
    else el.textContent = Math.floor(v);
  }, 20);
}
const cObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('[data-count]').forEach(el =>
        countUp(el, +el.dataset.count));
      cObs.unobserve(e.target);
    }
  });
}, { threshold: .4 });
document.querySelectorAll('.stats-row').forEach(el => cObs.observe(el));

/* ===== MARQUEE ===== */
const chips = [
  { color:'#005bff', label:'Ozon · комиссии' },
  { color:'#a020f0', label:'Wildberries · логистика' },
  { color:'#fc3f1d', label:'Яндекс Маркет · хранение' },
  { color:'#10b981', label:'Единый API' },
  { color:'#7c3aed', label:'CostBird · расходы' },
  { color:'#f59e0b', label:'REST API · JSON' },
];
const mk = document.getElementById('marquee');
if (mk) {
  [...chips, ...chips].forEach(c => {
    const d = document.createElement('div'); d.className = 'mp-chip';
    d.innerHTML = `<div class="mp-dot" style="background:${c.color}"></div>${c.label}`;
    mk.appendChild(d);
  });
}
