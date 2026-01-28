import { create } from 'zustand';
import { 
  Patient, 
  MedicalRecord, 
  DentalRecord, 
  Prescription,
  PatientAllergy,
  PatientMedication,
  PatientChronicCondition,
  PaginatedResponse 
} from '@/types';
import apiClient from '@/lib/api-client';

interface PatientState {
  patients: Patient[];
  currentPatient: Patient | null;
  medicalRecords: MedicalRecord[];
  currentMedicalRecord: MedicalRecord | null;
  dentalRecord: DentalRecord | null;
  prescriptions: Prescription[];
  isLoading: boolean;
  error: string | null;
  
  // Patient actions
  fetchPatients: (search?: string) => Promise<void>;
  fetchPatient: (id: string) => Promise<void>;
  fetchPatientByQR: (patientId: string) => Promise<void>;
  updatePatient: (id: string, data: Partial<Patient>) => Promise<void>;
  
  // Allergy actions
  addAllergy: (patientId: string, allergy: Partial<PatientAllergy>) => Promise<void>;
  updateAllergy: (patientId: string, allergyId: string, data: Partial<PatientAllergy>) => Promise<void>;
  deleteAllergy: (patientId: string, allergyId: string) => Promise<void>;
  
  // Medication actions
  addMedication: (patientId: string, medication: Partial<PatientMedication>) => Promise<void>;
  updateMedication: (patientId: string, medicationId: string, data: Partial<PatientMedication>) => Promise<void>;
  deleteMedication: (patientId: string, medicationId: string) => Promise<void>;
  
  // Chronic condition actions
  addChronicCondition: (patientId: string, condition: Partial<PatientChronicCondition>) => Promise<void>;
  updateChronicCondition: (patientId: string, conditionId: string, data: Partial<PatientChronicCondition>) => Promise<void>;
  deleteChronicCondition: (patientId: string, conditionId: string) => Promise<void>;
  
  // Medical records actions
  fetchMedicalRecords: (patientId: string) => Promise<void>;
  fetchMedicalRecord: (id: string) => Promise<void>;
  createMedicalRecord: (data: Partial<MedicalRecord>) => Promise<MedicalRecord>;
  updateMedicalRecord: (id: string, data: Partial<MedicalRecord>) => Promise<void>;
  
  // Dental record actions
  fetchDentalRecord: (patientId: string) => Promise<void>;
  updateDentalRecord: (id: string, data: Partial<DentalRecord>) => Promise<void>;
  addToothHistory: (dentalRecordId: string, toothData: object) => Promise<void>;
  
  // Prescription actions
  fetchPrescriptions: (patientId: string) => Promise<void>;
  createPrescription: (data: Partial<Prescription>) => Promise<Prescription>;
  
  clearError: () => void;
  clearCurrentPatient: () => void;
}

export const usePatientStore = create<PatientState>((set, get) => ({
  patients: [],
  currentPatient: null,
  medicalRecords: [],
  currentMedicalRecord: null,
  dentalRecord: null,
  prescriptions: [],
  isLoading: false,
  error: null,

  // Patient actions
  fetchPatients: async (search?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get<PaginatedResponse<Patient>>(
        '/api/patients/',
        search ? { search } : undefined
      );
      set({ patients: response.results, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchPatient: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const patient = await apiClient.get<Patient>(`/api/patients/${id}/`);
      set({ currentPatient: patient, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchPatientByQR: async (patientId: string) => {
    set({ isLoading: true, error: null });
    try {
      const patient = await apiClient.get<Patient>(`/api/patients/by-qr/${patientId}/`);
      set({ currentPatient: patient, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  updatePatient: async (id: string, data: Partial<Patient>) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.patch<Patient>(`/api/patients/${id}/`, data);
      set({ currentPatient: updated, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Allergy actions
  addAllergy: async (patientId: string, allergy: Partial<PatientAllergy>) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post(`/api/patients/${patientId}/allergies/`, allergy);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  updateAllergy: async (patientId: string, allergyId: string, data: Partial<PatientAllergy>) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.patch(`/api/patients/${patientId}/allergies/${allergyId}/`, data);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  deleteAllergy: async (patientId: string, allergyId: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.delete(`/api/patients/${patientId}/allergies/${allergyId}/`);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Medication actions
  addMedication: async (patientId: string, medication: Partial<PatientMedication>) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post(`/api/patients/${patientId}/medications/`, medication);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  updateMedication: async (patientId: string, medicationId: string, data: Partial<PatientMedication>) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.patch(`/api/patients/${patientId}/medications/${medicationId}/`, data);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  deleteMedication: async (patientId: string, medicationId: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.delete(`/api/patients/${patientId}/medications/${medicationId}/`);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Chronic condition actions
  addChronicCondition: async (patientId: string, condition: Partial<PatientChronicCondition>) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post(`/api/patients/${patientId}/chronic-conditions/`, condition);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  updateChronicCondition: async (patientId: string, conditionId: string, data: Partial<PatientChronicCondition>) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.patch(`/api/patients/${patientId}/chronic-conditions/${conditionId}/`, data);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  deleteChronicCondition: async (patientId: string, conditionId: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.delete(`/api/patients/${patientId}/chronic-conditions/${conditionId}/`);
      await get().fetchPatient(patientId);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Medical records actions
  fetchMedicalRecords: async (patientId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get<PaginatedResponse<MedicalRecord>>(
        `/api/emr/records/`,
        { patient_id: patientId }
      );
      set({ medicalRecords: response.results, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchMedicalRecord: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const record = await apiClient.get<MedicalRecord>(`/api/emr/records/${id}/`);
      set({ currentMedicalRecord: record, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  createMedicalRecord: async (data: Partial<MedicalRecord>) => {
    set({ isLoading: true, error: null });
    try {
      const record = await apiClient.post<MedicalRecord>('/api/emr/records/', data);
      set((state) => ({
        medicalRecords: [...state.medicalRecords, record],
        currentMedicalRecord: record,
        isLoading: false,
      }));
      return record;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  updateMedicalRecord: async (id: string, data: Partial<MedicalRecord>) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.patch<MedicalRecord>(`/api/emr/records/${id}/`, data);
      set((state) => ({
        medicalRecords: state.medicalRecords.map((r) => (r.id === id ? updated : r)),
        currentMedicalRecord: updated,
        isLoading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Dental record actions
  fetchDentalRecord: async (patientId: string) => {
    set({ isLoading: true, error: null });
    try {
      const record = await apiClient.get<DentalRecord>(`/api/emr/dental/${patientId}/`);
      set({ dentalRecord: record, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  updateDentalRecord: async (id: string, data: Partial<DentalRecord>) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.patch<DentalRecord>(`/api/emr/dental/${id}/`, data);
      set({ dentalRecord: updated, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  addToothHistory: async (dentalRecordId: string, toothData: object) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post(`/api/emr/dental/${dentalRecordId}/tooth-history/`, toothData);
      // Refresh dental record
      const { dentalRecord } = get();
      if (dentalRecord) {
        await get().fetchDentalRecord(dentalRecord.patient);
      }
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Prescription actions
  fetchPrescriptions: async (patientId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get<PaginatedResponse<Prescription>>(
        `/api/emr/prescriptions/`,
        { patient_id: patientId }
      );
      set({ prescriptions: response.results, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  createPrescription: async (data: Partial<Prescription>) => {
    set({ isLoading: true, error: null });
    try {
      const prescription = await apiClient.post<Prescription>('/api/emr/prescriptions/', data);
      set((state) => ({
        prescriptions: [...state.prescriptions, prescription],
        isLoading: false,
      }));
      return prescription;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
  clearCurrentPatient: () => set({ currentPatient: null, medicalRecords: [], dentalRecord: null, prescriptions: [] }),
}));
