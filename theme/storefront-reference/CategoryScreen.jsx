/* Category landing (Категория, e.g. Духовые): hero, subcategory tiles,
   popular products, brands. Sits between the catalog hub and the
   subcategory listing. Subcategory tiles open the listing ('subcategory'). */
const { Breadcrumbs: ClBreadcrumbs, Rating: ClRating } = window.MusicStoreDesignSystem_f8f6e3;

const clFmt = (n) => n.toLocaleString('ru-RU');
const clPlural = (n, one, few, many) => {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few;
  return many;
};

function SubcatCard({ cat, idx, name, count, go }) {
  return (
    <button className={`sf-subcard sf-tint-${idx % 8}`} onClick={() => go('subcategory')}>
      <span className="sf-subcard__media" style={{ borderRadius: "10px" }}>
        <i className={`ti ti-${cat.icon}`} aria-hidden="true"></i>
      </span>
      <span className="sf-subcard__body">
        <span className="sf-subcard__name">{name}</span>
        <span className="sf-subcard__count">{clFmt(count)} {clPlural(count, 'товар', 'товара', 'товаров')}</span>
      </span>
      <span className="sf-subcard__go" aria-hidden="true"><i className="ti ti-chevron-right"></i></span>
    </button>
  );
}

function ClMini({ p, go }) {
  return (
    <button className="sf-mini" onClick={() => go('product')}>
      <span className="sf-mini__fav" aria-label="В избранное"><i className="ti ti-heart"></i></span>
      <span className="sf-mini__media"><i className="ti ti-music"></i></span>
      <span className="sf-mini__name">{p.name}</span>
      <span className="sf-mini__sub">{p.subtitle}</span>
      {p.rating != null && <span className="sf-mini__rate"><ClRating value={p.rating} count={p.reviews} /></span>}
      <span className="sf-mini__price">{clFmt(p.price)} ₽</span>
    </button>
  );
}

function CategoryScreen({ go, catId = 'wind' }) {
  const d = window.STORE_DATA;
  const cat = d.catalogTree.find((c) => c.id === catId) || d.catalogTree[0];
  const total = cat.subs.reduce((s, [, n]) => s + n, 0);
  const popular = d.products.slice(0, 12);
  const brands = d.brands.slice(0, 8);

  return (
    <div className="sf-page">
      <div className="sf-wrap">
        <div className="sf-pagehead">
          <ClBreadcrumbs items={[
            { label: 'Главная', onClick: () => go('home') },
            { label: 'Каталог', onClick: () => go('catalog') },
            { label: cat.label },
          ]} />
          <h1 className="sf-pagehead__title">{cat.label}</h1>
          <div className="sf-pagehead__meta" style={{ margin: "16px 0px 0px", fontWeight: "600" }}>
            {cat.subs.length} {clPlural(cat.subs.length, 'подкатегория', 'подкатегории', 'подкатегорий')} · {clFmt(total)} {clPlural(total, 'товар', 'товара', 'товаров')}
          </div>
          <p className="sf-pagehead__sub" style={{ margin: "8px 0px 0px", fontSize: "14px" }}>{cat.desc}</p>
        </div>

        <section className="sf-section sf-section--tight">
          <div className="sf-subcat-grid">
            {cat.subs.map(([name, n], i) => (
              <SubcatCard key={name} cat={cat} idx={i} name={name} count={n} go={go} />
            ))}
          </div>
        </section>

        <section className="sf-section">
          <div className="sf-section__head">
            <h2 className="sf-section__title">Популярное в категории</h2>
          </div>
          <div className="sf-row6">
            {popular.map((p) => <ClMini key={p.id} p={p} go={go} />)}
          </div>
        </section>

        <section className="sf-section">
          <div className="sf-section__head">
            <h2 className="sf-section__title">Бренды в категории</h2>
            <button className="sf-section__link" onClick={() => go('subcategory')}>Все бренды <i className="ti ti-chevron-right" aria-hidden="true"></i></button>
          </div>
          <div className="sf-brandstrip">
            {brands.map((b) => (
              <button key={b.name} className="sf-brandlogo" onClick={() => go('subcategory')}>{b.name}</button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

Object.assign(window, { CategoryScreen });
