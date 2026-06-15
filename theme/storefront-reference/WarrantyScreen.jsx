/* Гарантия и возврат — сроки по категориям, процесс, условия, FAQ, форма заявки. */
const { Breadcrumbs: WBreadcrumbs, Accordion: WAccordion, Input: WInput, Select: WSelect, Checkbox: WCheckbox, Button: WButton } = window.MusicStoreDesignSystem_f8f6e3;

function WarrantyScreen({ go }) {
  const w = window.STORE_DATA.warranty;

  return (
    <main className="sf-page" data-screen-label="Гарантия и возврат">
      <div className="sf-wrap sf-warranty">
        <div className="sf-pagehead">
          <WBreadcrumbs className="sf-pagehead__crumbs" items={[
            { label: 'Главная', onClick: () => go('home') },
            { label: 'Покупателям' },
            { label: 'Гарантия и возврат' },
          ]} />
          <h1>Гарантия и возврат</h1>
          <p>Мы продаём только оригинальные инструменты с официальной гарантией производителя. Если что-то не подошло или возникла неисправность — поможем с возвратом, обменом и сервисом.</p>
        </div>

        {/* highlights */}
        <div className="sf-w-highlights">
          {[
            { i: 'shield-check', b: 'Официальная гарантия', s: 'На все инструменты и оборудование от производителя' },
            { i: 'rotate-2', b: 'Возврат за 14 дней', s: 'Без объяснения причин для товара надлежащего качества' },
            { i: 'tool', b: 'Свой сервис-центр', s: 'Диагностика, настройка и ремонт в наших мастерских' },
          ].map((h) => (
            <div className="sf-w-highlight" key={h.b}>
              <span className="sf-w-highlight__ico"><i className={`ti ti-${h.i}`}></i></span>
              <span><b>{h.b}</b><span>{h.s}</span></span>
            </div>
          ))}
        </div>

        {/* terms by category */}
        <section className="sf-block">
          <h2 className="sf-block__h">Сроки гарантии по категориям</h2>
          <p className="sf-block__sub">Базовые сроки гарантии производителя. Для отдельных моделей срок может быть увеличен — он указан в карточке товара и гарантийном талоне.</p>
          <div className="sf-wterms">
            {w.terms.map((t) => (
              <div className="sf-wterm" key={t.cat}>
                <span className="sf-wterm__ico"><i className={`ti ti-${t.icon}`}></i></span>
                <span className="sf-wterm__body">
                  <span className="sf-wterm__cat">{t.cat}</span>
                  <span className="sf-wterm__term">{t.term}</span>
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* return process */}
        <section className="sf-block">
          <h2 className="sf-block__h">Как оформить возврат</h2>
          <p className="sf-block__sub">Четыре шага — от обращения до возврата средств. Менеджер сопровождает вас на каждом этапе.</p>
          <div className="sf-steps4">
            {w.returnSteps.map((s, i) => (
              <div className="sf-step" key={s.h}>
                <span className="sf-step__n">{String(i + 1).padStart(2, '0')}</span>
                <span className="sf-step__ico"><i className={`ti ti-${s.icon}`}></i></span>
                <b>{s.h}</b>
                <p>{s.t}</p>
              </div>
            ))}
          </div>
        </section>

        {/* conditions */}
        <section className="sf-block">
          <h2 className="sf-block__h">Условия возврата</h2>
          <p className="sf-block__sub">Товар надлежащего качества можно вернуть в течение 14 дней с момента получения при соблюдении условий.</p>
          <div className="sf-cond-grid">
            <div className="sf-cond">
              <div className="sf-cond__h sf-cond__h--ok"><i className="ti ti-circle-check"></i> Можно вернуть, если</div>
              <div className="sf-cond__list">
                {w.conditions.map((c) => (
                  <div className="sf-cond__item sf-cond__item--ok" key={c}><i className="ti ti-check"></i><span>{c}</span></div>
                ))}
              </div>
            </div>
            <div className="sf-cond">
              <div className="sf-cond__h sf-cond__h--no"><i className="ti ti-circle-x"></i> Не подлежат возврату</div>
              <div className="sf-cond__list">
                {w.nonReturnable.map((c) => (
                  <div className="sf-cond__item sf-cond__item--no" key={c}><i className="ti ti-x"></i><span>{c}</span></div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* faq + return form */}
        <section className="sf-block">
          <div className="sf-w-split">
            <div>
              <h2 className="sf-block__h">Частые вопросы</h2>
              <p className="sf-block__sub">Коротко о гарантии, возврате и сервисе.</p>
              <div className="sf-faq">
                {w.faq.map((f, i) => (
                  <WAccordion key={f.q} title={f.q} defaultOpen={i === 0}>
                    <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', lineHeight: 1.65, margin: 0 }}>{f.a}</p>
                  </WAccordion>
                ))}
              </div>
            </div>

            <div>
              <h2 className="sf-block__h">Заявка на возврат</h2>
              <p className="sf-block__sub">Заполните форму — менеджер свяжется с вами в течение рабочего дня и согласует детали.</p>
              <form className="sf-form" onSubmit={(e) => e.preventDefault()}>
                <div className="sf-form__note"><i className="ti ti-info-circle"></i><span>Номер заказа указан в письме-подтверждении и в личном кабинете в разделе «Мои заказы».</span></div>
                <div className="sf-form__grid">
                  <WInput label="Номер заказа" placeholder="№ 100245" required />
                  <WSelect label="Причина возврата" placeholder="Выберите причину" options={w.returnReasons} />
                  <WInput className="sf-form__wide" label="Ваше имя" placeholder="Иван Петров" required />
                  <WInput label="Телефон" placeholder="+7 (___) ___-__-__" iconLeft="phone" required />
                  <WInput label="E-mail" placeholder="you@example.ru" iconLeft="mail" />
                  <div className="sf-form__wide">
                    <label className="sf-field-label">Комментарий</label>
                    <textarea className="sf-textarea" placeholder="Опишите ситуацию: что не подошло или какая неисправность"></textarea>
                  </div>
                  <div className="sf-form__wide">
                    <label className="sf-field-label">Фото или документы</label>
                    <div className="sf-file"><i className="ti ti-paperclip"></i> Прикрепите файлы — чек, фото товара (до 10 МБ)</div>
                  </div>
                  <div className="sf-form__wide">
                    <WCheckbox label="Согласен на обработку персональных данных" />
                  </div>
                </div>
                <div className="sf-form__actions">
                  <WButton type="submit" iconLeft="send">Отправить заявку</WButton>
                  <span className="sf-form__agree">Или позвоните: <b style={{ color: 'var(--text)' }}>8 (800) 550-10-32</b></span>
                </div>
              </form>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

window.WarrantyScreen = WarrantyScreen;
