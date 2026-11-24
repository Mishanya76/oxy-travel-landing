(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  /* Mobile navigation */
  const burger = $('.burger');
  const nav = $('#nav');
  burger?.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
  });
  $$('#nav a').forEach((link) => link.addEventListener('click', () => {
    nav.classList.remove('is-open');
    burger?.setAttribute('aria-expanded', 'false');
  }));

  /* Reveal on scroll (progressive enhancement) */
  const revealTargets = $$('.section__head, .feature-card, .anxiety, .destination, .slide, .reviews blockquote, .steps__grid li, .quiz__inner > *, .contacts__grid > *');
  revealTargets.forEach((el) => el.classList.add('js-reveal'));
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealTargets.forEach((el) => observer.observe(el));
  } else {
    revealTargets.forEach((el) => el.classList.add('is-visible'));
  }

  /* Hero parallax */
  const parallax = $('[data-parallax]');
  if (parallax && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let ticking = false;
    const update = () => {
      const y = Math.min(window.scrollY, 900) * 0.18;
      parallax.style.setProperty('--parallax', `${y}px`);
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
  }

  /* Photo slider */
  const slider = $('#slider');
  const scrollSlider = (direction) => {
    if (!slider) return;
    const first = $('.slide', slider);
    const gap = 20;
    const step = first ? first.getBoundingClientRect().width + gap : 380;
    slider.scrollBy({ left: direction * step, behavior: 'smooth' });
  };
  $('.slider__arrow--prev')?.addEventListener('click', () => scrollSlider(-1));
  $('.slider__arrow--next')?.addEventListener('click', () => scrollSlider(1));

  /* Lead modal */
  const modal = $('#leadModal');
  const form = $('#leadForm');
  const success = $('#modalSuccess');
  const modalLead = $('#modalLead');
  let lastFocused = null;

  const openModal = ({ destination = '', source = '' } = {}) => {
    lastFocused = document.activeElement;
    form.hidden = false;
    success.hidden = true;
    if (destination && form.elements.destination) form.elements.destination.value = destination;
    if (source) {
      modalLead.textContent = `Заявка: ${source}. Пришлём 3–5 вариантов и честно расскажем про каждый отель.`;
    } else {
      modalLead.textContent = 'Пришлём 3–5 вариантов и честно расскажем про каждый отель.';
    }
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    $('input[name="name"]', form)?.focus();
  };

  const closeModal = () => {
    modal.hidden = true;
    document.body.style.overflow = '';
    lastFocused?.focus?.();
  };

  $$('.js-lead').forEach((button) => button.addEventListener('click', () => {
    openModal({
      destination: button.dataset.destination || '',
      source: button.dataset.leadSource || button.textContent.trim()
    });
  }));

  $$('[data-close-modal]').forEach((el) => el.addEventListener('click', closeModal));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !modal.hidden) closeModal();
  });

  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const destination = data.get('destination') || 'Ещё не знаю';
    form.hidden = true;
    success.hidden = false;
    $('#successText').textContent = `Спасибо, ${String(data.get('name')).trim()}! Мы записали направление «${destination}». Чтобы ускорить ответ, продублируйте сообщение в VK — там мы отвечаем быстрее всего.`;
    try {
      localStorage.setItem('oxy_lead', JSON.stringify({
        name: data.get('name'),
        contact: data.get('contact'),
        destination,
        createdAt: new Date().toISOString()
      }));
    } catch (_) { /* storage unavailable — no problem */ }
  });

  /* Quiz */
  const questions = [
    {
      title: 'С кем едем отдыхать?',
      options: ['Вдвоём', 'С детьми', 'Компания друзей', 'Один — хочу перезагрузку']
    },
    {
      title: 'Какое настроение отпуска?',
      options: ['Море и релакс', 'Экзотика и впечатления', 'Активности и приключения', 'Красота без перелёта']
    },
    {
      title: 'Когда планируете поездку?',
      options: ['В ближайший месяц', 'Летом', 'Зимой / в праздники', 'Ещё смотрю даты']
    },
    {
      title: 'Комфортный бюджет на человека?',
      options: ['До 80 000 ₽', '80–150 000 ₽', '150–250 000 ₽', 'Выше 250 000 ₽']
    }
  ];

  const quizCard = $('#quizCard');
  const quizQuestion = $('#quizQuestion');
  const quizOptions = $('#quizOptions');
  const quizStep = $('#quizStep');
  const quizProgress = $('#quizProgress');
  const quizBack = $('#quizBack');
  const answers = [];

  const recommendation = () => {
    const mood = answers[1] || '';
    const budget = answers[3] || '';
    if (mood.includes('Красота без')) return 'Россия';
    if (mood.includes('Экзотика')) return budget.includes('250') ? 'Таиланд' : 'Таиланд / Азия';
    if (mood.includes('Активности')) return 'Египет';
    if (budget.includes('150') || budget.includes('250')) return 'ОАЭ';
    return 'Турция';
  };

  const checklistText = (destination) => `ЧЕК-ЛИСТ: что взять в ручную кладь\n\n1. Паспорт и копия билета/тура — в отдельный карман.\n2. Полис страхования и контакты менеджера OXY Travel.\n3. Зарядка, power bank до 100 Wh и кабель — в ручную кладь.\n4. Лекарства в оригинальной упаковке + рецепт, если нужно.\n5. Жидкости до 100 мл в прозрачном пакете.\n6. Сменная футболка и носки: чемодан может задержаться.\n7. Наушники, очки и солнцезащитный крем.\n8. Небольшая сумма наличных и карта без валютной конверсии.\n\nВаша подсказка от теста: ${destination}.\nOXY Travel — подбираем туры так, будто едем сами.\n`;

  const renderQuiz = () => {
    const index = answers.length;
    if (index >= questions.length) return renderResult();

    quizStep.textContent = String(index + 1);
    quizProgress.style.width = `${(index / questions.length) * 100}%`;
    quizQuestion.textContent = questions[index].title;
    quizOptions.innerHTML = '';
    quizBack.hidden = index === 0;

    questions[index].options.forEach((option) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'quiz__option';
      button.textContent = option;
      button.addEventListener('click', () => {
        answers[index] = option;
        answers.length = index + 1;
        button.classList.add('is-selected');
        setTimeout(renderQuiz, 220);
      });
      quizOptions.appendChild(button);
    });
  };

  const renderResult = () => {
    const destination = recommendation();
    quizProgress.style.width = '100%';
    $('#quizStep').textContent = '4';
    quizCard.innerHTML = `
      <div class="quiz__result">
        <span class="eyebrow">ВАШ ОТВЕТ ГОТОВ</span>
        <h3>Похоже, вам подойдёт: ${destination}</h3>
        <p>Мы учли компанию, настроение, сроки и бюджет. Пришлём 5 конкретных отелей и чек-лист для ручной клади.</p>
        <div class="quiz__result-actions">
          <button class="btn btn--lime" type="button" id="getChecklist">Забрать чек-лист 🎁</button>
          <button class="btn btn--vk" type="button" id="getHotels">Получить 5 отелей в VK</button>
        </div>
      </div>`;

    $('#getChecklist').addEventListener('click', () => {
      const blob = new Blob([checklistText(destination)], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'checklist-oxy-travel.txt';
      link.click();
      URL.revokeObjectURL(url);
    });

    $('#getHotels').addEventListener('click', () => {
      openModal({
        destination: destination.replace(' / Азия', ''),
        source: `тест: ${answers.join(' · ')}`
      });
    });
  };

  quizBack?.addEventListener('click', () => {
    if (answers.length > 0) {
      answers.pop();
      renderQuiz();
    }
  });

  if (quizCard) renderQuiz();
})();
