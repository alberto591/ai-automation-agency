import React, { useState } from 'react';
import './App.css';
import { supabase } from './supabaseClient';

function App() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const { data, error } = await supabase
        .from('lead_conversations')
        .insert([
          {
            customer_name: formData.name,
            customer_phone: formData.email, // Using email as phone for simplicity
            last_message: formData.message,
            ai_summary: 'Lead captured from landing page',
            status: 'New'
          }
        ]);

      if (error) {
        throw error;
      }

      setSubmitStatus('success');
      setFormData({ name: '', email: '', message: '' });
    } catch (error) {
      console.error('Error submitting form:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <div className="logo">Agenzia AI</div>
        <nav className="nav">
          <a href="#home">Home</a>
          <a href="#services">Servizi</a>
          <a href="#about">Chi Siamo</a>
          <a href="#contact">Contatti</a>
        </nav>
        <button className="cta-button">Contattaci</button>
      </header>

      {/* Hero Section */}
      <section id="home" className="hero">
        <div className="hero-content">
          <h1>Automazione Immobiliare con AI</h1>
          <p>Offriamo gestione lead 24/7 su WhatsApp, abbinamento proprietà con tecnologia RAG e un dashboard in tempo reale per i proprietari di agenzie.</p>
          <div className="hero-buttons">
            <button className="primary-button">Scopri di Più</button>
            <button className="secondary-button">Contattaci</button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="services" className="features">
        <h2>I Nostri Servizi</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>Gestione Lead 24/7</h3>
            <p>Rispondiamo ai lead su WhatsApp in tempo reale, 24 ore su 24, 7 giorni su 7.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🏠</div>
            <h3>Abbinamento Proprietà</h3>
            <p>Utilizziamo la tecnologia RAG per abbinare i lead alle proprietà più adatte.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Dashboard in Tempo Reale</h3>
            <p>Monitora i lead e le conversazioni in tempo reale con il nostro dashboard.</p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <h2>Cosa Dicono i Nostri Clienti</h2>
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <div className="testimonial-image">👤</div>
            <p>"Grazie ad Agenzia AI, abbiamo aumentato le nostre vendite del 30% in solo un mese!"</p>
            <div className="testimonial-author">- Marco Rossi</div>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-image">👤</div>
            <p>"Il servizio di gestione lead è eccezionale. Rispondono ai clienti in tempo reale!"</p>
            <div className="testimonial-author">- Laura Bianchi</div>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-image">👤</div>
            <p>"Il dashboard in tempo reale ci ha permesso di monitorare i lead in modo efficiente."</p>
            <div className="testimonial-author">- Giovanni Verdi</div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about">
        <h2>Chi Siamo</h2>
        <div className="about-content">
          <div className="about-text">
            <p>Siamo un'agenzia immobiliare moderna che utilizza l'intelligenza artificiale per offrire servizi innovativi ai nostri clienti. La nostra missione è quella di semplificare il processo di acquisto e vendita di immobili, offrendo soluzioni tecnologiche all'avanguardia.</p>
            <button className="primary-button">Scopri di Più</button>
          </div>
          <div className="about-image">🏢</div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="contact">
        <h2>Contattaci</h2>
        <div className="contact-content">
          <div className="contact-form">
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                name="name"
                placeholder="Nome"
                value={formData.name}
                onChange={handleChange}
                required
              />
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                required
              />
              <textarea
                name="message"
                placeholder="Messaggio"
                value={formData.message}
                onChange={handleChange}
                required
              ></textarea>
              <button type="submit" className="primary-button" disabled={isSubmitting}>
                {isSubmitting ? 'Invio in corso...' : 'Invia'}
              </button>
            </form>
            {submitStatus === 'success' && (
              <p style={{ color: 'green', marginTop: '1rem' }}>Grazie! Il tuo messaggio è stato inviato con successo.</p>
            )}
            {submitStatus === 'error' && (
              <p style={{ color: 'red', marginTop: '1rem' }}>Si è verificato un errore. Per favore, riprova.</p>
            )}
          </div>
          <div className="contact-info">
            <h3>Informazioni di Contatto</h3>
            <p>📞 Telefono: +39 123 456 789</p>
            <p>📧 Email: info@agenziaai.it</p>
            <p>📍 Indirizzo: Via Roma, 123, Milano, Italia</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-logo">Agenzia AI</div>
          <nav className="footer-nav">
            <a href="#home">Home</a>
            <a href="#services">Servizi</a>
            <a href="#about">Chi Siamo</a>
            <a href="#contact">Contatti</a>
          </nav>
          <div className="footer-social">
            <a href="#">Facebook</a>
            <a href="#">Twitter</a>
            <a href="#">Instagram</a>
          </div>
          <div className="footer-copyright">
            <p>&copy; 2023 Agenzia AI. Tutti i diritti riservati.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
