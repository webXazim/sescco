(function () {
  function getAppliedJobs() {
    try {
      return JSON.parse(localStorage.getItem('sescco-career-applied-jobs') || '{}') || {};
    } catch (error) {
      return {};
    }
  }

  function alreadyAppliedButton(reference) {
    var span = document.createElement('span');
    span.className = 'btn btn-applied';
    span.setAttribute('data-job-applied-message', '');
    span.textContent = reference ? 'Already Applied' : 'Already Applied';
    return span;
  }

  function applyState() {
    var appliedJobs = getAppliedJobs();
    document.querySelectorAll('[data-job-apply-area][data-job-slug]').forEach(function (area) {
      var slug = area.getAttribute('data-job-slug');
      var record = appliedJobs[slug];
      if (!record) return;

      area.querySelectorAll('[data-job-apply-link]').forEach(function (link) {
        var replacement = alreadyAppliedButton(record.reference || '');
        if (link.classList.contains('full')) replacement.classList.add('full');
        link.replaceWith(replacement);
      });

      var message = area.querySelector('[data-job-applied-message]');
      if (message) {
        message.textContent = 'Already Applied';
        message.title = record.reference ? ('Reference: ' + record.reference) : 'Application already submitted';
      }
    });

    document.querySelectorAll('[data-job-applied-note]').forEach(function (note) {
      var area = document.querySelector('[data-job-apply-area][data-job-slug]');
      if (!area) return;
      var slug = area.getAttribute('data-job-slug');
      var record = appliedJobs[slug];
      if (!record) return;
      note.classList.remove('is-hidden');
      var span = note.querySelector('span');
      if (span && record.reference) span.textContent = 'You have already applied to this post. Reference: ' + record.reference;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyState);
  } else {
    applyState();
  }
})();
