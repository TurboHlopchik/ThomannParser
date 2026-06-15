/* Отдельная новость — статья с хлебными крошками, мета и оглавлением. */
const { Breadcrumbs: ArtBreadcrumbs, Badge: ArtBadge } = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStateArt, useEffect: useEffectArt } = React;

const ART_RUBRIC_VARIANT = {
  'Новинки': 'success', 'Акции': 'sale', 'Обзоры': 'accent',
  'События': 'violet', 'Советы': 'neutral', 'Компания': 'neutral',
};

function ArticleScreen({ go }) {
  const a = window.STORE_DATA.article;
  const [active, setActive] = useStateArt(a.toc[0][0]);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (!el) return;
    const top = window.scrollY + el.getBoundingClientRect().top - (parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')) || 196) - 24;
    window.scrollTo({ top, behavior: 'smooth' });
  };

  useEffectArt(() => {
    const ids = a.toc.map((t) => t[0]);
    const onScroll = () => {
      const offset = (parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')) || 196) + 60;
      let current = ids[0];
      for (const id of ids) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top <= offset) current = id;
      }
      setActive(current);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <main className="sf-page" data-screen-label="Отдельная новость">
      <div className="sf-wrap sf-article">
        <div className="sf-article__head">
          <ArtBreadcrumbs className="sf-article__crumbs" items={[
            { label: 'Главная', onClick: () => go('home') },
            { label: 'Новости', onClick: () => go('news') },
            { label: a.crumbs[a.crumbs.length - 1] },
          ]} />
          <div className="sf-article__meta">
            <ArtBadge variant={ART_RUBRIC_VARIANT[a.rubric] || 'accent'}>{a.rubric}</ArtBadge>
            <span className="sf-article__date">{a.date}</span>
            <span className="sf-article__read"><i className="ti ti-clock"></i> {a.read} мин чтения</span>
            <span className="sf-article__author"><i className="ti ti-user"></i> {a.author}</span>
          </div>
          <h1>{a.title}</h1>
          <p className="sf-article__lead">{a.lead}</p>
        </div>

        <div className="sf-article__hero sf-ph">
          <i className="ti ti-photo"></i>
          <span className="sf-ph__label">обложка 16 : 7 — фотография</span>
        </div>

        <div className="sf-article__layout">
          <article className="sf-article__body">
            {a.sections.map((s) => (
              <section key={s.id} id={s.id} className="sf-article__sec">
                <h2>{s.h}</h2>
                {s.p.map((para, i) => <p key={i}>{para}</p>)}
              </section>
            ))}
          </article>

          <nav className="sf-toc" aria-label="Содержание">
            <div className="sf-toc__h">Содержание</div>
            <div className="sf-toc__list">
              {a.toc.map(([id, label]) => (
                <button key={id} className={`sf-toc__link ${active === id ? 'is-active' : ''}`} onClick={() => scrollTo(id)}>{label}</button>
              ))}
            </div>
          </nav>
        </div>
      </div>
    </main>
  );
}

window.ArticleScreen = ArticleScreen;
