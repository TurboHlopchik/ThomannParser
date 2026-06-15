{*
  ЧАНК: tpl.msCartRow — строка товара в корзине (msCart)
  Поля msCart: [[+id]] [[+pagetitle]] [[+price]] [[+count]] [[+cost]]
               [[+uri]] [[+thumb]] [[+article]] [[+remains]]
*}
<div class="sf-cart-row" data-cart-row="[[+id]]">
    <a class="sf-cart-row__img" href="[[+uri]]">[[+thumb:notempty=`<img src="[[+thumb]]" alt="[[+pagetitle]]">` :default=`<i class="ti ti-music"></i>`]]</a>
    <div class="sf-cart-row__info">
        <div class="sf-cart-row__brand">[[+vendor]]</div>
        <a class="sf-cart-row__name" href="[[+uri]]">[[+pagetitle]]</a>
        <div class="sf-cart-row__sku">Артикул: [[+article]]</div>
        [[+remains:gt=`0`?
            &then=`<span class="ms-badge ms-badge--success">В наличии</span>`
            &else=`<span class="ms-badge ms-badge--neutral">Под заказ</span>`
        ]]
    </div>
    <div class="sf-cart-row__right">
        <span class="sf-cart-row__price">[[+cost:msPrice]] ₽</span>
        <div class="ms-qty">
            <button class="ms-qty__btn" type="button" data-cart-minus="[[+id]]">−</button>
            <span class="ms-qty__val">[[+count]]</span>
            <button class="ms-qty__btn" type="button" data-cart-plus="[[+id]]">+</button>
        </div>
        <button class="ms-icb ms-icb--sm ms-icb--plain" type="button" data-cart-remove="[[+id]]" aria-label="Удалить"><i class="ti ti-trash"></i></button>
    </div>
</div>
