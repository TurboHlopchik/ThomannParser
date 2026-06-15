{* ЧАНК: tpl.brandCard — карточка бренда (pdoResources по разделу «Бренды») *}
<a class="ms-bc" href="[[+uri]]">
    <span class="ms-bc__logo">[[+logo:notempty=`<img src="[[+logo]]" alt="[[+pagetitle]]">` :default=`[[+pagetitle:substr=`0,2`:ucase]]`]]</span>
    <span class="ms-bc__body">
        <span class="ms-bc__name">[[+pagetitle]]</span>
        [[+products_count:notempty=`<span class="ms-bc__count">[[+products_count]] товаров</span>`]]
    </span>
    <i class="ti ti-chevron-right ms-bc__arrow"></i>
</a>
