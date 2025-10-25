/**
 * Authentication Context
 * Manages user authentication state globally for both customers and merchants
 */

'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type?: 'customer' | 'merchant';
  // Customer-specific fields
  phone?: string;
  total_orders?: number;
  total_spent?: string;
  token_balance?: number;
  // Merchant-specific fields
  company_name?: string;
  shops?: any[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  userType: 'customer' | 'merchant' | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: any) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [userType, setUserType] = useState<'customer' | 'merchant' | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      if (api.auth.isAuthenticated()) {
        // Try to load customer profile first
        try {
          const profile = await api.customers.getProfile();
          setUser({
            ...profile.user,
            user_type: 'customer',
            phone: profile.phone,
            total_orders: profile.total_orders,
            total_spent: profile.total_spent,
            token_balance: profile.token_balance,
          });
          setUserType('customer');
          return;
        } catch (customerError) {
          // Not a customer, try merchant
          console.log('Not a customer, trying merchant profile...');
        }

        // Try to load merchant profile
        try {
          const merchantProfile = await api.merchants.getProfile();
          setUser({
            id: merchantProfile.id,
            username: merchantProfile.username,
            email: merchantProfile.email,
            first_name: merchantProfile.first_name,
            last_name: merchantProfile.last_name,
            user_type: 'merchant',
            company_name: merchantProfile.company_name,
            shops: merchantProfile.shops,
          });
          setUserType('merchant');
          return;
        } catch (merchantError) {
          console.error('Not a customer or merchant:', merchantError);
          // Not a customer or merchant, logout
          api.auth.logout();
        }
      }
    } catch (error) {
      console.error('Error loading user:', error);
      // Token might be expired, clear it
      api.auth.logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    await api.auth.login(username, password);
    await loadUser();
  };

  const register = async (data: any) => {
    const response = await api.customers.register(data);
    setUser({
      ...response.user,
      user_type: 'customer',
    });
    setUserType('customer');
  };

  const logout = () => {
    api.auth.logout();
    setUser(null);
    setUserType(null);
  };

  const refreshUser = async () => {
    await loadUser();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        userType,
        login,
        logout,
        register,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
