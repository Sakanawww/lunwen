/* 课程管理前端：列表 / 新建编辑 / 成员角色管理（RBAC），ES5 风格 IIFE */
(function () {
  'use strict';

  var API = '/api/courses';

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function roleLabel(r) {
    var map = { owner: '授课', teacher: '协教', assistant: '助教', student: '学生' };
    return map[r] || r;
  }
  function roleChip(r) {
    return '<span class="role-chip role-' + esc(r) + '">' + esc(roleLabel(r)) + '</span>';
  }

  // ---------- 渲染课程卡片 ----------
  function renderCourses(list) {
    var grid = document.getElementById('courseGrid');
    if (!list.length) {
      grid.innerHTML = '<div class="empty-courses"><i class="ri-book-open-line"></i>暂无课程</div>';
      return;
    }
    var html = '';
    for (var i = 0; i < list.length; i++) {
      var c = list[i];
      var canManage = (c.my_role === 'owner' || c.my_role === 'admin');
      var canEnroll = (c.my_role === 'student');
      html +=
        '<div class="course-card">' +
          '<div class="c-top">' +
            '<h3><i class="ri-book-open-line"></i>' + esc(c.name) + '</h3>' +
            roleChip(c.my_role) +
          '</div>' +
          '<div class="c-code">' + (c.code ? esc(c.code) : '&nbsp;') + '</div>' +
          '<p class="c-desc">' + esc(c.description || '暂无简介') + '</p>' +
          '<div class="c-meta"><span>创建 ' + esc(c.created_at || '—') + '</span></div>' +
          '<div class="c-actions">' +
            (canEnroll ? '<button class="btn btn-ghost" onclick="window.__toggleEnroll(' + c.id + ')"><i class="ri-logout-box-line"></i> 退课</button>'
                       : (c.my_role === 'teacher' || c.my_role === 'assistant' || c.my_role === 'owner'
                          ? '' : '<button class="btn btn-ghost" onclick="window.__toggleEnroll(' + c.id + ')"><i class="ri-login-box-line"></i> 选课</button>')) +
            '<button class="btn btn-ghost" onclick="window.__showMembers(' + c.id + ', \'' + esc(c.name) + '\')"><i class="ri-team-line"></i> 成员</button>' +
            (canManage ? '<button class="btn btn-ghost" onclick="window.__editCourse(' + c.id + ')"><i class="ri-edit-line"></i> 编辑</button>' +
                         '<button class="btn btn-ghost" style="color:var(--danger);border-color:rgba(239,68,68,.35);" onclick="window.__delCourse(' + c.id + ')"><i class="ri-delete-bin-line"></i> 删除</button>' : '') +
          '</div>' +
        '</div>';
    }
    grid.innerHTML = html;
  }

  function loadCourses() {
    fetch(API)
      .then(function (r) { return r.json(); })
      .then(function (list) { renderCourses(list); })
      .catch(function () {
        document.getElementById('courseGrid').innerHTML =
          '<div class="empty-courses"><i class="ri-error-warning-line"></i>加载失败</div>';
      });
  }

  // ---------- 选课 / 退课 ----------
  window.__toggleEnroll = function (courseId) {
    var action = confirm('确定退出该课程？') ? { undo: true } : null;
    if (action === null) return;
    fetch(API + '/enroll', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ course_id: courseId, undo: true }),
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.detail) throw new Error(d.detail);
        if (window.toast) toast('已退出课程'); else alert('已退出课程');
        loadCourses();
      })
      .catch(function (e) { if (window.toast) toast(e.message || '操作失败', 'error'); else alert(e.message); });
  };

  // ---------- 成员管理 ----------
  function showMembers(courseId, name) {
    document.getElementById('membersTitle').textContent = '课程成员：' + name;
    var body = document.getElementById('membersBody');
    body.innerHTML = '<p>加载中…</p>';
    document.getElementById('membersMask').hidden = false;
    fetch(API + '/' + courseId + '/members')
      .then(function (r) { return r.json(); })
      .then(function (members) {
        if (!members.length) {
          body.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:20px 0;">暂无成员</p>';
          return;
        }
        var html = '';
        for (var i = 0; i < members.length; i++) {
          var mk = members[i];
          html +=
            '<div class="member-row">' +
              '<span>' + esc(mk.real_name) + ' <span style="color:var(--text-muted);">@' + esc(mk.username) + '</span></span>' +
              '<span style="display:flex;align-items:center;gap:8px;">' +
                '<select data-uid="' + mk.user_id + '">' +
                  '<option value="owner"' + (mk.role === 'owner' ? ' selected' : '') + '>授课 owner</option>' +
                  '<option value="teacher"' + (mk.role === 'teacher' ? ' selected' : '') + '>协教 teacher</option>' +
                  '<option value="assistant"' + (mk.role === 'assistant' ? ' selected' : '') + '>助教 assistant</option>' +
                  '<option value="student"' + (mk.role === 'student' ? ' selected' : '') + '>学生 student</option>' +
                '</select>' +
                '<button class="btn btn-grad" onclick="window.__setMemberRole(' + courseId + ', ' + mk.user_id + ', this.previousElementSibling.value)">保存</button>' +
                '<button class="btn btn-ghost" style="color:var(--danger);" onclick="window.__removeMember(' + courseId + ', ' + mk.user_id + ')">移除</button>' +
              '</span>' +
            '</div>';
        }
        body.innerHTML = html;
      })
      .catch(function (e) { body.innerHTML = '<p style="color:var(--danger);text-align:center;padding:16px 0;">加载失败</p>'; });
  }
  window.__showMembers = showMembers;

  window.__setMemberRole = function (courseId, userId, role) {
    fetch(API + '/' + courseId + '/members', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, role: role }),
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.detail) throw new Error(d.detail);
        if (window.toast) toast('角色已更新'); else alert('角色已更新');
        loadCourses();
      })
      .catch(function (e) { if (window.toast) toast(e.message || '设置失败', 'error'); else alert(e.message); });
  };

  window.__removeMember = function (courseId, userId) {
    if (!confirm('确定移除该成员？')) return;
    fetch(API + '/' + courseId + '/members/' + userId, { method: 'DELETE' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.detail) throw new Error(d.detail);
        if (window.toast) toast('已移除'); else alert('已移除');
        showMembers(courseId, document.getElementById('membersTitle').textContent.replace('课程成员：', ''));
        loadCourses();
      })
      .catch(function (e) { if (window.toast) toast(e.message || '移除失败', 'error'); else alert(e.message); });
  };

  document.getElementById('membersClose').addEventListener('click', function () {
    document.getElementById('membersMask').hidden = true;
  });

  // ---------- 新建 / 编辑课程 ----------
  function openEditor(course) {
    if (course) {
      document.getElementById('editTitle').textContent = '编辑课程';
      document.getElementById('editId').value = course.id;
      document.getElementById('editName').value = course.name || '';
      document.getElementById('editCode').value = course.code || '';
      document.getElementById('editDesc').value = course.description || '';
    } else {
      document.getElementById('editTitle').textContent = '新建课程';
      document.getElementById('editId').value = '';
      document.getElementById('editName').value = '';
      document.getElementById('editCode').value = '';
      document.getElementById('editDesc').value = '';
    }
    document.getElementById('editMask').hidden = false;
    document.getElementById('editName').focus();
  }
  window.__editCourse = function (id) {
    fetch(API + '/' + id)
      .then(function (r) { return r.json(); })
      .then(function (c) { openEditor(c); })
      .catch(function () { if (window.toast) toast('加载课程失败', 'error'); });
  };
  window.openModal = function () { openEditor(null); };

  document.getElementById('editClose').addEventListener('click', function () {
    document.getElementById('editMask').hidden = true;
  });
  document.getElementById('editCancel').addEventListener('click', function () {
    document.getElementById('editMask').hidden = true;
  });

  document.getElementById('editForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var id = document.getElementById('editId').value;
    var payload = {
      name: document.getElementById('editName').value.trim(),
      code: document.getElementById('editCode').value.trim(),
      description: document.getElementById('editDesc').value.trim(),
    };
    if (!payload.name) { if (window.toast) toast('请填写课程名称', 'error'); return; }
    var method = id ? 'PUT' : 'POST';
    var url = id ? API + '/' + id : API;
    fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.detail) throw new Error(d.detail);
        document.getElementById('editMask').hidden = true;
        if (window.toast) toast(id ? '课程已更新' : '课程已创建'); else alert('保存成功');
        loadCourses();
      })
      .catch(function (err) { if (window.toast) toast(err.message || '保存失败', 'error'); else alert(err.message); });
  });

  // ---------- 删除课程 ----------
  window.__delCourse = function (id) {
    if (!confirm('删除课程将一并删除其关联的作业、试题、知识库、会话等数据，且不可恢复。确定继续？')) return;
    fetch(API + '/' + id, { method: 'DELETE' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.detail) throw new Error(d.detail);
        if (window.toast) toast('课程已删除'); else alert('已删除');
        loadCourses();
      })
      .catch(function (e) { if (window.toast) toast(e.message || '删除失败', 'error'); else alert(e.message); });
  };

  // ---------- 导航进入课程管理 ----------
  window.initCoursePage = loadCourses;

  // 自动初始化（若本页存在课程网格容器）
  if (document.getElementById('courseGrid')) {
    loadCourses();
  }
})();