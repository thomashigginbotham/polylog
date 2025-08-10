import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

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
        setToken(storedToken);
        setUser(parsedUser);
        console.log('🔐 Restored authentication from localStorage');
      } catch (error) {
        console.error('❌ Failed to parse stored user data:', error);
        localStorage.removeItem('polylog_token');
        localStorage.removeItem('polylog_user');
      }
    }
    
    setIsLoading(false);
  }, []);

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