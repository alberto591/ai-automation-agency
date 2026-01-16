/**
 * Anzevino AI - Authentication Helper
 * Centralizes Supabase configuration and shared auth logic
 */

(function () {
    // Configuration - loaded from config.js (generated at build time)
    const SUPABASE_URL = window.ENV?.SUPABASE_URL || '';
    const SUPABASE_ANON_KEY = window.ENV?.SUPABASE_ANON_KEY || '';

    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
        console.error('❌ Missing Supabase configuration. Ensure config.js is loaded before auth-helper.js');
    }

    // Wait for Supabase library to load
    function initAuthHelper() {
        if (!window.supabase) {
            console.warn('Supabase library not loaded yet, retrying...');
            setTimeout(initAuthHelper, 100);
            return;
        }

        // Initialize Supabase - using a local variable to avoid conflict
        const _supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

        // Determine Dashboard URL (Local vs Prod)
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const DASHBOARD_URL = isLocal ? 'http://localhost:5174/dashboard/' : '/dashboard/';

        /**
         * Shared Auth Logic
         */
        const AuthHelper = {
            supabase: _supabase,

            /**
             * Get current session
             */
            async getSession() {
                const { data: { session }, error } = await _supabase.auth.getSession();
                if (error) {
                    console.error('Error getting session:', error);
                    return null;
                }
                return session;
            },

            /**
             * Handle Login
             */
            async login(email, password) {
                return await _supabase.auth.signInWithPassword({
                    email,
                    password
                });
            },

            /**
             * Handle Registration
             */
            async register(email, password, metadata) {
                return await _supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        data: metadata
                    }
                });
            },

            /**
             * Handle Logout
             */
            async logout() {
                await _supabase.auth.signOut();
                window.location.href = '/login.html';
            },

            /**
             * Send password reset email
             */
            async resetPassword(email) {
                return await _supabase.auth.resetPasswordForEmail(email, {
                    redirectTo: `${window.location.origin}/reset-password.html`
                });
            },

            /**
             * Update password (after receiving reset link)
             */
            async updatePassword(newPassword) {
                return await _supabase.auth.updateUser({
                    password: newPassword
                });
            },

            /**
             * Redirect if logged in
             */
            async redirectIfLoggedIn() {
                const session = await this.getSession();
                if (session) {
                    window.location.href = DASHBOARD_URL;
                }
            },

            /**
             * Update UI based on auth state (e.g. Nav headers)
             */
            async updateUIState() {
                const session = await this.getSession();
                const loginLink = document.getElementById('login-link');

                if (session && loginLink) {
                    // Change Login to Dashboard
                    loginLink.href = DASHBOARD_URL;
                    const textSpan = loginLink.querySelector('span[data-translate="nav-login"]');
                    if (textSpan) {
                        textSpan.textContent = 'Dashboard';
                        textSpan.setAttribute('data-translate', 'nav-dashboard');
                    }
                }
            }
        };

        // Auto-update UI on load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => AuthHelper.updateUIState());
        } else {
            AuthHelper.updateUIState();
        }

        // Expose to global scope
        window.AuthHelper = AuthHelper;
    }

    // Start initialization
    initAuthHelper();
})();
