import React from 'react';
import Toast from './Toast';

const ToastContainer = ({ toasts, dismissToast }) => {
    if (toasts.length === 0) return null;

    return (
        <div className="fixed top-4 right-4 z-[9999] pointer-events-none">
            <div className="flex flex-col items-end pointer-events-auto">
                {toasts.map((toast) => (
                    <Toast
                        key={toast.id}
                        id={toast.id}
                        message={toast.message}
                        priority={toast.priority}
                        onDismiss={dismissToast}
                    />
                ))}
            </div>
        </div>
    );
};

export default ToastContainer;
