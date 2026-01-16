import React, { createContext, useContext, useState, useCallback } from 'react';
import ToastContainer from '../components/ToastContainer';

const NotificationContext = createContext(null);

// eslint-disable-next-line react-refresh/only-export-components
export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotifications must be used within NotificationProvider');
    }
    return context;
};

let notificationIdCounter = 0;

export const NotificationProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);
    const [browserPermission, setBrowserPermission] = useState(
        typeof Notification !== 'undefined' ? Notification.permission : 'denied'
    );

    // Request browser notification permission
    const requestBrowserPermission = useCallback(async () => {
        if (typeof Notification === 'undefined') {
            console.warn('Browser notifications not supported');
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            setBrowserPermission(permission);
            return permission === 'granted';
        }

        return false;
    }, []);

    // Show toast notification
    const showToast = useCallback((message, priority = 'low') => {
        const id = `toast-${++notificationIdCounter}`;
        setToasts(prev => [...prev, { id, message, priority }]);
    }, []);

    // Dismiss toast
    const dismissToast = useCallback((id) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    // Show browser notification
    const showBrowserNotification = useCallback((title, options = {}) => {
        if (typeof Notification === 'undefined' || Notification.permission !== 'granted') {
            return;
        }

        // Don't show if tab is focused
        if (document.hasFocus()) {
            return;
        }

        new Notification(title, {
            icon: '/logo.png',
            badge: '/logo.png',
            ...options
        });
    }, []);

    // Play audio alert
    const playSound = useCallback((soundFile = 'notification') => {
        try {
            const audio = new Audio(`/sounds/${soundFile}.mp3`);
            audio.volume = 0.5;
            audio.play().catch(err => {
                console.warn('Could not play sound:', err);
            });
        } catch (err) {
            console.warn('Audio playback error:', err);
        }
    }, []);

    // Main notification function
    const notify = useCallback(({
        message,
        priority = 'low',
        browserNotification = false,
        browserTitle = '',
        browserOptions = {},
        sound = null
    }) => {
        // Always show toast
        showToast(message, priority);

        // Browser notification for medium/high/urgent
        if (browserNotification && (priority === 'medium' || priority === 'high' || priority === 'urgent')) {
            const title = browserTitle || message;
            showBrowserNotification(title, browserOptions);
        }

        // Audio for high/urgent
        if (sound && (priority === 'high' || priority === 'urgent')) {
            playSound(sound);
        }
    }, [showToast, showBrowserNotification, playSound]);

    const value = {
        notify,
        showToast,
        dismissToast,
        showBrowserNotification,
        playSound,
        requestBrowserPermission,
        browserPermission
    };

    return (
        <NotificationContext.Provider value={value}>
            {children}
            <ToastContainer toasts={toasts} dismissToast={dismissToast} />
        </NotificationContext.Provider>
    );
};
