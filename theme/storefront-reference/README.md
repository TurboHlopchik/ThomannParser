# Storefront UI kit

A high-fidelity, click-through recreation of the **ЦМИ** storefront, matching
the reference screenshots. It composes the design-system primitives (it does
**not** re-implement them) and adds only page-shell and screen-composition
styles in `storefront.css`.

> Brand: **ЦМИ — Центр Музыкальных Инструментов**. The header lockup is built in
> CSS in `Chrome.jsx` (`Logo`) — swap the monogram tile for the real logo asset
> when delivered.

## Screens
- **Home** (`HomeScreen.jsx`) — hero banner grid (black banner + cream/green
  promo tiles), circular popular-category row, Хиты продаж / Лучшее для вас
  product rows, special-offer panels, official-brand strip.
- **Catalog** (`CatalogScreen.jsx`) — breadcrumbs, category hero banner, filter
  sidebar (categories, brand search, price slider + ranges, material, collapsible
  groups), toolbar (grid/list toggle + active-filter chip + sort), product grid
  (full `ProductCard`), pagination + «Показывать по», «Как выбрать» guide.
- **Product** (`ProductScreen.jsx`) — thumbnail gallery, buy box (price, рассрочка,
  В корзину + Купить в 1 клик, избранное, installment + consultation
  panels), assurances strip, tabs, three-column О товаре / Характеристики / В
  комплекте, reviews block with rating bars, «С этим товаром покупают» row.
- **Cart** (`CartScreen.jsx`) — checkout steps, line items with quantity steppers
  and remove, order summary with promo field and totals, empty state. Reflects
  the brief: **no online payment** — a manager confirms and invoices.

## Running / structure
Open `index.html`. It loads `styles.css`, the Tabler icon webfont, the compiled
`_ds_bundle.js`, then `data.js` (sample catalog) and the screen scripts. `App.jsx`
is a tiny screen router with cart + toast + auth state; a floating **DevNav** at
the bottom lets reviewers jump between surfaces and toggle the **Гость / Вошёл**
state — logged-out shows «Вход» / «Регистрация» in the header, logged-in shows
«Профиль» (it is mock-only — remove for production).

Components used from the system: `Button`, `IconButton`, `Input`, `Select`,
`Checkbox`, `Switch`, `QuantityStepper`, `Badge`, `Toast`, `EmptyState`,
`Breadcrumbs`, `Tabs`, `FilterChip`, `Pagination`, `Accordion`, `ProductCard`,
`BrandCard`, `Rating`, `CheckoutSteps`.
