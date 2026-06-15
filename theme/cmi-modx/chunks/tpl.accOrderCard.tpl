{*
  ЧАНК: tpl.accOrderCard — карточка заказа в кабинете (msOrders)
  Поля: [[+id]] [[+num]] [[+createdon]] [[+status]] [[+cost]] [[+count]]
  Статусы по ТЗ: новый / в обработке / подтверждён / отправлен /
  завершён / отменён. Цвет бейджа задайте по [[+status_id]].
*}
<div class="sf-order-card">
    <div class="sf-order-card__main">
        <div class="sf-order-card__top">
            <span class="sf-order-card__num">Заказ №[[+num]]</span>
            <span class="ms-badge ms-badge--[[+status_id:is=`1`:then=`violet`:is=`2`:then=`warning`:is=`3`:then=`accent`:is=`4`:then=`accent`:is=`5`:then=`success`:is=`6`:then=`neutral`:default=`neutral`]]">[[+status]]</span>
        </div>
        <div class="sf-order-card__meta">от [[+createdon:date=`%d.%m.%Y`]] · [[+count]] тов.</div>
    </div>
    <div class="sf-order-card__right">
        <span class="sf-order-card__total">[[+cost:msPrice]] ₽</span>
        <a class="sf-order-card__link" href="[[~16]]?order=[[+id]]">Подробнее <i class="ti ti-chevron-right"></i></a>
    </div>
</div>
