(function () {
  const form = document.querySelector('[data-career-apply-form]');
  if (!form) return;

  const draftKey = form.dataset.draftKey;
  const emailInput = form.querySelector('input[name="email"]');
  const codeInput = form.querySelector('input[name="email_verification_code"]');
  const sendCodeButton = form.querySelector('[data-send-code]');
  const verifyCodeButton = form.querySelector('[data-verify-code]');
  const openModalButton = form.querySelector('[data-open-verification-modal]');
  const closeModalButtons = form.querySelectorAll('[data-close-verification-modal]');
  const statusElements = form.querySelectorAll('[data-email-status]');
  const verificationState = form.querySelector('[data-verification-state]');
  const verificationInline = form.querySelector('[data-verification-inline]');
  const verificationSummary = form.querySelector('[data-verification-summary]');
  const verificationModal = form.querySelector('[data-verification-modal]');
  const verificationEmailDisplay = form.querySelector('[data-verification-email-display]');
  const inlineVerifiedPill = form.querySelector('[data-inline-verified-pill]');
  const submitButton = form.querySelector('button[type="submit"]');
  let duplicateApplication = false;
  let emailVerified = false;
  let checkedEmail = '';

  function t(key, fallback) {
    return form.dataset[key] || fallback || '';
  }

  function csrfToken() {
    const input = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function setStatus(message, type) {
    statusElements.forEach((el) => {
      el.textContent = message || '';
      el.className = 'career-email-status';
      if (type) el.classList.add(type);
    });
  }

  function syncVerificationEmail() {
    if (!verificationEmailDisplay) return;
    const email = emailInput ? emailInput.value.trim() : '';
    verificationEmailDisplay.textContent = email || t('msgEnterEmailDisplay', 'Enter your email first');
  }

  function openModal() {
    if (!verificationModal) return;
    const email = emailInput ? emailInput.value.trim() : '';
    if (!email) {
      setStatus(t('msgEnterEmailFirst', 'Enter your email address first.'), 'warning');
      if (emailInput) emailInput.focus();
      return;
    }
    syncVerificationEmail();
    verificationModal.hidden = false;
    document.body.classList.add('career-modal-open');
    if (codeInput && !emailVerified) {
      window.setTimeout(() => codeInput.focus(), 30);
    }
  }

  function closeModal() {
    if (!verificationModal) return;
    verificationModal.hidden = true;
    document.body.classList.remove('career-modal-open');
  }

  function updateSummaryText(message) {
    if (!verificationSummary) return;
    if (message) {
      verificationSummary.textContent = message;
      return;
    }
    if (duplicateApplication) {
      verificationSummary.textContent = t('msgDuplicateSummary', 'You have already applied to this job with this email.');
    } else if (emailVerified) {
      verificationSummary.textContent = t('msgEmailVerifiedSuccess', 'Email verified successfully. You can now submit the application.');
    } else {
      verificationSummary.textContent = t('msgVerifyBeforeSubmit', 'Verify your email before submitting your application.');
    }
  }

  function setVerificationState(isVerified, message) {
    emailVerified = Boolean(isVerified);
    if (verificationState) verificationState.textContent = emailVerified ? t('labelVerified', 'Verified') : t('labelNotVerified', 'Not verified');
    if (verificationInline) verificationInline.classList.toggle('is-verified', emailVerified);
    if (inlineVerifiedPill) inlineVerifiedPill.hidden = !emailVerified;
    if (openModalButton) {
      openModalButton.disabled = duplicateApplication || emailVerified;
      openModalButton.textContent = emailVerified ? t('labelVerified', 'Verified') : t('labelVerifyEmail', 'Verify Email');
    }
    if (verifyCodeButton) {
      verifyCodeButton.disabled = duplicateApplication || emailVerified;
      verifyCodeButton.textContent = emailVerified ? t('labelVerified', 'Verified') : t('labelVerifyEmail', 'Verify Email');
    }
    if (sendCodeButton) sendCodeButton.disabled = duplicateApplication;
    if (codeInput) codeInput.readOnly = emailVerified;
    updateSummaryText(message || '');
    if (message) setStatus(message, emailVerified ? 'success' : duplicateApplication ? 'error' : 'warning');
    if (emailVerified) closeModal();
    setSubmitState();
  }

  function resetVerification(message) {
    if (codeInput) {
      codeInput.readOnly = false;
      codeInput.value = '';
    }
    setVerificationState(false, message || t('msgPleaseVerifyBeforeSubmit', 'Please verify this email before submitting the application.'));
  }

  function setSubmitState() {
    if (submitButton) submitButton.disabled = duplicateApplication || !emailVerified;
    if (sendCodeButton) sendCodeButton.disabled = duplicateApplication;
    if (verifyCodeButton) verifyCodeButton.disabled = duplicateApplication || emailVerified;
    if (openModalButton) openModalButton.disabled = duplicateApplication || emailVerified;
  }

  function saveDraft() {
    if (!draftKey) return;
    const data = {};
    form.querySelectorAll('input, textarea, select').forEach((field) => {
      if (!field.name) return;
      if (['file', 'hidden', 'password'].includes(field.type)) return;
      if (field.name === 'csrfmiddlewaretoken' || field.name === 'company_website' || field.name === 'email_verification_code') return;
      if (field.type === 'checkbox' || field.type === 'radio') data[field.name] = field.checked;
      else data[field.name] = field.value;
    });
    try { localStorage.setItem(draftKey, JSON.stringify(data)); } catch (error) {}
  }

  function restoreDraft() {
    if (!draftKey) return;
    let data = null;
    try { data = JSON.parse(localStorage.getItem(draftKey) || '{}'); } catch (error) { data = {}; }
    Object.entries(data || {}).forEach(([name, value]) => {
      const field = form.querySelector(`[name="${CSS.escape(name)}"]`);
      if (!field) return;
      if (field.value && field.type !== 'checkbox' && field.type !== 'radio') return;
      if (field.type === 'checkbox' || field.type === 'radio') field.checked = Boolean(value);
      else field.value = value;
    });
  }

  async function checkEmail() {
    const email = emailInput ? emailInput.value.trim() : '';
    duplicateApplication = false;
    if (!email || !form.dataset.checkEmailUrl) {
      setStatus('', '');
      resetVerification('');
      syncVerificationEmail();
      return;
    }
    if (email !== checkedEmail) {
      checkedEmail = email;
      resetVerification('');
    }
    syncVerificationEmail();
    try {
      const url = new URL(form.dataset.checkEmailUrl, window.location.origin);
      url.searchParams.set('email', email);
      const response = await fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}});
      const data = await response.json();
      if (data.applied) {
        duplicateApplication = true;
        setVerificationState(false);
        setStatus(data.reference ? `${data.message} Reference: ${data.reference}` : data.message, 'error');
        updateSummaryText(t('msgDuplicateShort', 'This email already has an application for this job.'));
      } else if (data.verified) {
        setVerificationState(true, data.message || t('msgEmailVerifiedSuccess', 'Email verified successfully. You can now submit the application.'));
      } else if (data.ok) {
        setVerificationState(false);
        setStatus(data.message || t('msgEmailCanBeUsed', 'This email can be used. Verify it before submitting.'), 'warning');
        updateSummaryText(t('msgVerifyBeforeSubmit', 'Verify your email before submitting your application.'));
      } else {
        setVerificationState(false);
        setStatus(data.message || t('msgCheckEmail', 'Please check your email address.'), 'warning');
      }
    } catch (error) {
      setStatus('', '');
    }
    setSubmitState();
  }

  async function sendCode() {
    const email = emailInput ? emailInput.value.trim() : '';
    if (!email) {
      setStatus(t('msgEnterEmailFirst', 'Enter your email address first.'), 'warning');
      if (emailInput) emailInput.focus();
      return;
    }
    duplicateApplication = false;
    setVerificationState(false);
    if (sendCodeButton) {
      sendCodeButton.disabled = true;
      sendCodeButton.dataset.originalText = sendCodeButton.textContent;
      sendCodeButton.textContent = t('msgSending', 'Sending...');
    }
    const body = new FormData();
    body.append('email', email);
    try {
      const response = await fetch(form.dataset.sendCodeUrl, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
        body: body,
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        if (data.duplicate) duplicateApplication = true;
        setStatus(data.message || t('msgCodeNotSent', 'Verification code could not be sent.'), data.duplicate ? 'error' : 'warning');
      } else {
        setStatus(data.message || t('msgCodeSent', 'Verification code sent. Please check your email.'), 'success');
        if (codeInput) {
          codeInput.readOnly = false;
          codeInput.focus();
        }
      }
    } catch (error) {
      setStatus(t('msgCodeSendFailed', 'Verification code could not be sent. Please try again.'), 'warning');
    }
    if (sendCodeButton) {
      sendCodeButton.textContent = sendCodeButton.dataset.originalText || t('labelSendCode', 'Send Code');
      sendCodeButton.disabled = duplicateApplication;
    }
    setSubmitState();
  }

  async function verifyCode() {
    const email = emailInput ? emailInput.value.trim() : '';
    const code = codeInput ? codeInput.value.trim() : '';
    if (!email) {
      setStatus(t('msgEnterEmailFirst', 'Enter your email address first.'), 'warning');
      if (emailInput) emailInput.focus();
      return;
    }
    if (!code || code.length !== 6) {
      setStatus(t('msgEnterCode', 'Enter the 6-digit code sent to your email.'), 'warning');
      if (codeInput) codeInput.focus();
      return;
    }
    if (verifyCodeButton) {
      verifyCodeButton.disabled = true;
      verifyCodeButton.dataset.originalText = verifyCodeButton.textContent;
      verifyCodeButton.textContent = t('msgVerifying', 'Verifying...');
    }
    const body = new FormData();
    body.append('email', email);
    body.append('code', code);
    try {
      const response = await fetch(form.dataset.verifyCodeUrl, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest'},
        body: body,
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        if (data.duplicate) duplicateApplication = true;
        setVerificationState(false);
        setStatus(data.message || t('msgEmailNotVerified', 'Email could not be verified.'), data.duplicate ? 'error' : 'warning');
      } else {
        setVerificationState(true, data.message || t('msgEmailVerifiedSuccess', 'Email verified successfully. You can now submit the application.'));
      }
    } catch (error) {
      setVerificationState(false);
      setStatus(t('msgVerificationFailed', 'Verification failed. Please try again.'), 'warning');
    }
    if (verifyCodeButton && !emailVerified) {
      verifyCodeButton.textContent = verifyCodeButton.dataset.originalText || t('labelVerifyEmail', 'Verify Email');
    }
    setSubmitState();
  }

  restoreDraft();
  syncVerificationEmail();
  setVerificationState(false);
  checkEmail();

  form.addEventListener('input', saveDraft);
  form.addEventListener('change', saveDraft);
  if (emailInput) {
    emailInput.addEventListener('input', function () {
      syncVerificationEmail();
      if (emailInput.value.trim() !== checkedEmail) {
        duplicateApplication = false;
        resetVerification(t('msgEmailChanged', 'Email changed. Please verify the new email before submitting.'));
      }
    });
    emailInput.addEventListener('blur', checkEmail);
    emailInput.addEventListener('change', checkEmail);
  }
  if (openModalButton) openModalButton.addEventListener('click', openModal);
  closeModalButtons.forEach((button) => button.addEventListener('click', closeModal));
  if (verificationModal) {
    verificationModal.addEventListener('click', function (event) {
      if (event.target === verificationModal) closeModal();
    });
  }
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && verificationModal && !verificationModal.hidden) closeModal();
  });
  if (sendCodeButton) sendCodeButton.addEventListener('click', sendCode);
  if (verifyCodeButton) verifyCodeButton.addEventListener('click', verifyCode);
  form.addEventListener('submit', function (event) {
    saveDraft();
    if (duplicateApplication) {
      event.preventDefault();
      setStatus(t('msgDuplicateSummary', 'You have already applied to this job with this email.'), 'error');
      if (emailInput) emailInput.focus();
      return;
    }
    if (!emailVerified) {
      event.preventDefault();
      setStatus(t('msgPleaseVerifyBeforeSubmit', 'Please verify your email before submitting the application.'), 'warning');
      openModal();
    }
  });
})();
