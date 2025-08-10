import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (googleToken: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('polylog_token');
    const storedUser = localStorage.getItem('polylog_user');
    
    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        
        // Check if token is expired
        const tokenPayload = JSON.parse(atob(storedToken.split('.')[1]));
        const expirationTime = tokenPayload.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        const timeUntilExpiry = expirationTime - currentTime;
        
        if (timeUntilExpiry <= 0) {
          // Token already expired
          console.log('🔐 Stored token has expired, clearing auth data');
          localStorage.removeItem('polylog_token');
          localStorage.removeItem('polylog_user');
        } else {
          // Token is still valid
          setToken(storedToken);
          setUser(parsedUser);
          console.log('🔐 Restored valid authentication from localStorage');
        }
      } catch (error) {
        console.error('❌ Failed to parse stored auth data:', error);
        localStorage.removeItem('polylog_token');
        localStorage.removeItem('polylog_user');
      }
    }
    
    setIsLoading(false);
  }, []);

  // Set up auto-refresh timer when user is authenticated
  useEffect(() => {
    if (!token || !user) return;

    try {
      const tokenPayload = JSON.parse(atob(token.split('.')[1]));
      const expirationTime = tokenPayload.exp * 1000;
      const currentTime = Date.now();
      const timeUntilExpiry = expirationTime - currentTime;
      
      // If token expires soon, try to refresh it
      if (timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0) { // Less than 5 minutes left
        console.log('🔐 Token expires soon, attempting refresh...');
        refreshToken().catch(() => {
          console.log('🔐 Token refresh failed, user will need to re-login');
          logout();
        });
      } else if (timeUntilExpiry > 5 * 60 * 1000) {
        // Set up auto-refresh timer for when token is close to expiring
        const refreshTimeout = timeUntilExpiry - 5 * 60 * 1000; // Refresh 5 minutes before expiry
        const timeoutId = setTimeout(() => {
          console.log('🔄 Auto-refreshing token...');
          refreshToken().catch(() => {
            console.log('🔐 Auto-refresh failed, user will need to re-login');
            logout();
          });
        }, refreshTimeout);

        return () => clearTimeout(timeoutId);
      }
    } catch (error) {
      console.error('❌ Error setting up token auto-refresh:', error);
    }
  }, [token, user]); // Remove circular dependency by not including refreshToken and logout

  const login = async (googleToken: string) => {
    try {
      setIsLoading(true);
      console.log('🔐 Attempting login with Google token...');

      const response = await fetch('http://localhost:8000/api/v1/auth/login/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: googleToken,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Store authentication data
      setToken(data.access_token);
      setUser(data.user);
      
      // Persist to localStorage
      localStorage.setItem('polylog_token', data.access_token);
      localStorage.setItem('polylog_user', JSON.stringify(data.user));
      
      console.log('✅ Login successful:', data.user.name);
      
    } catch (error) {
      console.error('❌ Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshToken = async () => {
    if (!token) {
      throw new Error('No token to refresh');
    }

    try {
      console.log('🔄 Refreshing JWT token...');

      const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      
      // Update token but keep existing user data
      setToken(data.access_token);
      localStorage.setItem('polylog_token', data.access_token);
      
      console.log('✅ Token refreshed successfully');
      
    } catch (error) {
      console.error('❌ Token refresh error:', error);
      // Clear invalid token
      logout();
      throw error;
    }
  };

  const logout = () => {
    console.log('🚪 Logging out...');
    
    // Clear state
    setUser(null);
    setToken(null);
    
    // Clear localStorage
    localStorage.removeItem('polylog_token');
    localStorage.removeItem('polylog_user');
    
    console.log('✅ Logout complete');
  };

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user && !!token,
    login,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}