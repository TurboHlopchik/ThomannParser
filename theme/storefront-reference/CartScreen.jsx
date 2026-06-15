/* Cart screen: checkout steps, line items, order summary, empty state. */
const {
  CheckoutSteps: CCheckoutSteps, QuantityStepper: CQty, Button: CButton,
  IconButton: CIconButton, Badge: CBadge, EmptyState: CEmptyState, Input: CInput,
  Breadcrumbs: CBreadcrumbs,
} = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStateC } = React;

const fmtC = (n) => n.toLocaleString('ru-RU') + ' ₽';

function CartRow({ item, onQty, onRemove }) {
  return (
    <div className="sf-cart-row">
      <div className="sf-cart-row__img"><i className="ti ti-music"></i></div>
      <div className="sf-cart-row__info">
        <div className="sf-cart-row__brand">{item.brand}</div>
        <div className="sf-cart-row__name">{item.name}</div>
        <div className="sf-cart-row__sku">Артикул: WND-{1000 + item.id}</div>
        {item.inStock
          ? <CBadge variant="success" icon="check">В наличии</CBadge>
          : <CBadge variant="neutral">Под заказ</CBadge>}
      </div>
      <div className="sf-cart-row__right">
        <span className="sf-cart-row__price">{fmtC(item.price * item.qty)}</span>
        <CQty value={item.qty} min={1} onChange={(n) => onQty(item.id, n)} size="sm" />
        <CIconButton icon="trash" variant="plain" size="sm" label="Удалить" onClick={() => onRemove(item.id)} />
      </div>
    </div>
  );
}

function Summary({ items, go }) {
  const subtotal = items.reduce((s, i) => s + i.price * i.qty, 0);
  const discount = items.reduce((s, i) => s + (i.oldPrice ? (i.oldPrice - i.price) * i.qty : 0), 0);
  return (
    <aside className="sf-summary">
      <div className="sf-summary__title">Ваш заказ</div>
      <div className="sf-summary__line"><span>Товары ({items.reduce((s, i) => s + i.qty, 0)})</span><span>{fmtC(subtotal + discount)}</span></div>
      {discount > 0 && <div className="sf-summary__line sf-summary__line--save"><span>Скидка</span><span>−{fmtC(discount)}</span></div>}
      <div className="sf-summary__line"><span>Доставка</span><span className="sf-summary__free">Рассчитает менеджер</span></div>

      <div className="sf-promo-field">
        <input placeholder="Промокод" />
        <button>Применить</button>
      </div>

      <div className="sf-summary__total"><span>Итого</span><span>{fmtC(subtotal)}</span></div>
      <CButton block size="lg" iconRight="arrow-right" onClick={() => {}}>Оформить заказ</CButton>
      <p className="sf-summary__note">Оплата онлайн недоступна. После оформления менеджер свяжется с вами для подтверждения и выставит счёт.</p>
    </aside>
  );
}

function CartScreen({ go, cart, setCart }) {
  const data = window.STORE_DATA.products;
  const [items, setItems] = useStateC(
    (cart && cart.length ? cart : [data[0], data[1], data[4]]).map((p) => ({ ...p, qty: p.qty || 1 }))
  );
  const onQty = (id, n) => setItems((arr) => arr.map((i) => i.id === id ? { ...i, qty: n } : i));
  const onRemove = (id) => setItems((arr) => arr.filter((i) => i.id !== id));

  return (
    <div className="sf-page">
      <div className="sf-wrap">
        <div className="sf-pagehead">
          <CBreadcrumbs items={[{ label: 'Главная', onClick: () => go('home') }, { label: 'Корзина' }]} />
          <h1 className="sf-pagehead__title">Корзина</h1>
        </div>
        {items.length > 0 && (
          <div className="sf-steps-wrap">
            <CCheckoutSteps steps={['Корзина', 'Данные', 'Доставка', 'Готово']} current={0} />
          </div>
        )}
        {items.length === 0 ? (
          <CEmptyState icon="shopping-cart" title="Корзина пуста"
            message="Добавьте товары из каталога, чтобы оформить заказ."
            action={<CButton onClick={() => go('catalog')}>В каталог</CButton>} />
        ) : (
          <div className="sf-cart-body">
            <div className="sf-cart-list">
              {items.map((it) => <CartRow key={it.id} item={it} onQty={onQty} onRemove={onRemove} />)}
              <button className="sf-cart-continue" onClick={() => go('catalog')}>
                <i className="ti ti-arrow-left"></i> Продолжить покупки
              </button>
            </div>
            <Summary items={items} go={go} />
          </div>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { CartScreen });
