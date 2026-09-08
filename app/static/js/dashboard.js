/* ============================================================
   dashboard.js —— 学情看板交互逻辑 + ECharts 图表
   依赖：ECharts 5 (全局 echarts)，base.html 的 toast()
   ============================================================ */
(function () {
  'use strict';

  if (typeof echarts === 'undefined') {
    if (window.console) console.error('[dashboard] echarts 未加载');
    return;
  }

  // ---- 图表配色（与 spec 第九节一致） ----
  var BLUE = '#5B7FFF', PURPLE = '#8B5CF6', GREEN = '#10B981',
      YELLOW = '#F59E0B', RED = '#EF4444', CYAN = '#06B6D4';
  var MUTED = '#667788', FAINT = '#99AAB5', BORDER = '#E8ECF0';

  function areaGradient(color, opacity0, opacity1) {
    return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      { offset: 0, color: 'rgba(' + color.join(',') + ',' + opacity0 + ')' },
      { offset: 1, color: 'rgba(' + color.join(',') + ',' + opacity1 + ')' }
    ]);
  }
  function rgba(color, a) {
    return 'rgba(' + color.join(',') + ',' + a + ')';
  }

  // ---- DOM 引用 ----
  var $ = function (id) { return document.getElementById(id); };
  var courseWrap = $('courseSelect');
  var timeWrap = $('timeRange');
  var refreshBtn = $('refreshBtn');
  var exportBtn = $('exportBtn');
  var trendTabs = document.querySelectorAll('#trendTabs .chart-tab');
  var activitySearch = $('activitySearch');
  var typeWrap = $('typeFilter');

  // 当前选中值（由 dropdown 组件更新）
  var sel = { course: null, range: 30, type: 'all', pageSize: 20 };

  // 选中项取值辅助：从面板 selected 项读取
  function selectedValue(wrap, fallback) {
    var el = wrap && wrap.querySelector('.dropdown-item.selected');
    return el ? el.getAttribute('data-value') : fallback;
  }

  // ---- 当前请求状态 ----
  var seq = 0;
  var cached = null;            // 最近一次接口返回
  var trendDays = null;         // 学习趋势内部分档覆盖
  var activityAll = [];
  var page = 1, pageSize = 20, filterKw = '', filterType = 'all';

  var charts = {
    trend: $('trendChart'),
    completion: $('completionChart'),
    kb: $('kbChart')
  };
  var instances = {};

  // 初始化图表实例（含 resize 自适应）
  Object.keys(charts).forEach(function (key) {
    instances[key] = echarts.init(charts[key]);
  });
  window.addEventListener('resize', function () {
    Object.keys(instances).forEach(function (k) { instances[k].resize(); });
  });

  // ---- 数字增长动画 ----
  function animateValue(el, target, decimals, duration) {
    duration = duration || 900;
    var start = 0;
    var t0 = performance.now();
    function frame(now) {
      var p = Math.min((now - t0) / duration, 1);
      var ease = 1 - Math.pow(1 - p, 4);
      var v = start + (target - start) * ease;
      el.textContent = decimals ? v.toFixed(decimals) : Math.round(v).toLocaleString();
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function renderMetrics(metrics) {
    ['total_students', 'submission_count', 'graded_count', 'chat_count', 'active_students'].forEach(function (mk) {
      var el = document.querySelector('.metric-value[data-metric="' + mk + '"]');
      if (el) animateValue(el, metrics[mk] || 0, 0);
    });
    var avg = document.querySelector('.metric-value[data-metric="avg_score"]');
    if (avg) animateValue(avg, metrics.avg_score != null ? metrics.avg_score : 0, 1);
  }

  // ---- 学习趋势折线图 ----
  function renderTrend(trend) {
    var option = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderColor: BORDER,
        borderWidth: 1,
        textStyle: { color: '#1A1A1A' },
        extraCssText: 'box-shadow:0 4px 12px rgba(0,0,0,0.08);border-radius:8px;'
      },
      legend: {
        data: ['作业提交', '答疑提问', '知识库访问'],
        bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8,
        textStyle: { color: MUTED }
      },
      grid: { left: '3%', right: '4%', bottom: '12%', top: '6%', containLabel: true },
      xAxis: {
        type: 'category', boundaryGap: false, data: trend.labels,
        axisLine: { lineStyle: { color: BORDER } },
        axisLabel: { color: FAINT }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#F0F2F5', type: 'dashed' } },
        axisLabel: { color: FAINT }
      },
      series: [
        { name: '作业提交', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
          itemStyle: { color: BLUE }, lineStyle: { color: BLUE, width: 2 },
          areaStyle: { color: areaGradient([91,127,255], 0.30, 0.05) },
          data: trend.submissions },
        { name: '答疑提问', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
          itemStyle: { color: PURPLE }, lineStyle: { color: PURPLE, width: 2 },
          areaStyle: { color: areaGradient([139,92,246], 0.30, 0.05) },
          data: trend.questions },
        { name: '知识库访问', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
          itemStyle: { color: GREEN }, lineStyle: { color: GREEN, width: 2 },
          areaStyle: { color: areaGradient([16,185,129], 0.30, 0.05) },
          data: trend.kb }
      ]
    };
    instances.trend.setOption(option, true);
  }

  // ---- 作业完成环形图 ----
  function renderCompletion(comp) {
    var expected = comp.expected || 1;
    var donePct = Math.round(comp.done / expected * 100);
    var pendingPct = Math.round(comp.pending / expected * 100);
    var overduePct = Math.max(100 - donePct - pendingPct, 0);
    var option = {
      tooltip: {
        trigger: 'item', formatter: '{b}: {c}%',
        backgroundColor: 'rgba(255,255,255,0.95)', borderColor: BORDER, textStyle: { color: '#1A1A1A' }
      },
      series: [{
        name: '作业完成情况', type: 'pie', radius: ['50%', '70%'],
        avoidLabelOverlap: false, padAngle: 3,
        itemStyle: { borderRadius: 8, borderColor: '#FFFFFF', borderWidth: 2 },
        label: { show: false },
        data: [
          { value: donePct, name: '已完成', itemStyle: { color: GREEN } },
          { value: pendingPct, name: '待提交', itemStyle: { color: YELLOW } },
          { value: overduePct, name: '已逾期', itemStyle: { color: RED } }
        ]
      }],
      graphic: [
        { type: 'text', left: 'center', top: 'center', style: { text: donePct + '%', fontSize: 26, fontWeight: 700, fill: '#1A1A1A' } },
        { type: 'text', left: 'center', top: '54%', style: { text: '已完成', fontSize: 12, fill: MUTED } }
      ]
    };
    instances.completion.setOption(option, true);
  }

  // ---- 知识库使用柱状图 ----
  function renderKb(kb) {
    var option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(255,255,255,0.95)', borderColor: BORDER, textStyle: { color: '#1A1A1A' } },
      grid: { left: '3%', right: '4%', bottom: '5%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category', data: ['文档上传', '知识片段', '提问引用', '作业批改'],
        axisLabel: { color: FAINT, interval: 0 },
        axisLine: { lineStyle: { color: BORDER } }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#F0F2F5', type: 'dashed' } },
        axisLabel: { color: FAINT }
      },
      series: [{
        name: '使用次数', type: 'bar', barWidth: '40%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: BLUE }, { offset: 1, color: PURPLE }
          ]),
          borderRadius: [8, 8, 0, 0]
        },
        label: { show: true, position: 'top', color: MUTED, fontSize: 12 },
        data: [
          { value: kb.docs, name: '文档上传' },
          { value: kb.chunks, name: '知识片段' },
          { value: kb.references, name: '提问引用' },
          { value: kb.gradings, name: '作业批改' }
        ]
      }]
    };
    instances.kb.setOption(option, true);
  }

  // ---- 热门问题列表 ----
  function renderHot(list) {
    var box = $('hotList');
    if (!list.length) {
      box.innerHTML = '<div class="empty-table"><i class="ri-question-line"></i>暂无提问数据</div>';
      return;
    }
    box.innerHTML = list.map(function (q, i) {
      var rankCls = 'rank-' + (i + 1 <= 3 ? i + 1 : '');
      return '<div class="question-item fade-in">' +
        '<div class="question-rank ' + rankCls + '">' + (i + 1) + '</div>' +
        '<div class="question-content">' +
          '<div class="question-text">' + esc(q.text) + '</div>' +
          '<div class="question-meta">' +
            '<span><i class="ri-message-3-line"></i>' + q.count + ' 次提问</span>' +
          '</div>' +
        '</div>' +
        '<div class="question-trend"><i class="ri-fire-line"></i>热</div>' +
      '</div>';
    }).join('');
  }

  // ---- 最近学习动态：搜索 + 类型筛选 + 分页 ----
  function filtered() {
    var kw = filterKw.toLowerCase();
    return activityAll.filter(function (a) {
      if (filterType !== 'all' && a.type !== filterType) return false;
      if (kw && (a.student + a.content).toLowerCase().indexOf(kw) === -1) return false;
      return true;
    });
  }
  function renderTable() {
    var list = filtered();
    var total = list.length;
    var pages = Math.max(1, Math.ceil(total / pageSize));
    if (page > pages) page = pages;
    var start = (page - 1) * pageSize;
    var slice = list.slice(start, start + pageSize);
    var body = $('activityBody');
    if (!slice.length) {
      body.innerHTML = '<tr class="empty-table"><td colspan="7"><i class="ri-inbox-archive-line"></i>暂无学习动态</td></tr>';
    } else {
      body.innerHTML = slice.map(function (a) {
        var typeTxt = a.type;
        var typeCls = a.type === '作业提交' ? 'submission' : 'question';
        var statusCls = a.status;
        var statusTxt = a.status === 'pending' ? '待批改'
          : a.status === 'graded' ? '已批改'
          : a.status === 'answered' ? '已回答'
          : a.status;
        var score = a.score != null ? a.score : '—';
        var t = (a.ts || '').split(' ');
        return '<tr class="fade-in">' +
          '<td><div class="time-cell"><span class="time-clock">' + esc(t[1] || a.ts) + '</span><span class="time-date">' + esc(t[0] || '') + '</span></div></td>' +
          '<td><div class="student-cell"><span class="student-avatar">' + esc((a.student || '?').charAt(0)) + '</span><span>' + esc(a.student) + '</span></div></td>' +
          '<td class="td-mono">' + esc(a.student_no) + '</td>' +
          '<td><span class="type-badge ' + typeCls + '"><i class="' + (a.type === '作业提交' ? 'ri-file-list-3-line' : 'ri-message-3-line') + '"></i>' + esc(typeTxt) + '</span></td>' +
          '<td class="content-cell" title="' + esc(a.content) + '">' + esc(a.content) + '</td>' +
          '<td><span class="status-badge ' + statusCls + '"><i class="' + (a.status === 'answered' ? 'ri-check-line' : 'ri-checkbox-circle-line') + '"></i>' + esc(statusTxt) + '</span></td>' +
          '<td class="score-cell">' + esc(score) + '</td>' +
        '</tr>';
      }).join('');
    }
    $('pageInfo').textContent = '共 ' + total + ' 条记录';
    renderPagination(pages);
  }
  function renderPagination(pages) {
    var ctrl = $('pageControls');
    var btns = [];
    btns.push('<button class="page-btn" data-p="' + (page - 1) + '" ' + (page <= 1 ? 'disabled' : '') + '><i class="ri-arrow-left-s-line"></i></button>');
    var win = [];
    for (var i = 1; i <= pages; i++) {
      if (i === 1 || i === pages || Math.abs(i - page) <= 1) win.push(i);
    }
    var prev = 0;
    win.forEach(function (p2) {
      if (p2 - prev > 1) btns.push('<span class="page-ellipsis">…</span>');
      btns.push('<button class="page-btn ' + (p2 === page ? 'active' : '') + '" data-p="' + p2 + '">' + p2 + '</button>');
      prev = p2;
    });
    btns.push('<button class="page-btn" data-p="' + (page + 1) + '" ' + (page >= pages ? 'disabled' : '') + '><i class="ri-arrow-right-s-line"></i></button>');
    ctrl.innerHTML = btns.join('');
  }
  $('pageControls').addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-p]');
    if (!btn || btn.disabled) return;
    page = parseInt(btn.getAttribute('data-p'), 10);
    renderTable();
  });
  activitySearch.addEventListener('input', function () {
    clearTimeout(this._t);
    var self = this;
    this._t = setTimeout(function () {
      filterKw = self.value.trim();
      page = 1;
      renderTable();
    }, 250);
  });

  // ---- 统一下拉框事件桥接（适配 dropdown.js 组件） ----
  function bindDropdown(wrapId, handler) {
    var wrap = $(wrapId);
    if (!wrap) return;
    // 读取已选中值（初始 selected）
    var initVal = selectedValue(wrap, null);
    if (initVal != null) handler(initVal, 'init');
    wrap.addEventListener('dropdown-change', function (e) {
      handler(e.detail.value, e.detail.label);
    });
  }

  // ---- 加载数据 ----
  function currentRange() {
    // 优先级：内部趋势分档 > 全局时间范围下拉
    if (trendDays != null) return trendDays;
    if (sel.range === 'all') return 0;      // 全部 → API 约定 range=0
    var r = parseInt(sel.range, 10);
    return isNaN(r) ? sel.range : r;
  }
  async function load() {
    var id = ++seq;
    var courseId = sel.course != null ? String(sel.course) : '';
    if (!courseId) { showToast('请先选择课程', 'error'); return; }
    refreshBtn.classList.add('loading');
    try {
      var r = await fetch('/api/dashboard/overview?course_id=' + encodeURIComponent(courseId) +
        '&range=' + encodeURIComponent(currentRange()));
      if (!r.ok) throw new Error('HTTP ' + r.status);
      var data = await r.json();
      if (id !== seq) return; // 丢弃过期响应
      cached = data;
      renderMetrics(data.metrics);
      renderTrend(data.trend);
      renderCompletion(data.completion);
      renderKb(data.kb_usage);
      renderHot(data.hot_questions);
      activityAll = data.activities || [];
      page = 1;
      renderTable();
    } catch (err) {
      if (id === seq) showToast('数据加载失败：' + err.message, 'error');
    } finally {
      if (id === seq) refreshBtn.classList.remove('loading');
    }
  }

  function showToast(msg, type) {
    if (typeof toast === 'function') toast(msg, type);
    else if (window.console) console.log(msg);
  }

  // ---- 事件绑定 ----（下拉框通过 dropdown.js 自定义事件触发 load）
  refreshBtn.addEventListener('click', load);
  bindDropdown('courseSelect', function (v) { sel.course = v; load(); });
  bindDropdown('timeRange', function (v) {
    sel.range = v; // '7' | '30' | '90' | 'all'
    trendDays = null; // 跟随全局时间范围
    load();
  });
  bindDropdown('typeFilter', function (v) {
    filterType = v;
    page = 1;
    renderTable();
  });
  bindDropdown('pageSize', function (v) {
    pageSize = parseInt(v, 10);
    page = 1;
    renderTable();
  });
  trendTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      trendTabs.forEach(function (t) { t.classList.remove('active'); });
      this.classList.add('active');
      trendDays = parseInt(this.getAttribute('data-days'), 10);
      load();
    });
  });
  exportBtn.addEventListener('click', function () {
    var courseId = sel.course != null ? String(sel.course) : '';
    var url = '/api/dashboard/export?course_id=' + encodeURIComponent(courseId) +
      '&range=' + encodeURIComponent(currentRange());
    // 简化为当前页跳转下载
    var a = document.createElement('a');
    a.href = url;
    a.download = '学情报告.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  });

  // ---- 工具函数 ----
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ---- 首次加载 ----
  // 初始值：课程、时间等由 dropdown 组件的 selected 决定；这里同步一次 sel
  sel.course = selectedValue(courseWrap, null) || null;
  sel.range = selectedValue(timeWrap, '30') || '30';
  if (window.__dashboardInitial && window.__dashboardInitial.active_course) {
    sel.course = String(window.__dashboardInitial.active_course);
  }
  load();

  // 自动刷新（每 5 分钟）
  setInterval(function () {
    if (document.visibilityState === 'visible' && !refreshBtn.classList.contains('loading')) load();
  }, 5 * 60 * 1000);
})();