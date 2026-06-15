{*
  ============================================================
  BASE TEMPLATE — «Базовый шаблон»
  Назначьте этот шаблон корневым ресурсам или используйте как
  основу. Общая HTML-обёртка: <head>, шапка, контент, подвал.
  Плейсхолдеры [[*field]] — поля ресурса MODX.
  [[$chunk]] — чанки. [[!snippet]] — некэшируемые сниппеты.
  ============================================================
*}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#FFFFFF">
    <meta name="color-scheme" content="light">

    <title>[[*longtitle:default=`[[*pagetitle]]`]] — ЦМИ</title>
    <meta name="description" content="[[*description]]">
    <meta name="keywords" content="[[*introtext]]">
    <link rel="canonical" href="[[~[[*id]]? &scheme=`full`]]">

    {* ---- Open Graph (микроразметка) ---- *}
    <meta property="og:type" content="website">
    <meta property="og:title" content="[[*longtitle:default=`[[*pagetitle]]`]]">
    <meta property="og:description" content="[[*description]]">
    <meta property="og:url" content="[[~[[*id]]? &scheme=`full`]]">

    {* ---- Шрифты и иконки ---- *}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css">

    {* ---- Стили проекта ---- *}
    <link rel="stylesheet" href="[[++assets_url]]template/css/cmi.css">

    [[*content_extra_head]]
</head>
<body class="sf-app">

    [[$site_header]]

    <main class="sf-page">
        [[*content]]
    </main>

    [[$site_footer]]

    {* ---- miniShop2 JS (корзина, форма заказа) ---- *}
    [[!+msation]]
    <script src="[[++assets_url]]template/js/cmi.js"></script>
    [[*content_extra_foot]]
</body>
</html>
