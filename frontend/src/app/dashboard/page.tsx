"use client";

import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Calendar, 
  Users, 
  Clock, 
  CheckCircle, 
  ArrowRight,
  TrendingUp,
  Activity,
  AlertCircle
} from "lucide-react";
import Link from "next/link";

// Mock data for demonstration
const mockStats = {
  doctor: {
    todayAppointments: 12,
    pendingAppointments: 5,
    completedToday: 7,
    totalPatients: 248,
    waitingQueue: 3,
  },
  patient: {
    upcomingAppointments: 2,
    completedVisits: 15,
    activePrescriptions: 3,
    pendingReports: 1,
  },
};

type DoctorStats = typeof mockStats.doctor;
type PatientStats = typeof mockStats.patient;

const mockUpcomingAppointments = [
  {
    id: "1",
    patientName: "Sarah Johnson",
    doctorName: "Dr. Smith",
    time: "09:00 AM",
    type: "Consultation",
    status: "confirmed",
  },
  {
    id: "2",
    patientName: "Michael Chen",
    doctorName: "Dr. Smith",
    time: "10:30 AM",
    type: "Follow-up",
    status: "scheduled",
  },
  {
    id: "3",
    patientName: "Emily Davis",
    doctorName: "Dr. Smith",
    time: "11:00 AM",
    type: "Procedure",
    status: "confirmed",
  },
];

const mockRecentPatients = [
  { id: "1", name: "John Doe", lastVisit: "2 days ago", condition: "Checkup" },
  { id: "2", name: "Jane Smith", lastVisit: "1 week ago", condition: "Follow-up" },
  { id: "3", name: "Robert Brown", lastVisit: "2 weeks ago", condition: "Treatment" },
];

export default function DashboardPage() {
  const { user } = useAuthStore();
  const isDoctor = user?.role === "doctor";
  const doctorStats = mockStats.doctor;
  const patientStats = mockStats.patient;

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back, {user?.first_name || "User"}!
          </h1>
          <p className="text-muted-foreground">
            {isDoctor 
              ? "Here's what's happening with your practice today."
              : "Here's an overview of your healthcare activities."
            }
          </p>
        </div>
        <div className="flex gap-2">
          {isDoctor ? (
            <Link href="/dashboard/queue">
              <Button>
                <Activity className="h-4 w-4 mr-2" />
                Live Queue
              </Button>
            </Link>
          ) : (
            <Link href="/dashboard/appointments/new">
              <Button>
                <Calendar className="h-4 w-4 mr-2" />
                Book Appointment
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      {isDoctor ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Today&apos;s Appointments</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{doctorStats.todayAppointments}</div>
              <p className="text-xs text-muted-foreground">
                +2 from yesterday
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{doctorStats.pendingAppointments}</div>
              <p className="text-xs text-muted-foreground">
                Awaiting confirmation
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{doctorStats.completedToday}</div>
              <p className="text-xs text-muted-foreground">
                Today&apos;s consultations
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{doctorStats.totalPatients}</div>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-500" />
                +12 this month
              </p>
            </CardContent>
          </Card>
          <Card className="bg-primary text-primary-foreground">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Waiting Queue</CardTitle>
              <Activity className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{doctorStats.waitingQueue}</div>
              <p className="text-xs opacity-80">
                Patients waiting
              </p>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Upcoming</CardTitle>
              <Calendar className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{patientStats.upcomingAppointments}</div>
              <p className="text-xs text-muted-foreground">
                Scheduled appointments
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Completed Visits</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{patientStats.completedVisits}</div>
              <p className="text-xs text-muted-foreground">
                Total consultations
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Prescriptions</CardTitle>
              <Activity className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{patientStats.activePrescriptions}</div>
              <p className="text-xs text-muted-foreground">
                Current medications
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Pending Reports</CardTitle>
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{patientStats.pendingReports}</div>
              <p className="text-xs text-muted-foreground">
                Awaiting results
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upcoming Appointments */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Upcoming Appointments</CardTitle>
              <CardDescription>
                {isDoctor ? "Today's schedule" : "Your scheduled visits"}
              </CardDescription>
            </div>
            <Link href="/dashboard/appointments">
              <Button variant="ghost" size="sm">
                View All <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockUpcomingAppointments.map((appointment) => (
                <div
                  key={appointment.id}
                  className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Calendar className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">
                        {isDoctor ? appointment.patientName : appointment.doctorName}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {appointment.time} · {appointment.type}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={appointment.status === "confirmed" ? "success" : "secondary"}
                  >
                    {appointment.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Patients (Doctor) or Health Summary (Patient) */}
        {isDoctor ? (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Recent Patients</CardTitle>
                <CardDescription>Latest patient interactions</CardDescription>
              </div>
              <Link href="/dashboard/patients">
                <Button variant="ghost" size="sm">
                  View All <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockRecentPatients.map((patient) => (
                  <div
                    key={patient.id}
                    className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Users className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{patient.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {patient.lastVisit} · {patient.condition}
                        </p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Health Summary</CardTitle>
              <CardDescription>Your latest health information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-medium text-green-800">Allergies</h4>
                  <p className="text-sm text-green-600">Penicillin, Peanuts</p>
                </div>
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-medium text-blue-800">Current Medications</h4>
                  <p className="text-sm text-blue-600">Metformin 500mg, Lisinopril 10mg</p>
                </div>
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h4 className="font-medium text-yellow-800">Upcoming</h4>
                  <p className="text-sm text-yellow-600">Blood work due in 2 weeks</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
