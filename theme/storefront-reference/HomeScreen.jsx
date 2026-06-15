/* Home: hero banner grid, categories, product rows, special offers, brands. */
const { Rating: HRating } = window.MusicStoreDesignSystem_f8f6e3;

const fmtH = (n) => n.toLocaleString('ru-RU') + ' ₽';

/* Compact card for home rows (no cart button — matches ЦМИ home). */
function MiniCard({ p, go }) {
  return (
    <button className="sf-mini" onClick={() => go('product')}>
      <span className="sf-mini__fav" aria-label="В избранное"><i className="ti ti-heart"></i></span>
      <span className="sf-mini__media"><i className="ti ti-music"></i></span>
      <span className="sf-mini__name">{p.name}</span>
      <span className="sf-mini__sub">{p.subtitle}</span>
      {p.rating != null && <span className="sf-mini__rate"><HRating value={p.rating} count={p.reviews} /></span>}
      <span className="sf-mini__price">{fmtH(p.price)}</span>
    </button>
  );
}

function HeroGrid({ go }) {
  return (
    <section className="sf-hero-grid">
      <button className="sf-banner" onClick={() => go('catalog')}>
        <div className="sf-banner__body">
          <h1>Профессиональные<br/>валторны</h1>
          <p className="sf-banner__brands">Yamaha, Hans Hoyer, Holton</p>
          <p className="sf-banner__note">Для студентов и профессионалов</p>
          <span className="sf-banner__cta">Смотреть каталог</span>
        </div>
        <i className="ti ti-music sf-banner__art"></i>
        <span className="sf-banner__dots"><i></i><i></i><i></i></span>
      </button>

      <div className="sf-hero-side">
        <button className="sf-promo sf-promo--cream sf-promo--wide" onClick={() => go('catalog')}>
          <div className="sf-promo__body">
            <h3>Рассрочка 0%</h3>
            <p className="sf-promo__big">на 6 месяцев</p>
            <p className="sf-promo__note">На все инструменты и аксессуары</p>
            <span className="sf-promo__cta">Подробнее</span>
          </div>
          <i className="ti ti-music sf-promo__art"></i>
        </button>
        <div className="sf-hero-side__row">
          <button className="sf-promo sf-promo--green" onClick={() => go('catalog')}>
            <div className="sf-promo__body">
              <h3>Скидки до 30%</h3>
              <p className="sf-promo__note">На выделенный ассортимент</p>
              <span className="sf-promo__cta sf-promo__cta--light">Смотреть</span>
            </div>
            <i className="ti ti-music sf-promo__art sf-promo__art--sm"></i>
          </button>
          <button className="sf-promo sf-promo--cream" onClick={() => go('catalog')}>
            <div className="sf-promo__body">
              <h3>Ноты</h3>
              <p className="sf-promo__note">Более 100 000 изданий</p>
              <span className="sf-promo__cta">Перейти</span>
            </div>
            <i className="ti ti-notes sf-promo__art sf-promo__art--sm"></i>
          </button>
        </div>
      </div>
    </section>
  );
}

function PopularCategories({ go }) {
  const cats = window.STORE_DATA.categories;
  return (
    <section className="sf-section">
      <div className="sf-section__head">
        <h2 className="sf-section__title">Популярные категории</h2>
        <button className="sf-section__link" onClick={() => go('catalog')}>Смотреть все <i className="ti ti-chevron-right"></i></button>
      </div>
      <div className="sf-circles">
        {cats.map((c) => (
          <button key={c.id} className="sf-circle" onClick={() => go('catalog')}>
            <span className="sf-circle__img"><i className={`ti ti-${c.icon}`}></i></span>
            <span className="sf-circle__label">{c.label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function ProductRow({ title, products, go }) {
  return (
    <section className="sf-section">
      <div className="sf-section__head">
        <h2 className="sf-section__title">{title}</h2>
        <button className="sf-section__link" onClick={() => go('catalog')}>Смотреть все <i className="ti ti-chevron-right"></i></button>
      </div>
      <div className="sf-row6">
        {products.map((p) => <MiniCard key={p.id} p={p} go={go} />)}
      </div>
    </section>
  );
}

function SpecialOffers({ go }) {
  return (
    <section className="sf-section">
      <div className="sf-section__head"><h2 className="sf-section__title">Специальные предложения</h2></div>
      <div className="sf-offers">
        <button className="sf-offer sf-offer--green" onClick={() => go('catalog')}>
          <h3>Весенние скидки<br/>до 25%</h3>
          <p>На духовые инструменты</p>
          <span className="sf-offer__cta sf-offer__cta--light">Выбрать инструмент</span>
        </button>
        <button className="sf-offer sf-offer--cream" onClick={() => go('catalog')}>
          <h3>Комплекты выгоднее</h3>
          <p>Экономия до 15% · инструмент + аксессуары</p>
          <span className="sf-offer__cta">Смотреть комплекты</span>
        </button>
        <button className="sf-offer sf-offer--cream" onClick={() => go('catalog')}>
          <h3>Бесплатная доставка</h3>
          <p>от 10 000 ₽ · по всей России</p>
          <span className="sf-offer__cta">Подробнее</span>
        </button>
      </div>
    </section>
  );
}

function BrandStrip({ go }) {
  const brands = window.STORE_DATA.brands.slice(0, 8);
  return (
    <section className="sf-section">
      <div className="sf-section__head">
        <h2 className="sf-section__title">Официальные бренды</h2>
        <button className="sf-section__link" onClick={() => go('home')}>Смотреть все <i className="ti ti-chevron-right"></i></button>
      </div>
      <div className="sf-brandstrip">
        {brands.map((b) => (
          <button key={b.name} className="sf-brandlogo" onClick={() => go('home')}>{b.name}</button>
        ))}
      </div>
    </section>
  );
}

function HomeScreen({ go, onAdd }) {
  const all = window.STORE_DATA.products;
  const hits = all.slice(0, 6);
  const best = [...all].slice(6, 12);
  return (
    <div className="sf-page">
      <div className="sf-wrap">
        <HeroGrid go={go} />
        <PopularCategories go={go} />
        <ProductRow title="Хиты продаж" products={hits} go={go} />
        <SpecialOffers go={go} />
        <ProductRow title="Лучшее для вас" products={best} go={go} />
        <BrandStrip go={go} />
      </div>
    </div>
  );
}

Object.assign(window, { HomeScreen });
