import { create } from 'zustand';
import { 
  Appointment, 
  AppointmentSlot, 
  LiveQueueItem, 
  PaginatedResponse 
} from '@/types';
import apiClient from '@/lib/api-client';

interface AppointmentFilters {
  status?: string;
  date_from?: string;
  date_to?: string;
  doctor_id?: string;
  patient_id?: string;
}

interface AppointmentState {
  appointments: Appointment[];
  currentAppointment: Appointment | null;
  availableSlots: AppointmentSlot[];
  liveQueue: LiveQueueItem[];
  isLoading: boolean;
  error: string | null;
  pagination: {
    count: number;
    next: string | null;
    previous: string | null;
  };
  
  // Actions
  fetchAppointments: (filters?: AppointmentFilters) => Promise<void>;
  fetchAppointment: (id: string) => Promise<void>;
  createAppointment: (data: Partial<Appointment>) => Promise<Appointment>;
  updateAppointment: (id: string, data: Partial<Appointment>) => Promise<void>;
  cancelAppointment: (id: string, reason?: string) => Promise<void>;
  rescheduleAppointment: (id: string, newDate: string, newTime: string) => Promise<void>;
  fetchAvailableSlots: (doctorId: string, clinicId: string, date: string) => Promise<void>;
  fetchLiveQueue: (doctorId: string, date?: string) => Promise<void>;
  checkInAppointment: (id: string) => Promise<void>;
  startConsultation: (id: string) => Promise<void>;
  completeAppointment: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useAppointmentStore = create<AppointmentState>((set, get) => ({
  appointments: [],
  currentAppointment: null,
  availableSlots: [],
  liveQueue: [],
  isLoading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
  },

  fetchAppointments: async (filters?: AppointmentFilters) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get<PaginatedResponse<Appointment>>(
        '/api/appointments/',
        filters
      );
      set({
        appointments: response.results,
        pagination: {
          count: response.count,
          next: response.next,
          previous: response.previous,
        },
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchAppointment: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const appointment = await apiClient.get<Appointment>(`/api/appointments/${id}/`);
      set({ currentAppointment: appointment, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  createAppointment: async (data: Partial<Appointment>) => {
    set({ isLoading: true, error: null });
    try {
      const appointment = await apiClient.post<Appointment>('/api/appointments/', data);
      set((state) => ({
        appointments: [...state.appointments, appointment],
        isLoading: false,
      }));
      return appointment;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  updateAppointment: async (id: string, data: Partial<Appointment>) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.patch<Appointment>(`/api/appointments/${id}/`, data);
      set((state) => ({
        appointments: state.appointments.map((a) => (a.id === id ? updated : a)),
        currentAppointment: state.currentAppointment?.id === id ? updated : state.currentAppointment,
        isLoading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  cancelAppointment: async (id: string, reason?: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post(`/api/appointments/${id}/cancel/`, { reason });
      await get().fetchAppointments();
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  rescheduleAppointment: async (id: string, newDate: string, newTime: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post(`/api/appointments/${id}/reschedule/`, {
        new_date: newDate,
        new_time: newTime,
      });
      await get().fetchAppointments();
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchAvailableSlots: async (doctorId: string, clinicId: string, date: string) => {
    set({ isLoading: true, error: null });
    try {
      const slots = await apiClient.get<AppointmentSlot[]>(
        `/api/appointments/available-slots/`,
        { doctor_id: doctorId, clinic_id: clinicId, date }
      );
      set({ availableSlots: slots, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchLiveQueue: async (doctorId: string, date?: string) => {
    set({ isLoading: true, error: null });
    try {
      const queue = await apiClient.get<LiveQueueItem[]>(
        `/api/appointments/live-queue/`,
        { doctor_id: doctorId, date }
      );
      set({ liveQueue: queue, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  checkInAppointment: async (id: string) => {
    await get().updateAppointment(id, { status: 'checked_in' } as Partial<Appointment>);
  },

  startConsultation: async (id: string) => {
    await get().updateAppointment(id, { status: 'in_progress' } as Partial<Appointment>);
  },

  completeAppointment: async (id: string) => {
    await get().updateAppointment(id, { status: 'completed' } as Partial<Appointment>);
  },

  clearError: () => set({ error: null }),
}));
