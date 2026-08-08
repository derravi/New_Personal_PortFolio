/* ============================================================
   CUSTOM DRAGGABLE MOBILE SCROLLBAR
   - Only activates on touch devices at mobile widths (<=767px).
   - Adds a slim neon pill on the right edge that:
       * visually tracks normal swipe scrolling, and
       * can be grabbed with a finger and dragged to scroll.
   - Never touches desktop behaviour: on desktop / non-touch
     devices this script no-ops and the native custom scrollbar
     (custom-scrollbar.css) is used instead.
   - Normal swipe scrolling anywhere else on the page is left
     completely alone (no preventDefault outside the thumb).
   ============================================================ */
(function () {
    'use strict';

    var MOBILE_BREAKPOINT = 767;
    var HANDLE_SIZE = 26; // fixed small round drag-button diameter (px), matches .cms-thumb in CSS
    var isTouchDevice = ('ontouchstart' in window) || navigator.maxTouchPoints > 0;

    if (!isTouchDevice) {
        // Non-touch device (mouse/trackpad only) - keep native scrollbar.
        return;
    }

    var wrap, track, thumb;
    var dragging = false;
    var dragStartY = 0;
    var dragStartThumbTop = 0;
    var trackTop = 0;
    var trackHeight = 0;
    var thumbHeight = 0;
    var thumbRange = 0;
    var maxScroll = 0;
    var rafPending = false;
    var enabled = false;

    function isMobileWidth() {
        return window.innerWidth <= MOBILE_BREAKPOINT;
    }

    function buildDom() {
        if (wrap) return;

        wrap = document.createElement('div');
        wrap.className = 'cms-wrap';
        wrap.setAttribute('aria-hidden', 'true');

        track = document.createElement('div');
        track.className = 'cms-track';

        thumb = document.createElement('div');
        thumb.className = 'cms-thumb';
        thumb.setAttribute('role', 'scrollbar');
        thumb.setAttribute('aria-orientation', 'vertical');

        wrap.appendChild(track);
        wrap.appendChild(thumb);
        document.body.appendChild(wrap);

        thumb.addEventListener('touchstart', onThumbTouchStart, { passive: false });
    }

    function measure() {
        if (!track) return;
        var trackRect = track.getBoundingClientRect();
        trackTop = trackRect.top;
        trackHeight = trackRect.height;

        var doc = document.documentElement;
        var docHeight = Math.max(doc.scrollHeight, document.body.scrollHeight);
        var winHeight = window.innerHeight;
        maxScroll = Math.max(0, docHeight - winHeight);

        if (maxScroll <= 4 || trackHeight <= 0) {
            // Nothing meaningful to scroll - hide the widget entirely.
            if (wrap) wrap.classList.add('cms-hidden');
            return;
        }
        if (wrap) wrap.classList.remove('cms-hidden');

        // Small fixed-size round button (not a proportional bar) - just a
        // draggable handle/marker that rides along the track.
        thumbHeight = HANDLE_SIZE;
        thumbHeight = Math.min(thumbHeight, trackHeight);
        thumbRange = trackHeight - thumbHeight;

        thumb.style.height = thumbHeight + 'px';
    }

    function currentScrollY() {
        return window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    }

    function updateThumbFromScroll() {
        if (!thumb || maxScroll <= 0) return;
        var ratio = currentScrollY() / maxScroll;
        ratio = Math.max(0, Math.min(1, ratio));
        var top = ratio * thumbRange;
        thumb.style.top = top + 'px';
    }

    function onScroll() {
        if (dragging || !enabled) return;
        if (rafPending) return;
        rafPending = true;
        window.requestAnimationFrame(function () {
            rafPending = false;
            updateThumbFromScroll();
        });
    }

    function setThumbTop(top) {
        top = Math.max(0, Math.min(thumbRange, top));
        thumb.style.top = top + 'px';
        return top;
    }

    function onThumbTouchStart(e) {
        if (!enabled || maxScroll <= 0) return;
        var touch = e.touches[0];
        dragging = true;
        wrap.classList.add('cms-dragging');
        dragStartY = touch.clientY;
        dragStartThumbTop = parseFloat(thumb.style.top || '0');

        document.addEventListener('touchmove', onThumbTouchMove, { passive: false });
        document.addEventListener('touchend', onThumbTouchEnd, { passive: false });
        document.addEventListener('touchcancel', onThumbTouchEnd, { passive: false });

        // Only prevent default for touches that start ON the thumb itself,
        // so the rest of the page keeps its normal, smooth native swipe scroll.
        e.preventDefault();
    }

    function onThumbTouchMove(e) {
        if (!dragging) return;
        var touch = e.touches[0];
        var deltaY = touch.clientY - dragStartY;
        var newTop = setThumbTop(dragStartThumbTop + deltaY);

        var ratio = thumbRange > 0 ? newTop / thumbRange : 0;
        var newScrollY = ratio * maxScroll;
        window.scrollTo(0, newScrollY);

        e.preventDefault();
    }

    function onThumbTouchEnd() {
        dragging = false;
        if (wrap) wrap.classList.remove('cms-dragging');
        document.removeEventListener('touchmove', onThumbTouchMove);
        document.removeEventListener('touchend', onThumbTouchEnd);
        document.removeEventListener('touchcancel', onThumbTouchEnd);
    }

    function enable() {
        if (enabled) return;
        buildDom();
        enabled = true;
        document.documentElement.classList.add('cms-enabled');
        measure();
        updateThumbFromScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    function disable() {
        if (!enabled) return;
        enabled = false;
        document.documentElement.classList.remove('cms-enabled');
        window.removeEventListener('scroll', onScroll);
        if (wrap) wrap.classList.add('cms-hidden');
    }

    function refresh() {
        if (isMobileWidth()) {
            enable();
            measure();
            updateThumbFromScroll();
        } else {
            disable();
        }
    }

    var resizeTimer = null;
    function onResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(refresh, 120);
    }

    // Recalculate when content height changes (images/lazy content loading, etc.)
    function watchContentChanges() {
        if (typeof ResizeObserver === 'undefined') return;
        var ro = new ResizeObserver(function () {
            if (enabled) {
                measure();
                updateThumbFromScroll();
            }
        });
        ro.observe(document.body);
    }

    // Hide the custom scrollbar while the site's off-canvas mobile menu is
    // open so it doesn't sit on top of / conflict with the drawer.
    function watchMobileDrawer() {
        var overlay = document.querySelector('.mobile-sidebar-overlay');
        var drawer = document.getElementById('mobileSidebar');
        if (!overlay && !drawer) return;

        var toggleVisibility = function () {
            var open = (drawer && drawer.classList.contains('open')) ||
                (overlay && overlay.classList.contains('active'));
            if (!wrap) return;
            if (open) {
                wrap.style.opacity = '0';
                wrap.style.pointerEvents = 'none';
            } else {
                wrap.style.opacity = '';
                wrap.style.pointerEvents = '';
            }
        };

        var observer = new MutationObserver(toggleVisibility);
        [overlay, drawer].forEach(function (el) {
            if (el) observer.observe(el, { attributes: true, attributeFilter: ['class'] });
        });
    }

    function init() {
        refresh();
        watchContentChanges();
        watchMobileDrawer();
        window.addEventListener('resize', onResize);
        window.addEventListener('orientationchange', onResize);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();