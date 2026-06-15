/* Store tweaks — live theming of the ЦМИ storefront via CSS custom properties.
   Loaded after tweaks-panel.jsx. Renders <StoreTweaks/> (mounted in App). */
const {
  useTweaks: useTweaksST, TweaksPanel: TweaksPanelST, TweakSection: TweakSectionST,
  TweakColor: TweakColorST, TweakRadio: TweakRadioST, TweakSelect: TweakSelectST,
  TweakToggle: TweakToggleST,
} = window;
const { useEffect: useEffectST } = React;

/* mix a hex toward white (amt 0..1) */
function mixWhite(hex, amt) {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const m = (c) => Math.round(c + (255 - c) * amt);
  return '#' + ((m(r) << 16) | (m(g) << 8) | m(b)).toString(16).padStart(6, '0');
}

/* mix a hex toward black (amt 0..1) */
function mixBlack(hex, amt) {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const m = (c) => Math.round(c * (1 - amt));
  return '#' + ((m(r) << 16) | (m(g) << 8) | m(b)).toString(16).padStart(6, '0');
}

/* Accent revert value: previous taupe was "#998780", original indigo "#3D00EC" */
const ST_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#954FFF",
  "dark": "#1A1A24",
  "bg": "#F4F4F7",
  "banner": false,
  "promo": "midnight",
  "radius": "round",
  "font": "Inter"
}/*EDITMODE-END*/;

/* promo-panel themes: [dark banner, accent panel, soft panel] */
const PROMO_THEMES = {
  violet:  ['#190A3A', '#3D00EC', '#ECE6FE'],
  midnight:['#14141A', '#2A2A38', '#E8E8EE'],
  classic: ['#1B1B20', '#2F3E34', '#EEE7DB'],
};
/* radius sets: [control(btn/input/pill), card, modal] */
const RADIUS_SETS = {
  round: ['999px', '14px', '16px'],
  soft:  ['12px', '14px', '16px'],
  sharp: ['3px', '5px', '7px'],
};
const FONT_STACKS = {
  'Inter':      "'Inter', system-ui, sans-serif",
  'Manrope':    "'Manrope', system-ui, sans-serif",
  'Golos Text': "'Golos Text', system-ui, sans-serif",
  'Onest':      "'Onest', system-ui, sans-serif",
  'Unbounded':  "'Unbounded', system-ui, sans-serif",
};


function StoreTweaks() {
  const [t, setTweak] = useTweaksST(ST_DEFAULTS);

  useEffectST(() => {
    const s = document.documentElement.style;
    // accent — single picked colour, hover/tint derived
    const a = t.accent;
    const ah = mixBlack(a, 0.18);
    const at = mixWhite(a, 0.88);
    s.setProperty('--accent', a);
    s.setProperty('--accent-hover', ah);
    s.setProperty('--accent-press', ah);
    s.setProperty('--accent-tint', at);
    s.setProperty('--accent-tint-2', mixWhite(at, 0.45));
    s.setProperty('--violet', a);
    s.setProperty('--violet-bg', at);
    s.setProperty('--link', a);
    // dark button
    s.setProperty('--btn-dark', t.dark);
    s.setProperty('--btn-dark-hover', mixWhite(t.dark, 0.16));
    // background
    s.setProperty('--bg', t.bg);
    s.setProperty('--page-bg', t.bg);
    // promo theme
    const [pd, pa, ps] = PROMO_THEMES[t.promo];
    s.setProperty('--panel-dark', pd);
    s.setProperty('--panel-accent', pa);
    s.setProperty('--panel-soft', ps);
    // radii
    const [ctrl, card, modal] = RADIUS_SETS[t.radius];
    s.setProperty('--r-btn', ctrl);
    s.setProperty('--r-input', ctrl);
    s.setProperty('--r-pill', ctrl);
    s.setProperty('--r-card', card);
    s.setProperty('--r-modal', modal);
    // font
    s.setProperty('--font-sans', FONT_STACKS[t.font] || FONT_STACKS.Inter);
    // promo banner under the header
    document.documentElement.dataset.banner = t.banner ? '1' : '0';
  }, [t]);

  return (
    <TweaksPanelST title="Тема магазина">
      <TweakSectionST label="Цвета" />
      <TweakColorST label="Акцент" value={t.accent}
        onChange={(v) => setTweak('accent', v)} />
      <TweakColorST label="Тёмные кнопки" value={t.dark}
        onChange={(v) => setTweak('dark', v)} />
      <TweakColorST label="Фон страницы" value={t.bg}
        onChange={(v) => setTweak('bg', v)} />

      <TweakSectionST label="Баннер" />
      <TweakToggleST label="Баннер под шапкой" value={t.banner}
        onChange={(v) => setTweak('banner', v)} />

      <TweakSectionST label="Промо-блоки" />
      <TweakRadioST label="Стиль плашек" value={t.promo}
        options={['violet', 'midnight', 'classic']}
        onChange={(v) => setTweak('promo', v)} />

      <TweakSectionST label="Скругления" />
      <TweakRadioST label="Форма" value={t.radius}
        options={['round', 'soft', 'sharp']}
        onChange={(v) => setTweak('radius', v)} />

      <TweakSectionST label="Шрифт" />
      <TweakSelectST label="Семейство" value={t.font}
        options={['Inter', 'Manrope', 'Golos Text', 'Onest', 'Unbounded']}
        onChange={(v) => setTweak('font', v)} />
    </TweaksPanelST>
  );
}

window.StoreTweaks = StoreTweaks;
