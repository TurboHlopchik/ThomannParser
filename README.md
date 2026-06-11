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

---

### Шаг 2 — Собрать URL всех товаров

```bash
# Весь каталог
python3 2_url_collector.py --categories categories.json --db products.db

# Только одна категория (рекомендуется для начала)
python3 2_url_collector.py --categories categories.json --db products.db --category-filter "Guitars"

# Продолжить после прерывания
python3 2_url_collector.py --resume
```

Результат: `products.db` (SQLite) с URL всех товаров.

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

## Импорт в MODX MiniShop2

1. Установите extra **msImport** через MODX Extras
2. `Компоненты → MiniShop2 → Импорт`
3. Загрузите XML файл нужной категории
4. Настройте маппинг полей по таблице ниже

### Маппинг полей

| Поле файла    | Поле MiniShop2 | Описание |
|---------------|----------------|----------|
| `pagetitle`   | pagetitle      | Название товара |
| `longtitle`   | longtitle      | Бренд + название |
| `alias`       | alias          | URL slug |
| `description` | description    | Краткое описание |
| `content`     | content        | Полное HTML описание |
| `price`       | price          | Цена |
| `old_price`   | old_price      | Старая цена |
| `article`     | article        | Артикул (SKU) |
| `image`       | image          | Главное фото (URL) |
| `gallery`     | gallery        | Галерея (разделитель `\|\|`) |
| `category`    | category       | Путь категории |
| `brand`       | vendor         | Бренд |
| `properties`  | options        | Характеристики |

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
