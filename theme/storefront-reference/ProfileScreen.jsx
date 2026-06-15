/* Profile / personal account screen. Private buyer + B2B «Партнёр». */
const {
  Badge: PrBadge, Button: PrButton, Input: PrInput, EmptyState: PrEmpty,
} = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStatePr } = React;

const fmtPr = (n) => n.toLocaleString('ru-RU') + ' ₽';

/* order status → badge variant */
const ORDER_STATUS = {
  'новый':       'violet',
  'в обработке': 'warning',
  'подтверждён': 'accent',
  'отправлен':   'accent',
  'завершён':    'success',
  'отменён':     'neutral',
};

const PROFILE_DATA = {
  name: 'Алексей Соколов',
  email: 'a.sokolov@example.com',
  phone: '+7 916 000-00-00',
  partner: false,
  company: {
    name: 'ООО «Гармония»', inn: '7701234567', kpp: '770101001',
    address: '125009, Москва, ул. Тверская, д. 1', contact: 'Соколов А. В.',
  },
  orders: [
    { id: '10458', date: '02.06.2026', status: 'в обработке', total: 192390, items: 2 },
    { id: '10412', date: '21.05.2026', status: 'отправлен', total: 84990, items: 1 },
    { id: '10387', date: '14.05.2026', status: 'завершён', total: 259990, items: 1 },
    { id: '10301', date: '28.04.2026', status: 'отменён', total: 6900, items: 1 },
  ],
};

function AccountNav({ active, setActive, partner, onLogout }) {
  const items = [
    ['orders', 'Мои заказы', 'package'],
    ['profile', 'Личные данные', 'user'],
    ['favorites', 'Избранное', 'heart'],
    ['addresses', 'Адреса доставки', 'map-pin'],
    partner ? ['company', 'Реквизиты компании', 'building-bank'] : null,
  ].filter(Boolean);
  return (
    <aside className="sf-acc-nav">
      <div className="sf-acc-card">
        <div className="sf-acc-avatar"><i className="ti ti-user"></i></div>
        <div className="sf-acc-card__name">{PROFILE_DATA.name}</div>
        <div className="sf-acc-card__mail">{PROFILE_DATA.email}</div>
        {partner && <span className="sf-acc-card__badge"><PrBadge variant="accent">Партнёр · юрлицо</PrBadge></span>}
      </div>
      <nav className="sf-acc-menu">
        {items.map(([id, label, icon]) => (
          <button key={id} className={`sf-acc-menu__item ${active === id ? 'is-active' : ''}`} onClick={() => setActive(id)}>
            <i className={`ti ti-${icon}`}></i> {label}
          </button>
        ))}
        <button className="sf-acc-menu__item sf-acc-menu__item--exit" onClick={onLogout}>
          <i className="ti ti-logout-2"></i> Выйти
        </button>
      </nav>
    </aside>
  );
}

function OrdersPanel({ go }) {
  const orders = PROFILE_DATA.orders;
  if (!orders.length) {
    return <PrEmpty icon="package" title="Заказов пока нет" message="Оформите первый заказ из каталога."
      action={<PrButton onClick={() => go('catalog')}>В каталог</PrButton>} />;
  }
  return (
    <div className="sf-orders">
      {orders.map((o) => (
        <div className="sf-order-card" key={o.id}>
          <div className="sf-order-card__main">
            <div className="sf-order-card__top">
              <span className="sf-order-card__num">Заказ №{o.id}</span>
              <PrBadge variant={ORDER_STATUS[o.status]}>{o.status}</PrBadge>
            </div>
            <div className="sf-order-card__meta">от {o.date} · {o.items} тов.</div>
          </div>
          <div className="sf-order-card__right">
            <span className="sf-order-card__total">{fmtPr(o.total)}</span>
            <button className="sf-order-card__link" onClick={() => go('product')}>Подробнее <i className="ti ti-chevron-right"></i></button>
          </div>
        </div>
      ))}
    </div>
  );
}

function ProfilePanel() {
  return (
    <div className="sf-acc-form">
      <div className="sf-acc-form__grid">
        <PrInput label="Имя и фамилия" defaultValue={PROFILE_DATA.name} />
        <PrInput label="Телефон" defaultValue={PROFILE_DATA.phone} iconLeft="phone" />
        <PrInput label="Email" defaultValue={PROFILE_DATA.email} iconLeft="mail" />
        <PrInput label="Дата рождения" placeholder="дд.мм.гггг" iconLeft="calendar" />
      </div>
      <div className="sf-acc-form__actions">
        <PrButton iconLeft="device-floppy">Сохранить</PrButton>
        <PrButton variant="ghost">Сменить пароль</PrButton>
      </div>
    </div>
  );
}

function CompanyPanel() {
  const c = PROFILE_DATA.company;
  return (
    <div className="sf-acc-form">
      <div className="sf-acc-note"><i className="ti ti-info-circle"></i> Для юрлиц доступны отдельные цены и оплата по счёту. Изменение реквизитов подтверждает менеджер.</div>
      <div className="sf-acc-form__grid">
        <PrInput label="Название компании" defaultValue={c.name} />
        <PrInput label="Контактное лицо" defaultValue={c.contact} />
        <PrInput label="ИНН" defaultValue={c.inn} required />
        <PrInput label="КПП" defaultValue={c.kpp} required />
        <PrInput label="Юридический адрес" defaultValue={c.address} className="sf-acc-form__wide" />
      </div>
      <div className="sf-acc-form__actions">
        <PrButton iconLeft="device-floppy">Сохранить</PrButton>
      </div>
    </div>
  );
}

function AddressesPanel() {
  return (
    <div className="sf-acc-form">
      <div className="sf-addr-list">
        <div className="sf-addr-card">
          <div><b>Основной адрес</b><span>125009, Москва, ул. Тверская, д. 1, кв. 10</span></div>
          <button className="sf-order-card__link"><i className="ti ti-pencil"></i></button>
        </div>
      </div>
      <PrButton variant="outline" iconLeft="plus">Добавить адрес</PrButton>
    </div>
  );
}

function FavoritesPanel({ go }) {
  return <PrEmpty icon="heart" title="В избранном пока пусто"
    message="Добавляйте инструменты в избранное, чтобы вернуться к ним позже."
    action={<PrButton onClick={() => go('catalog')}>В каталог</PrButton>} />;
}

function ProfileScreen({ go, onLogout, partner = PROFILE_DATA.partner }) {
  const [active, setActive] = useStatePr('orders');
  const titles = {
    orders: 'Мои заказы', profile: 'Личные данные', favorites: 'Избранное',
    addresses: 'Адреса доставки', company: 'Реквизиты компании',
  };
  return (
    <div className="sf-page">
      <div className="sf-wrap">
        <div className="sf-pagehead">
          <nav className="ms-crumbs">
            <a href="#" onClick={(e) => { e.preventDefault(); go('home'); }}>Главная</a>
            <span className="ms-crumbs__sep">›</span>
            <span className="ms-crumbs__current">Личный кабинет</span>
          </nav>
          <h1 className="sf-pagehead__title">Личный кабинет</h1>
        </div>
        <div className="sf-acc-body">
          <AccountNav active={active} setActive={setActive} partner={partner} onLogout={onLogout} />
          <div className="sf-acc-main">
            <h2 className="sf-acc-h">{titles[active]}</h2>
            {active === 'orders' && <OrdersPanel go={go} />}
            {active === 'profile' && <ProfilePanel />}
            {active === 'favorites' && <FavoritesPanel go={go} />}
            {active === 'addresses' && <AddressesPanel />}
            {active === 'company' && <CompanyPanel />}
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { ProfileScreen });
