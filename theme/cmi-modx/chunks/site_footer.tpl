{*
  ============================================================
  ЧАНК: site_footer  —  подвал сайта
  [[!pdoMenu]] для колонок при желании; здесь — статические
  ссылки на ресурсы (замените ID [[~ID]] на реальные).
  ============================================================
*}
<footer class="sf-footer">

    {* ---------- ПРЕИМУЩЕСТВА ---------- *}
    <section class="sf-wrap sf-features">
        <div class="sf-feature"><span class="sf-feature__ico"><i class="ti ti-shield-check"></i></span><span class="sf-feature__txt"><b>Официальная гарантия</b><span>На все инструменты</span></span></div>
        <div class="sf-feature"><span class="sf-feature__ico"><i class="ti ti-package"></i></span><span class="sf-feature__txt"><b>Более 20 000 товаров</b><span>В наличии и под заказ</span></span></div>
        <div class="sf-feature"><span class="sf-feature__ico"><i class="ti ti-user-check"></i></span><span class="sf-feature__txt"><b>Консультация</b><span>Опытные музыканты</span></span></div>
        <div class="sf-feature"><span class="sf-feature__ico"><i class="ti ti-truck"></i></span><span class="sf-feature__txt"><b>Доставка</b><span>По всей России</span></span></div>
    </section>

    <div class="sf-wrap sf-footer__in">
        <div class="sf-footer__news">
            <div class="sf-footer__h">Будьте в курсе</div>
            <p>Новости, обзоры и специальные предложения</p>
            {* Подписку можно повесить на FormIt или внешний сервис *}
            <form class="sf-news-form" action="[[~[[*id]]]]" method="post">
                <input type="email" name="subscribe_email" placeholder="Ваш e-mail" required>
                <button type="submit">Подписаться</button>
            </form>
            <p class="sf-footer__fine">Нажимая «Подписаться», вы соглашаетесь с политикой конфиденциальности</p>
        </div>

        <div class="sf-footer__col">
            <div class="sf-footer__h">Покупателям</div>
            <a href="[[~12]]">Доставка и оплата</a>
            <a href="[[~19]]">Гарантия и возврат</a>
            <a href="[[~20]]">Рассрочка и кредит</a>
            <a href="[[~21]]">Помощь и FAQ</a>
            <a href="[[~22]]">Контакты</a>
        </div>

        <div class="sf-footer__col">
            <div class="sf-footer__h">О компании</div>
            <a href="[[~23]]">О нас</a>
            <a href="[[~13]]">Магазины</a>
            <a href="[[~24]]">Новости</a>
            <a href="[[~25]]">Блог</a>
            <a href="[[~26]]">Сотрудничество</a>
        </div>

        <div class="sf-footer__col">
            <div class="sf-footer__h">Контакты</div>
            <a class="sf-footer__phone" href="tel:[[++cmi_phone_raw]]">[[++cmi_phone]]</a>
            <span class="sf-footer__hours">[[++cmi_hours]]</span>
            <a class="sf-footer__mail" href="mailto:[[++cmi_email]]"><i class="ti ti-mail"></i> [[++cmi_email]]</a>
            <div class="sf-social">
                <a href="[[++cmi_tg]]" aria-label="Telegram"><i class="ti ti-brand-telegram"></i></a>
                <a href="[[++cmi_vk]]" aria-label="VK"><i class="ti ti-brand-vk"></i></a>
                <a href="[[++cmi_yt]]" aria-label="YouTube"><i class="ti ti-brand-youtube"></i></a>
            </div>
        </div>
    </div>

    <div class="sf-wrap sf-footer__legal">
        <span>© [[!+year:default=`2026`]] Центр Музыкальных Инструментов</span>
        <span class="sf-footer__legal-links"><a href="[[~27]]">Политика конфиденциальности</a><a href="[[~28]]">Пользовательское соглашение</a></span>
    </div>
</footer>
