<?php
/**
 * Сниппет: cmiStars
 * Вывод 5 звёзд рейтинга разметкой дизайн-системы (★, заполнение по значению).
 * Использование:  [[+rating:cmiStars]]   или   [[*rating:cmiStars]]
 * Вход: $input — число 0..5. Выход: пять <span> со звёздами.
 *
 * Установка: создайте сниппет с именем "cmiStars" и вставьте этот код
 * (без открывающего <?php, если копируете в поле сниппета MODX).
 */
$value = (float) $input;
$rounded = (int) round($value);
$out = '';
for ($i = 1; $i <= 5; $i++) {
    $on = $i <= $rounded ? ' class="on"' : '';
    $out .= '<span' . $on . ' aria-hidden="true">★</span>';
}
return $out;
