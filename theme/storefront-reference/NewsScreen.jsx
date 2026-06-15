/* Новости — единая лента, список с миниатюрами слева. */
const { Breadcrumbs: NewsBreadcrumbs, Badge: NewsBadge, Pagination: NewsPagination } = window.MusicStoreDesignSystem_f8f6e3;
const { useState: useStateNews } = React;

const NEWS_RUBRIC_VARIANT = {
  'Новинки': 'success', 'Акции': 'sale', 'Обзоры': 'accent',
  'События': 'violet', 'Советы': 'neutral', 'Компания': 'neutral',
};

function NewsScreen({ go }) {
  const d = window.STORE_DATA;
  const [page, setPage] = useStateNews(1);

  return (
    <main className="sf-page" data-screen-label="Новости">
      <div className="sf-wrap">
        <div className="sf-pagehead">
          <NewsBreadcrumbs className="sf-pagehead__crumbs" items={[
            { label: 'Главная', onClick: () => go('home') },
            { label: 'Новости' },
          ]} />
          <h1>Новости и события</h1>
          <p>Поступления инструментов, акции, обзоры и советы по выбору. Новые материалы выходят каждую неделю — подпишитесь, чтобы не пропустить.</p>
        </div>

        <div className="sf-news-body">
          <div>
            <div className="sf-newslist">
              {d.news.map((n) => (
                <button key={n.id} className="sf-newscard" onClick={() => go('article')}>
                  <div className="sf-newscard__media sf-ph">
                    <i className={`ti ti-${n.icon}`}></i>
                    <span className="sf-ph__label">фото 4 : 3</span>
                  </div>
                  <div className="sf-newscard__body">
                    <div className="sf-newscard__meta">
                      <NewsBadge variant={NEWS_RUBRIC_VARIANT[n.rubric] || 'accent'}>{n.rubric}</NewsBadge>
                      <span className="sf-newscard__date">{n.date}</span>
                      <span className="sf-newscard__read"><i className="ti ti-clock"></i> {n.read} мин</span>
                    </div>
                    <div className="sf-newscard__title">{n.title}</div>
                    <p className="sf-newscard__excerpt">{n.excerpt}</p>
                    <span className="sf-newscard__more">Читать материал <i className="ti ti-arrow-right"></i></span>
                  </div>
                </button>
              ))}
            </div>

            <div className="sf-news-foot">
              <NewsPagination page={page} total={6} onChange={setPage} />
            </div>
          </div>

          <aside className="sf-news-aside">
            <div className="sf-aside-card sf-aside-card--accent">
              <div className="sf-aside-card__h">Будьте в курсе</div>
              <p className="sf-aside-card__p">Новости, обзоры и специальные предложения раз в неделю на вашу почту.</p>
              <div className="sf-aside-form">
                <input placeholder="Ваш e-mail" />
                <button>Подписаться</button>
              </div>
              <p className="sf-aside-fine">Нажимая «Подписаться», вы соглашаетесь с политикой конфиденциальности.</p>
            </div>

            <div className="sf-aside-card">
              <div className="sf-aside-card__h">Читают сейчас</div>
              <div className="sf-popular">
                {d.news.slice(0, 4).map((n, i) => (
                  <button key={n.id} className="sf-popular__item" onClick={() => go('article')}>
                    <span className="sf-popular__n">{i + 1}</span>
                    <span className="sf-popular__t">{n.title}</span>
                  </button>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}

window.NewsScreen = NewsScreen;
