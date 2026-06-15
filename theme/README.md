# Тема витрины ЦМИ (MODX 3 + MiniShop3)

Вёрстка интернет-магазина из дизайн-системы «Центр Музыкальных Инструментов»
(Claude Design handoff). Палитра — фиолетовый акцент `#954FFF` + Inter, pill-кнопки,
плоские поверхности, иконки Tabler.

## Состав

```
theme/
├── cmi-modx/               ← Готовый пакет шаблонов MODX (ставится в CMS)
│   ├── templates/          ← base, home, catalog, product, cart, profile
│   ├── chunks/             ← tpl.msProductTile, site_header/footer и т.д.
│   ├── snippets/cmiStars.php
│   └── assets/template/    ← css/cmi.css, js/cmi.js
├── storefront-reference/   ← Статический прототип витрины (визуальный эталон,
│                              в т.ч. страницы контактов/новостей/гарантии/статьи)
├── design-system/          ← Токены (colors, type, spacing, radii) + styles.css
└── DESIGN-HANDOFF.md       ← Исходный README бандла Claude Design
```

Подробная инструкция по установке пакета — в `cmi-modx/README.md`.

## ⚠️ Адаптация miniShop2 → MiniShop3

Пакет `cmi-modx` сгенерирован под **miniShop2 + mFilter2 + mSearch2**. Наш стек —
**MiniShop3**. Визуальный слой (HTML/CSS/JS) переносится без изменений, а вызовы
сниппетов нужно перевести на API MiniShop3. Что затронуто:

- `msProducts`, `msGallery`, `msCart`, `msOrder`, `msProductOptions` — сниппеты MS3;
- фильтрация `mFilter2` → механизм фильтров MiniShop3;
- поиск `mSearch2` → поиск MiniShop3;
- поля товара: характеристики Thomann (`option.*`) → опции MS3, бренд → `vendor`.

Статус адаптации фиксируется по мере раскладки страниц (категория → товар → …).
