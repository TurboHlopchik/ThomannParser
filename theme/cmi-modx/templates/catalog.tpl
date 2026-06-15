{*
  ============================================================
  ШАБЛОН: catalog  —  Каталог / категория
  Назначается разделам каталога. Слева — фильтры (mFilter2),
  справа — сетка/список товаров (msProducts) + пагинация.

  Сниппеты:
    [[!pdoCrumbs]]  — хлебные крошки
    [[!mFilter2]]   — фильтры (категория, бренд, цена, материал…)
    [[!msProducts]] — товары раздела (mFilter2 сам оборачивает вывод)
  ============================================================
*}
<div class="sf-wrap">

    <nav class="ms-crumbs" aria-label="breadcrumb">
        [[!pdoCrumbs? &tpl=`tpl.crumbLink` &tplCurrent=`tpl.crumbCurrent` &outputSeparator=``]]
    </nav>

    {* ---------- ХЕДЕР КАТЕГОРИИ ---------- *}
    <section class="sf-cathero">
        <div class="sf-cathero__body">
            <h1>[[*pagetitle]]</h1>
            <div class="sf-cathero__count">[[!msProducts? &parents=`[[*id]]` &limit=`0` &returnIds=`1` &toPlaceholder=`catCount`]][[+catCount:count]] товаров</div>
            [[*introtext:notempty=`<p>[[*introtext]]</p>`]]
        </div>
        <i class="ti ti-music sf-cathero__art"></i>
    </section>

    <div class="sf-cat-body">

        {* ---------- ФИЛЬТРЫ ----------
           MiniShop3-адаптация: фасеты строятся по бренду (vendor), цене и опциям
           товара. Опции импортируются парсером как option.<ключ> и привязываются
           к категории в MS3 — соответствующие фасеты `option|<ключ>` добавляются
           под конкретный раздел (наборы характеристик у категорий разные).
           Имя/синтаксис фильтрующего сниппета сверьте с версией mFilter для
           MiniShop3 (в miniShop2 это был mFilter2).
        *}
        <aside class="sf-filters">
            <div class="sf-filters__head"><span>Фильтры</span><button class="sf-filters__reset" type="button" data-mfilter-reset>Сбросить все</button></div>
            [[!mFilter2?
                &element=`mFilter2`
                &parents=`[[*id]]`
                &tplOuter=`tpl.mfilterOuter`
                &filters=`
                    ms|vendor:default;
                    ms|price:number;
                    option|body:default;
                    option|color:default
                `
                &tpls=`vendor==tpl.mfilterCheckbox`
            ]]
            <button class="ms-btn ms-btn--lg ms-btn--dark ms-btn--block" type="submit" form="mse2_filters">Показать товары</button>
        </aside>

        {* ---------- ОСНОВНАЯ КОЛОНКА ---------- *}
        <div class="sf-cat-main">
            <div class="sf-toolbar">
                <div class="sf-view">
                    <button class="is-active" type="button" data-view="grid" aria-label="Сетка"><i class="ti ti-layout-grid"></i></button>
                    <button type="button" data-view="list" aria-label="Список"><i class="ti ti-list"></i></button>
                </div>
                <div class="sf-toolbar__chips" data-active-filters></div>
                <div class="sf-toolbar__sort">
                    <div class="ms-field"><div class="ms-select-wrap">
                        <select class="ms-select" name="sort" data-sort>
                            <option value="">Сортировка: по релевантности</option>
                            <option value="price-asc">Сначала дешёвые</option>
                            <option value="price-desc">Сначала дорогие</option>
                            <option value="createdon-desc">По новизне</option>
                        </select>
                        <i class="ti ti-chevron-down"></i>
                    </div></div>
                </div>
            </div>

            {* Сетка товаров. mFilter2 перерисовывает содержимое #mse2_results *}
            <div id="mse2_results" class="sf-grid sf-grid--4">
                [[!msProducts?
                    &parents=`[[*id]]`
                    &limit=`12`
                    &tpl=`tpl.msProductTile`
                ]]
            </div>

            <div class="sf-cat-foot">
                <div class="ms-pag" id="mse2_pagination">[[!+page.nav]]</div>
                <div class="sf-perpage">
                    <span>Показывать по:</span>
                    <div class="ms-field"><div class="ms-select-wrap">
                        <select class="ms-select" data-perpage><option>12</option><option>24</option><option>48</option></select>
                        <i class="ti ti-chevron-down"></i>
                    </div></div>
                </div>
            </div>
        </div>
    </div>

    {* ---------- БЛОК-ГИД ---------- *}
    <section class="sf-guide">
        <i class="ti ti-music sf-guide__art"></i>
        <div class="sf-guide__intro">
            <h3>Как выбрать инструмент?</h3>
            <p>Для начинающих подойдут модели с простой эргономикой. Профессионалам важны материал, звучание и точная механика. Поможем подобрать инструмент под ваши задачи.</p>
            <a class="ms-btn ms-btn--md ms-btn--primary" href="[[~21]]">Читать руководство</a>
        </div>
        <div class="sf-guide__points">
            <div class="sf-guide__point"><i class="ti ti-shield-check"></i><b>Проверка перед отправкой</b><span>Каждый инструмент проходит проверку</span></div>
            <div class="sf-guide__point"><i class="ti ti-adjustments"></i><b>Подбор под задачи</b><span>Поможем выбрать под ваш уровень</span></div>
            <div class="sf-guide__point"><i class="ti ti-credit-card"></i><b>Рассрочка и кредит</b><span>Удобные условия оплаты</span></div>
        </div>
    </section>
</div>
