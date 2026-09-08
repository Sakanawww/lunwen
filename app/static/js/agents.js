/* Agent 服务商配置页：卡片网格、增删改、连接测试。原生 JS，无框架。 */
(function () {
  'use strict';
  var grid = document.getElementById('providerGrid');

  function iconFor(p) {
    return { deepseek: 'ri-chat-smile-line', qwen: 'ri-cloud-line', glm: 'ri-bug-line', custom: 'ri-terminal-box-line' }[p.provider] || 'ri-robot-2-line';
  }

  function quotaPct(p) {
    if (!p.quota_limit || p.quota_limit <= 0) return 0;
    return Math.min(100, p.quota_limit);
  }

  function card(p) {
    var el = document.createElement('div');
    el.className = 'provider-card';
    el.innerHTML =
      (p.is_default ? '<span class="default-badge"><i class="ri-star-fill"></i> 默认</span>' : '') +
      '<div class="card-top">' +
        '<div class="p-name"><i class="' + iconFor(p) + '"></i>' + esc(p.name) + '</div>' +
        '<span class="badge ' + (p.enabled ? 'b-on' : 'b-off') + '"><span class="dot"></span>' + (p.enabled ? '启用' : '停用') + '</span>' +
      '</div>' +
      '<div class="p-model">' + esc(p.model) + '</div>' +
      '<div class="p-url"><i class="ri-link"></i> ' + esc(p.base_url) + '</div>' +
      '<div class="p-key"><i class="ri-key-2-line"></i> ' + esc(p.key_masked || (p.has_key ? '****' : '未配置Key')) + '</div>' +
      '<div class="card-foot">' +
        (p.provider && p.provider !== 'custom'
          ? '<span class="pill" style="font-size:11px;padding:1px 8px;background:var(--bg-hover);color:var(--text-secondary);">' + p.provider + '</span>'
          : '<span class="pill" style="font-size:11px;padding:1px 8px;background:var(--bg-hover);color:var(--text-secondary);">兼容接口</span>') +
        '<span style="margin-left:auto;">' + (p.quota_limit ? '额度上限 ' + p.quota_limit : '') + '</span>' +
      '</div>' +
      (p.is_default
        ? ''
        : '<div class="p-actions">' +
            '<button class="btn btn-ghost" data-act="setdefault" data-id="' + p.id + '"><i class="ri-star-line"></i> 设默认</button>' +
          '</div>') +
      '<div class="p-actions">' +
        '<button class="btn btn-ghost" data-act="test" data-id="' + p.id + '"><i class="ri-wifi-line"></i> 测试连接</button>' +
        '<button class="btn btn-ghost" data-act="edit" data-id="' + p.id + '"><i class="ri-edit-2-line"></i> 编辑</button>' +
        (p.is_default ? '' : '<button class="btn btn-ghost" style="color:var(--danger);border-color:rgba(239,68,68,.4);" data-act="del" data-id="' + p.id + '"><i class="ri-delete-bin-line"></i></button>') +
      '</div>' +
      '<div class="test-msg" id="test-' + p.id + '"></div>';
    return el;
  }

  function esc(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function load() {
    grid.innerHTML = '<div class="empty-p"><i class="ri-loader-4-line"></i>加载中…</div>';
    fetch('/api/agents/providers')
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (list) {
        if (!list || !list.length) {
          grid.innerHTML = '<div class="empty-p" style="grid-column:1/-1;"><i class="ri-robot-2-line"></i>暂无服务商配置，点击右上角「添加服务商」。</div>';
          return;
        }
        grid.innerHTML = '';
        list.forEach(function (p) { grid.appendChild(card(p)); });
      })
      .catch(function (e) {
        grid.innerHTML = '<div class="empty-p" style="grid-column:1/-1;"><i class="ri-error-warning-line"></i>加载失败（需管理员登录）：' + esc(e.message) + '</div>';
      });
  }

  function showTest(id, ok, msg) {
    var box = document.getElementById('test-' + id);
    if (!box) return;
    box.className = 'test-msg show ' + (ok ? 'ok' : 'fail');
    box.textContent = msg;
    setTimeout(function () { box.classList.remove('show'); }, 5000);
  }

  grid.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-act]');
    if (!btn) return;
    var id = +btn.getAttribute('data-id');
    var act = btn.getAttribute('data-act');
    if (act === 'edit') { openEditor(id); }
    else if (act === 'test') {
      btn.disabled = true;
      btn.innerHTML = '<i class="ri-loader-4-line spinner"></i> 测试中…';
      fetch('/api/agents/providers/' + id + '/test', { method: 'POST' })
        .then(function (r) { return r.json(); })
        .then(function (d) { showTest(id, d.ok, d.message || '已返回'); })
        .catch(function (e2) { showTest(id, false, '请求失败：' + e2.message); })
        .finally(function () {
          btn.disabled = false;
          btn.innerHTML = '<i class="ri-wifi-line"></i> 测试连接';
        });
    }
    else if (act === 'del') {
      if (!confirm('确定删除该服务商？')) return;
      fetch('/api/agents/providers/' + id, { method: 'DELETE' })
        .then(function (r) { if (!r.ok) return r.json().then(function (d) { throw new Error(d.detail); }); return r.json(); })
        .then(function () { toast('已删除'); load(); })
        .catch(function (e2) { toast('删除失败：' + e2.message, 'error'); });
    }
    else if (act === 'setdefault') {
      // 读取该服务商数据 → 保存 is_default=true
      fetch('/api/agents/providers').then(function (r) { return r.json(); }).then(function (list) {
        var p = list.find(function (x) { return x.id === id; });
        if (!p) return;
        p.is_default = true;
        // 需重新走完整保存（含 key，若已加密则不重传）
        saveAsDefault(p);
      });
    }
  });

  function saveAsDefault(p) {
    var body = { name: p.name, provider: p.provider, base_url: p.base_url, model: p.model,
                 api_key: '', quota_limit: p.quota_limit, is_default: true, enabled: p.enabled };
    fetch('/api/agents/providers/' + p.id, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(function (r) { return r.json(); })
      .then(function () { toast('已设为默认'); load(); })
      .catch(function (e) { toast('设置失败：' + e.message, 'error'); });
  }

  var overlay = document.getElementById('editorOverlay');
  window.openEditor = function (id) {
    document.getElementById('pid').value = '';
    document.getElementById('pname').value = '';
    document.getElementById('pprovider').value = 'custom';
    document.getElementById('purl').value = '';
    document.getElementById('pmodel').value = '';
    document.getElementById('pkey').value = '';
    document.getElementById('pquota').value = '';
    document.getElementById('keyHint').textContent = '';
    document.getElementById('editorTitle').textContent = '添加服务商';
    if (id) {
      fetch('/api/agents/providers').then(function (r) { return r.json(); }).then(function (list) {
        var p = list.find(function (x) { return x.id === id; });
        if (!p) return;
        document.getElementById('editorTitle').textContent = '编辑服务商';
        document.getElementById('pid').value = p.id;
        document.getElementById('pname').value = p.name;
        document.getElementById('pprovider').value = p.provider;
        document.getElementById('purl').value = p.base_url;
        document.getElementById('pmodel').value = p.model;
        document.getElementById('pquota').value = p.quota_limit || '';
        document.getElementById('keyHint').textContent = p.has_key ? '（已配置，留空不修改）' : '';
      });
    }
    overlay.hidden = false;
  };
  window.closeEditor = function () { overlay.hidden = true; };
  window.saveProvider = function (e) {
    e.preventDefault();
    var payload = {
      name: document.getElementById('pname').value.trim(),
      provider: document.getElementById('pprovider').value,
      base_url: document.getElementById('purl').value.trim(),
      model: document.getElementById('pmodel').value.trim(),
      api_key: document.getElementById('pkey').value,
      quota_limit: document.getElementById('pquota').value ? +document.getElementById('pquota').value : null,
      is_default: false,
      enabled: true,
    };
    if (!payload.name || !payload.base_url || !payload.model) { toast('请填写必填字段', 'error'); return; }
    var id = document.getElementById('pid').value;
    var url = id ? '/api/agents/providers/' + id : '/api/agents/providers';
    var method = id ? 'PUT' : 'POST';
    var btn = document.getElementById('saveBtn');
    btn.disabled = true;
    fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(function (r) {
      if (!r.ok) return r.json().then(function (d) { throw new Error(d.detail || '保存失败'); });
      return r.json();
    }).then(function () {
      toast(id ? '已更新' : '已添加');
      closeEditor();
      load();
    }).catch(function (err) {
      toast('保存失败：' + err.message, 'error');
    }).finally(function () {
      btn.disabled = false;
    });
    return false;
  };

  if (overlay) overlay.addEventListener('click', function (e) { if (e.target === overlay) closeEditor(); });
  load();
})();