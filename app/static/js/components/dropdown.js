/* ============================================================
   dropdown.js —— 统一下拉框组件交互逻辑
   提供 DROPDOWN.init(container, options) 初始化任意类型下拉框：
     - standard：单选（含分组 / 自定义日期范围）
     - search  ：支持搜索过滤 + 空状态
     - multi   ：多选（全选 / 计数 / 重置或确定按钮）
     - compact ：紧凑单选（分页大小等）
   - 点击外部关闭、键盘导航、位置自适应
   - 通过 CustomEvent('dropdown-change') 向外广播
   ============================================================ */
(function (global) {
  'use strict';

  var all = [];          // 所有已初始化的实例
  var overlay = null;

  function ensureOverlay() {
    if (overlay) return;
    overlay = document.createElement('div');
    overlay.className = 'dropdown-overlay';
    document.body.appendChild(overlay);
  }

  function closeAll(exclude) {
    all.forEach(function (inst) {
      if (inst !== exclude && inst.panel.classList.contains('show')) {
        inst.close();
      }
    });
  }

  /* ---------- 位置自适应（保持面板在视口内） ---------- */
  function adjustPosition(panel, trigger) {
    if (window.innerWidth <= 768) return; // 移动端为底部抽屉
    var rect = trigger.getBoundingClientRect();
    panel.style.top = '';
    panel.style.bottom = '';
    panel.style.marginTop = '';
    panel.style.marginBottom = '';

    var panelH = panel.scrollHeight;
    if (rect.bottom + panelH > window.innerHeight - 10) {
      panel.style.top = 'auto';
      panel.style.bottom = '100%';
      panel.style.marginBottom = '4px';
    } else {
      panel.style.top = '100%';
      panel.style.bottom = 'auto';
      panel.style.marginTop = '4px';
    }

    var rect2 = trigger.getBoundingClientRect();
    panel.style.left = '';
    panel.style.right = '';
    if (rect2.right + 240 > window.innerWidth - 10) {
      panel.style.left = 'auto';
      panel.style.right = '0';
    }
  }

  function Dropdown(container, options) {
    this.container = container;
    this.options = options || {};
    this.trigger = container.querySelector('.dropdown-trigger');
    this.panel = container.querySelector('.dropdown-panel');
    this.searchInput = container.querySelector('.dropdown-search input');
    this.multi = container.classList.contains('dropdown-multi');

    this.initEvents();
    if (all.indexOf(this) === -1) all.push(this);
  }

  Dropdown.prototype.getItems = function () {
    return Array.prototype.slice.call(
      this.container.querySelectorAll('.dropdown-item:not(.disabled)')
    );
  };

  Dropdown.prototype.open = function () {
    closeAll(this);
    ensureOverlay();
    this.panel.classList.add('show');
    this.trigger.classList.add('active');
    overlay.classList.add('show');
    adjustPosition(this.panel, this.trigger);

    if (this.searchInput) {
      // 自然重排后聚焦
      requestAnimationFrame(function () {
        this.searchInput.focus();
      }.bind(this));
    }
  };

  Dropdown.prototype.close = function (restoreFocus) {
    this.panel.classList.remove('show');
    this.trigger.classList.remove('active');
    if (overlay) overlay.classList.remove('show');
    if (restoreFocus) this.trigger.focus();
  };

  Dropdown.prototype.toggle = function () {
    if (this.panel.classList.contains('show')) this.close();
    else this.open();
  };

  Dropdown.prototype.selectSingle = function (item, silent) {
    this.container.querySelectorAll('.dropdown-item').forEach(function (it) {
      it.classList.remove('selected');
    });
    item.classList.add('selected');

    var label = item.querySelector('.dropdown-item-label') || { textContent: item.textContent.trim() };
    var icon = item.querySelector('.dropdown-item-icon');

    var triggerLabel = this.container.querySelector('.dropdown-trigger-label');
    var triggerIcon = this.container.querySelector('.dropdown-trigger-icon');

    if (triggerLabel) {
      triggerLabel.textContent = label.textContent;
      this.trigger.classList.remove('placeholder');
    }
    if (triggerIcon && icon) {
      triggerIcon.className = icon.className;
      triggerIcon.innerHTML = '';
      while (icon.firstChild) triggerIcon.appendChild(icon.firstChild);
    }

    this.close();
    if (!silent) this.dispatch(item.dataset.value, label.textContent);
  };

  Dropdown.prototype.updateMultiTrigger = function () {
    var count = this.container.querySelectorAll('.dropdown-item.selected').length;
    var countEl = this.container.querySelector('.dropdown-selected-count');
    var infoEl = this.container.querySelector('.dropdown-selected-info');
    var allItems = this.getItems().length;

    if (countEl) {
      countEl.style.display = count > 0 ? 'inline' : 'none';
      countEl.textContent = '(' + count + ')';
    }
    if (infoEl) infoEl.textContent = '已选 ' + count + ' 项';

    // 全选勾选状态
    var selectAll = this.container.querySelector('.select-all-checkbox');
    if (selectAll) selectAll.checked = count === allItems && allItems > 0;
  };

  Dropdown.prototype.dispatch = function (value, label) {
    this.container.dispatchEvent(new CustomEvent('dropdown-change', {
      detail: { value: value, label: label, container: this.container }
    }));
  };

  Dropdown.prototype.initEvents = function () {
    var self = this;

    // 触发器
    this.trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      self.toggle();
    });

    // 关闭按钮（若存在）
    var clearBtn = this.container.querySelector('.dropdown-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        self.clear();
      });
    }

    // 面板点击不冒泡
    this.panel.addEventListener('click', function (e) { e.stopPropagation(); });

    // 单选选项
    this.getItems().forEach(function (item) {
      if (!self.multi && item.onclick) return; // 保留页面自带 onClick（分组等）
      if (self.multi) {
        var cb = item.querySelector('input[type="checkbox"]');
        item.addEventListener('click', function () {
          var willSelect = !item.classList.contains('selected');
          item.classList.toggle('selected', willSelect);
          if (cb) cb.checked = willSelect;
          self.updateMultiTrigger();
        });
      } else if (!item.dataset.noAuto) {
        item.addEventListener('click', function () {
          self.selectSingle(item);
        });
      }
    });

    // 多选：全选
    var selectAll = this.container.querySelector('.select-all-checkbox');
    if (selectAll) {
      selectAll.addEventListener('change', function () {
        var checked = selectAll.checked;
        self.container.querySelectorAll('.dropdown-item').forEach(function (it) {
          it.classList.toggle('selected', checked);
          var cb = it.querySelector('input[type="checkbox"]');
          if (cb) cb.checked = checked;
        });
        self.updateMultiTrigger();
      });
    }

    // 多选：操作按钮
    var confirmBtn = this.container.querySelector('[data-act="ok"]');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', function () {
        var vals = self.container.querySelectorAll('.dropdown-item.selected');
        var list = Array.prototype.map.call(vals, function (it) {
          return it.dataset.value;
        });
        self.dispatch(list.join(','), list.length + ' 项已选');
        self.close();
      });
    }
    var resetBtn = this.container.querySelector('[data-act="reset"]');
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        self.container.querySelectorAll('.dropdown-item').forEach(function (it) {
          it.classList.remove('selected');
          var cb = it.querySelector('input[type="checkbox"]');
          if (cb) cb.checked = false;
        });
        self.updateMultiTrigger();
      });
    }

    // 搜索过滤 + 空状态
    if (this.searchInput) {
      this.searchInput.addEventListener('input', function () {
        var kw = self.searchInput.value.toLowerCase().trim();
        var visible = 0;
        self.container.querySelectorAll('.dropdown-item').forEach(function (item) {
          var txtEl = item.querySelector('.dropdown-item-label');
          var txt = (txtEl ? txtEl.textContent : item.textContent).toLowerCase();
          var show = txt.indexOf(kw) !== -1;
          item.style.display = show ? '' : 'none';
          if (show) visible++;
        });
        var empty = self.container.querySelector('.dropdown-empty');
        if (empty) empty.classList.toggle('show', visible === 0);
      });
    }

    // 自定义范围应用按钮
    var rangeBtn = this.container.querySelector('[data-act="apply-range"]');
    if (rangeBtn) {
      rangeBtn.addEventListener('click', function () {
        var start = self.container.querySelector('[data-range="start"]');
        var end = self.container.querySelector('[data-range="end"]');
        var label = (start && start.value ? start.value : '') + ' 至 ' + (end && end.value ? end.value : '');
        var lblEl = self.container.querySelector('.dropdown-trigger-label');
        if (lblEl && start && start.value && end && end.value) {
          lblEl.textContent = label;
          self.trigger.classList.remove('placeholder');
        }
        self.dispatch('custom', label);
        self.close();
      });
    }

    // 键盘导航
    this.initKeyboard();
  };

  Dropdown.prototype.initKeyboard = function () {
    var self = this;
    var focusedIndex = -1;

    function focusItem(i) {
      var items = self.getItems().filter(function (it) { return it.style.display !== 'none'; });
      if (!items.length) return;
      if (i < 0) i = items.length - 1;
      if (i > items.length - 1) i = 0;
      items.forEach(function (it, idx) {
        it.classList.toggle('focused', idx === i);
      });
      focusedIndex = i;
      if (items[i]) items[i].scrollIntoView({ block: 'nearest' });
    }

    this.trigger.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        if (!self.panel.classList.contains('show')) self.open();
        else focusItem(focusedIndex + 1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        focusItem(focusedIndex - 1);
      } else if (e.key === 'Escape') {
        self.close(true);
      }
    });

    this.panel.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); focusItem(focusedIndex + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); focusItem(focusedIndex - 1); }
      else if (e.key === 'Home') { e.preventDefault(); focusItem(0); }
      else if (e.key === 'End') { e.preventDefault(); focusItem(self.getItems().length - 1); }
      else if (e.key === 'Enter' || e.key === ' ') {
        if (focusedIndex >= 0) {
          var visible = self.getItems().filter(function (it) { return it.style.display !== 'none'; });
          if (visible[focusedIndex]) visible[focusedIndex].click();
        }
        e.preventDefault();
      } else if (e.key === 'Escape') {
        self.close(true);
      }
    });
  };

  // 清空（多选）
  Dropdown.prototype.clear = function () {
    var self = this;
    this.container.querySelectorAll('.dropdown-item').forEach(function (it) {
      it.classList.remove('selected');
      var cb = it.querySelector('input[type="checkbox"]');
      if (cb) cb.checked = false;
    });
    this.updateMultiTrigger();
    if (!this.multi) {
      var lbl = this.container.querySelector('.dropdown-trigger-label');
      var placeholder = this.container.getAttribute('data-placeholder');
      if (lbl && placeholder) { lbl.textContent = placeholder; this.trigger.classList.add('placeholder'); }
      this.dispatch('', placeholder || '');
    }
  };

  // 程序化设置单选值
  Dropdown.prototype.setValue = function (value, silent) {
    var items = this.container.querySelectorAll('.dropdown-item');
    var found = null;
    items.forEach(function (it) {
      if (String(it.dataset.value) === String(value)) found = it;
    });
    if (found) this.selectSingle(found, silent);
  };

  // 对外 API
  global.DROPDOWN = {
    init: function (selectorOrEl, options) {
      var els;
      if (typeof selectorOrEl === 'string') {
        els = Array.prototype.slice.call(document.querySelectorAll(selectorOrEl));
      } else {
        els = [selectorOrEl];
      }
      var instances = [];
      els.forEach(function (el) {
        if (el && !el.__dropdown) {
          el.__dropdown = new Dropdown(el, options);
          instances.push(el.__dropdown);
        }
      });
      return instances.length === 1 ? instances[0] : instances;
    },
    refresh: function () { closeAll(); }
  };

  // 全局点击外部关闭
  document.addEventListener('click', function (e) {
    all.forEach(function (inst) {
      if (!inst.container.contains(e.target)) {
        inst.close();
      }
    });
  });

  // 页面尺寸变化时重排已展开面板
  window.addEventListener('resize', function () {
    all.forEach(function (inst) {
      if (inst.panel.classList.contains('show')) {
        adjustPosition(inst.panel, inst.trigger);
      }
    });
  });

  // 自动初始化页面上所有下拉框容器
  function autoInit() {
    var els = document.querySelectorAll('.dropdown-container:not([data-js-done])');
    els.forEach(function (el) {
      el.setAttribute('data-js-done', '1');
      el.__dropdown = new Dropdown(el);
      all.push(el.__dropdown);
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }
})(window);