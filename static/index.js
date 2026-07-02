/* ===== CANVAS BACKGROUND ===== */
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let W, H, pts = [];
function resize() {
  W = canvas.width = innerWidth; H = canvas.height = innerHeight;
  pts = []; const n = Math.floor(W * H / 18000);
  for (let i = 0; i < n; i++)
    pts.push({ x: Math.random()*W, y: Math.random()*H, vx: (Math.random()-.5)*.2, vy: (Math.random()-.5)*.2 });
}
function drawCanvas() {
  ctx.clearRect(0, 0, W, H);
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i]; p.x += p.vx; p.y += p.vy;
    if (p.x < 0 || p.x > W) p.vx *= -1; if (p.y < 0 || p.y > H) p.vy *= -1;
    ctx.beginPath(); ctx.arc(p.x, p.y, 1.5, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(124,58,237,.5)'; ctx.fill();
    for (let j = i+1; j < pts.length; j++) {
      const q = pts[j], d = Math.hypot(p.x-q.x, p.y-q.y);
      if (d < 120) { ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y);
        ctx.strokeStyle=`rgba(124,58,237,${.15*(1-d/120)})`; ctx.lineWidth=.5; ctx.stroke(); }
    }
  }
  requestAnimationFrame(drawCanvas);
}
window.addEventListener('resize', resize); resize(); drawCanvas();

/* ===== REVEAL ===== */
const obs = new IntersectionObserver(e => e.forEach(x => { if (x.isIntersecting) x.target.classList.add('visible'); }), {threshold:.12});
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));

/* ===== COUNTER ===== */
function countUp(el, target) {
  let v=0, step=target/60;
  const iv=setInterval(()=>{ v+=step; if(v>=target){el.textContent=target;clearInterval(iv);}else el.textContent=Math.floor(v); },16);
}
const cObs = new IntersectionObserver(e => {
  e.forEach(x => { if(x.isIntersecting){ x.target.querySelectorAll('[data-count]').forEach(el=>countUp(el,+el.dataset.count)); cObs.unobserve(x.target); }});
},{threshold:.4});
document.querySelectorAll('.hero-trust,.stats-row').forEach(el=>cObs.observe(el));

/* ===== MARQUEE ===== */
const chips=[
  {color:'#005bff',label:'Ozon · комиссии'},{color:'#a020f0',label:'Wildberries · логистика'},
  {color:'#fc3f1d',label:'Яндекс Маркет · хранение'},{color:'#10b981',label:'Единый дашборд'},
  {color:'#7c3aed',label:'CostBird · расходы'},{color:'#f59e0b',label:'Уведомления о штрафах'},
];
const mk=document.getElementById('marquee');
if(mk){[...chips,...chips].forEach(c=>{const d=document.createElement('div');d.className='mp-chip';d.innerHTML=`<div class="mp-dot" style="background:${c.color}"></div>${c.label}`;mk.appendChild(d);})}

/* ===== DASHBOARD DATA ===== */
const mpData = {
  wb:{color:'#a020f0',total:'74 071 ₽',rev:'312 400 ₽',pct:'23.7%',delta:'↑ 12%',alert:'Штрафы выросли на 40% — проверьте упаковку',
    rows:[{l:'Комиссия',v:48320,max:50000,c:'#7c3aed'},{l:'Логистика',v:12840,max:50000,c:'#9f67f7'},
          {l:'Хранение',v:8200,max:50000,c:'#c4b5fd'},{l:'Штрафы',v:3210,max:50000,c:'#ef4444'},{l:'Реклама',v:1500,max:50000,c:'#f59e0b'}]},
  ozon:{color:'#005bff',total:'68 600 ₽',rev:'290 000 ₽',pct:'23.7%',delta:'↑ 5%',alert:'Расходы на хранение выросли — пересмотрите поставки',
    rows:[{l:'Комиссия',v:39800,max:50000,c:'#005bff'},{l:'Логистика',v:15600,max:50000,c:'#3b82f6'},
          {l:'Хранение',v:8100,max:50000,c:'#93c5fd'},{l:'Штрафы',v:3200,max:50000,c:'#ef4444'},{l:'Реклама',v:1900,max:50000,c:'#f59e0b'}]},
  ym:{color:'#fc3f1d',total:'47 800 ₽',rev:'198 000 ₽',pct:'24.1%',delta:'↓ 3%',alert:'Всё в норме. Расходы снизились на 3%',
    rows:[{l:'Комиссия',v:29400,max:50000,c:'#fc3f1d'},{l:'Логистика',v:8900,max:50000,c:'#f97316'},
          {l:'Хранение',v:5900,max:50000,c:'#fdba74'},{l:'Штрафы',v:1800,max:50000,c:'#ef4444'},{l:'Реклама',v:1800,max:50000,c:'#f59e0b'}]},
};

function drawDonut(rows, color) {
  const c=document.getElementById('donut-canvas'); if(!c)return;
  const cx=c.getContext('2d'), s=55, cx2=55, cy2=55;
  const total=rows.reduce((a,r)=>a+r.v,0);
  let angle=-Math.PI/2;
  rows.forEach(r=>{
    const slice=(r.v/total)*Math.PI*2;
    cx.beginPath(); cx.moveTo(cx2,cy2);
    cx.arc(cx2,cy2,s,angle,angle+slice);
    cx.closePath(); cx.fillStyle=r.c; cx.fill();
    angle+=slice;
  });
  cx.beginPath(); cx.arc(cx2,cy2,34,0,Math.PI*2);
  cx.fillStyle='#0f1629'; cx.fill();
  cx.fillStyle='#e8eeff'; cx.font='bold 13px Syne,sans-serif'; cx.textAlign='center';
  cx.fillText(Math.round(rows[0].v/total*100)+'%', cx2, cy2+5);
}

function updateDash(key) {
  const d=mpData[key];
  document.getElementById('kpi-total').textContent=d.total;
  document.getElementById('kpi-rev').textContent=d.rev;
  document.getElementById('kpi-pct').textContent=d.pct;
  document.getElementById('alert-text').textContent=d.alert;
  const bars=document.getElementById('dash-bars');
  if(bars){bars.innerHTML=d.rows.map(r=>`
    <div class="db-row">
      <div class="db-label">${r.l}</div>
      <div class="db-track"><div class="db-fill" style="width:0%;background:${r.c}" data-w="${Math.round(r.v/r.max*100)}"></div></div>
      <div class="db-val">${r.v.toLocaleString('ru-RU')} ₽</div>
    </div>`).join('');
    setTimeout(()=>bars.querySelectorAll('.db-fill').forEach(b=>b.style.width=b.dataset.w+'%'),50);
  }
  drawDonut(d.rows, d.color);
}

document.querySelectorAll('.dash-tab').forEach(tab=>{
  tab.addEventListener('click',()=>{
    document.querySelectorAll('.dash-tab').forEach(t=>t.classList.remove('active'));
    tab.classList.add('active'); updateDash(tab.dataset.mp);
  });
});
updateDash('wb');

/* ===== LIVE DEMO ===== */
const demoData = {
  wb:{rows:[{label:'💰 Комиссия за продажи',val:48320,max:60000,c:'#7c3aed'},{label:'🚚 Логистика',val:12840,max:60000,c:'#9f67f7'},{label:'📦 Хранение',val:8200,max:60000,c:'#c4b5fd'},{label:'⚠️ Штрафы',val:3210,max:60000,c:'#ef4444'},{label:'📢 Реклама',val:1500,max:60000,c:'#f59e0b'}],total:74071},
  ozon:{rows:[{label:'💰 Комиссия за продажи',val:39800,max:60000,c:'#005bff'},{label:'🚚 Логистика',val:15600,max:60000,c:'#3b82f6'},{label:'📦 Хранение',val:8100,max:60000,c:'#93c5fd'},{label:'⚠️ Штрафы',val:3200,max:60000,c:'#ef4444'},{label:'📢 Реклама',val:1900,max:60000,c:'#f59e0b'}],total:68600},
  ym:{rows:[{label:'💰 Комиссия за продажи',val:29400,max:60000,c:'#fc3f1d'},{label:'🚚 Логистика',val:8900,max:60000,c:'#f97316'},{label:'📦 Хранение',val:5900,max:60000,c:'#fdba74'},{label:'⚠️ Штрафы',val:1800,max:60000,c:'#ef4444'},{label:'📢 Реклама',val:1800,max:60000,c:'#f59e0b'}],total:47800},
};
function fmt(n){return n.toLocaleString('ru-RU')+' ₽'}
function renderDemo(key){
  const d=demoData[key];
  const panel=document.getElementById('expense-panel'); if(!panel)return;
  panel.innerHTML=`<div class="expense-rows">`+
    d.rows.map(r=>`<div class="expense-row"><div><div class="exp-label">${r.label}</div>
      <div class="exp-bar-wrap"><div class="exp-bar" style="background:${r.c}" data-w="${Math.round(r.val/r.max*100)}"></div></div></div>
      <div class="exp-val">${fmt(r.val)}</div></div>`).join('')+
    `<div class="total-row"><span class="total-label">Итого за июнь 2024</span><span class="total-val">${fmt(d.total)}</span></div></div>`;
  setTimeout(()=>panel.querySelectorAll('.exp-bar').forEach(b=>b.style.width=b.dataset.w+'%'),60);
}
document.querySelectorAll('.mp-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.mp-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active'); renderDemo(btn.dataset.mp);
  });
});
renderDemo('wb');

/* ===== SUBSCRIBE ===== */
const subBtn=document.getElementById('sub-btn');
if(subBtn)subBtn.addEventListener('click',()=>{
  const inp=document.getElementById('email-in');
  if(!inp.value.includes('@')){inp.style.borderColor='var(--red)';return;}
  subBtn.textContent='В очереди ✓'; subBtn.style.background='#10b981'; subBtn.style.pointerEvents='none'; inp.disabled=true;
});
