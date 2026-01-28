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
          const tokens = await apiClient.post<AuthTokens>('/api/users/token/', credentials);
          apiClient.setTokens(tokens);
          
          // Fetch user data
          const user = await apiClient.get<User>('/api/users/me/');
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
          await apiClient.post('/api/users/register/', data);
          
          // Auto-login after registration
          await get().login({ email: data.email, password: data.password });
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Registration failed. Please try again.';
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
          const user = await apiClient.get<User>('/api/users/me/');
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
