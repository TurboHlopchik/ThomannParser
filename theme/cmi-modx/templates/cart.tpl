{*
  ============================================================
  ШАБЛОН: cart  —  Корзина и оформление заказа
  Назначается ресурсу «Корзина». Онлайн-оплаты нет (по ТЗ):
  заказ сохраняется, менеджер связывается и выставляет счёт.

  Сниппеты:
    [[!msCart]]   — содержимое корзины (строки товаров)
    [[!msOrder]]  — форма оформления (доставка/получатель)
  ============================================================
*}
[[$doc_head]]
<div class="sf-wrap sf-wrap--narrow">

    <h1 class="sf-cart-title">Корзина</h1>

    {* Индикатор шагов (статический; активный шаг — «Корзина») *}
    <div class="sf-steps-wrap">
        <div class="ms-steps" role="list">
            <div class="ms-steps__step" data-state="current" role="listitem"><div class="ms-steps__line"></div><div class="ms-steps__circle">1</div><div class="ms-steps__label">Корзина</div></div>
            <div class="ms-steps__step" data-state="upcoming" role="listitem"><div class="ms-steps__line"></div><div class="ms-steps__circle">2</div><div class="ms-steps__label">Данные</div></div>
            <div class="ms-steps__step" data-state="upcoming" role="listitem"><div class="ms-steps__line"></div><div class="ms-steps__circle">3</div><div class="ms-steps__label">Доставка</div></div>
            <div class="ms-steps__step" data-state="upcoming" role="listitem"><div class="ms-steps__circle">4</div><div class="ms-steps__label">Готово</div></div>
        </div>
    </div>

    <div class="sf-cart-body">
        {* ---------- СПИСОК ТОВАРОВ ---------- *}
        <div class="sf-cart-list">
            [[!msCart? &tpl=`tpl.msCartRow`]]
            <a class="sf-cart-continue" href="[[~2]]"><i class="ti ti-arrow-left"></i> Продолжить покупки</a>
        </div>

        {* ---------- ИТОГИ + ОФОРМЛЕНИЕ ---------- *}
        <aside class="sf-summary">
            <div class="sf-summary__title">Ваш заказ</div>
            <div class="sf-summary__line"><span>Товары ([[!+msCart.total_count]])</span><span>[[!+msCart.total_cost:msPrice]] ₽</span></div>
            <div class="sf-summary__line"><span>Доставка</span><span class="sf-summary__free">Рассчитает менеджер</span></div>

            <div class="sf-promo-field">
                <input type="text" name="promo" placeholder="Промокод">
                <button type="button">Применить</button>
            </div>

            <div class="sf-summary__total"><span>Итого</span><span>[[!+msCart.total_cost:msPrice]] ₽</span></div>
            <button class="ms-btn ms-btn--lg ms-btn--primary ms-btn--block" type="submit" form="msOrderForm"><i class="ti ti-arrow-right"></i> Оформить заказ</button>
            <p class="sf-summary__note">Оплата онлайн недоступна. После оформления менеджер свяжется с вами для подтверждения и выставит счёт.</p>
        </aside>
    </div>

    {* ---------- ФОРМА ЗАКАЗА (msOrder) ---------- *}
    <div class="sf-order">
        [[!msOrder]]
    </div>
</div>
[[$doc_foot]]
