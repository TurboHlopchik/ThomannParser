/* Storefront app shell — simple screen router + cart/toast state. */
const { Toast: AppToast } = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStateApp, useEffect: useEffectApp } = React;

function App() {
  const [screen, setScreen] = useStateApp(() => localStorage.getItem('sf_screen') || 'home');
  const [cart, setCart] = useStateApp([]);
  const [toast, setToast] = useStateApp(null);
  const [authed, setAuthed] = useStateApp(() => localStorage.getItem('sf_authed') === '1');

  const go = (s) => { setScreen(s); localStorage.setItem('sf_screen', s); window.scrollTo({ top: 0 }); };
  const setAuth = (v) => { setAuthed(v); localStorage.setItem('sf_authed', v ? '1' : '0'); };

  const login = () => { setAuth(true); setToast({ type: 'success', title: 'Вы вошли в личный кабинет' }); };
  const logout = () => { setAuth(false); };

  const onAdd = (p) => {
    setCart((c) => {
      const ex = c.find((i) => i.id === p.id);
      return ex ? c.map((i) => i.id === p.id ? { ...i, qty: i.qty + 1 } : i) : [...c, { ...p, qty: 1 }];
    });
    setToast({ type: 'success', title: 'Добавлено в корзину', message: `${p.brand} · ${p.name}` });
  };

  useEffectApp(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3200);
    return () => clearTimeout(t);
  }, [toast]);

  const cartCount = cart.reduce((s, i) => s + i.qty, 0);

  return (
    <div className="sf-app">
      <window.Header go={go} screen={screen} cartCount={cartCount} favCount={3} onSearch={() => go('subcategory')}
        authed={authed} onLogin={login} onLogout={logout} onProfile={() => go('profile')} />

      <section className="sf-topbanner" aria-label="Промо-баннер">
        <div className="sf-topbanner__inner">
          <span className="sf-topbanner__note">Баннер 1920 × 320 — промо-изображение</span>
        </div>
      </section>

      {screen === 'home' && <window.HomeScreen go={go} onAdd={onAdd} />}
      {screen === 'catalog' && <window.CatalogHubScreen go={go} />}
      {screen === 'category' && <window.CategoryScreen go={go} />}
      {screen === 'subcategory' && <window.CatalogScreen go={go} onAdd={onAdd} />}
      {screen === 'product' && <window.ProductScreen go={go} onAdd={onAdd} />}
      {screen === 'cart' && <window.CartScreen go={go} cart={cart} setCart={setCart} />}
      {screen === 'profile' && <window.ProfileScreen go={go} onLogout={() => { logout(); go('home'); }} />}
      {screen === 'news' && <window.NewsScreen go={go} />}
      {screen === 'article' && <window.ArticleScreen go={go} />}
      {screen === 'warranty' && <window.WarrantyScreen go={go} />}
      {screen === 'contacts' && <window.ContactsScreen go={go} />}

      <window.Footer go={go} />

      {toast && (
        <div className="sf-toast-host">
          <AppToast {...toast} onClose={() => setToast(null)} />
        </div>
      )}

      {window.StoreTweaks ? <window.StoreTweaks /> : null}

      <DevNav screen={screen} go={go} authed={authed} setAuth={setAuth} />
    </div>
  );
}

/* Small in-mock screen switcher so reviewers can jump between surfaces.
   Links are grouped into dropdown categories that open upward. */
function DevNav({ screen, go, authed, setAuth }) {
  const [open, setOpen] = useStateApp(null);
  const groups = [
    { id: 'shop', label: 'Магазин', items: [['home', 'Главная'], ['catalog', 'Каталог'], ['category', 'Категория'], ['subcategory', 'Подкатегория'], ['product', 'Товар'], ['cart', 'Корзина']] },
    { id: 'content', label: 'Контент', items: [['news', 'Новости'], ['article', 'Статья'], ['warranty', 'Гарантия и возврат'], ['contacts', 'Контакты']] },
    { id: 'account', label: 'Кабинет', items: [['profile', 'Профиль']] },
  ];

  useEffectApp(() => {
    if (!open) return;
    const onDown = (e) => { if (!e.target.closest('.sf-devnav')) setOpen(null); };
    document.addEventListener('mousedown', onDown);
    return () => document.removeEventListener('mousedown', onDown);
  }, [open]);

  const pick = (id) => { go(id); setOpen(null); };

  return (
    <div className="sf-devnav">
      {groups.map((g) => {
        const groupActive = g.items.some(([id]) => id === screen) || (g.id === 'account' && screen === 'profile');
        const isOpen = open === g.id;
        return (
          <div className="sf-devnav__group" key={g.id}>
            {isOpen && (
              <div className="sf-devnav__menu" role="menu">
                {g.items.map(([id, label]) => (
                  <button key={id} role="menuitem" className={screen === id ? 'is-active' : ''} onClick={() => pick(id)}>{label}</button>
                ))}
                {g.id === 'account' && (
                  <React.Fragment>
                    <span className="sf-devnav__menu-sep"></span>
                    <button onClick={() => { setAuth(!authed); setOpen(null); }}>
                      {authed ? 'Состояние: Вошёл' : 'Состояние: Гость'}
                    </button>
                  </React.Fragment>
                )}
              </div>
            )}
            <button className={`sf-devnav__btn ${groupActive ? 'is-active' : ''} ${isOpen ? 'is-open' : ''}`}
              onClick={() => setOpen(isOpen ? null : g.id)}>
              {g.label} <i className="ti ti-chevron-down"></i>
            </button>
          </div>
        );
      })}
      <span className="sf-devnav__sep"></span>
      <button className={`sf-devnav__btn ${authed ? 'is-active' : ''}`} onClick={() => setAuth(!authed)} title="Переключить состояние входа">
        <i className={`ti ti-${authed ? 'user-check' : 'user'}`}></i> {authed ? 'Вошёл' : 'Гость'}
      </button>
    </div>
  );
}

var __sfRootEl = document.getElementById('root');
if (!__sfRootEl.__sfRoot) __sfRootEl.__sfRoot = ReactDOM.createRoot(__sfRootEl);
__sfRootEl.__sfRoot.render(<App />);
