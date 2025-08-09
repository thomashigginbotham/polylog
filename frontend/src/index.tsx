import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './assets/styles/globals.css';

// Google OAuth
import { GoogleOAuthProvider } from '@react-oauth/google';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

if (!googleClientId) {
  console.warn('Google Client ID not found. OAuth will not work.');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={googleClientId || ''}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>
);
