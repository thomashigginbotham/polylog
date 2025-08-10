import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignIn from '../components/auth/GoogleSignIn';

export default function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const [error, setError] = useState<string | null>(null);

  // Redirect if already authenticated
  if (isAuthenticated && !isLoading) {
    return <Navigate to="/chat" replace />;
  }

  const handleSignInError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Polylog
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-4">
            Many voices, one conversation
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Sign in to join the collaborative AI chat experience
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-8">
          <div className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-md flex items-start justify-between">
                <div className="flex items-start">
                  <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm">{error}</span>
                </div>
                <button
                  onClick={clearError}
                  className="ml-2 text-red-400 hover:text-red-600 transition-colors"
                >
                  ×
                </button>
              </div>
            )}

            {/* Loading State */}
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">
                  Authenticating...
                </p>
              </div>
            ) : (
              <>
                {/* Sign In Section */}
                <div className="text-center">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Welcome to Polylog
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Sign in with your Google account to start collaborating with AI and other users.
                  </p>
                </div>

                {/* Google Sign-In Component */}
                <GoogleSignIn onError={handleSignInError} />
              </>
            )}
          </div>
        </div>

        {/* Features */}
        <div className="text-center space-y-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            What you can do with Polylog:
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
            <div className="flex flex-col items-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-2xl mb-2">🤖</span>
              <span className="font-medium text-gray-900 dark:text-white">AI Assistant</span>
              <span className="text-gray-600 dark:text-gray-400">Chat with AI</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-2xl mb-2">👥</span>
              <span className="font-medium text-gray-900 dark:text-white">Collaborate</span>
              <span className="text-gray-600 dark:text-gray-400">Multi-user chat</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
              <span className="text-2xl mb-2">⚡</span>
              <span className="font-medium text-gray-900 dark:text-white">Real-time</span>
              <span className="text-gray-600 dark:text-gray-400">Instant updates</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500 dark:text-gray-400">
          <p>By signing in, you agree to our Terms of Service and Privacy Policy</p>
        </div>
      </div>
    </div>
  );
}