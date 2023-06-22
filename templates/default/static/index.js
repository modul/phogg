const userLang = navigator.language || navigator.userLanguage || 'en';
const language = userLang.startsWith('de') ? 'de' : 'en';

function hide(node) {
  node.style.display = 'none';
}

function show(node) {
  node.style.display = 'unset';
}

function setupSlideShow() {
  const slidesContainer = document.getElementById("slides-container");
  const slide = document.querySelector(".slide");
  const prevButton = document.getElementById("slide-arrow-prev");
  const nextButton = document.getElementById("slide-arrow-next");
  const slidesCount = slidesContainer.childElementCount;
  let currentSlide = 0;

  function goToSlide(n) {
    slidesContainer.scrollLeft = n * slide.clientWidth;
    currentSlide = n;
  }

  slidesContainer.addEventListener("scroll", () => {
    const scrollLeft = slidesContainer.scrollLeft;
    const slideWidth = slide.clientWidth;
    const slideNumber = Math.round(scrollLeft / slideWidth);
    if (slideNumber !== currentSlide) {
      currentSlide = slideNumber;
    }
  });

  nextButton.addEventListener("click", () => {
    if (currentSlide < slidesCount - 1) {
      goToSlide(currentSlide + 1);
    }
  });

  prevButton.addEventListener("click", () => {
    if (currentSlide > 0) {
      goToSlide(currentSlide - 1);
    }
  });
}

window.onload = function() {
  const lang = ':lang(' + language + ')';
  document.title = language === 'de' ? 'FotoGRafie' : 'PhotoGRaphy';
  document.querySelectorAll(`[lang]:not(${lang})`).forEach(hide);
  document.querySelectorAll(`[lang]${lang}`).forEach(show);

  setupSlideShow();
};
