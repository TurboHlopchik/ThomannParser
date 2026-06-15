/* Контакты — отделы, форма обратной связи, карта, мессенджеры, шоурумы, реквизиты. */
const { Breadcrumbs: CBreadcrumbs, Input: CInput, Select: CSelect, Checkbox: CCheckbox, Button: CButton } = window.MusicStoreDesignSystem_f8f6e3;

function ContactsScreen({ go }) {
  const c = window.STORE_DATA.contacts;
  const d = window.STORE_DATA;

  return (
    <main className="sf-page" data-screen-label="Контакты">
      <div className="sf-wrap sf-contacts">
        <div className="sf-pagehead">
          <CBreadcrumbs className="sf-pagehead__crumbs" items={[
            { label: 'Главная', onClick: () => go('home') },
            { label: 'Контакты' },
          ]} />
          <h1>Контакты</h1>
          <p>Свяжитесь с нужным отделом напрямую или напишите нам — ответим в течение рабочего дня. Работаем по всей России.</p>
        </div>

        {/* departments */}
        <div className="sf-dept-grid">
          {c.departments.map((dep) => (
            <div className="sf-dept" key={dep.name}>
              <span className="sf-dept__ico"><i className={`ti ti-${dep.icon}`}></i></span>
              <div className="sf-dept__name">{dep.name}</div>
              <div className="sf-dept__note">{dep.note}</div>
              <div className="sf-dept__lines">
                <a className="sf-dept__phone" href={`tel:${dep.phone.replace(/\D/g, '')}`}>{dep.phone}</a>
                <a className="sf-dept__row" href={`mailto:${dep.email}`}><i className="ti ti-mail"></i> {dep.email}</a>
                <span className="sf-dept__hours">{dep.hours}</span>
              </div>
            </div>
          ))}
        </div>

        {/* feedback form + map/social */}
        <section className="sf-block">
          <div className="sf-contact-split">
            <div>
              <h2 className="sf-block__h">Напишите нам</h2>
              <p className="sf-block__sub">Опишите вопрос — менеджер свяжется с вами и поможет подобрать инструмент или решить вопрос по заказу.</p>
              <form className="sf-form" onSubmit={(e) => e.preventDefault()}>
                <div className="sf-form__grid">
                  <CInput label="Ваше имя" placeholder="Иван Петров" required />
                  <CInput label="Телефон" placeholder="+7 (___) ___-__-__" iconLeft="phone" required />
                  <CInput label="E-mail" placeholder="you@example.ru" iconLeft="mail" />
                  <CSelect label="Тема обращения" placeholder="Выберите тему" options={['Общий вопрос', 'Подбор инструмента', 'Сервис и гарантия', 'Оптовый заказ / B2B']} />
                  <div className="sf-form__wide">
                    <label className="sf-field-label">Сообщение</label>
                    <textarea className="sf-textarea" placeholder="Чем мы можем помочь?"></textarea>
                  </div>
                  <div className="sf-form__wide">
                    <CCheckbox label="Согласен на обработку персональных данных" />
                  </div>
                </div>
                <div className="sf-form__actions">
                  <CButton type="submit" iconLeft="send">Отправить</CButton>
                </div>
              </form>
            </div>

            <div className="sf-contact-right">
              <div className="sf-map sf-ph">
                <i className="ti ti-map-pin"></i>
                <span className="sf-ph__label">карта — интерактивная схема проезда</span>
              </div>
              <div>
                <h3 className="sf-block__h" style={{ fontSize: '18px', marginBottom: '14px' }}>Мессенджеры и соцсети</h3>
                <div className="sf-soclist">
                  {c.social.map((s) => (
                    <a className="sf-soc" key={s.name} href="#" onClick={(e) => e.preventDefault()}>
                      <span className="sf-soc__ico"><i className={`ti ti-${s.icon}`}></i></span>
                      <span className="sf-soc__body">
                        <span className="sf-soc__name">{s.name}</span>
                        <span className="sf-soc__handle">{s.handle}</span>
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* showrooms */}
        <section className="sf-block">
          <h2 className="sf-block__h">Шоурумы</h2>
          <p className="sf-block__sub">Приезжайте послушать и протестировать инструменты. Самовывоз оформленных заказов — в день обращения.</p>
          <div className="sf-store-grid">
            {c.stores.map((st) => (
              <div className="sf-store" key={st.city}>
                <div className="sf-store__city"><i className="ti ti-building-store"></i> {st.city}</div>
                <div className="sf-store__row"><i className="ti ti-map-pin"></i><span>{st.addr}</span></div>
                <div className="sf-store__row"><i className="ti ti-clock"></i><span>{st.hours}</span></div>
                <div className="sf-store__row"><i className="ti ti-phone"></i><a href={`tel:${st.phone.replace(/\D/g, '')}`}>{st.phone}</a></div>
              </div>
            ))}
          </div>
        </section>

        {/* requisites */}
        <section className="sf-block">
          <h2 className="sf-block__h">Реквизиты для юридических лиц</h2>
          <p className="sf-block__sub">Для оптовых заказов и оплаты по счёту. Закрывающие документы предоставляем по запросу в B2B-отделе.</p>
          <div className="sf-req">
            {c.requisites.map(([k, v]) => (
              <div className="sf-req__row" key={k}>
                <span className="sf-req__k">{k}</span>
                <span className="sf-req__v">{v}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

window.ContactsScreen = ContactsScreen;
