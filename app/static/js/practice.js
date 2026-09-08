/* 答题练习页交互：机题浏览、选项选择、代码行号、草稿、提交判题。原生 JS。 */
(function () {
  'use strict';

  var QUESTIONS = window.__QUESTIONS || [];
  var index = 0;

  var el = {
    qTitle: document.getElementById('qTitle'),
    qProgress: document.getElementById('qProgress'),
    qIndexLabel: document.getElementById('qIndexLabel'),
    qMeta: document.getElementById('qMeta'),
    qStem: document.getElementById('qStem'),
    optList: document.getElementById('optList'),
    answerText: document.getElementById('answerText'),
    codeLines: document.getElementById('codeLines'),
    submitBtn: document.getElementById('submitBtn'),
    draftBtn: document.getElementById('draftBtn'),
    resultBox: document.getElementById('resultBox'),
    resultIcon: document.getElementById('resultIcon'),
    resultText: document.getElementById('resultText'),
    resultExpect: document.getElementById('resultExpect'),
  };

  function esc(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  var TYPE_LABEL = { choice: '选择题', fill: '填空题', short: '简答题' };
  var TYPE_ICON = { choice: 'ri-checkbox-circle-line', fill: 'ri-edit-box-line', short: 'ri-question-answer-line' };

  function render() {
    if (!QUESTIONS.length) return;
    var q = QUESTIONS[index];
    el.qTitle.textContent = '题目 ' + (index + 1) + ' / ' + QUESTIONS.length;
    el.qIndexLabel.textContent = (index + 1) + ' / ' + QUESTIONS.length;
    el.qMeta.innerHTML =
      '<span class="pill ' + q.type + '"><i class="' + TYPE_ICON[q.type] + '"></i> ' + (TYPE_LABEL[q.type] || q.type) + '</span>' +
      '<span class="pill diff"><i class="ri-line-chart-line"></i> 难度 ' + (Number(q.difficulty) || 3) + '</span>';
    el.qStem.textContent = q.stem;

    if (q.type === 'choice' && q.options && q.options.length) {
      el.optList.style.display = '';
      el.optList.innerHTML = q.options.map(function (op, i) {
        var key = String.fromCharCode(65 + i); // A, B, C, D
        var text = op;
        // 去掉已有的 "A." 前缀
        var m = /^([A-Za-z])[.、．)\s]+(.*)$/.exec(text.trim());
        if (m) { key = m[1].toUpperCase(); text = m[2]; }
        return '<div class="opt-item" data-key="' + key + '" onclick="window.__pick(this)">' +
          '<span class="opt-key">' + key + '</span><span class="opt-text">' + esc(text) + '</span></div>';
      }).join('');
      el.answerText.style.display = 'none';
      el.codeLines.style.display = 'none';
    } else {
      el.optList.style.display = 'none';
      el.answerText.style.display = '';
      el.codeLines.style.display = '';
      el.answerText.placeholder = q.type === 'fill' ? '在此填写答案…' : '在此输入你的作答…';
      renderLines();
    }

    var draft = localStorage.getItem('practice_draft_' + q.id);
    var choice = localStorage.getItem('practice_choice_' + q.id);
    restoreChoice(choice);
    if (draft) el.answerText.value = draft;

    window.__prevBtn = document.getElementById('prevQ');
    document.getElementById('prevQ').disabled = index === 0;
    document.getElementById('nextQ').textContent = index === QUESTIONS.length - 1 ? '完成' : '下一题';
    hideResult();
  }

  function restoreChoice(key) {
    Array.prototype.forEach.call(document.querySelectorAll('.opt-item'), function (o) {
      o.classList.toggle('selected', o.getAttribute('data-key') === key);
    });
  }

  function renderLines() {
    var lines = Math.max(8, el.answerText.value.split('\n').length + 1);
    var html = '';
    for (var i = 1; i <= lines; i++) html += i + '<br>';
    el.codeLines.innerHTML = html;
  }

  window.__pick = function (item) {
    Array.prototype.forEach.call(document.querySelectorAll('.opt-item'), function (o) {
      o.classList.remove('selected');
    });
    item.classList.add('selected');
    var q = QUESTIONS[index];
    localStorage.setItem('practice_choice_' + q.id, item.getAttribute('data-key'));
    hideResult();
  };

  window.__nav = function (d) {
    saveState();
    var n = index + d;
    if (n < 0 || n >= QUESTIONS.length) return;
    index = n;
    render();
  };

  window.__draft = function () {
    saveState();
    toast('草稿已保存');
  };

  function saveState() {
    var q = QUESTIONS[index];
    localStorage.setItem('practice_draft_' + q.id, el.answerText.value);
    var sel = document.querySelector('.opt-item.selected');
    if (sel) localStorage.setItem('practice_choice_' + q.id, sel.getAttribute('data-key'));
  }

  function hideResult() {
    el.resultBox.classList.remove('show', 'correct', 'wrong');
  }

  function showResult(ok, expected, isChoice) {
    el.resultBox.classList.remove('correct', 'wrong');
    el.resultBox.classList.add('show', ok ? 'correct' : 'wrong');
    el.resultIcon.className = ok ? 'ri-checkbox-circle-line' : 'ri-close-circle-line';
    el.resultText.textContent = ok ? (isChoice ? '回答正确！' : '回答正确！') : '回答错误';
    if (!ok && expected) el.resultExpect.textContent = '参考答案：' + expected;
    else el.resultExpect.textContent = '';
  }

  async function submit() {
    var q = QUESTIONS[index];
    var sel = document.querySelector('.opt-item.selected');
    var answer = sel ? sel.getAttribute('data-key') : el.answerText.value;
    if (!answer || !String(answer).trim()) {
      toast('请先作答再提交', 'error');
      return;
    }
    el.submitBtn.disabled = true;
    el.submitBtn.classList.add('loading');
    el.submitBtn.innerHTML = '<i class="ri-loader-4-line spinner"></i> 判题中…';
    try {
      var resp = await fetch('/api/practice/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: q.id, answer: String(answer) }),
      });
      var data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || ('HTTP ' + resp.status));
      showResult(data.correct, data.expected, data.mechanism);
      // 判题后清除该题草稿
      localStorage.removeItem('practice_draft_' + q.id);
      localStorage.removeItem('practice_choice_' + q.id);
    } catch (err) {
      toast('判题失败：' + err.message, 'error');
    } finally {
      el.submitBtn.disabled = false;
      el.submitBtn.classList.remove('loading');
      el.submitBtn.innerHTML = '<i class="ri-send-plane-fill"></i> 提交判题';
    }
  }

  el.answerText.addEventListener('input', renderLines);
  el.answerText.addEventListener('input', saveState);
  el.optList.addEventListener('click', function (e) {
    var item = e.target.closest('.opt-item');
    if (item) window.__pick(item);
  });
  el.submitBtn.addEventListener('click', submit);

  render();
})();