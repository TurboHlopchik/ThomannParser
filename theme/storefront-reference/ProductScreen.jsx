/* Product detail: gallery, buy box, assurances, tabs, reviews, related. */
const {
  Breadcrumbs: PBreadcrumbs, Rating: PRating, Badge: PBadge, Button: PButton,
  IconButton: PIconButton, Tabs: PTabs, QuantityStepper: PQty,
} = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStateP } = React;

const fmtP = (n) => n.toLocaleString('ru-RU') + ' ₽';

function Gallery() {
  const [active, setActive] = useStateP(0);
  return (
    <div className="sf-gallery">
      <div className="sf-gallery__thumbs">
        {[0, 1, 2, 3, 4].map((i) => (
          <button key={i} className={`sf-gallery__thumb ${active === i ? 'is-active' : ''}`} onClick={() => setActive(i)}>
            <i className="ti ti-music"></i>
          </button>
        ))}
      </div>
      <div className="sf-gallery__main">
        <button className="sf-gallery__nav sf-gallery__nav--prev" aria-label="Назад" onClick={() => setActive((active + 4) % 5)}><i className="ti ti-chevron-left"></i></button>
        <i className="ti ti-music sf-gallery__hero"></i>
        <button className="sf-gallery__nav sf-gallery__nav--next" aria-label="Вперёд" onClick={() => setActive((active + 1) % 5)}><i className="ti ti-chevron-right"></i></button>
        <button className="sf-gallery__zoom"><i className="ti ti-arrows-maximize"></i> Увеличить</button>
      </div>
    </div>
  );
}

function BuyBox({ go, onAdd }) {
  const p = window.STORE_DATA.product;
  return (
    <div className="sf-buybox">
      <div className="sf-buybox__main">
        <div className="sf-buybox__stock"><span className="sf-buybox__dot"></span> В наличии</div>
        <div className="sf-buybox__price">{fmtP(p.price)}</div>
        <div className="sf-buybox__inst">или от 9 483 ₽ / мес. в рассрочку <i className="ti ti-info-circle"></i></div>
        <div className="sf-buybox__actions">
          <PButton block size="lg" iconLeft="shopping-cart" onClick={onAdd}>В корзину</PButton>
          <PButton block size="lg" variant="secondary" iconLeft="bolt">Купить в 1 клик</PButton>
        </div>
        <div className="sf-buybox__links">
          <button><i className="ti ti-heart"></i> Добавить в избранное</button>
        </div>
      </div>

      <div className="sf-buybox__panel">
        <div className="sf-buybox__panel-row">
          <div>
            <b>Рассрочка без переплат</b>
            <span>от 9 483 ₽ / мес. на 6 месяцев</span>
          </div>
          <PButton size="sm" variant="ghost">Подробнее</PButton>
        </div>
      </div>

      <div className="sf-buybox__panel sf-buybox__consult">
        <div>
          <b>Есть вопросы?</b>
          <span>Наши специалисты помогут подобрать инструмент</span>
          <button className="sf-buybox__consult-cta">Получить консультацию</button>
        </div>
        <i className="ti ti-music"></i>
      </div>
    </div>
  );
}

function Assurances() {
  const items = [
    ['shield-check', 'Гарантия', '12 месяцев'],
    ['rosette-discount-check', 'Официальный дилер', 'Только оригинальная продукция'],
    ['truck', 'Бесплатная доставка', 'По всей России от 10 000 ₽'],
    ['refresh', 'Возврат 14 дней', 'Если не подошёл инструмент'],
  ];
  return (
    <div className="sf-assure">
      {items.map(([ic, t, d]) => (
        <div className="sf-assure__item" key={t}>
          <i className={`ti ti-${ic}`}></i>
          <div><b>{t}</b><span>{d}</span></div>
        </div>
      ))}
    </div>
  );
}

function ProdInfo({ tab }) {
  const specs = window.STORE_DATA.product.specs;
  if (tab === 'Характеристики') {
    return (
      <table className="sf-spec"><tbody>
        {specs.map(([k, v]) => <tr key={k}><td className="sf-spec__k">{k}</td><td className="sf-spec__v">{v}</td></tr>)}
      </tbody></table>
    );
  }
  return (
    <div className="sf-prose">
      <p>Hans Hoyer 801MAL — профессиональная двойная валторна в строе F/Bb, созданная для музыкантов, которым важны богатое звучание, точная интонация и комфорт при игре.</p>
      <p>Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета.

Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры. Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры.Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры.Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры.Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры.Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры.Инструмент изготовлен из высококачественной латуни, оснащён шарнирными рычагами и сменным раструбом золотистого цвета. Идеально подходит для оркестровой, камерной и сольной игры.</p>
    </div>
  );
}

function RelatedRow({ go }) {
  const items = window.STORE_DATA.related;
  return (
    <section className="sf-section">
      <div className="sf-section__head"><h2 className="sf-section__title">С этим товаром покупают</h2></div>
      <div className="sf-row6">
        {items.map((p) => (
          <button className="sf-mini" key={p.id} onClick={() => go('product')}>
            {p.badge && <span className="sf-mini__badge"><PBadge variant={p.badge.variant}>{p.badge.label}</PBadge></span>}
            <span className="sf-mini__media"><i className="ti ti-music"></i></span>
            <span className="sf-mini__name">{p.name}</span>
            <span className="sf-mini__sub">{p.subtitle}</span>
            <span className="sf-mini__buyrow">
              <span className="sf-mini__price">{fmtP(p.price)}</span>
              <span className="sf-mini__cart"><i className="ti ti-shopping-cart"></i></span>
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}

function ProductScreen({ go, onAdd }) {
  const p = window.STORE_DATA.product;
  const [tab, setTab] = useStateP('Описание');
  return (
    <div className="sf-page">
      <div className="sf-wrap">
        <PBreadcrumbs items={p.crumbs.map((c, i) => i < p.crumbs.length - 1 ? { label: c, href: '#' } : { label: c })} />
        <div className="sf-prodtop">
          <PBadge variant={p.badge.variant}>{p.badge.label}</PBadge>
          <h1 className="sf-prod-title">{p.title}</h1>
          <div className="sf-prod-subline">{p.subtitle}</div>
          <div className="sf-prod-meta">
            <span className="sf-prod-meta__sku">Артикул: {p.sku}</span>
          </div>
        </div>

        <div className="sf-prod">
          <div className="sf-prod__left">
            <Gallery />
            <section className="sf-advantages">
              <Assurances />
            </section>
          </div>
          <BuyBox go={go} onAdd={onAdd} />
          <div className="sf-prod__info">
            <div className="sf-prod-tabs">
              <PTabs tabs={['Описание', 'Характеристики']} value={tab} onChange={setTab} />
            </div>
            <div className="sf-prod-tabs__body"><ProdInfo tab={tab} /></div>
          </div>
        </div>

        <RelatedRow go={go} />
      </div>
    </div>
  );
}

Object.assign(window, { ProductScreen });
