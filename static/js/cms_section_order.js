(function () {
  function getOrder(element) {
    var order = parseInt(element.getAttribute('data-section-order') || '100', 10);
    return Number.isNaN(order) ? 100 : order;
  }

  function applySectionOrder() {
    document.querySelectorAll('[data-section-order]').forEach(function (element) {
      var order = getOrder(element);
      element.style.order = String(order);
      if (element.hasAttribute('hidden')) {
        element.style.display = 'none';
      }
    });

    document.querySelectorAll('.cms-section-sort').forEach(function (container) {
      var orderedChildren = Array.prototype.slice.call(container.children)
        .filter(function (child) { return child.hasAttribute('data-section-order'); })
        .map(function (child, index) { return { child: child, order: getOrder(child), index: index }; })
        .sort(function (a, b) {
          if (a.order === b.order) return a.index - b.index;
          return a.order - b.order;
        });

      orderedChildren.forEach(function (entry) {
        container.appendChild(entry.child);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applySectionOrder);
  } else {
    applySectionOrder();
  }

  window.addEventListener('load', applySectionOrder);
})();
