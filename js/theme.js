/* Light/Dark theme - shared across all German Learning pages. Key: german-theme */
(function() {
    var KEY = 'german-theme';
    var HIDE_DELAY_MS = 2500;
    var hideTimer = null;

    function getDark() { return localStorage.getItem(KEY) === 'dark'; }
    function setDark(dark) { localStorage.setItem(KEY, dark ? 'dark' : 'light'); }
    function apply(dark) {
        document.body.classList.toggle('theme-dark', dark);
        var btn = document.getElementById('theme-float-btn');
        if (btn) {
            btn.textContent = dark ? '☀️' : '🌙';
            if (dark) {
                btn.classList.add('theme-float-btn--hidden');
            } else {
                btn.classList.remove('theme-float-btn--hidden');
            }
        }
        var label = document.getElementById('theme-label');
        if (label) label.textContent = dark ? 'Light' : 'Dark';
        var icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = dark ? '☀️' : '🌙';
        updateHotspotVisibility();
    }
    function toggle() {
        var dark = !document.body.classList.contains('theme-dark');
        setDark(dark);
        apply(dark);
    }
    function isBtnHidden() {
        var btn = document.getElementById('theme-float-btn');
        return btn ? btn.classList.contains('theme-float-btn--hidden') : false;
    }
    function showBtn() {
        var btn = document.getElementById('theme-float-btn');
        if (btn) btn.classList.remove('theme-float-btn--hidden');
        if (getDark()) scheduleAutoHide();
    }
    function hideBtn() {
        var btn = document.getElementById('theme-float-btn');
        if (btn) btn.classList.add('theme-float-btn--hidden');
    }
    function scheduleAutoHide() {
        if (hideTimer) clearTimeout(hideTimer);
        if (!getDark()) return;
        hideTimer = setTimeout(hideBtn, HIDE_DELAY_MS);
    }
    function cancelAutoHide() {
        if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
    }
    function injectFloatingBtn() {
        if (document.getElementById('theme-float-btn')) return;
        var btn = document.createElement('button');
        btn.id = 'theme-float-btn';
        btn.type = 'button';
        btn.className = 'theme-float-btn';
        btn.setAttribute('aria-label', 'Toggle light/dark theme');
        btn.textContent = getDark() ? '☀️' : '🌙';
        btn.onclick = function() {
            cancelAutoHide();
            toggle();
            if (getDark()) {
                hideBtn();
            }
        };
        btn.addEventListener('mouseenter', cancelAutoHide);
        btn.addEventListener('mouseleave', function() { if (getDark()) scheduleAutoHide(); });
        document.body.appendChild(btn);
        if (getDark()) updateHotspotVisibility();
    }
    function bindSidebarToggle() {
        var sidebarBtn = document.getElementById('theme-toggle');
        if (sidebarBtn) sidebarBtn.addEventListener('click', toggle);
    }
    function onHotspotClick(e) {
        e.preventDefault();
        if (!getDark()) return;
        showBtn();
    }
    function injectHotspot() {
        if (document.getElementById('theme-hotspot')) return;
        var spot = document.createElement('div');
        spot.id = 'theme-hotspot';
        spot.className = 'theme-hotspot';
        spot.setAttribute('aria-label', 'Show theme toggle');
        spot.onclick = onHotspotClick;
        document.body.appendChild(spot);
    }
    function updateHotspotVisibility() {
        var spot = document.getElementById('theme-hotspot');
        if (!spot) return;
        if (getDark() && isBtnHidden()) {
            spot.classList.add('theme-hotspot--active');
        } else {
            spot.classList.remove('theme-hotspot--active');
        }
    }
    var origHideBtn = hideBtn;
    hideBtn = function() {
        origHideBtn();
        updateHotspotVisibility();
    };
    showBtn = function() {
        var btn = document.getElementById('theme-float-btn');
        if (btn) btn.classList.remove('theme-float-btn--hidden');
        if (getDark()) scheduleAutoHide();
        updateHotspotVisibility();
    };
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            apply(getDark());
            injectFloatingBtn();
            injectHotspot();
            bindSidebarToggle();
            updateHotspotVisibility();
        });
    } else {
        apply(getDark());
        injectFloatingBtn();
        injectHotspot();
        bindSidebarToggle();
        updateHotspotVisibility();
    }
    window.toggleTheme = toggle;
})();
