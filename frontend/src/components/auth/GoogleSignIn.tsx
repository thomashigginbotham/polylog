import React, { useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';

declare global {
  interface Window {
    google: any;
  }
}

interface GoogleSignInProps {
  onError?: (error: string) => void;
}

export default function GoogleSignIn({ onError }: GoogleSignInProps) {
  const { login, isLoading } = useAuth();
  const buttonRef = useRef<HTMLDivElement>(null);
  const [isGoogleLoaded, setIsGoogleLoaded] = React.useState(false);

  useEffect(() => {
    // Check if Google Identity Services is loaded
    const checkGoogleLoaded = () => {
      if (window.google?.accounts?.id) {
        setIsGoogleLoaded(true);
        initializeGoogleSignIn();
      } else {
        // Retry after 100ms
        setTimeout(checkGoogleLoaded, 100);
      }
    };

    checkGoogleLoaded();
  }, []);

  const initializeGoogleSignIn = () => {
    if (!window.google?.accounts?.id || !buttonRef.current) return;

    try {
      window.google.accounts.id.initialize({
        client_id: '1012577899600-qled0milh4mm13ltbd6u0eelpo81jkk2.apps.googleusercontent.com', // From your .env
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
      });

      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: 'outline',
        size: 'large',
        text: 'signin_with',
        shape: 'rectangular',
        logo_alignment: 'left',
      });

      console.log('🔐 Google Sign-In initialized');
    } catch (error) {
      console.error('❌ Google Sign-In initialization error:', error);
    }
  };

  const handleCredentialResponse = async (response: any) => {
    try {
      console.log('🔐 Google credential received');
      
      // The response contains an ID token, but we need an access token
      // For simplicity, we'll decode the ID token to get user info and create our own session
      // In production, you'd want to validate this server-side
      
      const base64Url = response.credential.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      
      const userInfo = JSON.parse(jsonPayload);
      console.log('👤 Google user info:', userInfo);
      
      // For development, we'll simulate an access token using the ID token
      // In production, you'd exchange this for a proper access token
      await login(response.credential);
      
    } catch (error) {
      console.error('❌ Google sign-in error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Google sign-in failed';
      onError?.(errorMessage);
    }
  };

  const handleManualSignIn = () => {
    if (!window.google?.accounts?.oauth2) {
      console.error('❌ Google OAuth2 not loaded');
      return;
    }

    // Alternative: Use OAuth2 flow to get access token
    window.google.accounts.oauth2.initTokenClient({
      client_id: '1012577899600-qled0milh4mm13ltbd6u0eelpo81jkk2.apps.googleusercontent.com',
      scope: 'openid profile email',
      callback: async (response: any) => {
        if (response.access_token) {
          try {
            await login(response.access_token);
          } catch (error) {
            console.error('❌ OAuth2 login error:', error);
            const errorMessage = error instanceof Error ? error.message : 'Login failed';
            onError?.(errorMessage);
          }
        }
      },
    }).requestAccessToken();
  };

  if (!isGoogleLoaded) {
    return (
      <div className="flex items-center justify-center py-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading Google Sign-In...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Google Sign-In Button (renders here automatically) */}
      <div ref={buttonRef} className="flex justify-center"></div>
      
      {/* Alternative manual button for development */}
      <div className="text-center">
        <button
          onClick={handleManualSignIn}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
              Signing in...
            </>
          ) : (
            <>
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google (OAuth2)
            </>
          )}
        </button>
      </div>
      
      <p className="text-xs text-gray-500 text-center">
        Use either button above to sign in with Google
      </p>
    </div>
  );
}