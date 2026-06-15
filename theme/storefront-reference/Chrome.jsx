/* Storefront chrome: header (logo + search + actions), nav bar, footer. */
const { IconButton } = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStateChrome, useEffect: useEffectChrome, useRef: useRefChrome } = React;

/* Hide the header on scroll-down, reveal it immediately on scroll-up. */
function useHideOnScroll() {
  const [hidden, setHidden] = useStateChrome(false);
  useEffectChrome(() => {
    let last = window.scrollY;
    let ticking = false;
    const measure = () => {
      const h = document.querySelector('.sf-header');
      if (h) document.documentElement.style.setProperty('--header-h', h.offsetHeight + 'px');
    };
    measure();
    const update = () => {
      const y = window.scrollY;
      const next = y > last && y > 140;   // down → hide; up / near top → show
      setHidden(next);
      document.documentElement.classList.toggle('header-hidden', next);
      last = y;
      ticking = false;
    };
    const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', measure, { passive: true });
    return () => { window.removeEventListener('scroll', onScroll); window.removeEventListener('resize', measure); };
  }, []);
  return hidden;
}

function Logo({ onClick }) {
  return (
    <button className="sf-logo" onClick={onClick} aria-label="ЦМИ — на главную">
      <span className="sf-logo__mark"><i className="ti ti-building-store"></i></span>
      <span className="sf-logo__text">
        <span className="sf-logo__name">ЦМИ</span>
        <span className="sf-logo__sub">Центр Музыкальных<br/>Инструментов</span>
      </span>
    </button>
  );
}

function Header({ go, screen, cartCount = 0, favCount = 0, onSearch, authed = false, onLogin, onLogout, onProfile }) {
  const [menuOpen, setMenuOpen] = useStateChrome(false);
  const hidden = useHideOnScroll();
  const d = window.STORE_DATA;
  const actions = [
    { icon: 'truck-delivery', label: 'Доставка и оплата', sm: true },
    { icon: 'map-pin', label: 'Магазины', sm: true },
    { icon: 'heart', label: 'Избранное', count: favCount, go: 'catalog' },
    { icon: 'shopping-cart', label: 'Корзина', count: cartCount, go: 'cart' },
  ];
  return (
    <React.Fragment>
    <header className={`sf-header ${hidden ? 'is-hidden' : ''}`}>
      {/* top row */}
      <div className="sf-wrap sf-header__top">
        <button className="sf-burger" aria-label="Меню" onClick={() => setMenuOpen(true)}><i className="ti ti-menu-2"></i></button>
        <Logo onClick={() => go('home')} />
        <div className="sf-search">
          <input placeholder="Поиск инструментов, брендов, категорий…"
            onKeyDown={(e) => { if (e.key === 'Enter') onSearch && onSearch(e.target.value); }} />
          <button className="sf-search__btn" aria-label="Найти" onClick={() => onSearch && onSearch('')}><i className="ti ti-search"></i></button>
        </div>
        <div className="sf-actions">
          {actions.map((a) => (
            <button key={a.label} className={`sf-action ${a.sm ? 'sf-action--sm' : ''}`} data-count={a.count || null} onClick={() => go(a.go || 'catalog')}>
              <i className={`ti ti-${a.icon}`}></i>
              <span>{a.label}</span>
            </button>
          ))}
          {authed ? (
            <button className="sf-action" onClick={() => onProfile && onProfile()}>
              <i className="ti ti-user"></i>
              <span>Профиль</span>
            </button>
          ) : (
            <div className="sf-auth">
              <button className="sf-auth__login" onClick={() => onLogin && onLogin()}><i className="ti ti-login-2"></i> Вход</button>
              <button className="sf-auth__reg" onClick={() => onLogin && onLogin()}>Регистрация</button>
            </div>
          )}
        </div>
      </div>

      {/* nav row */}
      <div className="sf-nav">
        <div className="sf-wrap sf-nav__in">
          <button className="sf-nav__catalog" onClick={() => go('catalog')}><i className="ti ti-menu-2"></i> Каталог</button>
          <nav className="sf-nav__links">
            {d.nav.map((l, i) => {
              const active = i === 0 && (screen === 'category' || screen === 'subcategory');
              return (
                <button key={l} className={`sf-nav__link ${active ? 'is-active' : ''}`} onClick={() => go(i === 0 ? 'category' : 'catalog')}>{l}</button>
              );
            })}
          </nav>
          <div className="sf-nav__phone">
            <a href={`tel:${d.phone.replace(/\D/g, '')}`}>{d.phone}</a>
            <span>{d.hours}</span>
          </div>
        </div>
      </div>
    </header>

      {menuOpen && (
        <div className="sf-drawer" onClick={() => setMenuOpen(false)}>
          <div className="sf-drawer__panel" onClick={(e) => e.stopPropagation()}>
            <div className="sf-drawer__head"><span>Меню</span><button aria-label="Закрыть" onClick={() => setMenuOpen(false)}><i className="ti ti-x"></i></button></div>

            <div className="sf-drawer__group">Каталог</div>
            {d.nav.map((l, i) => (
              <button key={l} className="sf-drawer__item" onClick={() => { setMenuOpen(false); go(i === 0 ? 'category' : 'catalog'); }}>{l}</button>
            ))}

            <div className="sf-drawer__group">Сервис</div>
            <button className="sf-drawer__item sf-drawer__item--ico" onClick={() => { setMenuOpen(false); go('home'); }}><i className="ti ti-truck-delivery"></i> Доставка и оплата</button>
            <button className="sf-drawer__item sf-drawer__item--ico" onClick={() => { setMenuOpen(false); go('home'); }}><i className="ti ti-map-pin"></i> Магазины</button>
            <button className="sf-drawer__item sf-drawer__item--ico" onClick={() => { setMenuOpen(false); go('catalog'); }}><i className="ti ti-heart"></i> Избранное {favCount > 0 && <span className="sf-drawer__count">{favCount}</span>}</button>
            <button className="sf-drawer__item sf-drawer__item--ico" onClick={() => { setMenuOpen(false); go('cart'); }}><i className="ti ti-shopping-cart"></i> Корзина {cartCount > 0 && <span className="sf-drawer__count">{cartCount}</span>}</button>

            <div className="sf-drawer__group">Личный кабинет</div>
            {authed ? (
              <button className="sf-drawer__item sf-drawer__item--ico" onClick={() => { setMenuOpen(false); onProfile && onProfile(); }}><i className="ti ti-user"></i> Профиль</button>
            ) : (
              <div className="sf-drawer__auth">
                <button className="sf-auth__login" onClick={() => { setMenuOpen(false); onLogin && onLogin(); }}><i className="ti ti-login-2"></i> Вход</button>
                <button className="sf-auth__reg" onClick={() => { setMenuOpen(false); onLogin && onLogin(); }}>Регистрация</button>
              </div>
            )}

            <div className="sf-drawer__group">Контакты</div>
            <a className="sf-drawer__phone" href={`tel:${d.phone.replace(/\D/g, '')}`}>{d.phone}</a>
            <span className="sf-drawer__hours">{d.hours}</span>
            <a className="sf-drawer__mail" href={`mailto:${d.email}`}><i className="ti ti-mail"></i> {d.email}</a>
            <div className="sf-drawer__social">
              <a href="#" aria-label="Telegram"><i className="ti ti-brand-telegram"></i></a>
              <a href="#" aria-label="VK"><i className="ti ti-brand-vk"></i></a>
              <a href="#" aria-label="YouTube"><i className="ti ti-brand-youtube"></i></a>
            </div>
          </div>
        </div>
      )}
    </React.Fragment>
  );
}

function FeatureStrip() {
  return (
    <section className="sf-wrap sf-features">
      {window.STORE_DATA.features.map((f) => (
        <div className="sf-feature" key={f.title}>
          <span className="sf-feature__ico"><i className={`ti ti-${f.icon}`}></i></span>
          <span className="sf-feature__txt"><b>{f.title}</b><span>{f.note}</span></span>
        </div>
      ))}
    </section>
  );
}

function Footer({ go }) {
  const d = window.STORE_DATA;
  const nav = (label) => {
    const map = { 'Гарантия и возврат': 'warranty', 'Контакты': 'contacts', 'Новости': 'news' };
    return map[label];
  };
  const cols = [
    { h: 'Покупателям', links: ['Доставка и оплата', 'Гарантия и возврат', 'Рассрочка и кредит', 'Помощь и FAQ', 'Контакты'] },
    { h: 'О компании', links: ['О нас', 'Магазины', 'Новости', 'Блог', 'Вакансии'] },
  ];
  return (
    <footer className="sf-footer">
      <FeatureStrip />
      <div className="sf-wrap sf-footer__in">
        <div className="sf-footer__news">
          <div className="sf-footer__h">Будьте в курсе</div>
          <p>Новости, обзоры и специальные предложения</p>
          <div className="sf-news-form">
            <input placeholder="Ваш e-mail" />
            <button>Подписаться</button>
          </div>
          <p className="sf-footer__fine">Нажимая «Подписаться», вы соглашаетесь с политикой конфиденциальности</p>
        </div>
        {cols.map((c) => (
          <div className="sf-footer__col" key={c.h}>
            <div className="sf-footer__h">{c.h}</div>
            {c.links.map((l) => {
              const dest = nav(l);
              return <a key={l} href="#" onClick={(e) => { e.preventDefault(); if (dest && go) go(dest); }}>{l}</a>;
            })}
          </div>
        ))}
        <div className="sf-footer__col">
          <div className="sf-footer__h">Контакты</div>
          <a className="sf-footer__phone" href="#">{d.phone}</a>
          <span className="sf-footer__hours">{d.hours}</span>
          <a className="sf-footer__mail" href="#"><i className="ti ti-mail"></i> {d.email}</a>
          <div className="sf-social">
            <a href="#" aria-label="Telegram"><i className="ti ti-brand-telegram"></i></a>
            <a href="#" aria-label="VK"><i className="ti ti-brand-vk"></i></a>
            <a href="#" aria-label="YouTube"><i className="ti ti-brand-youtube"></i></a>
          </div>
        </div>
      </div>
      <div className="sf-wrap sf-footer__legal">
        <span>© 2026 Центр Музыкальных Инструментов</span>
        <span className="sf-footer__legal-links"><a href="#">Политика конфиденциальности</a><a href="#">Пользовательское соглашение</a></span>
      </div>
    </footer>
  );
}

Object.assign(window, { Header, Footer, Logo, FeatureStrip });
