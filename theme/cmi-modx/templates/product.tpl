{*
  ============================================================
  ШАБЛОН: product  —  Карточка товара
  Назначается товарам miniShop2. Все [[+поле]] доступны напрямую
  как поля ресурса-товара ([[*price]], [[*article]] и т.д.) —
  ниже используется синтаксис [[*field]] для полей текущего товара.

  Сниппеты:
    [[!pdoCrumbs]]      — хлебные крошки
    [[!msGallery]]      — галерея изображений товара
    [[!msProducts]]     — сопутствующие товары
  Доп. поля по ТЗ: [[*article]] (внутр. артикул), [[*price_b2b]],
    [[*remains]] (наличие на складе).
  ============================================================
*}
<div class="sf-wrap">

    <nav class="ms-crumbs" aria-label="breadcrumb">
        [[!pdoCrumbs? &tpl=`tpl.crumbLink` &tplCurrent=`tpl.crumbCurrent` &outputSeparator=``]]
    </nav>

    <div class="sf-prodtop">
        [[*badge:notempty=`<span class="ms-badge ms-badge--[[*badge:split=`:`:0]]">[[*badge:split=`:`:1]]</span>`]]
        <h1 class="sf-prod-title">[[*pagetitle]]</h1>
        [[*introtext:notempty=`<div class="sf-prod-subline">[[*introtext]]</div>`]]
        <div class="sf-prod-meta">
            <span class="ms-rating"><span class="ms-rating__stars">[[*rating:default=`0`:cmiStars]]</span></span>
            <span class="sf-prod-meta__rate">[[*rating]]</span>
            <span class="sf-prod-meta__rev">([[*count_reviews:default=`0`]] отзывов)</span>
            <span class="sf-prod-meta__sku">Артикул: [[*article]]</span>
        </div>
    </div>

    <div class="sf-prod">
        <div class="sf-prod__left">
            {* Галерея miniShop2 *}
            <div class="sf-gallery">
                <div class="sf-gallery__thumbs">
                    [[!msGallery? &tpl=`tpl.galleryThumb` &limit=`5`]]
                </div>
                <div class="sf-gallery__main">
                    <button class="sf-gallery__nav sf-gallery__nav--prev" type="button" aria-label="Назад"><i class="ti ti-chevron-left"></i></button>
                    [[*image:notempty=`<img src="[[*image]]" alt="[[*pagetitle]]">` :default=`<i class="ti ti-music sf-gallery__hero"></i>`]]
                    <button class="sf-gallery__nav sf-gallery__nav--next" type="button" aria-label="Вперёд"><i class="ti ti-chevron-right"></i></button>
                    <button class="sf-gallery__zoom" type="button"><i class="ti ti-arrows-maximize"></i> Увеличить</button>
                </div>
            </div>

            <div class="sf-assure">
                <div class="sf-assure__item"><i class="ti ti-shield-check"></i><div><b>Гарантия</b><span>12 месяцев</span></div></div>
                <div class="sf-assure__item"><i class="ti ti-rosette-discount-check"></i><div><b>Официальный дилер</b><span>Только оригинал</span></div></div>
                <div class="sf-assure__item"><i class="ti ti-truck"></i><div><b>Доставка</b><span>По всей России от 10 000 ₽</span></div></div>
                <div class="sf-assure__item"><i class="ti ti-refresh"></i><div><b>Возврат 14 дней</b><span>Если не подошёл</span></div></div>
            </div>
        </div>

        {* ---------- БЛОК ПОКУПКИ (msProductForm) ---------- *}
        <div class="sf-buybox">
            <form action="[[~[[*id]]]]" method="post" class="ms2_form">
                <input type="hidden" name="id" value="[[*id]]">
                <div class="sf-buybox__main">
                    [[*remains:gt=`0`?
                        &then=`<div class="sf-buybox__stock"><span class="sf-buybox__dot"></span> В наличии</div>`
                        &else=`<div class="sf-buybox__stock" style="color:var(--warning)"><span class="sf-buybox__dot" style="background:var(--warning)"></span> Под заказ</div>`
                    ]]
                    <div class="sf-buybox__price">[[*price:msPrice]] ₽</div>
                    {* Цена для юрлиц — показывать партнёрам *}
                    [[!ifLoggedin:and:isMemberOf=`Партнёр`? &then=`<div class="sf-buybox__inst">Для юрлиц: [[*price_b2b:msPrice]] ₽ · оплата по счёту</div>` &else=`<div class="sf-buybox__inst">или от [[*price:div=`6`:msPrice]] ₽ / мес. в рассрочку <i class="ti ti-info-circle"></i></div>`]]

                    <div class="sf-buybox__actions">
                        <button class="ms-btn ms-btn--lg ms-btn--primary ms-btn--block" type="submit" name="ms2_action" value="cart/add"><i class="ti ti-shopping-cart"></i> В корзину</button>
                        <button class="ms-btn ms-btn--lg ms-btn--secondary ms-btn--block" type="submit" name="ms2_action" value="order/oneclick"><i class="ti ti-bolt"></i> Купить в 1 клик</button>
                    </div>
                    <div class="sf-buybox__links">
                        <button type="button" data-fav="[[*id]]"><i class="ti ti-heart"></i> Добавить в избранное</button>
                    </div>
                </div>
            </form>

            <div class="sf-buybox__panel">
                <div class="sf-buybox__panel-row">
                    <div><b>Рассрочка без переплат</b><span>от [[*price:div=`6`:msPrice]] ₽ / мес. на 6 месяцев</span></div>
                    <a class="ms-btn ms-btn--sm ms-btn--ghost" href="[[~20]]">Подробнее</a>
                </div>
            </div>

            <div class="sf-buybox__panel sf-buybox__consult">
                <div><b>Есть вопросы?</b><span>Специалисты помогут подобрать инструмент</span><a class="sf-buybox__consult-cta" href="[[~22]]">Получить консультацию</a></div>
                <i class="ti ti-music"></i>
            </div>
        </div>
    </div>

    {* ---------- ТАБЫ ---------- *}
    <div class="sf-prod-tabs">
        <div class="ms-tabs" role="tablist">
            <button class="ms-tabs__tab" aria-selected="true" data-tab="desc">Описание</button>
            <button class="ms-tabs__tab" aria-selected="false" data-tab="specs">Характеристики</button>
            <button class="ms-tabs__tab" aria-selected="false" data-tab="reviews">Отзывы ([[*count_reviews:default=`0`]])</button>
            <button class="ms-tabs__tab" aria-selected="false" data-tab="delivery">Доставка и оплата</button>
        </div>
    </div>
    <div class="sf-prod-tabs__body">
        <div class="sf-prod-grid3">
            <div>
                <h4 class="sf-prod-h">О товаре</h4>
                <div class="sf-prose">[[*content]]</div>
            </div>
            <div>
                <h4 class="sf-prod-h">Характеристики</h4>
                {* Характеристики — выводите через msProductOptions / свои TV *}
                <table class="sf-spec"><tbody>
                    [[!msProductOptions? &tpl=`tpl.specRow`]]
                </tbody></table>
            </div>
            <div>
                <h4 class="sf-prod-h">В комплекте</h4>
                <div class="sf-kit">
                    <div class="sf-kit__item"><span class="sf-kit__img"><i class="ti ti-briefcase"></i></span><b>Кейс</b><span>В комплекте</span></div>
                    <div class="sf-kit__item"><span class="sf-kit__img"><i class="ti ti-microphone-2"></i></span><b>Мундштук</b><span>В комплекте</span></div>
                </div>
            </div>
        </div>
    </div>

    {* ---------- СОПУТСТВУЮЩИЕ ---------- *}
    <section class="sf-section">
        <div class="sf-section__head"><h2 class="sf-section__title">С этим товаром покупают</h2></div>
        <div class="sf-row6">
            [[!msProducts? &parents=`[[*parent]]` &exclude=`[[*id]]` &limit=`6` &tpl=`tpl.msProductTile`]]
        </div>
    </section>
</div>
