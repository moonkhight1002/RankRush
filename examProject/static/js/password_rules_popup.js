document.querySelectorAll('[data-password-popup]').forEach((popup) => {
    const trigger = popup.querySelector('[data-password-popup-trigger]');
    const content = popup.querySelector('[data-password-popup-content]');
    const rulesList = popup.querySelector('[data-password-rules-list]');
    const passwordInput = popup.parentElement?.querySelector('input[type="password"]');
    const rawRules = passwordInput?.dataset.passwordRules || '';
    const rules = rawRules
        .split('|')
        .map((rule) => rule.trim())
        .filter(Boolean);

    if (!trigger || !content || !rulesList || !passwordInput || rules.length === 0) {
        popup.hidden = true;
        return;
    }

    rulesList.innerHTML = rules.map((rule) => `<li>${rule}</li>`).join('');

    const setOpen = (isOpen) => {
        content.hidden = !isOpen;
        trigger.setAttribute('aria-expanded', String(isOpen));
        popup.classList.toggle('is-open', isOpen);
    };

    trigger.addEventListener('click', () => {
        setOpen(content.hidden);
    });

    trigger.addEventListener('blur', (event) => {
        const nextTarget = event.relatedTarget;
        if (!popup.contains(nextTarget)) {
            setOpen(false);
        }
    });

    document.addEventListener('click', (event) => {
        if (!popup.contains(event.target)) {
            setOpen(false);
        }
    });
});
