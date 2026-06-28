document.addEventListener("DOMContentLoaded", function () {

// SESCCO production image fallback: broken CMS/media images should not leave
// empty cards in production. Templates can override via data-fallback.
const productionFallbackImage = "/static/img/fallbacks/industrial-fallback.svg";
document.querySelectorAll("img").forEach((image) => {
  image.loading = image.loading || "lazy";
  image.decoding = image.decoding || "async";
  image.addEventListener("error", () => {
    if (image.dataset.fallbackApplied === "1") return;
    image.dataset.fallbackApplied = "1";
    image.src = image.dataset.fallback || productionFallbackImage;
    image.classList.add("is-fallback-image");
  }, { once: true });
});


  // Keep the top navigation stable; premium motion is handled in section content, not the header.
  const siteHeader = document.querySelector(".site-header");
  if (siteHeader) {
    const syncHeaderState = () => {
      siteHeader.classList.remove("nav-hidden");
      siteHeader.classList.toggle("nav-scrolled", window.scrollY > 8);
      document.body.classList.add("public-header-visible");
      document.body.classList.remove("public-header-hidden");
    };

    syncHeaderState();
    window.addEventListener("scroll", syncHeaderState, { passive: true });
    window.addEventListener("resize", syncHeaderState);
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) syncHeaderState();
    });
  }
  const toggle = document.querySelector(".mobile-toggle");
  const nav = document.querySelector(".nav-links");

  // Mark the current navigation item, including localized URLs.
  if (nav) {
    const currentPath = window.location.pathname.replace(/^\/(ar|zh-hans|en)(?=\/|$)/, "") || "/";
    nav.querySelectorAll("a").forEach((link) => {
      const url = new URL(link.getAttribute("href"), window.location.origin);
      const linkPath = url.pathname.replace(/^\/(ar|zh-hans|en)(?=\/|$)/, "") || "/";
      const isHome = linkPath === "/";
      const isActive = isHome ? currentPath === "/" : currentPath === linkPath || currentPath.startsWith(linkPath);
      if (isActive) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      }
    });
  }

  if (toggle && nav) {
    const openLabel = toggle.getAttribute("aria-label") || "Open menu";
    const closeLabel = "Close menu";

    const setMobileNavState = (isOpen) => {
      nav.classList.toggle("mobile-open", isOpen);
      toggle.classList.toggle("is-open", isOpen);
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      toggle.setAttribute("aria-label", isOpen ? closeLabel : openLabel);
      document.body.classList.toggle("nav-open", isOpen);
    };

    toggle.addEventListener("click", function () {
      setMobileNavState(!nav.classList.contains("mobile-open"));
    });

    const closeMobileNav = () => {
      setMobileNavState(false);
    };

    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", closeMobileNav);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && nav.classList.contains("mobile-open")) {
        closeMobileNav();
        toggle.focus({ preventScroll: true });
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 980 && nav.classList.contains("mobile-open")) {
        closeMobileNav();
      }
    });
  }

  // Certificate gallery modal: one reusable modal for all CMS-uploaded certificate images.
  const certificateModal = document.querySelector("[data-certificate-modal]");
  if (certificateModal) {
    const modalImage = certificateModal.querySelector("[data-certificate-modal-image]");
    const modalTitle = certificateModal.querySelector("[data-certificate-modal-title]");
    const modalMeta = certificateModal.querySelector("[data-certificate-modal-meta]");
    const modalDescription = certificateModal.querySelector("[data-certificate-modal-description]");
    const modalDescriptionBlock = certificateModal.querySelector("[data-certificate-modal-description-block]");
    const modalType = certificateModal.querySelector("[data-certificate-modal-type]");
    const modalTypeRow = certificateModal.querySelector("[data-certificate-modal-type-row]");
    const modalIssuer = certificateModal.querySelector("[data-certificate-modal-issuer]");
    const modalIssuerRow = certificateModal.querySelector("[data-certificate-modal-issuer-row]");
    const modalDownload = certificateModal.querySelector("[data-certificate-modal-download]");
    const openButtons = document.querySelectorAll("[data-certificate-open]");
    let lastFocusedTrigger = null;

    const closeCertificateModal = () => {
      certificateModal.classList.remove("is-open");
      certificateModal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("certificate-modal-open");
      document.documentElement.classList.remove("certificate-modal-open");
      if (modalImage) {
        modalImage.removeAttribute("src");
        modalImage.removeAttribute("alt");
      }
      if (lastFocusedTrigger) {
        lastFocusedTrigger.focus({ preventScroll: true });
      }
    };

    const openCertificateModal = (trigger) => {
      const imageSrc = trigger.dataset.image;
      if (!imageSrc) return;
      lastFocusedTrigger = trigger;
      const title = trigger.dataset.title || "Certificate";
      const description = trigger.dataset.description || "";
      const certificateType = trigger.dataset.type || "";
      const issuer = trigger.dataset.issuer || "";
      const meta = trigger.dataset.meta || "";
      const downloadUrl = trigger.dataset.download || "";

      if (modalImage) {
        modalImage.src = imageSrc;
        modalImage.alt = title;
      }
      if (modalTitle) modalTitle.textContent = title;
      if (modalDescription) modalDescription.textContent = description;
      if (modalDescriptionBlock) modalDescriptionBlock.hidden = !description;
      if (modalType) modalType.textContent = certificateType;
      if (modalTypeRow) modalTypeRow.hidden = !certificateType;
      if (modalIssuer) modalIssuer.textContent = issuer;
      if (modalIssuerRow) modalIssuerRow.hidden = !issuer;
      if (modalMeta) {
        modalMeta.textContent = meta;
        modalMeta.hidden = true;
      }
      if (modalDownload) {
        if (downloadUrl) {
          modalDownload.href = downloadUrl;
          modalDownload.hidden = false;
        } else {
          modalDownload.hidden = true;
          modalDownload.removeAttribute("href");
        }
      }

      certificateModal.classList.add("is-open");
      certificateModal.setAttribute("aria-hidden", "false");
      document.body.classList.add("certificate-modal-open");
      document.documentElement.classList.add("certificate-modal-open");
      document.body.classList.remove("nav-open");
      const siteNav = document.querySelector("[data-mobile-nav]");
      const siteNavToggle = document.querySelector("[data-mobile-toggle]");
      if (siteNav) siteNav.classList.remove("mobile-open");
      if (siteNavToggle) siteNavToggle.setAttribute("aria-expanded", "false");
      const closeButton = certificateModal.querySelector("[data-certificate-close]");
      if (closeButton) closeButton.focus({ preventScroll: true });
    };

    openButtons.forEach((button) => {
      button.addEventListener("click", () => openCertificateModal(button));
    });

    certificateModal.querySelectorAll("[data-certificate-close]").forEach((closeEl) => {
      closeEl.addEventListener("click", closeCertificateModal);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && certificateModal.classList.contains("is-open")) {
        closeCertificateModal();
      }
    });
  }


  // Project detail slideshow gallery. Images are uploaded in Admin → Projects → Project → Gallery images.
  document.querySelectorAll("[data-project-slider]").forEach((slider) => {
    const slides = Array.from(slider.querySelectorAll("[data-project-slide]"));
    const prev = slider.querySelector("[data-project-slide-prev]");
    const next = slider.querySelector("[data-project-slide-next]");
    const thumbsWrap = slider.querySelector("[data-project-slide-thumbs]");
    const titleEl = slider.querySelector("[data-project-slide-title]");
    const descEl = slider.querySelector("[data-project-slide-description]");
    const countEl = slider.querySelector("[data-project-slider-count]");
    if (!slides.length) return;

    let activeIndex = Math.max(0, slides.findIndex((slide) => slide.classList.contains("is-active")));
    let autoplayTimer = null;
    const thumbs = [];

    const updateSlider = (index) => {
      activeIndex = (index + slides.length) % slides.length;
      slides.forEach((slide, slideIndex) => {
        slide.classList.toggle("is-active", slideIndex === activeIndex);
      });
      thumbs.forEach((thumb, thumbIndex) => {
        thumb.classList.toggle("is-active", thumbIndex === activeIndex);
        thumb.setAttribute("aria-selected", thumbIndex === activeIndex ? "true" : "false");
      });
      const activeSlide = slides[activeIndex];
      const caption = activeSlide.dataset.caption || "Project image";
      const description = activeSlide.dataset.description || "Project gallery image";
      if (titleEl) titleEl.textContent = caption;
      if (descEl) descEl.textContent = description;
      if (countEl) countEl.textContent = `${activeIndex + 1} / ${slides.length}`;
    };

    if (thumbsWrap) {
      slides.forEach((slide, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "project-gallery-thumb";
        button.setAttribute("aria-label", `Show project image ${index + 1}`);
        const img = slide.querySelector("img");
        if (img) {
          const thumbImg = document.createElement("img");
          thumbImg.src = img.currentSrc || img.src;
          thumbImg.alt = "";
          button.appendChild(thumbImg);
        } else {
          button.appendChild(document.createElement("span"));
        }
        button.addEventListener("click", () => {
          updateSlider(index);
          restartAutoplay();
        });
        thumbsWrap.appendChild(button);
        thumbs.push(button);
      });
    }

    const stopAutoplay = () => {
      if (autoplayTimer) {
        window.clearInterval(autoplayTimer);
        autoplayTimer = null;
      }
    };

    const startAutoplay = () => {
      if (slides.length <= 1 || autoplayTimer || document.hidden) return;
      autoplayTimer = window.setInterval(() => updateSlider(activeIndex + 1), 5000);
    };

    function restartAutoplay() {
      stopAutoplay();
      startAutoplay();
    }

    if (prev) prev.addEventListener("click", () => {
      updateSlider(activeIndex - 1);
      restartAutoplay();
    });
    if (next) next.addEventListener("click", () => {
      updateSlider(activeIndex + 1);
      restartAutoplay();
    });
    if (slides.length <= 1) {
      if (prev) prev.hidden = true;
      if (next) next.hidden = true;
      if (thumbsWrap) thumbsWrap.hidden = true;
    }
    updateSlider(activeIndex);
    slider.addEventListener("mouseenter", stopAutoplay);
    slider.addEventListener("mouseleave", startAutoplay);
    slider.addEventListener("focusin", stopAutoplay);
    slider.addEventListener("focusout", startAutoplay);
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stopAutoplay();
      else startAutoplay();
    });
    startAutoplay();
  });


  // Services list realtime filtering and sorting.
  const servicesFilter = document.querySelector("[data-services-filter]");
  const servicesGrid = document.querySelector("[data-services-grid]");
  if (servicesFilter && servicesGrid) {
    const searchInput = servicesFilter.querySelector("[data-services-search]");
    const categorySelect = servicesFilter.querySelector("[data-services-category]");
    const sortSelect = servicesFilter.querySelector("[data-services-sort]");
    const summaryEl = document.querySelector("[data-services-summary]");
    const emptyEl = servicesGrid.querySelector("[data-services-empty]");
    const serviceCards = Array.from(servicesGrid.querySelectorAll("[data-service-card]"));

    const normalise = (value) => (value || "")
      .toString()
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();

    serviceCards.forEach((card) => {
      const title = card.querySelector("h3") ? card.querySelector("h3").textContent : "";
      card.dataset.title = normalise(title);
      card.dataset.searchText = normalise(card.textContent);
    });

    const sortCards = (cards) => {
      const mode = sortSelect ? sortSelect.value : "default";
      return [...cards].sort((a, b) => {
        if (mode === "title") {
          return (a.dataset.title || "").localeCompare(b.dataset.title || "");
        }
        if (mode === "featured") {
          const featuredDiff = Number(b.dataset.featured || 0) - Number(a.dataset.featured || 0);
          if (featuredDiff) return featuredDiff;
        }
        if (mode === "newest") {
          return Number(b.dataset.created || 0) - Number(a.dataset.created || 0);
        }
        return Number(a.dataset.order || 0) - Number(b.dataset.order || 0);
      });
    };

    const syncQueryString = () => {
      const params = new URLSearchParams(window.location.search);
      const query = searchInput ? searchInput.value.trim() : "";
      const category = categorySelect ? categorySelect.value : "";
      const sort = sortSelect ? sortSelect.value : "default";

      query ? params.set("q", query) : params.delete("q");
      category ? params.set("category", category) : params.delete("category");
      sort && sort !== "default" ? params.set("sort", sort) : params.delete("sort");

      const nextUrl = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ""}`;
      window.history.replaceState({}, "", nextUrl);
    };

    const applyServiceFilters = () => {
      const query = normalise(searchInput ? searchInput.value : "");
      const category = categorySelect ? categorySelect.value : "";
      let visibleCount = 0;

      const sortedCards = sortCards(serviceCards);
      sortedCards.forEach((card) => servicesGrid.appendChild(card));
      if (emptyEl) servicesGrid.appendChild(emptyEl);

      sortedCards.forEach((card) => {
        const matchesQuery = !query || (card.dataset.searchText || "").includes(query);
        const matchesCategory = !category || card.dataset.category === category;
        const isVisible = matchesQuery && matchesCategory;
        card.hidden = !isVisible;
        card.classList.toggle("is-filtered-out", !isVisible);
        if (isVisible) visibleCount += 1;
      });

      if (emptyEl) emptyEl.hidden = visibleCount !== 0;
      if (summaryEl) {
        summaryEl.textContent = visibleCount === serviceCards.length
          ? `${visibleCount} services available`
          : `${visibleCount} of ${serviceCards.length} services shown`;
      }
      syncQueryString();
    };

    servicesFilter.addEventListener("submit", (event) => {
      event.preventDefault();
      applyServiceFilters();
    });
    if (searchInput) searchInput.addEventListener("input", applyServiceFilters);
    if (categorySelect) categorySelect.addEventListener("change", applyServiceFilters);
    if (sortSelect) sortSelect.addEventListener("change", applyServiceFilters);
    applyServiceFilters();
  }

});

// Upgrade 85: Projects page realtime filtering, URL sync, and client-side sorting.
(function () {
  const form = document.querySelector('[data-project-filter-form]');
  const resultsWrap = document.querySelector('[data-project-results]');
  if (!form || !resultsWrap) return;

  const searchInput = form.querySelector('[data-project-search]');
  const statusSelect = form.querySelector('[data-project-status]');
  const yearSelect = form.querySelector('[data-project-year]');
  const sortSelect = form.querySelector('[data-project-sort]');
  const clearBtn = form.querySelector('[data-project-clear]');
  const tabs = Array.from(document.querySelectorAll('[data-project-category]'));
  const feedback = document.querySelector('[data-project-filter-feedback]');
  const emptyState = document.querySelector('[data-project-empty]');
  const featured = document.querySelector('[data-project-featured]');
  let activeCategory = new URLSearchParams(window.location.search).get('category') || '';

  function norm(value) {
    return String(value || '').toLowerCase().replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
  }

  function cardText(card) {
    return norm([
      card.dataset.title,
      card.dataset.categoryName,
      card.dataset.statusLabel,
      card.dataset.year,
      card.dataset.location,
      card.dataset.client,
      card.dataset.contractor,
      card.dataset.description
    ].join(' '));
  }

  function matches(card) {
    const q = norm(searchInput ? searchInput.value : '');
    const status = statusSelect ? statusSelect.value : '';
    const year = yearSelect ? yearSelect.value : '';
    const category = activeCategory;
    if (category && card.dataset.category !== category) return false;
    if (status && card.dataset.status !== status) return false;
    if (year && card.dataset.year !== year) return false;
    if (q && !cardText(card).includes(q)) return false;
    return true;
  }

  function compareCards(a, b) {
    const sort = sortSelect ? sortSelect.value : '-year';
    const ay = parseInt(a.dataset.year || '0', 10);
    const by = parseInt(b.dataset.year || '0', 10);
    const at = norm(a.dataset.title);
    const bt = norm(b.dataset.title);
    if (sort === 'year') return ay - by || at.localeCompare(bt);
    if (sort === '-year') return by - ay || at.localeCompare(bt);
    if (sort === 'title') return at.localeCompare(bt);
    return 0;
  }

  function syncUrl() {
    const params = new URLSearchParams();
    const q = searchInput ? searchInput.value.trim() : '';
    if (q) params.set('q', q);
    if (activeCategory) params.set('category', activeCategory);
    if (statusSelect && statusSelect.value) params.set('status', statusSelect.value);
    if (yearSelect && yearSelect.value) params.set('year', yearSelect.value);
    if (sortSelect && sortSelect.value && sortSelect.value !== '-year') params.set('sort', sortSelect.value);
    const next = `${window.location.pathname}${params.toString() ? `?${params}` : ''}`;
    window.history.replaceState({}, '', next);
  }

  function updateTabs() {
    tabs.forEach((tab) => tab.classList.toggle('active', (tab.dataset.projectCategory || '') === activeCategory));
  }

  function applyFilters() {
    const cards = Array.from(resultsWrap.querySelectorAll('[data-project-card]'));
    cards.sort(compareCards).forEach((card) => resultsWrap.appendChild(card));

    let count = 0;
    cards.forEach((card) => {
      const visible = matches(card);
      card.classList.toggle('is-hidden', !visible);
      if (visible) count += 1;
    });

    const featuredVisible = featured ? matches(featured) : false;
    if (featured) featured.classList.toggle('is-hidden', !featuredVisible);

    if (emptyState) emptyState.hidden = count > 0 || featuredVisible;
    if (feedback) {
      const total = count + (featuredVisible ? 1 : 0);
      const singleMessage = feedback.dataset.single || 'Showing 1 matching project.';
      const manyMessage = feedback.dataset.many || 'Showing {count} matching projects.';
      feedback.textContent = total === 1 ? singleMessage : manyMessage.replace('{count}', total);
    }

    const hasFilters = Boolean((searchInput && searchInput.value.trim()) || activeCategory || (statusSelect && statusSelect.value) || (yearSelect && yearSelect.value) || (sortSelect && sortSelect.value !== '-year'));
    if (clearBtn) clearBtn.hidden = !hasFilters;
    updateTabs();
    syncUrl();
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    applyFilters();
  });
  ['input', 'change'].forEach((eventName) => form.addEventListener(eventName, applyFilters));

  tabs.forEach((tab) => {
    tab.addEventListener('click', function () {
      activeCategory = tab.dataset.projectCategory || '';
      applyFilters();
    });
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      if (searchInput) searchInput.value = '';
      if (statusSelect) statusSelect.value = '';
      if (yearSelect) yearSelect.value = '';
      if (sortSelect) sortSelect.value = '-year';
      activeCategory = '';
      applyFilters();
      if (searchInput) searchInput.focus();
    });
  }

  applyFilters();
})();

// Upgrade 89: keep fixed header offset accurate after logos/fonts/responsive changes.
document.addEventListener("DOMContentLoaded", function () {
  const header = document.querySelector(".site-header");
  if (!header) return;

  const syncHeaderHeight = () => {
    const measured = Math.ceil(header.getBoundingClientRect().height || 82);
    // Guard against feedback loops: CSS uses --site-header-height for offsets,
    // and older observers could accidentally write an already-grown header back
    // into the same variable. Clamp to the real expected public header range.
    const compact = window.matchMedia("(max-width: 560px)").matches ? 64 : (window.matchMedia("(max-width: 980px)").matches ? 68 : 74);
    const height = Math.min(92, Math.max(compact, measured > 120 ? compact : measured));
    document.documentElement.style.setProperty("--site-header-height", `${height}px`);
  };

  syncHeaderHeight();
  window.addEventListener("load", syncHeaderHeight, { once: true });
  window.addEventListener("resize", syncHeaderHeight, { passive: true });

  if ("ResizeObserver" in window) {
    let frame = null;
    const observer = new ResizeObserver(() => {
      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(syncHeaderHeight);
    });
    observer.observe(header);
  }
});

// Upgrade 93: mobile form usability helpers.
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('.upload-box input[type="file"]').forEach(function (input) {
    const box = input.closest('.upload-box');
    if (!box) return;
    const originalText = box.querySelector('span') ? box.querySelector('span').textContent : '';
    input.addEventListener('change', function () {
      const count = input.files ? input.files.length : 0;
      box.classList.toggle('is-file-selected', count > 0);
      const help = box.querySelector('span');
      if (!help) return;
      if (!count) {
        help.textContent = originalText;
      } else if (count === 1) {
        help.textContent = input.files[0].name;
      } else {
        help.textContent = count + ' files selected';
      }
    });
  });

  document.querySelectorAll('form input, form select, form textarea').forEach(function (field) {
    field.addEventListener('invalid', function () {
      setTimeout(function () {
        try { field.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e) { field.scrollIntoView(); }
      }, 0);
    }, { once: false });
  });
});

// Upgrade 95: small-screen polish helpers.
document.addEventListener("DOMContentLoaded", function () {
  const root = document.documentElement;
  const syncViewportHeight = function () {
    root.style.setProperty("--app-vh", (window.innerHeight * 0.01) + "px");
  };
  syncViewportHeight();
  window.addEventListener("resize", syncViewportHeight, { passive: true });
  window.addEventListener("orientationchange", function () {
    setTimeout(syncViewportHeight, 250);
  }, { passive: true });

  document.querySelectorAll('.tabs, .category-tabs, .filter-tabs, .project-category-tabs, .service-category-tabs').forEach(function (rail) {
    const active = rail.querySelector('.active, [aria-current="page"]');
    if (!active) return;

    // Keep tab rails horizontally centered without causing vertical page jumps.
    // scrollIntoView({block:'nearest'}) can still move the page down on the
    // Clients page because its active tab rail sits below the hero section.
    try {
      const railBox = rail.getBoundingClientRect();
      const activeBox = active.getBoundingClientRect();
      const delta = (activeBox.left + activeBox.width / 2) - (railBox.left + railBox.width / 2);
      rail.scrollLeft += delta;
    } catch (e) {}
  });

  // Defensive fix: never let the clients/trust page start slightly scrolled
  // just because an active tab rail was initialized below the hero.
  if (!window.location.hash && document.querySelector('.trust-logo-tabs')) {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    requestAnimationFrame(function () {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    });
  }
});



/* Upgrade 98 — Exact integrated SESCCO trust sphere */
(function () {
  const wrap = document.querySelector('[data-home-sphere-wrap]');
  const sphere = document.querySelector('[data-home-sphere]');
  if (!wrap || !sphere) return;
  if (window.matchMedia && window.matchMedia('(max-width: 980px)').matches) {
    wrap.setAttribute('aria-hidden', 'true');
    return;
  }

  const fallbackCards = [
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_01_industrial_construction.webp', title: 'Industrial Construction', sub: 'Field execution & coordination' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_02_electrical_works.webp', title: 'Electrical Works', sub: 'Power systems and installation' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_03_project_control.webp', title: 'Project Control', sub: 'Planning, reporting and quality' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_04_safety_management.webp', title: 'Safety Management', sub: 'HSE-first delivery culture' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_05_qa_inspection.webp', title: 'QA Inspection', sub: 'Checklist-led quality control' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_06_site_engineering.webp', title: 'Site Engineering', sub: 'Civil, MEP and technical teams' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_07_substation_works.webp', title: 'Substation Works', sub: 'Electrical infrastructure delivery' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_08_pipeline_fabrication.webp', title: 'Pipeline Fabrication', sub: 'Mechanical and field support' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_09_mep_coordination.webp', title: 'MEP Coordination', sub: 'Cross-discipline technical planning' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch1_10_civil_site_team.webp', title: 'Civil Site Team', sub: 'Construction supervision' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_01_structural_steel_erection.webp', title: 'Structural Steel Erection', sub: 'Steel framing and erection support' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_02_hvac_systems.webp', title: 'HVAC Systems', sub: 'Cooling, ventilation and ductwork solutions' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_03_fire_protection.webp', title: 'Fire Protection', sub: 'Detection, suppression and safety systems' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_04_instrumentation_control.webp', title: 'Instrumentation & Control', sub: 'Sensors, panels and system integration' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_05_telecom_infrastructure.webp', title: 'Telecom Infrastructure', sub: 'Network, cabling and communications support' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_06_water_treatment.webp', title: 'Water Treatment', sub: 'Process systems and utility plant support' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_07_solar_energy.webp', title: 'Solar Energy', sub: 'Renewable power and installation support' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_08_survey_earthworks.webp', title: 'Survey & Earthworks', sub: 'Site layout, levels and ground preparation' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_09_warehouse_logistics.webp', title: 'Warehouse Logistics', sub: 'Material handling and supply support' },
    { type: 'image', src: '/static/img/hero_sphere/optimized/batch2_10_industrial_automation.webp', title: 'Industrial Automation', sub: 'Smart controls and process efficiency' }
  ];

  function readConfiguredCards() {
    const script = document.getElementById('home-sphere-card-data');
    if (!script) return [];
    try {
      const parsed = JSON.parse(script.textContent || '[]');
      if (!Array.isArray(parsed)) return [];
      return parsed
        .filter((item) => item && item.type === 'image' && item.src)
        .map((item) => ({
          type: 'image',
          src: item.src || '',
          title: item.title || '',
          sub: '',
          big: '',
          alt: item.alt || item.title || '',
        }));
    } catch (error) {
      return [];
    }
  }

  const configuredCards = readConfiguredCards();
  const cards = configuredCards.length ? configuredCards : fallbackCards;

  const state = {
    rotationX: -8,
    rotationY: 0,
    autoRotationX: 0,
    autoRotationY: 0,
    baseTiltX: -8,
    pointerTargetX: 0,
    pointerTargetY: 0,
    pointerCurrentX: 0,
    pointerCurrentY: 0,
    pointerSpinTargetX: 0,
    pointerSpinTargetY: 0,
    pointerSpinCurrentX: 0,
    pointerSpinCurrentY: 0,
    pointerRelX: 0,
    pointerRelY: 0,
    wheelTargetX: 0,
    wheelTargetY: 0,
    wheelCurrentX: 0,
    wheelCurrentY: 0,
    focusTargetX: 0,
    focusTargetY: 0,
    focusCurrentX: 0,
    focusCurrentY: 0,
    focusedIndex: null,
    hovering: false,
    dragging: false,
    moved: false,
    lastX: 0,
    lastY: 0,
    radius: 265,
    autoSpeed: 0.04,
    manualUntil: 0
  };

  function radiusForViewport() {
    const width = wrap.getBoundingClientRect().width;
    return Math.max(160, Math.min(245, width * 0.405));
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function lerp(start, end, alpha) {
    return start + (end - start) * alpha;
  }

  function directionalSpin(value, maxSpeed) {
    const deadZone = 0.12;
    const magnitude = Math.abs(value);
    if (magnitude < deadZone) return 0;
    const normalized = (magnitude - deadZone) / (1 - deadZone);
    return Math.sign(value) * Math.min(maxSpeed, normalized * maxSpeed);
  }

  function pointerVectorFromEvent(event) {
    const rect = wrap.getBoundingClientRect();
    return {
      x: clamp(((event.clientX - rect.left) / rect.width - 0.5) * 2, -1, 1),
      y: clamp(((event.clientY - rect.top) / rect.height - 0.5) * 2, -1, 1)
    };
  }

  function syncPointerIntent(relX, relY) {
    state.pointerRelX = relX;
    state.pointerRelY = relY;
    state.pointerTargetY = clamp(relX * 5, -5, 5);
    state.pointerTargetX = clamp(-relY * 4, -4, 4);
    state.pointerSpinTargetY = directionalSpin(relX, 0.18);
    state.pointerSpinTargetX = directionalSpin(-relY, 0.13);
  }

  function holdManualControl(duration = 900) {
    state.manualUntil = Math.max(state.manualUntil, performance.now() + duration);
  }

  function shortestAngle(from, to) {
    return from + ((((to - from) % 360) + 540) % 360) - 180;
  }

  function fibonacciSphere(index, total) {
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));
    const y = 1 - (index / (total - 1)) * 2;
    const radiusAtY = Math.sqrt(1 - y * y);
    const theta = goldenAngle * index;
    return {
      x: Math.cos(theta) * radiusAtY,
      y,
      z: Math.sin(theta) * radiusAtY
    };
  }

  function buildCards() {
    sphere.innerHTML = '';
    cards.forEach((item, index) => {
      const card = document.createElement('article');
      card.className = `home-sphere-card${item.type === 'data' ? ' is-data' : ''}`;
      card.dataset.title = item.title;
      card.dataset.sub = item.sub;
      card.dataset.index = index;

      if (item.type === 'image') {
        card.innerHTML = `
          <img src="${item.src}" alt="${item.alt || item.title}" draggable="false" />
        `;
      } else {
        card.innerHTML = `
          <div class="data-card-content">
            <div>
              <div class="big">${item.big}</div>
              <div class="label">${item.title}</div>
              <div class="sub">${item.sub}</div>
            </div>
          </div>
        `;
      }

      card.addEventListener('click', (event) => {
        if (state.moved) event.preventDefault();
        // Cards are decorative in the hero sphere; do not snap/select on click.
      });

      sphere.appendChild(card);
    });
  }

  function placeCards() {
    state.radius = radiusForViewport();
    const items = [...sphere.children];
    const total = items.length;

    items.forEach((card, index) => {
      const p = fibonacciSphere(index, total);
      const tx = p.x * state.radius;
      const ty = p.y * state.radius;
      const tz = p.z * state.radius;
      const ry = Math.atan2(p.x, p.z) * (180 / Math.PI);
      const rx = -Math.asin(p.y) * (180 / Math.PI);
      const baseDepth = (p.z + 1) / 2;
      const scale = 0.86 + baseDepth * 0.16;
      card.style.transform = `translate3d(${tx}px, ${ty}px, ${tz}px) scale(${scale}) rotateY(${ry}deg) rotateX(${rx}deg)`;
    });
  }

  function getRotatedPoint(p, rotX, rotY) {
    const yRad = rotY * Math.PI / 180;
    const xRad = rotX * Math.PI / 180;

    const x1 = p.x * Math.cos(yRad) - p.z * Math.sin(yRad);
    const z1 = p.x * Math.sin(yRad) + p.z * Math.cos(yRad);
    const y1 = p.y;

    const y2 = y1 * Math.cos(xRad) - z1 * Math.sin(xRad);
    const z2 = y1 * Math.sin(xRad) + z1 * Math.cos(xRad);

    return { x: x1, y: y2, z: z2 };
  }

  function focusCard(index) {
    // Upgrade 177: sphere should rotate smoothly without snapping/selecting a card.
    // Keep the function as a no-op for backward compatibility with older handlers.
    state.focusedIndex = null;
    state.focusTargetX = 0;
    state.focusTargetY = 0;
    wrap.classList.remove('is-focused');
  }

  function clearFocus() {
    state.focusedIndex = null;
    state.focusTargetX = 0;
    state.focusTargetY = 0;
    wrap.classList.remove('is-focused');
  }

  function updateDepth() {
    const items = [...sphere.children];
    let best = null;
    let bestZ = -Infinity;

    items.forEach((card, index) => {
      const p = fibonacciSphere(index, items.length);
      const result = getRotatedPoint(p, state.rotationX, state.rotationY);
      const normalized = (result.z + 1) / 2;

      card.style.zIndex = `${Math.round(normalized * 1000)}`;
      card.style.opacity = '1';
      card.style.filter = `saturate(${0.90 + normalized * 0.26}) brightness(${0.72 + normalized * 0.32}) blur(${(1 - normalized) * 0.32}px)`;

      if (result.z > bestZ) {
        bestZ = result.z;
        best = card;
      }
    });

    // Upgrade 177: no visual card selection/highlight during rotation.
    items.forEach((card) => card.classList.remove('is-active'));
  }

  function animate() {
    const pointerOverSphere = state.hovering || wrap.matches(':hover');
    const manualActive = pointerOverSphere || state.dragging || performance.now() < state.manualUntil;
    if (pointerOverSphere && !state.dragging) {
      state.autoRotationX += state.pointerSpinCurrentX;
      state.autoRotationY += state.pointerSpinCurrentY;
    } else if (!manualActive) {
      state.autoRotationY += state.autoSpeed;
    }

    // Auto orbit pauses during manual input. Once the pointer leaves or the
    // wheel gesture settles, manual offsets ease out and the ambient orbit resumes.
    if (!manualActive) {
      state.wheelTargetX = lerp(state.wheelTargetX, 0, 0.018);
      state.wheelTargetY = lerp(state.wheelTargetY, 0, 0.018);
    }

    state.pointerCurrentX = lerp(state.pointerCurrentX, state.pointerTargetX, 0.1);
    state.pointerCurrentY = lerp(state.pointerCurrentY, state.pointerTargetY, 0.1);
    state.pointerSpinCurrentX = lerp(state.pointerSpinCurrentX, state.pointerSpinTargetX, 0.08);
    state.pointerSpinCurrentY = lerp(state.pointerSpinCurrentY, state.pointerSpinTargetY, 0.08);
    state.wheelCurrentX = lerp(state.wheelCurrentX, state.wheelTargetX, 0.08);
    state.wheelCurrentY = lerp(state.wheelCurrentY, state.wheelTargetY, 0.08);
    state.focusCurrentX = lerp(state.focusCurrentX, state.focusTargetX, 0.08);
    state.focusCurrentY = lerp(state.focusCurrentY, state.focusTargetY, 0.08);

    const displayX = state.baseTiltX + state.autoRotationX + state.focusCurrentX + state.pointerCurrentX + state.wheelCurrentX;
    const displayY = state.autoRotationY + state.focusCurrentY + state.pointerCurrentY + state.wheelCurrentY;

    state.rotationX = displayX;
    state.rotationY = displayY;

    sphere.style.transform = `rotateX(${displayX}deg) rotateY(${displayY}deg)`;
    updateDepth();
    requestAnimationFrame(animate);
  }

  wrap.addEventListener('pointerdown', (event) => {
    state.dragging = true;
    state.moved = false;
    state.lastX = event.clientX;
    state.lastY = event.clientY;
    holdManualControl(1200);
    wrap.setPointerCapture(event.pointerId);
  });

  wrap.addEventListener('pointermove', (event) => {
    state.hovering = true;
    wrap.classList.add('is-hovered');
    holdManualControl(500);
    const pointerVector = pointerVectorFromEvent(event);
    syncPointerIntent(pointerVector.x, pointerVector.y);

    if (!state.dragging) return;

    const dx = event.clientX - state.lastX;
    const dy = event.clientY - state.lastY;

    if (Math.abs(dx) + Math.abs(dy) > 3) state.moved = true;
    clearFocus();

    state.wheelTargetY += dx * 0.18;
    state.wheelTargetX = clamp(state.wheelTargetX - dy * 0.06, -14, 14);
    state.lastX = event.clientX;
    state.lastY = event.clientY;
  });

  wrap.addEventListener('pointerup', (event) => {
    state.dragging = false;
    holdManualControl(700);
    try { wrap.releasePointerCapture(event.pointerId); } catch (e) {}
    setTimeout(() => { state.moved = false; }, 0);
  });

  wrap.addEventListener('pointercancel', () => {
    state.dragging = false;
    state.moved = false;
  });

  wrap.addEventListener('wheel', (event) => {
    // When the pointer is over the sphere, use wheel intent to turn the visual
    // instead of letting the page scroll swallow the interaction.
    event.preventDefault();
    clearFocus();
    holdManualControl(1300);
    const primaryDelta = Math.abs(event.deltaY) >= Math.abs(event.deltaX)
      ? event.deltaY
      : event.deltaX;
    const manualTurn = clamp(primaryDelta * 0.22, -42, 42);
    const pointerVector = pointerVectorFromEvent(event);
    syncPointerIntent(pointerVector.x, pointerVector.y);
    const horizontalWeight = Math.max(0.18, Math.abs(pointerVector.x));
    const verticalWeight = Math.max(0.18, Math.abs(pointerVector.y));
    const horizontalDirection = pointerVector.x || 1;
    const verticalDirection = -pointerVector.y || 1;

    state.wheelTargetY += manualTurn * horizontalWeight * Math.sign(horizontalDirection);
    state.wheelCurrentY += manualTurn * horizontalWeight * Math.sign(horizontalDirection) * 0.34;
    state.wheelTargetX += manualTurn * verticalWeight * Math.sign(verticalDirection);
    state.wheelCurrentX += manualTurn * verticalWeight * Math.sign(verticalDirection) * 0.28;
  }, { passive: false });

  const enterManualSphere = () => {
    state.hovering = true;
    holdManualControl(900);
    wrap.classList.add('is-hovered');
  };

  const leaveManualSphere = () => {
    state.hovering = false;
    holdManualControl(450);
    state.pointerTargetX = 0;
    state.pointerTargetY = 0;
    state.pointerSpinTargetX = 0;
    state.pointerSpinTargetY = 0;
    state.pointerRelX = 0;
    state.pointerRelY = 0;
    wrap.classList.remove('is-hovered');
  };

  wrap.addEventListener('pointerenter', enterManualSphere);
  wrap.addEventListener('mouseenter', enterManualSphere);
  wrap.addEventListener('pointerleave', leaveManualSphere);
  wrap.addEventListener('mouseleave', leaveManualSphere);

  wrap.addEventListener('dblclick', clearFocus);
  window.addEventListener('resize', placeCards);

  buildCards();
  placeCards();
  animate();
})();

// Upgrade 166 — stable accordions across the site.
// Keeps FAQ / details cards compact so a closed item does not stretch into a blank card
// when a neighboring accordion is opened.
(function () {
  function getGroup(detail) {
    return detail.closest('[data-accordion-group], .contact-faq-grid, .services-faq-grid, .faq-accordion-grid, .grid');
  }

  function closeSiblingDetails(detail) {
    const group = getGroup(detail);
    if (!group) return;
    group.querySelectorAll('details[open]').forEach((item) => {
      if (item !== detail) item.removeAttribute('open');
    });
  }

  document.querySelectorAll('details.card, details.contact-faq-card, details.services-faq-item, details[data-accordion-item]').forEach((detail) => {
    detail.setAttribute('data-accordion-item', '');
    detail.addEventListener('toggle', function () {
      if (detail.open) closeSiblingDetails(detail);
    });
  });
})();
