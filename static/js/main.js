document.addEventListener('DOMContentLoaded', function () {
  const toasts = document.querySelectorAll('#toast-container .toast');
  toasts.forEach((toast) => {
    const hideTimer = setTimeout(() => {
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 260);
    }, 4000);

    const closeBtn = toast.querySelector('.toast__close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        clearTimeout(hideTimer);
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 220);
      });
    }
  });

  const createAccountForm = document.getElementById('create-account-form');
  if (createAccountForm) {
    createAccountForm.addEventListener('submit', function (event) {
      const password = document.getElementById('password');
      const passwordConfirm = document.getElementById('password_confirm');
      if (password && passwordConfirm && password.value !== passwordConfirm.value) {
        event.preventDefault();
        const container = document.getElementById('toast-container') || (function () {
          const c = document.createElement('div');
          c.id = 'toast-container';
          document.body.appendChild(c);
          return c;
        })();
        const t = document.createElement('div');
        t.className = 'toast error';
        t.innerHTML = '<div class="toast__content">Passwords do not match.</div><button type="button" class="toast__close" aria-label="Close">&times;</button>';
        container.appendChild(t);
        setTimeout(() => {
          t.classList.add('hide');
          setTimeout(() => t.remove(), 220);
        }, 3000);
        const b = t.querySelector('.toast__close');
        if (b) b.addEventListener('click', () => { t.classList.add('hide'); setTimeout(() => t.remove(), 180); });
      }
    });
  }

});
