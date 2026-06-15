{*
  ============================================================
  ЧАНК: tpl.msProductTile  —  плитка товара для сетки
  Используется в &tpl сниппета [[!msProducts]] / [[!pdoResources]].
  Поля miniShop2: [[+pagetitle]] [[+uri]] [[+price]] [[+old_price]]
                  [[+image]] [[+rating]] [[+count_reviews]]
  Кастомные поля (TV / доп. поля товара по ТЗ):
    [[+sku_internal]]  — внутренний артикул
    [[+price_b2b]]     — цена для юрлиц
    [[+remains]]       — наличие на собственном складе (число)
    [[+brand]]         — бренд
  Бейдж: задайте TV `badge` со значением вида "violet:Хит" /
         "sale:−12%" / "success:Новинка".
  ============================================================
*}
<div class="ms-pc">
    <div class="ms-pc__media">
        [[+badge:notempty=`<span class="ms-pc__badge"><span class="ms-badge ms-badge--[[+badge:split=`:`:0]]">[[+badge:split=`:`:1]]</span></span>`]]
        <button class="ms-pc__fav" type="button" aria-label="В избранное" data-fav="[[+id]]"><span class="ms-icb ms-icb--sm ms-icb--plain"><i class="ti ti-heart"></i></span></button>
        <a href="[[+uri]]">
            [[+image:notempty=`<img src="[[+image]]" alt="[[+pagetitle]]">` :default=`<i class="ti ti-music ms-pc__ph"></i>`]]
        </a>
    </div>

    [[+brand:notempty=`<div class="ms-pc__brand">[[+brand]]</div>`]]
    <a class="ms-pc__name" href="[[+uri]]">[[+pagetitle]]</a>
    [[+article:notempty=`<div class="ms-pc__sub">[[+article]]</div>`]]

    {* Рейтинг: 5 звёзд, заполнение по [[+rating]] (0..5) *}
    <span class="ms-rating"><span class="ms-rating__stars">
        [[+rating:default=`0`:cmiStars]]
    </span>[[+count_reviews:notempty=`<span class="ms-rating__count">[[+rating]] ([[+count_reviews]])</span>`]]</span>

    <div class="ms-pc__prices">
        <span class="ms-pc__price">[[+price:msPrice]] ₽</span>
        [[+old_price:notempty=`<span class="ms-pc__old">[[+old_price:msPrice]] ₽</span>`]]
    </div>

    {* Наличие: >0 — в наличии (зелёная точка), иначе под заказ (оранжевая) *}
    [[+remains:gt=`0`?
        &then=`<div class="ms-pc__stock"><span class="ms-pc__dot ms-pc__dot--in"></span> В наличии</div>`
        &else=`<div class="ms-pc__stock"><span class="ms-pc__dot ms-pc__dot--order"></span> Под заказ</div>`
    ]]

    <div class="ms-pc__foot">
        <button class="ms-pc__carticon" type="button" data-add-to-cart="[[+id]]">
            <span class="ms-pc__carticon-circle"><i class="ti ti-shopping-cart"></i></span>
            <span class="ms-pc__carticon-label">[[+remains:gt=`0`? &then=`В корзину` &else=`Под заказ`]]</span>
        </button>
    </div>
</div>
