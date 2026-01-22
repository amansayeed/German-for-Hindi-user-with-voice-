/**
 * ============================================
 * RESPONSIVE AUTO-HIDE NAVIGATION SYSTEM
 * Production-ready, Performance-optimized
 * 
 * Usage: <script src="js/navbar.js"></script>
 * 
 * BROWSER TESTING CHECKLIST:
 * ✓ iOS Safari 15+ (notch, dynamic island, rubber-band scroll)
 * ✓ Android Chrome 90+ (various screen sizes)
 * ✓ Desktop Chrome 90+
 * ✓ Desktop Firefox 90+
 * ✓ Desktop Safari 14+
 * ✓ Edge Chromium 90+
 * ============================================
 */

(function() {
    'use strict';
    
    /* ============================================
       ⚙️ CONFIGURATION - CUSTOMIZE HERE
       ============================================ */
    const CONFIG = {
        // Auto-hide behavior
        scrollThreshold: 100,      // Min scroll (px) before auto-hide activates
        scrollDelta: 10,           // Min scroll distance (px) to trigger show/hide
        topThreshold: 50,          // Always show toggle when within this (px) from top
        
        // ⏱️ TIMING CUSTOMIZATION
        autoHideDelay: 150,        // Delay (ms) before hiding on scroll down
        showDelay: 0,              // Delay (ms) before showing on scroll up
        throttleDelay: 16,         // ~60fps scroll throttle (16ms)
        scrollingTimeout: 150,     // Time (ms) to detect "stopped scrolling"
        
        // Animation
        transitionDuration: 300    // Match CSS --nav-transition-speed
    };
    
    /* ============================================
       STATE MANAGEMENT
       ============================================ */
    const state = {
        lastScrollY: 0,
        ticking: false,
        menuOpen: false,
        scrollPosition: 0,         // Preserved scroll when menu opens
        isTouch: false,
        isScrolling: false,        // For dynamic shadow
        scrollingTimer: null,      // Timer for scroll end detection
        hideTimer: null,           // Timer for delayed hide
        prefersReducedMotion: false,
        orientation: screen.orientation?.type || 'portrait'
    };
    
    /* ============================================
       DOM ELEMENTS (cached for performance)
       ============================================ */
    let elements = {};
    
    function cacheElements() {
        elements = {
            toggle: document.querySelector('.sidebar-toggle'),
            sidebar: document.getElementById('sidebar'),
            overlay: document.querySelector('.sidebar-overlay'),
            body: document.body,
            navItems: document.querySelectorAll('.sidebar-nav-item')
        };
    }
    
    /* ============================================
       UTILITY FUNCTIONS
       ============================================ */
    
    // Throttle function for scroll performance
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // Check if we're on desktop (sidebar always visible)
    function isDesktop() {
        return window.innerWidth >= 1025;
    }
    
    // Check device type for touch handling
    function detectTouch() {
        state.isTouch = 'ontouchstart' in window || 
                       navigator.maxTouchPoints > 0;
    }
    
    // Detect reduced motion preference
    function detectReducedMotion() {
        state.prefersReducedMotion = window.matchMedia(
            '(prefers-reduced-motion: reduce)'
        ).matches;
        
        // Listen for changes
        window.matchMedia('(prefers-reduced-motion: reduce)')
            .addEventListener('change', (e) => {
                state.prefersReducedMotion = e.matches;
                console.log('🔄 Reduced motion preference changed:', e.matches);
            });
    }
    
    /* ============================================
       🌟 DYNAMIC SHADOW ON SCROLL
       Shadow appears when actively scrolling
       ============================================ */
    function setScrollingState(isScrolling) {
        const { toggle } = elements;
        if (!toggle || state.prefersReducedMotion) return;
        
        if (isScrolling && !state.isScrolling) {
            state.isScrolling = true;
            toggle.classList.add('is-scrolling');
        } else if (!isScrolling && state.isScrolling) {
            state.isScrolling = false;
            toggle.classList.remove('is-scrolling');
        }
    }
    
    function handleScrollEnd() {
        // Clear existing timer
        if (state.scrollingTimer) {
            clearTimeout(state.scrollingTimer);
        }
        
        // Set timer to detect scroll end
        state.scrollingTimer = setTimeout(() => {
            setScrollingState(false);
        }, CONFIG.scrollingTimeout);
    }
    
    /* ============================================
       AUTO-HIDE SCROLL HANDLER
       With customizable delay
       ============================================ */
    function handleScroll() {
        const currentScrollY = window.scrollY;
        const { toggle } = elements;
        
        // Skip on desktop or if no toggle exists
        if (isDesktop() || !toggle) return;
        
        // Activate scrolling shadow
        setScrollingState(true);
        handleScrollEnd();
        
        // IMPORTANT: Don't auto-hide when menu is open
        if (state.menuOpen) {
            state.lastScrollY = currentScrollY;
            return;
        }
        
        const scrollDelta = currentScrollY - state.lastScrollY;
        
        // At top of page - always show immediately
        if (currentScrollY < CONFIG.topThreshold) {
            cancelHideTimer();
            showToggle(0); // No delay at top
        }
        // Scrolling down past threshold - hide with delay
        else if (scrollDelta > CONFIG.scrollDelta && 
                 currentScrollY > CONFIG.scrollThreshold) {
            hideToggleWithDelay();
        }
        // Scrolling up - show with optional delay
        else if (scrollDelta < -CONFIG.scrollDelta) {
            cancelHideTimer();
            showToggle(CONFIG.showDelay);
        }
        
        state.lastScrollY = currentScrollY;
    }
    
    function cancelHideTimer() {
        if (state.hideTimer) {
            clearTimeout(state.hideTimer);
            state.hideTimer = null;
        }
    }
    
    function showToggle(delay = 0) {
        const { toggle } = elements;
        if (!toggle) return;
        
        cancelHideTimer();
        
        if (delay > 0 && !state.prefersReducedMotion) {
            setTimeout(() => {
                toggle.classList.remove('auto-hidden');
            }, delay);
        } else {
            toggle.classList.remove('auto-hidden');
        }
    }
    
    function hideToggleWithDelay() {
        const { toggle } = elements;
        if (!toggle || state.menuOpen) return;
        
        // Clear existing timer
        cancelHideTimer();
        
        // If reduced motion, hide immediately
        if (state.prefersReducedMotion || CONFIG.autoHideDelay === 0) {
            toggle.classList.add('auto-hidden');
            return;
        }
        
        // Otherwise, delay the hide
        state.hideTimer = setTimeout(() => {
            if (!state.menuOpen) {
                toggle.classList.add('auto-hidden');
            }
        }, CONFIG.autoHideDelay);
    }
    
    // Throttled scroll handler using requestAnimationFrame
    function onScroll() {
        if (!state.ticking) {
            window.requestAnimationFrame(() => {
                handleScroll();
                state.ticking = false;
            });
            state.ticking = true;
        }
    }
    
    /* ============================================
       MENU TOGGLE FUNCTIONS
       ============================================ */
    function openMenu() {
        const { toggle, sidebar, overlay, body } = elements;
        
        state.menuOpen = true;
        
        // Save scroll position before locking body
        state.scrollPosition = window.scrollY;
        
        // Update ARIA states
        toggle?.setAttribute('aria-expanded', 'true');
        sidebar?.setAttribute('aria-hidden', 'false');
        
        // Add classes
        sidebar?.classList.add('open', 'visible');
        overlay?.classList.add('active');
        body?.classList.add('nav-open');
        
        // Update toggle icon
        if (toggle) {
            toggle.innerHTML = '<span class="toggle-icon" aria-hidden="true">✕</span>';
        }
        
        // Ensure toggle stays visible when menu is open
        showToggle();
        
        // Focus first nav item for keyboard users
        setTimeout(() => {
            elements.navItems[0]?.focus();
        }, CONFIG.transitionDuration);
    }
    
    function closeMenu() {
        const { toggle, sidebar, overlay, body } = elements;
        
        state.menuOpen = false;
        
        // Update ARIA states
        toggle?.setAttribute('aria-expanded', 'false');
        sidebar?.setAttribute('aria-hidden', 'true');
        
        // Remove classes
        sidebar?.classList.remove('open', 'visible');
        overlay?.classList.remove('active');
        body?.classList.remove('nav-open');
        
        // Update toggle icon
        if (toggle) {
            toggle.innerHTML = '<span class="toggle-icon" aria-hidden="true">☰</span>';
        }
        
        // Restore scroll position
        window.scrollTo(0, state.scrollPosition);
        
        // Return focus to toggle
        toggle?.focus();
    }
    
    function toggleMenu() {
        // Skip toggle on desktop
        if (isDesktop()) return;
        
        if (state.menuOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    }
    
    // Expose toggle function globally
    window.toggleSidebar = toggleMenu;
    
    /* ============================================
       KEYBOARD NAVIGATION (Accessibility)
       ============================================ */
    function handleKeydown(e) {
        // Escape closes menu
        if (e.key === 'Escape' && state.menuOpen) {
            closeMenu();
            return;
        }
        
        // Tab trap when menu is open
        if (e.key === 'Tab' && state.menuOpen) {
            const { navItems, toggle } = elements;
            const focusableItems = [toggle, ...navItems];
            const firstItem = focusableItems[0];
            const lastItem = focusableItems[focusableItems.length - 1];
            
            if (e.shiftKey && document.activeElement === firstItem) {
                e.preventDefault();
                lastItem?.focus();
            } else if (!e.shiftKey && document.activeElement === lastItem) {
                e.preventDefault();
                firstItem?.focus();
            }
        }
    }
    
    /* ============================================
       ORIENTATION CHANGE HANDLER
       ============================================ */
    function handleOrientationChange() {
        // Close menu on orientation change to prevent layout issues
        if (state.menuOpen) {
            closeMenu();
        }
        
        // Update state
        state.orientation = screen.orientation?.type || 
                          (window.innerHeight > window.innerWidth ? 'portrait' : 'landscape');
        
        // Recalculate scroll position
        state.lastScrollY = window.scrollY;
    }
    
    /* ============================================
       RESIZE HANDLER
       ============================================ */
    const handleResize = throttle(() => {
        const { toggle, sidebar, overlay, body } = elements;
        
        if (isDesktop()) {
            // Reset everything for desktop
            state.menuOpen = false;
            sidebar?.classList.remove('open', 'visible');
            overlay?.classList.remove('active');
            body?.classList.remove('nav-open');
            toggle?.classList.remove('auto-hidden');
            toggle?.setAttribute('aria-expanded', 'false');
            
            if (toggle) {
                toggle.innerHTML = '<span class="toggle-icon" aria-hidden="true">☰</span>';
            }
        } else {
            // Ensure proper state for mobile/tablet
            if (!state.menuOpen) {
                sidebar?.classList.remove('open', 'visible');
                sidebar?.setAttribute('aria-hidden', 'true');
            }
        }
    }, 150);
    
    /* ============================================
       INITIALIZATION
       ============================================ */
    function init() {
        // Cache DOM elements
        cacheElements();
        
        const { toggle, sidebar, overlay } = elements;
        
        // Check if navbar elements exist
        if (!toggle && !sidebar) {
            console.warn('⚠️ Navbar elements not found. Skipping initialization.');
            return;
        }
        
        // Detect capabilities
        detectTouch();
        detectReducedMotion();
        
        // Log configuration for debugging
        console.log('🧭 Navigation Config:', {
            autoHideDelay: CONFIG.autoHideDelay + 'ms',
            scrollThreshold: CONFIG.scrollThreshold + 'px',
            reducedMotion: state.prefersReducedMotion,
            isTouch: state.isTouch
        });
        
        // Set initial ARIA states
        toggle?.setAttribute('aria-expanded', 'false');
        toggle?.setAttribute('aria-controls', 'sidebar');
        toggle?.setAttribute('aria-label', 'Toggle navigation menu');
        sidebar?.setAttribute('aria-hidden', isDesktop() ? 'false' : 'true');
        sidebar?.setAttribute('role', 'navigation');
        sidebar?.setAttribute('aria-label', 'Main navigation');
        
        // Set initial toggle content
        if (toggle) {
            toggle.innerHTML = '<span class="toggle-icon" aria-hidden="true">☰</span>';
        }
        
        // Event Listeners
        
        // Scroll - throttled and passive
        window.addEventListener('scroll', 
            throttle(onScroll, CONFIG.throttleDelay), 
            { passive: true }
        );
        
        // Resize - throttled
        window.addEventListener('resize', handleResize, { passive: true });
        
        // Orientation change
        if (screen.orientation) {
            screen.orientation.addEventListener('change', handleOrientationChange);
        } else {
            window.addEventListener('orientationchange', handleOrientationChange);
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', handleKeydown);
        
        // Overlay click closes menu
        overlay?.addEventListener('click', closeMenu);
        
        // Touch event handling for overlay (prevents scroll through)
        overlay?.addEventListener('touchmove', (e) => {
            if (state.menuOpen) e.preventDefault();
        }, { passive: false });
        
        // Toggle button click
        toggle?.addEventListener('click', toggleMenu);
        
        // Handle visibility change (for when app returns from background)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                state.lastScrollY = window.scrollY;
                // Clear scrolling state when returning
                setScrollingState(false);
            }
        });
        
        // Initialize scroll position
        state.lastScrollY = window.scrollY;
        
        console.log('✅ Auto-hide navigation initialized');
        console.log('📱 Device info:', {
            touch: state.isTouch,
            reducedMotion: state.prefersReducedMotion,
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            devicePixelRatio: window.devicePixelRatio,
            orientation: state.orientation
        });
    }
    
    /* ============================================
       CLEANUP (for SPA/dynamic usage)
       ============================================ */
    function cleanup() {
        cancelHideTimer();
        if (state.scrollingTimer) {
            clearTimeout(state.scrollingTimer);
        }
        window.removeEventListener('scroll', onScroll);
        window.removeEventListener('resize', handleResize);
        document.removeEventListener('keydown', handleKeydown);
    }
    
    // Expose cleanup for external use
    window.cleanupNavigation = cleanup;
    
    // Expose config for runtime customization
    window.navbarConfig = CONFIG;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();

/* ============================================
   🧪 BROWSER TESTING NOTES
   ============================================
   
   iOS Safari (15+):
   - Test notch/Dynamic Island safe areas
   - Test rubber-band scroll behavior
   - Test landscape orientation
   - Test with reduced motion ON in Settings > Accessibility
   
   Android Chrome (90+):
   - Test various screen densities (mdpi to xxxhdpi)
   - Test with navigation gestures
   - Test split-screen mode
   - Test with TalkBack screen reader
   
   Desktop Chrome/Firefox (90+):
   - Test with DevTools responsive mode
   - Test keyboard navigation (Tab, Escape)
   - Test with prefers-reduced-motion in DevTools
   - Test print preview (Ctrl+P)
   
   Safari macOS (14+):
   - Test with Reduce Motion in Accessibility
   - Test with VoiceOver
   
   Edge (Chromium 90+):
   - Same as Chrome testing
   
   RUNTIME CONFIGURATION:
   Access window.navbarConfig to modify settings:
   - window.navbarConfig.autoHideDelay = 200;
   - window.navbarConfig.scrollThreshold = 150;
   
============================================ */
