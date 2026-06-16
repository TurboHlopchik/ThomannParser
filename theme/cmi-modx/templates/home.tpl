{*
  ============================================================
  ШАБЛОН: home  —  Главная
  Назначается ресурсу «Главная» (id 1). Использует base.tpl как
  обёртку (через свойство «content» — здесь это содержимое <main>).
  Если используете базовый шаблон отдельно — перенесите <head>/шапку
  из base.tpl. Ниже — только контент главной.

  Сниппеты:
    [[!msProducts]]  — выборки товаров (хиты, новинки)
    [[!pdoResources]] — бренды
  ============================================================
*}
[[$doc_head]]
<div class="sf-wrap">

    {* ---------- БАННЕР + ПРОМО ---------- *}
    <section class="sf-hero-grid">
        <a class="sf-banner" href="[[~2]]">
            <div class="sf-banner__body">
                <h1>Профессиональные<br>валторны</h1>
                <p class="sf-banner__brands">Yamaha, Hans Hoyer, Holton</p>
                <p class="sf-banner__note">Для студентов и профессионалов</p>
                <span class="sf-banner__cta">Смотреть каталог</span>
            </div>
            <i class="ti ti-music sf-banner__art"></i>
            <span class="sf-banner__dots"><i></i><i></i><i></i></span>
        </a>
        <div class="sf-hero-side">
            <a class="sf-promo sf-promo--soft sf-promo--wide" href="[[~20]]">
                <div class="sf-promo__body">
                    <h3>Рассрочка 0%</h3>
                    <p class="sf-promo__big">на 6 месяцев</p>
                    <p class="sf-promo__note">На все инструменты и аксессуары</p>
                    <span class="sf-promo__cta">Подробнее</span>
                </div>
                <i class="ti ti-music sf-promo__art"></i>
            </a>
            <div class="sf-hero-side__row">
                <a class="sf-promo sf-promo--accent" href="[[~29]]">
                    <div class="sf-promo__body">
                        <h3>Скидки до 30%</h3>
                        <p class="sf-promo__note">На выделенный ассортимент</p>
                        <span class="sf-promo__cta sf-promo__cta--light">Смотреть</span>
                    </div>
                    <i class="ti ti-music sf-promo__art sf-promo__art--sm"></i>
                </a>
                <a class="sf-promo sf-promo--soft" href="[[~30]]">
                    <div class="sf-promo__body">
                        <h3>Ноты</h3>
                        <p class="sf-promo__note">Более 100 000 изданий</p>
                        <span class="sf-promo__cta">Перейти</span>
                    </div>
                    <i class="ti ti-file-music sf-promo__art sf-promo__art--sm"></i>
                </a>
            </div>
        </div>
    </section>

    {* ---------- ПОПУЛЯРНЫЕ КАТЕГОРИИ (pdoMenu по каталогу) ---------- *}
    <section class="sf-section">
        <div class="sf-section__head">
            <h2 class="sf-section__title">Популярные категории</h2>
            <a class="sf-section__link" href="[[~2]]">Смотреть все <i class="ti ti-chevron-right"></i></a>
        </div>
        <div class="sf-circles">
            [[!pdoMenu? &parents=`2` &level=`1` &limit=`8` &tpl=`tpl.circleCat`]]
        </div>
    </section>

    {* ---------- ХИТЫ ПРОДАЖ (msProducts с фильтром по TV «hit») ---------- *}
    <section class="sf-section">
        <div class="sf-section__head">
            <h2 class="sf-section__title">Хиты продаж</h2>
            <a class="sf-section__link" href="[[~2]]">Смотреть все <i class="ti ti-chevron-right"></i></a>
        </div>
        <div class="sf-row6">
            [[!msProducts?
                &parents=`2`
                &tv.hit=`1`
                &limit=`6`
                &tpl=`tpl.msProductTile`
            ]]
        </div>
    </section>

    {* ---------- СПЕЦПРЕДЛОЖЕНИЯ ---------- *}
    <section class="sf-section">
        <div class="sf-section__head"><h2 class="sf-section__title">Специальные предложения</h2></div>
        <div class="sf-offers">
            <a class="sf-offer sf-offer--accent" href="[[~29]]"><h3>Весенние скидки<br>до 25%</h3><p>На духовые инструменты</p><span class="sf-offer__cta sf-offer__cta--light">Выбрать инструмент</span></a>
            <a class="sf-offer sf-offer--soft" href="[[~31]]"><h3>Комплекты выгоднее</h3><p>Экономия до 15% · инструмент + аксессуары</p><span class="sf-offer__cta">Смотреть комплекты</span></a>
            <a class="sf-offer sf-offer--soft" href="[[~12]]"><h3>Бесплатная доставка</h3><p>от 10 000 ₽ · по всей России</p><span class="sf-offer__cta">Подробнее</span></a>
        </div>
    </section>

    {* ---------- НОВИНКИ ---------- *}
    <section class="sf-section">
        <div class="sf-section__head">
            <h2 class="sf-section__title">Новинки</h2>
            <a class="sf-section__link" href="[[~2]]">Смотреть все <i class="ti ti-chevron-right"></i></a>
        </div>
        <div class="sf-row6">
            [[!msProducts? &parents=`2` &sortby=`createdon` &sortdir=`DESC` &limit=`6` &tpl=`tpl.msProductTile`]]
        </div>
    </section>

    {* ---------- ОФИЦИАЛЬНЫЕ БРЕНДЫ ---------- *}
    <section class="sf-section">
        <div class="sf-section__head">
            <h2 class="sf-section__title">Официальные бренды</h2>
            <a class="sf-section__link" href="[[~3]]">Смотреть все <i class="ti ti-chevron-right"></i></a>
        </div>
        <div class="sf-brandstrip">
            [[!pdoResources? &parents=`3` &limit=`8` &tpl=`tpl.brandLogo` &includeTVs=`logo`]]
        </div>
    </section>

    {* ---------- SEO-ТЕКСТ (поле content ресурса) ---------- *}
    <section class="sf-seo">[[*content]]</section>
</div>
[[$doc_foot]]
