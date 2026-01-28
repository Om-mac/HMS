// User types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone_number: string;
  date_of_birth: string | null;
  address: string;
  role: 'admin' | 'doctor' | 'patient' | 'staff';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  user_type: "doctor" | "patient";
  password_confirm?: string;
}

// Patient types
export interface Patient {
  id: string;
  user: User;
  patient_id: string;
  blood_type: string;
  gender: string;
  height_cm: number | null;
  weight_kg: number | null;
  bmi: number | null;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relation: string;
  insurance_provider: string;
  insurance_policy_number: string;
  insurance_expiry: string | null;
  preferred_language: string;
  allergies: PatientAllergy[];
  medications: PatientMedication[];
  chronic_conditions: PatientChronicCondition[];
  created_at: string;
  updated_at: string;
}

export interface PatientAllergy {
  id: string;
  allergen: string;
  reaction: string;
  severity: 'mild' | 'moderate' | 'severe' | 'life_threatening';
  diagnosed_date: string | null;
  notes: string;
}

export interface PatientMedication {
  id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  start_date: string;
  end_date: string | null;
  prescribing_doctor: string;
  purpose: string;
  is_current: boolean;
}

export interface PatientChronicCondition {
  id: string;
  condition_name: string;
  icd_code: string;
  diagnosed_date: string | null;
  status: 'active' | 'controlled' | 'in_remission' | 'resolved';
  notes: string;
}

// Doctor types
export interface Doctor {
  id: string;
  user: User;
  license_number: string;
  specialization: Specialization;
  qualification: string;
  experience_years: number;
  bio: string;
  consultation_fee: number;
  rating: number;
  total_reviews: number;
  is_accepting_patients: boolean;
  clinics: ClinicAssignment[];
}

export interface Specialization {
  id: string;
  name: string;
  description: string;
}

export interface ClinicAssignment {
  id: string;
  clinic: Clinic;
  is_primary: boolean;
  consultation_fee: number | null;
}

export interface DoctorSchedule {
  id: string;
  doctor: string;
  clinic: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  slot_duration: number;
  is_active: boolean;
}

// Clinic types
export interface Clinic {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone: string;
  email: string;
  website: string;
  description: string;
  is_active: boolean;
  facilities: ClinicFacility[];
}

export interface ClinicFacility {
  id: string;
  name: string;
  description: string;
}

// Appointment types
export interface Appointment {
  id: string;
  appointment_number: string;
  patient: Patient;
  doctor: Doctor;
  clinic: Clinic;
  appointment_date: string;
  start_time: string;
  end_time: string;
  status: AppointmentStatus;
  appointment_type: AppointmentType;
  reason: string;
  notes: string;
  symptoms: string[];
  check_in_time: string | null;
  check_out_time: string | null;
  created_at: string;
  updated_at: string;
}

export type AppointmentStatus = 
  | 'scheduled' 
  | 'confirmed' 
  | 'checked_in' 
  | 'in_progress' 
  | 'completed' 
  | 'cancelled' 
  | 'no_show'
  | 'rescheduled';

export type AppointmentType = 
  | 'consultation' 
  | 'follow_up' 
  | 'emergency' 
  | 'procedure' 
  | 'vaccination' 
  | 'lab_test' 
  | 'imaging';

export interface AppointmentSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface LiveQueueItem {
  id: string;
  appointment: Appointment;
  position: number;
  estimated_wait_time: number;
  called_at: string | null;
  status: 'waiting' | 'called' | 'in_consultation' | 'completed' | 'skipped';
}

// EMR types
export interface MedicalRecord {
  id: string;
  patient: string;
  doctor: Doctor;
  appointment: string | null;
  record_type: string;
  chief_complaint: string;
  diagnosis: string;
  treatment_plan: string;
  notes: string;
  vitals: VitalSigns;
  files: MedicalFile[];
  created_at: string;
  updated_at: string;
}

export interface VitalSigns {
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  temperature?: number;
  respiratory_rate?: number;
  oxygen_saturation?: number;
  weight?: number;
  height?: number;
}

export interface MedicalFile {
  id: string;
  file_type: 'lab_report' | 'xray' | 'scan' | 'prescription' | 'other';
  title: string;
  description: string;
  file_url: string;
  signed_url?: string;
  uploaded_at: string;
}

export interface Prescription {
  id: string;
  medical_record: string;
  patient: string;
  doctor: Doctor;
  prescription_date: string;
  valid_until: string;
  items: PrescriptionItem[];
  notes: string;
  is_digital_signed: boolean;
}

export interface PrescriptionItem {
  id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  quantity: number;
  instructions: string;
  is_substitute_allowed: boolean;
}

// Dental types
export interface DentalRecord {
  id: string;
  patient: string;
  doctor: Doctor;
  last_cleaning_date: string | null;
  next_cleaning_date: string | null;
  notes: string;
  tooth_history: ToothHistory[];
  created_at: string;
  updated_at: string;
}

export interface ToothHistory {
  id: string;
  tooth_number: number;
  surface: string;
  condition: ToothCondition;
  treatment: string;
  treatment_date: string;
  notes: string;
}

export type ToothCondition = 
  | 'healthy' 
  | 'cavity' 
  | 'filled' 
  | 'crown' 
  | 'root_canal' 
  | 'extraction' 
  | 'missing' 
  | 'implant' 
  | 'bridge';

// Transfer types
export interface PatientAccess {
  id: string;
  patient: Patient;
  granted_by: User;
  granted_to_doctor: Doctor | null;
  granted_to_clinic: Clinic | null;
  access_level: 'view' | 'full';
  reason: string;
  valid_from: string;
  valid_until: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TransferRequest {
  id: string;
  patient: Patient;
  from_clinic: Clinic;
  to_clinic: Clinic;
  from_doctor: Doctor;
  to_doctor: Doctor | null;
  status: 'pending' | 'accepted' | 'rejected' | 'completed' | 'cancelled';
  reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

// Notification types
export interface Notification {
  id: string;
  recipient: string;
  notification_type: string;
  channel: 'email' | 'sms' | 'whatsapp' | 'push';
  subject: string;
  message: string;
  status: 'pending' | 'sent' | 'delivered' | 'failed' | 'read';
  sent_at: string | null;
  read_at: string | null;
}

// Waitlist types
export interface WaitlistEntry {
  id: string;
  patient: Patient;
  doctor: Doctor;
  clinic: Clinic;
  preferred_date: string;
  preferred_time_start: string | null;
  preferred_time_end: string | null;
  reason: string;
  status: 'waiting' | 'notified' | 'booked' | 'expired' | 'cancelled';
  notification_sent_at: string | null;
  created_at: string;
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// Dashboard statistics
export interface DoctorDashboardStats {
  today_appointments: number;
  pending_appointments: number;
  completed_today: number;
  total_patients: number;
  waiting_queue_count: number;
  upcoming_appointments: Appointment[];
  recent_patients: Patient[];
}

export interface PatientDashboardStats {
  upcoming_appointments: Appointment[];
  recent_records: MedicalRecord[];
  active_prescriptions: Prescription[];
  pending_transfers: TransferRequest[];
}
