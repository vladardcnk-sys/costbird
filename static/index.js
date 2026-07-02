/* ===== CODE TYPING EFFECT ===== */
const codes = {
  expenses: `{
  <span class="t-k">"seller_id"</span>: <span class="t-s">"wb_a1b2c3"</span>,
  <span class="t-k">"marketplace"</span>: <span class="t-s">"wildberries"</span>,
  <span class="t-k">"period"</span>: <span class="t-s">"2024-06"</span>,
  <span class="t-k">"expenses"</span>: {
    <span class="t-k">"commission"</span>: <span class="t-n">48320.50</span>,
    <span class="t-k">"logistics"</span>:  <span class="t-n">12840.00</span>,
    <span class="t-k">"storage"</span>:    <span class="t-n">3210.75</span>,
    <span class="t-k">"fines"</span>:      <span class="t-n">1500.00</span>,
    <span class="t-k">"ads"</span>:        <span class="t-n">8200.00</span>,
    <span class="t-k">"total"</span>:      <span class="t-n">74071.25</span>
  }
}`,
  summary: `{
  <span class="t-k">"period"</span>: <span class="t-s">"2024-06"</span>,
  <span class="t-k">"total_expenses"</span>: <span class="t-n">142830.40</span>,
  <span class="t-k">"by_marketplace"</span>: {
    <span class="t-k">"wildberries"</span>: <span class="t-n">74071.25</span>,
    <span class="t-k">"ozon"</span>:        <span class="t-n">68759.15</span>
  },
  <span class="t-k">"vs_prev_month"</span>: <span class="t-p">"+12.4%"</span>
}`,
  breakdown: `{
  <span class="t-k">"total_skus"</span>: <span class="t-n">48</span>,
  <span class="t-k">"items"</span>: [{
    <span class="t-k">"sku"</span>:       <span class="t-s">"SKU-001"</span>,
    <span class="t-k">"name"</span>:      <span class="t-s">"Футболка XL"</span>,
    <span class="t-k">"units_sold"</span>: <span class="t-n">142</span>,
    <span class="t-k">"commission"</span>: <span class="t-n">8420.30</span>,
    <span class="t-k">"profit"</span>:     <span class="t-n">31240.50</span>
  }]
}`
};

function typeCode(html) {
  const el = document.getElementById('code-out');
  if (!el) return;
  const plain = html.replace(/<[^>]+>/g, '');
  let i = 0;
  const iv = setInterval(() => {
    i += 4;
    let count = 0, pos = 0;
    while (pos < html.length && count < i) {
      if (html[pos] === '<') { while (pos < html.length && html[pos] !== '>') pos++; }
      else count++;
      pos++;
    }
    el.innerHTML = html.substring(0, pos) + '<span class="cursor"></span>';
    if (i >= plain.length) { clearInterval(iv); el.innerHTML = html; }
  }, 18);
}

document.querySelectorAll('.ctab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.ctab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    typeCode(codes[tab.dataset.tab]);
  });
});

typeCode(codes.expenses);

/* ===== LIVE DEMO ===== */
const mpData = {
  wb: {
    color: '#a020f0',
    rows: [
      { label: 'Комиссия за продажу', val: 48320, max: 60000 },
      { label: 'Логистика (FBO)',      val: 12840, max: 60000 },
      { label: 'Хранение на складе',   val:  3210, max: 60000 },
      { label: 'Штрафы',               val:  1500, max: 60000 },
      { label: 'Реклама',              val:  8200, max: 60000 },
    ],
    total: 74070
  },
  ozon: {
    color: '#005bff',
    rows: [
      { label: 'Комиссия за продажу', val: 39800, max: 60000 },
      { label: 'Логистика (FBO)',      val: 15600, max: 60000 },
      { label: 'Хранение',             val:  4100, max: 60000 },
      { label: 'Обработка заказа',     val:  2300, max: 60000 },
      { label: 'Реклама',              val: 11200, max: 60000 },
    ],
    total: 73000
  },
  ym: {
    color: '#fc3f1d',
    rows: [
      { label: 'Комиссия за продажу', val: 29400, max: 60000 },
      { label: 'Логистика (FBY)',      val:  8900, max: 60000 },
      { label: 'Хранение',             val:  2100, max: 60000 },
      { label: 'Обработка',            val:  1800, max: 60000 },
      { label: 'Размещение',           val:  5600, max: 60000 },
    ],
    total: 47800
  }
};

function fmt(n) { return n.toLocaleString('ru-RU') + ' ₽'; }

function renderDemo(key) {
  const d = mpData[key];
  const panel = document.getElementById('expense-panel');
  if (!panel) return;
  panel.innerHTML = `<div class="expense-rows">` +
    d.rows.map(r => `
      <div class="expense-row">
        <div>
          <div class="exp-label">${r.label}</div>
          <div class="exp-bar-wrap">
            <div class="exp-bar" style="background:${d.color}" data-w="${Math.round(r.val/r.max*100)}"></div>
          </div>
        </div>
        <div class="exp-val">${fmt(r.val)}</div>
      </div>`).join('') +
    `<div class="total-row">
      <span class="total-label">Итого за период</span>
      <span class="total-val">${fmt(d.total)}</span>
    </div></div>`;
  setTimeout(() => {
    panel.querySelectorAll('.exp-bar').forEach(b => { b.style.width = b.dataset.w + '%'; });
  }, 60);
}

document.querySelectorAll('.mp-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.mp-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderDemo(btn.dataset.mp);
  });
});

renderDemo('wb');

/* ===== SUBSCRIBE ===== */
const subBtn = document.getElementById('sub-btn');
if (subBtn) {
  subBtn.addEventListener('click', () => {
    const inp = document.getElementById('email-in');
    if (!inp.value.includes('@')) {
      inp.style.borderColor = 'var(--red)'; return;
    }
    subBtn.textContent = 'В очереди ✓';
    subBtn.style.background = '#10b981';
    subBtn.style.pointerEvents = 'none';
    inp.disabled = true;
  });
}
