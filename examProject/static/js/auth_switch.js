document.addEventListener('DOMContentLoaded', function() {
    var body = document.body;
    var wrapper = document.querySelector('.auth-wrapper');
    var switchLinks = document.querySelectorAll('.js-auth-switch-link');
    var storageKey = 'rankrush-auth-switch';
    var mobileQuery = window.matchMedia('(max-width: 768px)');

    if (wrapper) {
        try {
            var payload = sessionStorage.getItem(storageKey);
            if (payload) {
                var savedState = JSON.parse(payload);
                if (
                    savedState &&
                    savedState.scope === body.dataset.authScope &&
                    savedState.view === body.dataset.authView
                ) {
                    wrapper.classList.add('is-auth-arriving');
                    window.setTimeout(function() {
                        wrapper.classList.remove('is-auth-arriving');
                    }, 460);
                }
            }
        } catch (error) {
            sessionStorage.removeItem(storageKey);
        }
        sessionStorage.removeItem(storageKey);
    }

    switchLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            var href = link.getAttribute('href');
            var targetView = link.dataset.authTarget;
            var targetScope = link.dataset.authScope || body.dataset.authScope || '';

            if (
                !href ||
                href.charAt(0) === '#' ||
                event.defaultPrevented ||
                event.metaKey ||
                event.ctrlKey ||
                event.shiftKey ||
                event.altKey ||
                link.target === '_blank'
            ) {
                return;
            }

            if (!wrapper || wrapper.dataset.switching === 'true') {
                return;
            }

            if (mobileQuery.matches) {
                return;
            }

            event.preventDefault();
            wrapper.dataset.switching = 'true';
            wrapper.classList.add('is-auth-switching');
            body.classList.add('is-auth-switching');

            if (targetScope && targetView) {
                sessionStorage.setItem(storageKey, JSON.stringify({
                    scope: targetScope,
                    view: targetView
                }));
            }

            if (targetView === 'register') {
                wrapper.classList.add('panel-active');
            } else if (targetView === 'login') {
                wrapper.classList.remove('panel-active');
            }

            window.setTimeout(function() {
                window.location.href = href;
            }, 360);
        });
    });
});
