{*
  ============================================================
  ЧАНК: tpl.msProductRow  —  карточка товара для списка (горизонтально)
  Используется как &tpl у [[!msProducts]] при отображении списком.
  Поля — те же, что в tpl.msProductTile.
  ============================================================
*}
<div class="sf-listcard">
    <a class="sf-listcard__media" href="[[+uri]]">
        [[+badge:notempty=`<span class="sf-listcard__badge"><span class="ms-badge ms-badge--[[+badge:split=`:`:0]]">[[+badge:split=`:`:1]]</span></span>`]]
        <span class="sf-listcard__fav" data-fav="[[+id]]" role="button" aria-label="В избранное"><i class="ti ti-heart"></i></span>
        [[+image:notempty=`<img src="[[+image]]" alt="[[+pagetitle]]">` :default=`<i class="ti ti-music sf-listcard__ph"></i>`]]
    </a>

    <a class="sf-listcard__body" href="[[+uri]]">
        <div class="sf-listcard__name">[[+pagetitle]]</div>
        [[+article:notempty=`<div class="sf-listcard__sub">[[+article]]</div>`]]
        <span class="ms-rating"><span class="ms-rating__stars">[[+rating:default=`0`:cmiStars]]</span>[[+count_reviews:notempty=`<span class="ms-rating__count">[[+rating]] ([[+count_reviews]])</span>`]]</span>
        [[+introtext:notempty=`<p class="sf-listcard__desc">[[+introtext]]</p>`]]
        [[+remains:gt=`0`?
            &then=`<div class="sf-listcard__stock"><span class="sf-listcard__dot sf-listcard__dot--in"></span> В наличии</div>`
            &else=`<div class="sf-listcard__stock"><span class="sf-listcard__dot sf-listcard__dot--order"></span> Под заказ</div>`
        ]]
    </a>

    <div class="sf-listcard__buy">
        <div class="sf-listcard__prices">
            <span class="sf-listcard__price">[[+price:msPrice]] ₽</span>
            [[+old_price:notempty=`<span class="sf-listcard__old">[[+old_price:msPrice]] ₽</span>`]]
        </div>
        <button class="ms-btn ms-btn--md ms-btn--block [[+remains:gt=`0`? &then=`ms-btn--primary` &else=`ms-btn--outline`]]" type="button" data-add-to-cart="[[+id]]">
            <i class="ti ti-shopping-cart"></i> [[+remains:gt=`0`? &then=`В корзину` &else=`Под заказ`]]
        </button>
        <button class="sf-listcard__favlink" type="button" data-fav="[[+id]]"><i class="ti ti-heart"></i> В избранное</button>
    </div>
</div>
