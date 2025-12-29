import * as Sentry from "@sentry/react";

/**
 * Error Boundary component with Sentry integration.
 * Catches React errors and reports them to Sentry.
 */
const ErrorBoundary = Sentry.ErrorBoundary;

/**
 * Fallback UI shown when an error occurs.
 */
function ErrorFallback({ error, resetError }) {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            padding: '2rem',
            backgroundColor: '#0f172a',
            color: '#e2e8f0'
        }}>
            <div style={{
                maxWidth: '600px',
                textAlign: 'center',
                background: 'rgba(255, 255, 255, 0.05)',
                backdropFilter: 'blur(10px)',
                borderRadius: '16px',
                padding: '3rem',
                border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
                <h1 style={{
                    fontSize: '2rem',
                    fontWeight: 'bold',
                    marginBottom: '1rem',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                }}>
                    Oops! Something went wrong
                </h1>

                <p style={{
                    color: '#94a3b8',
                    marginBottom: '2rem',
                    lineHeight: '1.6'
                }}>
                    We've been notified and are working on a fix. Please try refreshing the page.
                </p>

                {error && (
                    <details style={{
                        marginBottom: '2rem',
                        textAlign: 'left',
                        background: 'rgba(0, 0, 0, 0.2)',
                        padding: '1rem',
                        borderRadius: '8px',
                        fontSize: '0.875rem'
                    }}>
                        <summary style={{ cursor: 'pointer', marginBottom: '0.5rem', color: '#f87171' }}>
                            Error Details
                        </summary>
                        <pre style={{
                            overflow: 'auto',
                            color: '#fca5a5',
                            fontSize: '0.75rem',
                            margin: 0
                        }}>
                            {error.toString()}
                        </pre>
                    </details>
                )}

                <button
                    onClick={resetError}
                    style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        padding: '0.75rem 2rem',
                        borderRadius: '8px',
                        border: 'none',
                        fontSize: '1rem',
                        fontWeight: '600',
                        cursor: 'pointer',
                        transition: 'transform 0.2s',
                    }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                >
                    Try Again
                </button>
            </div>
        </div>
    );
}

/**
 * Wrap your app with this component to catch and report errors.
 */
export default function AppErrorBoundary({ children }) {
    return (
        <ErrorBoundary fallback={ErrorFallback} showDialog>
            {children}
        </ErrorBoundary>
    );
}
