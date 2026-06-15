/* ============================================================
   ЦМИ — клиентские интерактивы витрины (без React).
   Mobile-drawer, табы товара, переключатель вид сетка/список.
   Корзина/избранное работают через AJAX miniShop2 (jQuery
   miniShop2 подключается ядром компонента); здесь — только UI.
   ============================================================ */
(function () {
  'use strict';

  /* ---- Мобильное меню ---- */
  var drawer = document.querySelector('[data-drawer]');
  function openDrawer() { if (drawer) drawer.hidden = false; }
  function closeDrawer() { if (drawer) drawer.hidden = true; }
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-drawer-open]')) openDrawer();
    if (e.target.closest('[data-drawer-close]')) closeDrawer();
    if (drawer && e.target === drawer) closeDrawer();
  });

  /* ---- Скрытие шапки при скролле вниз / показ при скролле вверх ---- */
  var header = document.querySelector('.sf-header');
  var last = window.scrollY, ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var y = window.scrollY;
      if (header) header.classList.toggle('is-hidden', y > last && y > 140);
      last = y; ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- Табы карточки товара ---- */
  document.addEventListener('click', function (e) {
    var tab = e.target.closest('.ms-tabs__tab');
    if (!tab) return;
    var group = tab.closest('.ms-tabs');
    group.querySelectorAll('.ms-tabs__tab').forEach(function (t) {
      t.setAttribute('aria-selected', t === tab ? 'true' : 'false');
    });
    /* покажите/скройте соответствующие панели по data-tab при необходимости */
  });

  /* ---- Переключатель вид: сетка / список ---- */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-view]');
    if (!btn) return;
    var bar = btn.closest('.sf-view');
    bar.querySelectorAll('[data-view]').forEach(function (b) { b.classList.toggle('is-active', b === btn); });
    var results = document.getElementById('mse2_results');
    if (!results) return;
    var grid = btn.getAttribute('data-view') === 'grid';
    results.classList.toggle('sf-grid', grid);
    results.classList.toggle('sf-grid--4', grid);
    results.classList.toggle('sf-list', !grid);
    /* ПРИМЕЧАНИЕ: для списка перерисуйте товары чанком tpl.msProductRow
       (через mse2 &tpl или отдельный AJAX). */
  });

  /* ---- Добавление в корзину (заглушка → подключите miniShop2 AJAX) ---- */
  document.addEventListener('click', function (e) {
    var add = e.target.closest('[data-add-to-cart]');
    if (!add) return;
    e.preventDefault();
    var id = add.getAttribute('data-add-to-cart');
    /* miniShop2: отправьте форму ms2_form или вызовите
       miniShop2.send(...) c action 'cart/add'. */
    if (window.miniShop2 && window.jQuery) {
      window.jQuery.post(document.location.href, { id: id, count: 1, ms2_action: 'cart/add' });
    }
  });
})();
