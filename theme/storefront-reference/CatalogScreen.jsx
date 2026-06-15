/* Catalog: category hero, filter sidebar, toolbar, product grid, guide. */
const {
  ProductCard: CatProductCard, Breadcrumbs: CatBreadcrumbs, Checkbox: CatCheckbox,
  Select: CatSelect, Pagination: CatPagination, FilterChip: CatChip, Button: CatButton,
  Accordion: CatAccordion, Input: CatInput, Badge: CatBadge, Rating: CatRating,
  IconButton: CatIconButton,
} = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStateCat } = React;

const fmtCat = (n) => n.toLocaleString('ru-RU') + ' ₽';

/* Horizontal card for the catalog list view. */
function ListCard({ p, onAdd, go }) {
  return (
    <div className="sf-listcard">
      <div className="sf-listcard__media" onClick={() => go('product')}>
        {p.badge && <span className="sf-listcard__badge"><CatBadge variant={p.badge.variant}>{p.badge.label}</CatBadge></span>}
        <button className="sf-listcard__fav" aria-label="В избранное"><i className="ti ti-heart"></i></button>
        <i className="ti ti-music sf-listcard__ph" aria-hidden="true"></i>
      </div>
      <div className="sf-listcard__body" onClick={() => go('product')}>
        <div className="sf-listcard__name">{p.name}</div>
        <div className="sf-listcard__sub">{p.subtitle}</div>
        <CatRating value={p.rating} count={p.reviews} />
        {p.desc && <p className="sf-listcard__desc">{p.desc}</p>}
        <div className="sf-listcard__stock">
          <span className={`sf-listcard__dot sf-listcard__dot--${p.inStock ? 'in' : 'order'}`}></span>
          {p.inStock ? 'В наличии' : 'Под заказ'}
        </div>
      </div>
      <div className="sf-listcard__buy">
        <div className="sf-listcard__prices">
          <span className="sf-listcard__price">{fmtCat(p.price)}</span>
          {p.oldPrice && <span className="sf-listcard__old">{fmtCat(p.oldPrice)}</span>}
        </div>
        <CatButton block iconLeft="shopping-cart" variant={p.inStock ? 'primary' : 'outline'} onClick={onAdd}>
          {p.inStock ? 'В корзину' : 'Под заказ'}
        </CatButton>
        <button className="sf-listcard__favlink"><i className="ti ti-heart"></i> В избранное</button>
      </div>
    </div>
  );
}

function FilterSidebar() {
  const f = window.STORE_DATA.filters;
  return (
    <aside className="sf-filters">
      <div className="sf-filters__head">
        <span>Фильтры</span>
        <button className="sf-filters__reset">Сбросить все</button>
      </div>

      <div className="sf-filters__group">
        <div className="sf-filters__label">Вид товара</div>
        <div className="sf-filters__list">
          {f.categories.map(([t, n], i) => <CatCheckbox key={t} label={t} count={n} defaultChecked={i === 0} />)}
          <button className="sf-filters__more">Показать ещё</button>
        </div>
      </div>

      <div className="sf-filters__group">
        <div className="sf-filters__label">Бренд</div>
        <CatInput placeholder="Поиск бренда" iconLeft="search" className="sf-filters__search" />
        <div className="sf-filters__list">
          {f.brands.map(([t, n], i) => <CatCheckbox key={t} label={t} count={n} defaultChecked={i === 0} />)}
          <button className="sf-filters__more">Показать ещё</button>
        </div>
      </div>

      <div className="sf-filters__group">
        <div className="sf-filters__label">Цена, ₽</div>
        <div className="sf-slider"><span className="sf-slider__track"></span><span className="sf-slider__fill"></span><span className="sf-slider__knob" style={{ left: '0%' }}></span><span className="sf-slider__knob" style={{ left: '100%' }}></span></div>
        <div className="sf-price-range">
          <input className="sf-price-input" defaultValue="10 000" />
          <input className="sf-price-input" defaultValue="620 000" />
        </div>
        <div className="sf-filters__list sf-filters__list--ranges">
          {f.priceRanges.map(([t, n]) => (
            <button key={t} className="sf-range"><span>{t}</span><span className="sf-range__n">({n})</span></button>
          ))}
        </div>
      </div>

      <div className="sf-filters__group">
        <div className="sf-filters__label">В наличии</div>
        <div className="sf-filters__list">
          <CatCheckbox label="В наличии" count={96} defaultChecked />
          <CatCheckbox label="Под заказ" count={32} />
        </div>
      </div>

      <CatButton block size="lg" variant="dark" className="sf-filters__apply">Показать 128 товаров</CatButton>
    </aside>
  );
}

function CatalogScreen({ go, onAdd }) {
  const products = Array.from({ length: 20 }, (_, i) => {
    const base = window.STORE_DATA.products;
    return { ...base[i % base.length], id: `g${i}` };
  });
  const [page, setPage] = useStateCat(1);
  const [view, setView] = useStateCat('grid');
  return (
    <div className="sf-page">
      <div className="sf-wrap">
        <div className="sf-pagehead">
          <CatBreadcrumbs items={[{ label: 'Главная', onClick: () => go('home') }, { label: 'Каталог', onClick: () => go('catalog') }, { label: 'Духовые', onClick: () => go('category') }, { label: 'Саксофоны' }]} />
          <h1 className="sf-pagehead__title">Саксофоны</h1>
          <div className="sf-pagehead__meta" style={{ margin: "16px 0px 0px", fontWeight: "600" }}>128 товаров</div>
          <p className="sf-pagehead__sub" style={{ margin: "8px 0px 0px" }}>Широкий выбор саксофонов для студентов, любителей и профессионалов. Разные строи, материалы и комплектации.</p>
        </div>
        <div className="sf-cat-body">
          <FilterSidebar />
          <div className="sf-cat-main">
            <div className="sf-toolbar">
              <div className="sf-view">
                <button className={view === 'grid' ? 'is-active' : ''} onClick={() => setView('grid')} aria-label="Сетка"><i className="ti ti-layout-grid"></i></button>
                <button className={view === 'list' ? 'is-active' : ''} onClick={() => setView('list')} aria-label="Список"><i className="ti ti-list"></i></button>
              </div>
              <div className="sf-toolbar__chips">
                <CatChip label="Альт-саксофоны" active removable style={{ backgroundColor: 'rgb(233, 233, 240)' }} />
                <button className="sf-toolbar__clear">Очистить все</button>
              </div>
              <div className="sf-toolbar__sort">
                <CatSelect options={['Сортировка: по релевантности', 'Сначала дешёвые', 'Сначала дорогие', 'По новизне']} />
              </div>
            </div>
            {view === 'grid' ? (
              <div className="sf-grid sf-grid--4">
                {products.map((p) => <CatProductCard key={p.id} {...p} cartVariant="icon" onAdd={() => onAdd(p)} />)}
              </div>
            ) : (
              <div className="sf-list">
                {products.map((p) => <ListCard key={p.id} p={p} onAdd={() => onAdd(p)} go={go} />)}
              </div>
            )}
            <div className="sf-cat-foot">
              <CatPagination page={page} total={7} onChange={setPage} />
              <div className="sf-perpage">
                <span>Показывать по:</span>
                <CatSelect options={['20', '40', '60']} />
              </div>
            </div>
          </div>
        </div>

        <section className="sf-guide">
          <i className="ti ti-music sf-guide__art"></i>
          <div className="sf-guide__intro">
            <h3>Как выбрать саксофон?</h3>
            <p>Для начинающих подойдут модели с простым строем и удобной эргономикой. Профессионалам важны материал, звучание и точная механика. Мы поможем подобрать идеальный инструмент под ваши задачи.</p>
            <CatButton onClick={() => go('product')}>Читать руководство</CatButton>
          </div>
          <div className="sf-guide__points">
            {[['shield-check', 'Проверка перед отправкой', 'Каждый инструмент проходит профессиональную проверку'],
              ['adjustments', 'Подбор под задачи', 'Поможем выбрать инструмент под ваш уровень и цели'],
              ['credit-card', 'Рассрочка и кредит', 'Удобные условия оплаты до 24 месяцев']].map(([ic, t, d]) => (
              <div className="sf-guide__point" key={t}>
                <i className={`ti ti-${ic}`}></i>
                <b>{t}</b>
                <span>{d}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

Object.assign(window, { CatalogScreen });
