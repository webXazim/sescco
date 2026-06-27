(function () {
  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const gsap = window.gsap;

  const releasePreload = () => document.documentElement.classList.remove("gsap-preload");

  if (reduceMotion || !gsap) {
    releasePreload();
    return;
  }

  const ScrollTrigger = window.ScrollTrigger;
  if (ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  document.documentElement.dataset.gsapEnhancements = "ready";

  gsap.defaults({
    ease: "power3.out",
    duration: 0.75
  });

  const toArray = gsap.utils.toArray;
  const isVisible = (el) => {
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  function getHeroAnimationTargets() {
    const hero = document.querySelector(
      ".hero-home, .contact-hero, .services-modern-hero, .page-photo-hero, .service-detail-hero, .career-hero, .career-detail-hero, .career-form-hero, .hero.dark"
    );
    if (!hero) return { items: [], visual: null };

    const items = [
      hero.querySelector(".breadcrumb"),
      hero.querySelector(".eyebrow"),
      hero.querySelector(".hero-kicker"),
      hero.querySelector("h1"),
      hero.querySelector("p"),
      hero.querySelector(".hero-actions")
    ].filter(Boolean);

    const visual = hero.querySelector(".hero-trust-sphere-exact, .hero-visual-photo, .hero-media, .page-hero-media");
    return { items, visual };
  }

  function prepHero(targets) {
    if (targets.items.length) {
      gsap.set(targets.items, { autoAlpha: 0, y: 26 });
    }
    if (targets.visual) {
      gsap.set(targets.visual, { autoAlpha: 0, scale: 0.965 });
    }
  }

  function revealHero(targets) {
    if (targets.items.length) {
      gsap.to(targets.items, {
        autoAlpha: 1,
        y: 0,
        duration: 0.9,
        stagger: 0.08,
        delay: 0.06,
        clearProps: "transform,opacity,visibility"
      });
    }

    const visual = targets.visual;
    if (visual) {
      gsap.to(visual, {
        autoAlpha: 1,
        scale: 1,
        duration: 1.05,
        delay: 0.16,
        clearProps: "transform,opacity,visibility"
      });
    }
  }

  function revealOnScroll() {
    const selector = [
      ".service-card",
      ".trust-logo-card",
      ".certificate-card",
      ".service-process-step",
      ".service-feature-card",
      ".service-deliverable-card",
      ".project-detailed-scope-card",
      ".operational-assurance-item",
      ".trust-standard-card",
      ".trust-document-card",
      ".contact-method-card",
      ".contact-intro-card",
      ".contact-form-card",
      ".contact-side-item",
      ".contact-map-head",
      ".contact-map-frame",
      ".contact-map-side-card",
      ".contact-office-card",
      ".office-card",
      ".career-job-card",
      ".career-benefit-card",
      ".career-step",
      ".career-hero-panel",
      ".career-detail-quick-card",
      ".job-summary-card",
      ".career-application-form",
      ".faq-accordion-card",
      ".services-faq-item",
      ".contact-faq-card",
      ".why-choose-card",
      ".info-strip",
      ".info-item",
      ".home-trust-strip",
      ".project-filter-tabs",
      ".project-live-filter",
      ".project-stats-strip",
      ".project-stat-item",
      ".project-metrics-card",
      ".project-gallery-card",
      ".cta",
      ".cta-card-contrast",
      ".dynamic-section",
      ".section .container > .eyebrow",
      ".section .container > h2",
      ".section .container > p",
      ".section-sm .container > .eyebrow",
      ".section-sm .container > h2",
      ".section-sm .container > p",
      ".contact-section-head",
      ".career-section-head",
      ".career-form-section-title",
      ".trust-documents-head"
    ].join(",");

    const elements = toArray(selector)
      .filter(isVisible)
      .filter((el) => !el.closest(".site-header"))
      .filter((el) => !el.closest(".hero-home, .contact-hero, .services-modern-hero, .page-photo-hero, .service-detail-hero, .career-hero, .career-detail-hero, .career-form-hero, .hero.dark"));
    if (!elements.length) return;

    gsap.set(elements, { autoAlpha: 0, y: 28 });

    if (!ScrollTrigger) {
      gsap.to(elements, {
        autoAlpha: 1,
        y: 0,
        stagger: 0.045,
        clearProps: "transform,opacity,visibility"
      });
      return;
    }

    ScrollTrigger.batch(elements, {
      start: "top 88%",
      once: true,
      onEnter: (batch) => {
        gsap.to(batch, {
          autoAlpha: 1,
          y: 0,
          duration: 0.72,
          stagger: 0.055,
          clearProps: "transform,opacity,visibility",
          overwrite: true
        });
      }
    });
  }

  function polishAccordions() {
    document.querySelectorAll("[data-accordion-item]").forEach((item) => {
      const body = item.querySelector(".services-faq-answer") || item.querySelector(":scope > div");
      if (!body) return;

      item.addEventListener("toggle", () => {
        if (!item.open) return;
        gsap.fromTo(body,
          { autoAlpha: 0, y: -8 },
          { autoAlpha: 1, y: 0, duration: 0.34, ease: "power2.out", clearProps: "transform,opacity,visibility" }
        );
      });
    });
  }

  function polishInteractiveElements() {
    const buttons = toArray(".btn")
      .filter(isVisible)
      .filter((button) => !button.closest(".site-header"));
    buttons.forEach((button) => {
      button.addEventListener("mouseenter", () => {
        gsap.to(button, { y: -1, duration: 0.18, ease: "power2.out", overwrite: true });
      });
      button.addEventListener("mouseleave", () => {
        gsap.to(button, { y: 0, duration: 0.22, ease: "power2.out", overwrite: true, clearProps: "transform" });
      });
    });

    const liftItems = toArray([
      ".service-modern-card",
      ".project-card",
      ".certificate-card",
      ".why-choose-card",
      ".contact-method-card",
      ".contact-office-card",
      ".career-job-card",
      ".trust-document-card"
    ].join(",")).filter(isVisible);

    liftItems.forEach((item) => {
      item.addEventListener("mouseenter", () => {
        gsap.to(item, { y: -4, duration: 0.24, ease: "power2.out", overwrite: true });
      });
      item.addEventListener("mouseleave", () => {
        gsap.to(item, { y: 0, duration: 0.26, ease: "power2.out", overwrite: true, clearProps: "transform" });
      });
    });
  }

  function polishFormFields() {
    const fields = toArray("input, select, textarea").filter((field) => !field.closest(".site-header"));
    fields.forEach((field) => {
      field.addEventListener("focus", () => {
        gsap.to(field, { scale: 1.01, duration: 0.16, ease: "power2.out", overwrite: true });
      });
      field.addEventListener("blur", () => {
        gsap.to(field, { scale: 1, duration: 0.18, ease: "power2.out", overwrite: true, clearProps: "transform" });
      });
    });
  }

  function polishHeroDepth() {
    if (!ScrollTrigger) return;
    const hero = document.querySelector(".hero-home, .contact-hero, .page-photo-hero, .service-detail-hero, .career-hero, .hero.dark");
    if (!hero) return;

    const photo = hero.querySelector(".hero-visual-photo, .hero-media, .page-hero-media");
    if (photo) {
      gsap.to(photo, {
        yPercent: 4,
        ease: "none",
        scrollTrigger: {
          trigger: hero,
          start: "top top",
          end: "bottom top",
          scrub: true
        }
      });
    }
  }

  function init() {
    const heroTargets = getHeroAnimationTargets();
    prepHero(heroTargets);
    releasePreload();
    revealHero(heroTargets);
    revealOnScroll();
    polishAccordions();
    polishInteractiveElements();
    polishFormFields();
    polishHeroDepth();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
