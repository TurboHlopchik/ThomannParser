# Необходимые модули MODX для пакета cmi-modx

Список выведен из реальных вызовов сниппетов во всех шаблонах/чанках пакета.

## Сводка

| Модуль | Сниппеты в вёрстке | Нужен для | Обязательность |
|--------|--------------------|-----------|----------------|
| **MiniShop3** | `msProducts`, `msCart`, `msOrder`, `msGallery`, `msProductOptions`, `msOrders`, `msFavoritesCount` | каталог, товар, корзина, заказ, галерея, опции, кабинет | ✅ обязателен |
| **pdoTools** | `pdoMenu`, `pdoCrumbs`, `pdoResources`, движок Fenom | меню, хлебные крошки, вывод ресурсов | ✅ обязателен (зависимость MS3) |
| **Login** | `ifLoggedin`, `Login`, `Profile`, `UpdateProfile` | вход/регистрация, кабинет, цена для юрлиц | ✅ нужен (шапка, профиль, товар) |
| **mFilter (для MS3)** | `mFilter2` | фильтры в каталоге | ⚠️ для фильтрации |
| **mSearch (для MS3)** | `mSearch2` | поиск в шапке | ⚠️ для поиска |
| **msFavorites** (или встроенное избранное MS3) | `msFavoritesCount` | счётчик избранного в шапке | ⚙️ опционально |

> `cmiStars` (звёзды рейтинга) — сниппет из пакета (`snippets/cmiStars.php`),
> отдельный модуль не нужен. Шрифт Inter и иконки Tabler — с CDN.

## По страницам

| Шаблон | Сниппеты | Модули |
|--------|----------|--------|
| `base.tpl` | подключает шапку/подвал; `[[!+msation]]` — проверить (вероятно ассеты MS3) | MiniShop3 |
| `site_header` (чанк) | `msCart`, `pdoMenu`, `mSearch2`, `msFavoritesCount`, `ifLoggedin` | MiniShop3, pdoTools, mSearch, Login, (msFavorites) |
| `site_footer` (чанк) | `pdoMenu` | pdoTools |
| `catalog.tpl` | `pdoCrumbs`, `mFilter2`, `msProducts` | pdoTools, mFilter, MiniShop3 |
| `product.tpl` | `pdoCrumbs`, `msGallery`, `msProductOptions`, `msProducts`, `ifLoggedin` | pdoTools, MiniShop3, Login |
| `home.tpl` | `msProducts`, `pdoResources`, `pdoMenu` | MiniShop3, pdoTools |
| `cart.tpl` | `msCart`, `msOrder` | MiniShop3 |
| `profile.tpl` | `Profile`, `UpdateProfile`, `Login`, `ifLoggedin`, `msOrders` | Login, MiniShop3 |

## Минимум под текущий этап (каталог + товар на живых данных)

- **MiniShop3** + **pdoTools** — карточка и листинг отрисуются с данными.
- **ImpEx3** — импорт CSV.
- **Login** — нужен только для блока «цена для юрлиц» в товаре и кабинета;
  без него карточка отрендерится (ветка `ifLoggedin` просто отдаст гостевой вид).
- **mFilter/mSearch (MS3)** — можно подключить позже; без них страницы
  рендерятся, но левый фильтр и строка поиска не активны.

> Важно: `mFilter2`/`mSearch2` — версии под miniShop2. Для MiniShop3 ставьте
> mFilter/mSearch, выпущенные под MS3.
