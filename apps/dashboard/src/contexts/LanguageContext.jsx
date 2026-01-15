import { createContext, useContext, useState, useEffect } from 'react'
import { translations } from '../translations/dashboard'

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
    const [language, setLanguage] = useState(() => {
        // Get saved language from localStorage or default to Italian
        return localStorage.getItem('dashboard_language') || 'it'
    })

    useEffect(() => {
        // Save language preference to localStorage
        localStorage.setItem('dashboard_language', language)
    }, [language])

    const t = (key) => {
        return translations[language]?.[key] || key
    }

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    )
}

export function useLanguage() {
    const context = useContext(LanguageContext)
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider')
    }
    return context
}
