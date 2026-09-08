(function () {
  'use strict';

  const els = {
    messages: document.getElementById('messages'),
    messagesPad: document.getElementById('messagesPad'),
    question: document.getElementById('question'),
    sendBtn: document.getElementById('sendBtn'),
    newChatBtn: document.getElementById('newChatBtn'),
    srcBody: document.getElementById('srcBody'),
  };
  if (!els.question) return;

  function esc(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /* ---------- Markdown 渲染 ---------- */
  function inline(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  }

  function renderText(text) {
    text = String(text || '');
    let html = '';

    // 代码块优先
    let rest = text;
    const codeRe = /```([\s\S]*?)```/g;
    let last = 0, m;
    while ((m = codeRe.exec(rest)) !== null) {
      html += renderBlock(rest.slice(last, m.index));
      html += '<pre><code>' + esc(m[1]) + '</code></pre>';
      last = codeRe.lastIndex;
    }
    html += renderBlock(rest.slice(last));
    return html || esc(text);
  }

  function renderBlock(block) {
    if (!block || !block.trim()) return '';
    const lines = block.replace(/\r/g, '').split('\n');
    let html = '';
    let para = [];
    const flushPara = () => {
      if (para.length) {
        html += '<p>' + para.map(inline).join('<br>') + '</p>';
        para = [];
      }
    };

    let listType = null, listItems = [];
    const flushList = () => {
      if (listItems.length) {
        const tag = listType === 'ol' ? 'ol' : 'ul';
        html += '<' + tag + '>' + listItems.map(li => '<li>' + inline(li) + '</li>').join('') + '</' + tag + '>';
        listItems = [];
        listType = null;
      }
    };

    for (let i = 0; i < lines.length; i++) {
      const raw = lines[i];
      const t = raw.trim();

      if (!t) { flushPara(); flushList(); continue; }

      const ul = /^[-*+]\s+(.*)/.exec(t);
      if (ul) {
        flushPara();
        if (listType && listType !== 'ul') flushList();
        listType = 'ul';
        listItems.push(ul[1]);
        continue;
      }
      const ol = /^\d+\.\s+(.*)/.exec(t);
      if (ol) {
        flushPara();
        if (listType && listType !== 'ol') flushList();
        listType = 'ol';
        listItems.push(ol[1]);
        continue;
      }

      if (listType) flushList();
      const quote = /^>\s?(.*)/.exec(t);
      if (quote) { flushPara(); html += '<blockquote>' + inline(quote[1]) + '</blockquote>'; continue; }
      const head = /^(#{1,3})\s+(.*)/.exec(t);
      if (head) { flushPara(); const lvl = head[1].length; html += '<h' + lvl + '>' + inline(head[2]) + '</h' + lvl + '>'; continue; }

      para.push(t);
    }
    flushPara();
    flushList();
    return html;
  }

  /* ---------- DOM 构建 ---------- */
  function makeBubble(role, text) {
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = renderText(text);
    return bubble;
  }

  function appendSources(bubble, sources) {
    if (!sources || !sources.length) return;
    const sc = document.createElement('div');
    sc.className = 'sources-card';
    sc.innerHTML =
      '<button class="sources-head" data-id="' + (sc._i = 0) + '">' +
      '<i class="ri-attachment-line"></i><span>引用来源（' + sources.length + '）</span>' +
      '<i class="ri-arrow-down-s-line"></i></button>' +
      '<div class="sources-list">' +
      sources.map(s => '<div class="source-item"><i class="ri-file-text-line"></i><span>' + esc(s) + '</span></div>').join('') +
      '</div>';
    sc.querySelector('.sources-head').addEventListener('click', function () {
      const list = sc.querySelector('.sources-list');
      list.hidden = !list.hidden;
    });
    bubble.appendChild(sc);
  }

  function addMessage(role, text, sources) {
    const row = document.createElement('div');
    row.className = 'msg-row ' + role;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = role === 'user' ? '<i class="ri-user-fill"></i>' : '<i class="ri-robot-2-fill"></i>';

    const bubble = makeBubble(role, text);
    if (role === 'ai') appendSources(bubble, sources);

    row.appendChild(avatar);
    row.appendChild(bubble);
    els.messagesPad.appendChild(row);
    els.messages.scrollTop = els.messages.scrollHeight;
    return row;
  }

  function addTyping() {
    const row = document.createElement('div');
    row.className = 'msg-row ai typing';
    row.innerHTML =
      '<div class="avatar"><i class="ri-robot-2-fill"></i></div>' +
      '<div class="bubble"><i></i><i></i><i></i></div>';
    els.messagesPad.appendChild(row);
    els.messages.scrollTop = els.messages.scrollHeight;
    return row;
  }

  function showWelcome() {
    els.messagesPad.innerHTML = '';
    const w = document.createElement('div');
    w.className = 'welcome';
    const qs = [
      '什么是二叉树的前序遍历？',
      '链表和数组有什么区别？',
      '如何计算算法的时间复杂度？',
      '请解释一下动态规划的思想',
    ];
    w.innerHTML =
      '<div class="w-logo"><i class="ri-robot-2-fill"></i></div>' +
      '<h1>智能答疑助手</h1>' +
      '<p class="w-desc">基于 RAG 知识库的课程问答，回答附带可靠来源引用</p>' +
      '<div class="suggest-grid">' +
      qs.map(q => '<button class="suggest-card"><span class="q-icon"><i class="ri-question-line"></i></span><span>' + esc(q) + '</span></button>').join('') +
      '</div>';
    els.messagesPad.appendChild(w);
    w.querySelectorAll('.suggest-card').forEach(b => {
      b.addEventListener('click', () => { els.question.value = b.querySelector('span:last-child').textContent; send(); });
    });
  }

  /* ---------- 右侧引用 ---------- */
  function renderSources(sources) {
    if (!els.srcBody) return;
    if (!sources || !sources.length) {
      els.srcBody.innerHTML = '<div class="src-empty"><i class="ri-book-open-line"></i>未引用知识库</div>';
      return;
    }
    const groups = {};
    sources.forEach(s => {
      const doc = (s.split('·')[0] || '来源');
      (groups[doc] = groups[doc] || []).push(s);
    });
    els.srcBody.innerHTML = Object.keys(groups).map(doc =>
      '<div class="src-card"><div class="doc-name"><i class="ri-file-text-line"></i>' + esc(doc) + '</div>' +
      '<ul class="src-frags">' +
      groups[doc].map(s => '<li>' + esc((s.split('·')[1] || s).substring(0, 80)) + '</li>').join('') +
      '</ul></div>'
    ).join('');
  }

  /* ---------- 会话 ---------- */
  async function switchSession(sessionId) {
    window.__currentSessionId = sessionId ? Number(sessionId) : null;
    document.querySelectorAll('.session-item').forEach(item =>
      item.classList.toggle('active', item.dataset.id === String(sessionId || '')));
    if (sessionId) {
      const r = await fetch('/api/sessions/' + sessionId + '/messages');
      const data = await r.json();
      const msgs = Array.isArray(data) ? data : (data.messages || []);
      els.messagesPad.innerHTML = '';
      msgs.forEach(msg => {
        let src = [];
        try { src = msg.sources ? JSON.parse(msg.sources) : []; } catch (e) {}
        if (msg.role === 'user') addMessage('user', msg.content);
        else if (msg.role === 'assistant' || msg.role === 'ai') addMessage('ai', msg.content, src);
      });
      if (!msgs.length) showWelcome();
    } else {
      showWelcome();
    }
    renderSources([]);
  }

  function refreshSessions() {
    fetch('/api/sessions')
      .then(r => r.json())
      .then(data => {
        const sessions = Array.isArray(data) ? data : (data.sessions || []);
        const el = document.getElementById('sessionList');
        if (!el) return;
        if (!sessions || !sessions.length) {
          el.innerHTML = '<div class="session-empty">暂无历史会话</div>';
          return;
        }
        const now = new Date();
        const today = now.toDateString();
        const yesterday = new Date(now.getTime() - 86400000).toDateString();
        const groups = { 今天: [], 昨天: [], 更早: [] };
        sessions.forEach(s => {
          const d = s.created_at ? new Date(s.created_at) : null;
          if (!d) { groups.更早.push(s); return; }
          if (d.toDateString() === today) groups.今天.push(s);
          else if (d.toDateString() === yesterday) groups.昨天.push(s);
          else groups.更早.push(s);
        });
        el.innerHTML = Object.keys(groups).map(g =>
          groups[g].length
            ? '<div class="session-group"><div class="session-label">' + g + '</div>' +
              groups[g].map(s =>
                '<div class="session-item-row">' +
                '<button class="session-item" data-id="' + s.id + '" onclick="window.__switchSession(\'' + s.id + '\')">' +
                '<span class="s-icon"><i class="ri-message-3-line"></i></span>' +
                '<span class="s-content">' +
                '<span class="s-title">' + esc(s.title || '会话 ' + s.id) + '</span>' +
                '<span class="s-preview">' + esc(s.title || '') + ' · ' + (s.created_at || '').slice(5, 16) + '</span>' +
                '</span></button>' +
                '<button class="session-del" data-id="' + s.id + '" onclick="event.stopPropagation(); window.__delSession(\'' + s.id + '\')" aria-label="删除会话" title="移入回收站"><i class="ri-delete-bin-line"></i></button>' +
                '</div>'
              ).join('') + '</div>'
            : ''
        ).join('');
      })
      .catch(() => {});
  }

  /* ---------- 发送（SSE 流式） ---------- */
  async function send() {
    const text = els.question.value.trim();
    if (!text) return;
    const typing = els.messagesPad.querySelector('.typing');
    if (typing) typing.remove();

    addMessage('user', text);
    els.question.value = '';
    els.question.style.height = 'auto';

    const aiRow = addTyping();
    const aiBubble = aiRow.querySelector('.bubble');
    aiBubble.classList.remove('typing');
    internalTyping(aiBubble);
    aiBubble.innerHTML = '';

    setBusy(true);
    try {
      const resp = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, course_id: null, session_id: null }),
      });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let acc = '', curText = '', finalText = '', finalSources = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });
        const events = acc.split('\n\n');
        acc = events.pop();
        for (const ev of events) {
          const line = ev.split('\n').find(l => l.indexOf('data:') === 0);
          if (!line) continue;
          const data = line.slice(5).trim();
          if (data === '[DONE]') continue;
          try {
            const obj = JSON.parse(data);
            if (obj.token !== undefined) {
              curText += obj.token;
              aiBubble.innerHTML = renderText(curText);
              els.messages.scrollTop = els.messages.scrollHeight;
            } else if (obj.text !== undefined) {
              finalText = obj.text;
              finalSources = obj.sources || [];
            }
          } catch (e) {}
        }
      }

      stopTyping();
      aiBubble.innerHTML = renderText(finalText || curText);
      appendSources(aiBubble, finalSources);
      renderSources(finalSources);
      refreshSessions();
    } catch (err) {
      stopTyping();
      aiBubble.innerHTML = '<span style="color:var(--danger)">出错：' + esc(err.message) + '</span>';
    } finally {
      setBusy(false);
    }
  }

  function internalTyping(bubble) {
    if (bubble._t) return;
    bubble._t = setInterval(() => {
      if (bubble && !bubble.textContent) {
        bubble.innerHTML = '<i></i><i></i><i></i>';
        bubble.classList.add('typing');
      }
    }, 100);
  }
  function stopTyping() {
    document.querySelectorAll('.typing').forEach(el => {
      el.classList.remove('typing');
      if (el._t) { clearInterval(el._t); el._t = null; }
    });
  }

  function setBusy(b) {
    els.sendBtn.disabled = b;
    els.sendBtn.innerHTML = b ? '<i class="ri-loader-4-line spinner"></i>' : '<i class="ri-send-plane-fill"></i>';
  }

  /* ---------- 会话软删除（移入回收站，可恢复） ---------- */
  async function deleteSession(sessionId) {
    if (!confirm('删除后可在回收站恢复，确定继续？')) return;
    try {
      const resp = await fetch('/api/sessions/' + sessionId, { method: 'DELETE' });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || ('HTTP ' + resp.status));
      const row = document.querySelector('.session-item-row [data-id="' + sessionId + '"]');
      if (row) row.closest('.session-item-row').remove();
      if (window.__currentSessionId === Number(sessionId)) switchSession(null);
      refreshSessions();
      toast('已移入回收站');
    } catch (err) {
      toast('删除失败：' + err.message, 'error');
    }
  }
  window.__delSession = deleteSession;

  /* ---------- 事件绑定 ---------- */
  els.sendBtn.addEventListener('click', send);
  els.newChatBtn.addEventListener('click', () => { switchSession(null); els.question.focus(); });
  els.question.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  els.question.addEventListener('input', () => {
    els.question.style.height = 'auto';
    els.question.style.height = Math.min(els.question.scrollHeight, 200) + 'px';
  });

  window.__switchSession = switchSession;

  refreshSessions();
  switchSession(null);
})();