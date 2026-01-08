/**
 * Anzevino AI - Authentication Helper
 * Centralizes Supabase configuration and shared auth logic
 */

(function () {
    // Configuration
    const SUPABASE_URL = 'https://zozgvcdnkwtyioyazgmx.supabase.co';
    const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpvemd2Y2Rua3d0eWlveWF6Z214Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzU1MjMsImV4cCI6MjA4MTY1MTUyM30.Z-IsY7vYkwIo6sB22ZpGIMTFD9kXSRdO6Ykv_bXwOvg';

    // Wait for Supabase library to load
    function initAuthHelper() {
        if (!window.supabase) {
            console.warn('Supabase library not loaded yet, retrying...');
            setTimeout(initAuthHelper, 100);
            return;
        }

        // Initialize Supabase - using a local variable to avoid conflict
        const _supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

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
                    window.location.href = '/dashboard/';
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
                    loginLink.href = '/dashboard/';
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
