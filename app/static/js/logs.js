/* 系统日志页：搜索 / 筛选 / 分页 / 导出。原生 JS，无框架。 */
(function () {
  'use strict';
  const PAGE_SIZE = 10;
  const state = { page: 1, total: 0, pages: 1 };

  function statusPill(s) {
    const cls = s === 'failed' ? 'failed' : s === 'error' ? 'error' : 'success';
    const txt = s === 'failed' ? '失败' : s === 'error' ? '错误' : '成功';
    return '<span class="pill-status ' + cls + '"><i class="ri-' + (cls === 'success' ? 'checkbox-circle-line' : 'close-circle-line') + '"></i>' + txt + '</span>';
  }

  function readStatus() {
    const s = document.querySelector('#statusWrap .dropdown-item.selected');
    return s ? s.getAttribute('data-value') : 'ALL';
  }

  function parseDuration(detail) {
    const m = /\((\d+)ms\)/.exec(detail || '');
    return m ? m[1] : '';
  }

  function render(rows) {
    const body = document.getElementById('logBody');
    if (!rows || !rows.length) {
      body.innerHTML = '<tr><td colspan="8" class="log-empty"><i class="ri-file-list-3-line"></i>暂无日志</td></tr>';
      return;
    }
    body.innerHTML = rows.map(function (r) {
      var d = r.detail || '';
      return '<tr>' +
        '<td class="td-mono">' + r.id + '</td>' +
        '<td>' + (r.user_id || '—') + '</td>' +
        '<td><span class="badge badge-pill b-info">' + escapeHtml(r.action) + '</span></td>' +
        '<td style="color:var(--text-secondary);max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + escapeHtml(d) + '</td>' +
        '<td>' + statusPill(r.status || 'success') + '</td>' +
        '<td class="num td-mono">' + parseDuration(d) + '</td>' +
        '<td class="td-mono">' + escapeHtml(r.ip || '—') + '</td>' +
        '<td class="num td-mono">' + (r.created_at || '—') + '</td>' +
        '</tr>';
    }).join('');
  }

  function escapeHtml(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function buildQuery() {
    const p = new URLSearchParams();
    p.set('page', state.page);
    p.set('page_size', PAGE_SIZE);
    const kw = document.getElementById('logSearch').value.trim();
    if (kw) p.set('keyword', kw);
    const status = readStatus();
    if (status && status !== 'ALL') p.set('status', status);
    const uid = document.getElementById('userFilter').value.trim();
    if (uid) p.set('user_id', uid);
    const s = document.getElementById('startDate').value;
    if (s) p.set('start_date', s);
    const e = document.getElementById('endDate').value;
    if (e) p.set('end_date', e);
    return p;
  }

  function loadStats() {
    fetch('/api/logs/statistics?days=7')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        const ok = document.getElementById('stTotal');
        if (ok) {
          const actions = (d.action_statistics || []).reduce(function (a, x) { return a + x.count; }, 0);
          ok.setAttribute('data-total', actions);
          ok.textContent = actions;
        }
      }).catch(function () {});
  }

  function fetchLogs() {
    const body = document.getElementById('logBody');
    body.innerHTML = '<tr><td colspan="8" class="log-empty"><i class="ri-loader-4-line"></i>加载中…</td></tr>';
    fetch('/api/logs/operations?' + buildQuery().toString())
      .then(function (r) { return r.json(); })
      .then(function (d) {
        state.total = d.total || 0;
        state.pages = Math.max(1, Math.ceil(state.total / PAGE_SIZE));
        if (state.page > state.pages) { state.page = state.pages; return fetchLogs(); }
        render(d.data || []);
        updatePager();
      })
      .catch(function () {
        body.innerHTML = '<tr><td colspan="8" class="log-empty"><i class="ri-error-warning-line"></i>加载失败，请检查是否已登录管理员账号</td></tr>';
      });
  }

  function updatePager() {
    document.getElementById('pageInfo').textContent = state.page + ' / ' + state.pages;
    document.getElementById('prevBtn').disabled = state.page <= 1;
    document.getElementById('nextBtn').disabled = state.page >= state.pages;
  }

  window.searchLogs = function () { state.page = 1; fetchLogs(); };
  window.page = function (d) { state.page += d; fetchLogs(); };
  window.exportCsv = function () {
    let url = '/api/logs/operations?' + buildQuery().toString();
    fetch(url).then(r => r.json()).then(d => {
      const rows = d.data || [];
      const head = ['ID', '用户', '操作', '详情', '状态', 'IP', '时间'];
      const lines = [head.join(',')];
      rows.forEach(function (r) {
        lines.push([r.id, r.user_id || '', (r.action||'').replace(/,/g, '，'),
          (r.detail||'').replace(/,/g, '，').replace(/\n/g, ' '),
          r.status || '', r.ip || '', r.created_at || ''].join(','));
      });
      const blob = new Blob(["\ufeff" + lines.join('\n')], { type: 'text/csv;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'operation_logs.csv';
      a.click();
    });
  };

  // 初始化
  const wrap = document.getElementById('statusWrap');
  if (wrap) wrap.addEventListener('dropdown-change', function () { state.page = 1; fetchLogs(); });
  loadStats();
  fetchLogs();
})();