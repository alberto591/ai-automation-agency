/**
 * Tests for NotificationContext
 * 
 * These tests verify:
 * - Toast notifications
 * - Browser notification permission
 * - Audio alert playback
 * - Priority-based notification logic
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { NotificationProvider, useNotifications } from '../contexts/NotificationContext';

// Mock Notification API
const mockNotification = vi.fn();
global.Notification = mockNotification;
global.Notification.permission = 'default';
global.Notification.requestPermission = vi.fn().mockResolvedValue('granted');

// Mock Audio
global.Audio = vi.fn().mockImplementation(() => ({
    play: vi.fn().mockResolvedValue(undefined),
    volume: 0.5
}));

// Mock document.hasFocus
Object.defineProperty(document, 'hasFocus', {
    writable: true,
    value: vi.fn(() => true)
});

// Test component
function TestComponent() {
    const { notify, showToast, requestBrowserPermission, browserPermission } = useNotifications();

    return (
        <div>
            <div data-testid="permission">{browserPermission}</div>
            <button onClick={() => showToast('Test message', 'low')} data-testid="show-toast">
                Show Toast
            </button>
            <button onClick={() => notify({ message: 'Test', priority: 'high', sound: 'urgent' })} data-testid="notify">
                Notify
            </button>
            <button onClick={requestBrowserPermission} data-testid="request-permission">
                Request Permission
            </button>
        </div>
    );
}

describe('NotificationContext', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        global.Notification.permission = 'default';
    });

    it('should render without crashing', () => {
        render(
            <NotificationProvider>
                <div>Test</div>
            </NotificationProvider>
        );
    });

    it('should provide notification context', () => {
        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        expect(screen.getByTestId('permission')).toBeInTheDocument();
    });

    it('should show toast notification', async () => {
        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('show-toast');
        button.click();

        await waitFor(() => {
            expect(screen.getByText('Test message')).toBeInTheDocument();
        });
    });

    it('should request browser notification permission', async () => {
        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('request-permission');
        button.click();

        await waitFor(() => {
            expect(global.Notification.requestPermission).toHaveBeenCalled();
        });
    });

    it('should play audio for high priority notifications', () => {
        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('notify');
        button.click();

        expect(global.Audio).toHaveBeenCalledWith('/sounds/urgent.mp3');
    });

    it('should not show browser notification when tab is focused', () => {
        document.hasFocus = vi.fn(() => true);
        global.Notification.permission = 'granted';

        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('notify');
        button.click();

        expect(mockNotification).not.toHaveBeenCalled();
    });

    it('should show browser notification when tab is not focused', () => {
        document.hasFocus = vi.fn(() => false);
        global.Notification.permission = 'granted';

        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('notify');
        button.click();

        expect(mockNotification).toHaveBeenCalled();
    });

    it('should auto-dismiss toast after 5 seconds', async () => {
        vi.useFakeTimers();

        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('show-toast');
        button.click();

        await waitFor(() => {
            expect(screen.getByText('Test message')).toBeInTheDocument();
        });

        // Fast-forward 5 seconds
        vi.advanceTimersByTime(5000);

        await waitFor(() => {
            expect(screen.queryByText('Test message')).not.toBeInTheDocument();
        });

        vi.useRealTimers();
    });

    it('should handle multiple toasts', async () => {
        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('show-toast');

        // Show 3 toasts
        button.click();
        button.click();
        button.click();

        await waitFor(() => {
            const toasts = screen.getAllByText('Test message');
            expect(toasts.length).toBe(3);
        });
    });

    it('should throw error when useNotifications used outside provider', () => {
        // Suppress console.error for this test
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => { });

        expect(() => {
            render(<TestComponent />);
        }).toThrow('useNotifications must be used within NotificationProvider');

        consoleError.mockRestore();
    });
});

describe('Toast Priority Styling', () => {
    it('should apply correct styles for low priority', async () => {
        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('show-toast');
        button.click();

        await waitFor(() => {
            const toast = screen.getByText('Test message').closest('div');
            expect(toast).toHaveClass('bg-gray-50');
        });
    });
});

describe('Audio Playback', () => {
    it('should handle audio playback errors gracefully', () => {
        const audioMock = {
            play: vi.fn().mockRejectedValue(new Error('Audio blocked')),
            volume: 0.5
        };
        global.Audio = vi.fn(() => audioMock);

        const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => { });

        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );

        const button = screen.getByTestId('notify');
        button.click();

        // Should not throw, just warn
        expect(consoleWarn).toHaveBeenCalledWith(expect.stringContaining('Could not play sound'));

        consoleWarn.mockRestore();
    });
});
