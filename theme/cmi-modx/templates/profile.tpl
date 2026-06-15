{*
  ============================================================
  ШАБЛОН: profile  —  Личный кабинет
  Назначается ресурсу «Профиль» (id 16). Доступ — только
  авторизованным; гостя редиректьте на «Вход» (Login сниппет
  или ifLoggedin с &else-редиректом).

  Сниппеты:
    [[!Profile]]       — данные текущего пользователя (Login пакет)
    [[!msOrders]]      — список заказов пользователя (miniShop2)
    [[!UpdateProfile]] — форма редактирования профиля (Login)
  Для юрлиц («Партнёр») выводится блок реквизитов компании
  (доп. поля профиля: company, inn, kpp, legal_address, contact).
  ============================================================
*}
[[!ifLoggedin? &else=`[[!Login? &loginResourceId=`17`]]`]]

<div class="sf-wrap">
    <nav class="ms-crumbs" style="margin-bottom:16px">
        <a href="[[~1]]">Главная</a><span class="ms-crumbs__sep">›</span>
        <span class="ms-crumbs__current">Личный кабинет</span>
    </nav>
    <h1 class="sf-cat-title" style="margin-bottom:24px">Личный кабинет</h1>

    <div class="sf-acc-body">

        {* ---------- БОКОВОЕ МЕНЮ ---------- *}
        <aside class="sf-acc-nav">
            <div class="sf-acc-card">
                <div class="sf-acc-avatar"><i class="ti ti-user"></i></div>
                <div class="sf-acc-card__name">[[!+fullname:default=`[[!+username]]`]]</div>
                <div class="sf-acc-card__mail">[[!+email]]</div>
                [[!ifLoggedin:isMemberOf=`Партнёр`? &then=`<span class="sf-acc-card__badge"><span class="ms-badge ms-badge--accent">Партнёр · юрлицо</span></span>`]]
            </div>
            <nav class="sf-acc-menu">
                <a class="sf-acc-menu__item is-active" href="[[~16]]"><i class="ti ti-package"></i> Мои заказы</a>
                <a class="sf-acc-menu__item" href="[[~16]]?section=profile"><i class="ti ti-user"></i> Личные данные</a>
                <a class="sf-acc-menu__item" href="[[~14]]"><i class="ti ti-heart"></i> Избранное</a>
                <a class="sf-acc-menu__item" href="[[~16]]?section=addresses"><i class="ti ti-map-pin"></i> Адреса доставки</a>
                [[!ifLoggedin:isMemberOf=`Партнёр`? &then=`<a class="sf-acc-menu__item" href="[[~16]]?section=company"><i class="ti ti-building-bank"></i> Реквизиты компании</a>`]]
                <a class="sf-acc-menu__item sf-acc-menu__item--exit" href="[[~1]]?logout=true&service=logout"><i class="ti ti-logout-2"></i> Выйти</a>
            </nav>
        </aside>

        {* ---------- ОСНОВНАЯ КОЛОНКА ---------- *}
        <div class="sf-acc-main">
            <h2 class="sf-acc-h">Мои заказы</h2>

            {* Список заказов miniShop2 текущего пользователя *}
            <div class="sf-orders">
                [[!msOrders? &tpl=`tpl.accOrderCard` &limit=`20`]]
            </div>

            {* --- Заглушка пустого состояния (если заказов нет) ---
            <div class="ms-empty">
                <i class="ti ti-package ms-empty__icon"></i>
                <div class="ms-empty__title">Заказов пока нет</div>
                <div class="ms-empty__msg">Оформите первый заказ из каталога.</div>
                <div class="ms-empty__action"><a class="ms-btn ms-btn--md ms-btn--primary" href="[[~2]]">В каталог</a></div>
            </div>
            *}
        </div>
    </div>
</div>
