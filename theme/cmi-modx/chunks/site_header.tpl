{*
  ============================================================
  ЧАНК: site_header  —  шапка сайта
  Сниппеты:
    [[!msCart]]        — счётчик и сумма корзины (miniShop2)
    [[!pdoMenu]]       — верхнее меню каталога (pdoTools)
    [[!mSearch2]]      — поисковая форма (mSearch2), action на ресурс поиска
  Замените ID ресурсов в скобках [[~ID]] на реальные.
  ============================================================
*}
<header class="sf-header">

    {* ---------- ВЕРХНЯЯ СТРОКА ---------- *}
    <div class="sf-wrap sf-header__top">
        <button class="sf-burger" aria-label="Меню" data-drawer-open><i class="ti ti-menu-2"></i></button>

        <a class="sf-logo" href="[[~1]]" aria-label="ЦМИ — на главную">
            <span class="sf-logo__mark"><i class="ti ti-building-store"></i></span>
            <span class="sf-logo__text">
                <span class="sf-logo__name">ЦМИ</span>
                <span class="sf-logo__sub">Центр Музыкальных<br>Инструментов</span>
            </span>
        </a>

        {* Поисковая форма mSearch2. &tpl — чанк автоподсказок; action ведёт на ресурс поиска *}
        <form class="sf-search" action="[[~[[++mse2_results_id:default=`1`]]]]" method="get">
            <input type="text" name="query" value="[[!+mse2.query]]" placeholder="Поиск инструментов, брендов, категорий…" autocomplete="off">
            <button class="sf-search__btn" type="submit" aria-label="Найти"><i class="ti ti-search"></i></button>
        </form>

        <div class="sf-actions">
            <a class="sf-action sf-action--sm" href="[[~12]]"><i class="ti ti-truck-delivery"></i><span>Доставка и оплата</span></a>
            <a class="sf-action sf-action--sm" href="[[~13]]"><i class="ti ti-map-pin"></i><span>Магазины</span></a>
            <a class="sf-action sf-action--badge" href="[[~14]]" data-count="[[!msFavoritesCount]]"><i class="ti ti-heart"></i><span>Избранное</span></a>

            {* Корзина: msCart с кастомным чанком-обёрткой для счётчика *}
            <a class="sf-action sf-action--badge" href="[[~15]]" data-count="[[!msCart? &tpl=`tpl.msMiniCartCount`]]"><i class="ti ti-shopping-cart"></i><span>Корзина</span></a>

            {* Гость → Вход/Регистрация; авторизован → Профиль. isLoggedIn управляет выводом *}
            [[!ifLoggedin? &then=`
                <a class="sf-action" href="[[~16]]"><i class="ti ti-user"></i><span>Профиль</span></a>
            ` &else=`
                <div class="sf-auth">
                    <a class="sf-auth__login" href="[[~17]]"><i class="ti ti-login-2"></i> Вход</a>
                    <a class="sf-auth__reg" href="[[~18]]">Регистрация</a>
                </div>
            `]]
        </div>
    </div>

    {* ---------- СТРОКА НАВИГАЦИИ ---------- *}
    <div class="sf-nav">
        <div class="sf-wrap sf-nav__in">
            <a class="sf-nav__catalog" href="[[~2]]"><i class="ti ti-menu-2"></i> Каталог</a>

            {* pdoMenu: верхний уровень каталога. &tpl/&tplActive — чанки пунктов меню *}
            <nav class="sf-nav__links">
                [[!pdoMenu?
                    &parents=`2`
                    &level=`1`
                    &tpl=`tpl.navLink`
                    &tplActive=`tpl.navLinkActive`
                ]]
            </nav>

            <div class="sf-nav__phone">
                <a href="tel:[[++cmi_phone_raw:default=`88005501025`]]">[[++cmi_phone:default=`8 (800) 550-10-25`]]</a>
                <span>[[++cmi_hours:default=`Ежедневно 10:00 — 20:00`]]</span>
            </div>
        </div>
    </div>
</header>

{* ---------- МОБИЛЬНОЕ МЕНЮ (drawer) ---------- *}
<div class="sf-drawer" hidden data-drawer>
    <div class="sf-drawer__panel">
        <div class="sf-drawer__head"><span>Меню</span><button aria-label="Закрыть" data-drawer-close><i class="ti ti-x"></i></button></div>

        <div class="sf-drawer__group">Каталог</div>
        [[!pdoMenu? &parents=`2` &level=`1` &tpl=`tpl.drawerLink`]]

        <div class="sf-drawer__group">Сервис</div>
        <a class="sf-drawer__item sf-drawer__item--ico" href="[[~12]]"><i class="ti ti-truck-delivery"></i> Доставка и оплата</a>
        <a class="sf-drawer__item sf-drawer__item--ico" href="[[~13]]"><i class="ti ti-map-pin"></i> Магазины</a>
        <a class="sf-drawer__item sf-drawer__item--ico" href="[[~14]]"><i class="ti ti-heart"></i> Избранное</a>
        <a class="sf-drawer__item sf-drawer__item--ico" href="[[~15]]"><i class="ti ti-shopping-cart"></i> Корзина</a>

        <div class="sf-drawer__group">Личный кабинет</div>
        [[!ifLoggedin? &then=`
            <a class="sf-drawer__item sf-drawer__item--ico" href="[[~16]]"><i class="ti ti-user"></i> Профиль</a>
        ` &else=`
            <div class="sf-drawer__auth">
                <a class="sf-auth__login" href="[[~17]]"><i class="ti ti-login-2"></i> Вход</a>
                <a class="sf-auth__reg" href="[[~18]]">Регистрация</a>
            </div>
        `]]

        <div class="sf-drawer__group">Контакты</div>
        <a class="sf-drawer__phone" href="tel:[[++cmi_phone_raw]]">[[++cmi_phone]]</a>
        <span class="sf-drawer__hours">[[++cmi_hours]]</span>
        <a class="sf-drawer__mail" href="mailto:[[++cmi_email:default=`info@cmi.ru`]]"><i class="ti ti-mail"></i> [[++cmi_email]]</a>
        <div class="sf-drawer__social">
            <a href="[[++cmi_tg]]" aria-label="Telegram"><i class="ti ti-brand-telegram"></i></a>
            <a href="[[++cmi_vk]]" aria-label="VK"><i class="ti ti-brand-vk"></i></a>
            <a href="[[++cmi_yt]]" aria-label="YouTube"><i class="ti ti-brand-youtube"></i></a>
        </div>
    </div>
</div>
