# Thomann.de → MODX MiniShop2 Parser

Полный pipeline парсинга каталога Thomann.de с переводом на русский и экспортом в MODX MiniShop2.

---

## Установка

```bash
cd parser/
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Требование:** запускать с домашнего интернета (Thomann блокирует облачные IP).

---

## Pipeline: 5 шагов

### Шаг 1 — Получить структуру категорий

```bash
python3 1_category_parser.py
# → categories.json
```

Результат: `categories.json` с полным деревом категорий.

**Отладка парсинга без запросов к Thomann** (если дерево пустое/неполное — селекторы
нужно подогнать под реальную вёрстку):

```bash
# Самопроверка логики парсинга на встроенном образце (без сети)
python3 1_category_parser.py --self-test

# Сохраните страницу один раз с домашнего IP и прогоняйте парсер по файлу:
curl -A "Mozilla/5.0" https://www.thomann.de/intl/cat.html -o cat.html
python3 1_category_parser.py --html-file cat.html --output categories.json
```

---

### Шаг 2 — Собрать URL всех товаров

Сбор идёт **рекурсивным обходом дерева категорий**: верхние/промежуточные страницы
у Thomann — это лендинги (JS, ссылки на под-категории в `fx-category-grid`), а реальные
списки товаров — на страницах-листьях (например `st_models.html`), которые отдают по 50
товаров с рабочей пагинацией `?ls=50&pg=N`. Скрипт сам спускается до листьев и
пагинирует их, помечая каждый товар категорией. Очередь категорий хранится в БД —
сбор полностью возобновляемый.

> Глобальный `search.html` ограничен ~155 страницами (~7000 товаров), поэтому для
> полного каталога (124k) используется именно обход по категориям.

```bash
# Тест: первые 5 листовых категорий
python3 2_url_collector.py --max-leaves 5

# Полный сбор всего каталога (возобновляемый; Ctrl+C — и повторный запуск продолжит)
python3 2_url_collector.py

# Только одна верхняя категория
python3 2_url_collector.py --seed-category "Guitars"

# Перестроить очередь категорий с нуля
python3 2_url_collector.py --reset-queue

# Старый (ограниченный) режим через search.html
python3 2_url_collector.py --search-mode

python3 2_url_collector.py --self-test
```

Результат: `products.db` (SQLite) с URL всех товаров (status `pending`), у каждого
проставлена категория из пути обхода.

---

### Шаг 3 — Спарсить данные о товарах

```bash
# Все товары из БД
python3 3_product_scraper.py --db products.db

# Тест: только 10 товаров
python3 3_product_scraper.py --db products.db --limit 10

# Только одна категория
python3 3_product_scraper.py --db products.db --category "Guitars"
```

Можно прервать Ctrl+C — прогресс сохраняется. Повторный запуск продолжит с места остановки.

---

### Шаг 4 — Перевести на русский

**Вариант A: DeepL (рекомендуется)**
1. Зарегистрируйтесь на [deepl.com/pro-api](https://www.deepl.com/pro-api) (Free: 500к символов/мес)
2. Скопируйте API ключ

```bash
python3 4_translator.py --engine deepl --api-key YOUR_DEEPL_KEY
```

**Вариант B: Claude API**
1. Получите ключ на [console.anthropic.com](https://console.anthropic.com)

```bash
python3 4_translator.py --engine claude --api-key YOUR_ANTHROPIC_KEY
```

**Вариант C: Google Translate (бесплатно, хуже качество)**
```bash
python3 4_translator.py --engine google
```

---

### Шаг 5 — Экспортировать для MODX

```bash
# Всё в один файл
python3 5_exporter.py --use-russian --format both --output export/thomann

# Разбить по верхнеуровневым категориям (удобно для поэтапного импорта)
python3 5_exporter.py --use-russian --split-by-category --output export/thomann

# Также экспортировать дерево категорий
python3 5_exporter.py --use-russian --split-by-category --export-categories
```

Результат: `export/thomann_guitars.xml`, `export/thomann_drums.xml` и т.д.

---

## Импорт в MODX 3 + MiniShop3 (ImpEx3)

Связка **MODX 3 + MiniShop3**. Импорт — через **ImpEx3** (modstore.pro), формат
**CSV** (не XML; XML-ветка экспортёра осталась только для старого MiniShop2 и не
используется). `5_exporter.py` по умолчанию отдаёт CSV под ImpEx3.

> `msImportExport` — это инструмент для MiniShop**2** (таблицы `ms2_*`), на
> MiniShop3 он не подходит. Его преемник для MS3 — **ImpEx3**.

1. Установите **ImpEx3** через modstore.pro
2. `Компоненты → ImpEx3 → Импорт`
3. Загрузите CSV нужной категории (рекомендуется `--split-by-category`)
4. На шаге маппинга сопоставьте колонки по таблице ниже

### Маппинг полей

| Колонка CSV        | Поле MiniShop3 | Описание |
|--------------------|----------------|----------|
| `pagetitle`        | pagetitle      | Название товара |
| `longtitle`        | longtitle      | Бренд + название |
| `alias`            | alias          | URL slug |
| `description`      | description    | Краткое описание |
| `content`          | content        | Полное HTML описание |
| `price`            | price          | Цена |
| `old_price`        | old_price      | Старая цена |
| `article`          | article        | Артикул (SKU) |
| `image`            | image          | Главное фото (URL) |
| `gallery`          | gallery        | Галерея, несколько URL через `\|\|` |
| `category`         | parent / категория | Путь категории — ImpEx3 строит дерево |
| `vendor`           | vendor         | Бренд (производитель) |
| `option.<ключ>`    | опция товара   | Характеристики → фильтруемые опции MS3 |

**Характеристики** выгружаются как отдельные колонки `option.<ключ>`
(например `option.body`, `option.number_of_frets`). MiniShop3 создаёт по ним
опции автоматически, и товары становятся фильтруемыми по этим параметрам. Набор
опций в каждом файле — объединение характеристик всех товаров категории, поэтому
импортируйте **по категориям** (`--split-by-category`), чтобы колонки оставались
осмысленными.

---

## Оценка времени и стоимости для полного каталога (124к товаров)

| Этап | Время | Стоимость |
|------|-------|-----------|
| Шаг 1 (категории) | ~5 мин | бесплатно |
| Шаг 2 (URL, ~2400 категорий) | ~3–5 часов | бесплатно |
| Шаг 3 (парсинг, 2 сек/товар) | ~70 часов | бесплатно |
| Шаг 4 (перевод, DeepL) | ~8 часов | ~$30–50 |
| Шаг 5 (экспорт) | ~10 мин | бесплатно |

**Совет:** разбейте на части по категориям. Запустите Guitars → импортируйте → запустите Drums → импортируйте и т.д.

---

## Советы

- Не снижайте `--delay` ниже 1.5 сек — риск бана IP
- Все данные хранятся в SQLite (`products.db`) — можно прерываться и продолжать
- После шага 3 проверьте результат: `python3 -c "import sqlite3; c=sqlite3.connect('products.db'); print(c.execute('SELECT status, COUNT(*) FROM products GROUP BY status').fetchall())"`
