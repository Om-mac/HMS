import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthTokens, LoginCredentials, RegisterData } from '@/types';
import apiClient from '@/lib/api-client';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await apiClient.post<AuthTokens>('/api/auth/login/', credentials);
          apiClient.setTokens(tokens);
          
          // Fetch user data
          const user = await apiClient.get<User>('/api/auth/profile/');
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Login failed. Please check your credentials.';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiClient.post<{ tokens: AuthTokens; user: User }>('/api/auth/register/', data);
          
          // Set tokens from registration response
          apiClient.setTokens(response.tokens);
          set({ user: response.user, isAuthenticated: true, isLoading: false });
        } catch (error: any) {
          const errorData = error.response?.data;
          let message = 'Registration failed. Please try again.';
          
          if (errorData) {
            if (typeof errorData === 'string') {
              message = errorData;
            } else if (errorData.detail) {
              message = errorData.detail;
            } else if (errorData.email) {
              message = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email;
            } else if (errorData.password) {
              message = Array.isArray(errorData.password) ? errorData.password[0] : errorData.password;
            } else if (errorData.phone_number) {
              message = Array.isArray(errorData.phone_number) ? errorData.phone_number[0] : errorData.phone_number;
            } else if (errorData.non_field_errors) {
              message = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors;
            }
          }
          
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        apiClient.clearTokens();
        set({ user: null, isAuthenticated: false, error: null });
      },

      fetchUser: async () => {
        set({ isLoading: true });
        try {
          const user = await apiClient.get<User>('/api/auth/profile/');
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error) {
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated }),
    }
  )
);
