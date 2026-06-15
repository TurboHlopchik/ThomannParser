/* Catalog hub (каталог index): top-level categories with their subcategories,
   plus a top-brands block. Subcategory / category clicks open the listing. */
const { Breadcrumbs: HubBreadcrumbs } = window.MusicStoreDesignSystem_f8f6e3;

const fmtHubNum = (n) => n.toLocaleString('ru-RU');
const plural = (n, one, few, many) => {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few;
  return many;
};

function CategoryPanel({ cat, idx, go }) {
  const total = cat.subs.reduce((s, [, n]) => s + n, 0);
  const subCount = cat.subs.length;
  return (
    <div className={`sf-cathub-cat sf-tint-${idx % 8}`} style={{ borderRadius: "16px" }}>
      <button className="sf-cathub-cat__head" onClick={() => go('category')}>
        <span className="sf-cathub-cat__icon" style={{ borderRadius: "10px" }}><i className={`ti ti-${cat.icon}`} aria-hidden="true"></i></span>
        <span className="sf-cathub-cat__titles">
          <span className="sf-cathub-cat__title">{cat.label}</span>
          <span className="sf-cathub-cat__count">
            {subCount} {plural(subCount, 'категория', 'категории', 'категорий')} · {fmtHubNum(total)} {plural(total, 'товар', 'товара', 'товаров')}
          </span>
        </span>
        <span className="sf-cathub-cat__all">Все <i className="ti ti-chevron-right" aria-hidden="true"></i></span>
      </button>
      <div className="sf-cathub-cat__subs">
        {cat.subs.map(([name, n]) => (
          <button key={name} className="sf-cathub-sub" onClick={() => go('subcategory')}>
            <span className="sf-cathub-sub__name">{name}</span>
            <span className="sf-cathub-sub__n">{fmtHubNum(n)}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function TopBrands({ go }) {
  const brands = window.STORE_DATA.brands.slice(0, 12);
  return (
    <section className="sf-section">
      <div className="sf-section__head">
        <h2 className="sf-section__title">Топовые бренды</h2>
        <button className="sf-section__link" onClick={() => go('subcategory')}>Все бренды <i className="ti ti-chevron-right" aria-hidden="true"></i></button>
      </div>
      <div className="sf-cathub-brands">
        {brands.map((b) => (
          <button key={b.name} className="sf-brandtile" onClick={() => go('subcategory')}>
            <span className="sf-brandtile__name">{b.name}</span>
            <span className="sf-brandtile__count">{b.count} {plural(b.count, 'товар', 'товара', 'товаров')}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function CatalogHubScreen({ go }) {
  const tree = window.STORE_DATA.catalogTree;
  return (
    <div className="sf-page" style={{ fontWeight: "500" }}>
      <div className="sf-wrap">
        <div className="sf-pagehead">
          <HubBreadcrumbs items={[{ label: 'Главная', onClick: () => go('home') }, { label: 'Каталог' }]} />
          <h1 className="sf-pagehead__title" style={{ fontWeight: "800" }}>Каталог</h1>
          <p className="sf-pagehead__sub" style={{ padding: "0px", lineHeight: "1.64", fontSize: "16px", color: "rgb(115, 115, 131)", margin: "16px 0px 0px", fontWeight: "600" }}>Музыкальные инструменты, ноты, аксессуары и студийное оборудование. Более 80 000 товаров от мировых брендов.</p>
        </div>
        <div className="sf-cathub-grid">
          {tree.map((cat, i) => <CategoryPanel key={cat.id} cat={cat} idx={i} go={go} />)}
        </div>
        <TopBrands go={go} />
      </div>
    </div>
  );
}

Object.assign(window, { CatalogHubScreen });
