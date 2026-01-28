"use client";

import { useState, useEffect } from "react";
import { useAppointmentStore } from "@/stores/appointment-store";
import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Calendar, 
  Clock, 
  User,
  MapPin,
  Plus,
  Search,
  Filter,
  MoreVertical,
  CheckCircle,
  XCircle,
  RefreshCw
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { formatDate, formatTime, getStatusColor } from "@/lib/utils";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// Mock appointments for demonstration
const mockAppointments = [
  {
    id: "1",
    appointment_number: "APT-001",
    patient: { user: { full_name: "Sarah Johnson" }, patient_id: "HMS-ABC123" },
    doctor: { user: { full_name: "Dr. John Smith" }, specialization: { name: "General Medicine" } },
    clinic: { name: "City Medical Center", address: "123 Health St" },
    appointment_date: "2024-12-20",
    start_time: "09:00",
    end_time: "09:30",
    status: "confirmed",
    appointment_type: "consultation",
    reason: "Regular checkup",
  },
  {
    id: "2",
    appointment_number: "APT-002",
    patient: { user: { full_name: "Michael Chen" }, patient_id: "HMS-DEF456" },
    doctor: { user: { full_name: "Dr. John Smith" }, specialization: { name: "General Medicine" } },
    clinic: { name: "City Medical Center", address: "123 Health St" },
    appointment_date: "2024-12-20",
    start_time: "10:30",
    end_time: "11:00",
    status: "scheduled",
    appointment_type: "follow_up",
    reason: "Post-surgery follow-up",
  },
  {
    id: "3",
    appointment_number: "APT-003",
    patient: { user: { full_name: "Emily Davis" }, patient_id: "HMS-GHI789" },
    doctor: { user: { full_name: "Dr. John Smith" }, specialization: { name: "General Medicine" } },
    clinic: { name: "City Medical Center", address: "123 Health St" },
    appointment_date: "2024-12-21",
    start_time: "14:00",
    end_time: "14:30",
    status: "checked_in",
    appointment_type: "procedure",
    reason: "Blood test",
  },
  {
    id: "4",
    appointment_number: "APT-004",
    patient: { user: { full_name: "Robert Brown" }, patient_id: "HMS-JKL012" },
    doctor: { user: { full_name: "Dr. John Smith" }, specialization: { name: "General Medicine" } },
    clinic: { name: "City Medical Center", address: "123 Health St" },
    appointment_date: "2024-12-19",
    start_time: "11:00",
    end_time: "11:30",
    status: "completed",
    appointment_type: "consultation",
    reason: "Headache and fever",
  },
];

export default function AppointmentsPage() {
  const { user } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTab, setSelectedTab] = useState("upcoming");
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<any>(null);

  const isDoctor = user?.role === "doctor";

  const filteredAppointments = mockAppointments.filter((apt) => {
    const matchesSearch =
      apt.patient.user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      apt.appointment_number.toLowerCase().includes(searchQuery.toLowerCase());

    if (selectedTab === "upcoming") {
      return matchesSearch && ["scheduled", "confirmed", "checked_in"].includes(apt.status);
    } else if (selectedTab === "completed") {
      return matchesSearch && apt.status === "completed";
    } else if (selectedTab === "cancelled") {
      return matchesSearch && ["cancelled", "no_show"].includes(apt.status);
    }
    return matchesSearch;
  });

  const handleCancelAppointment = () => {
    // In real app, call API to cancel
    console.log("Cancelling appointment:", selectedAppointment?.id);
    setCancelDialogOpen(false);
    setSelectedAppointment(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Appointments</h1>
          <p className="text-muted-foreground">
            {isDoctor ? "Manage your patient appointments" : "View and manage your appointments"}
          </p>
        </div>
        <Link href="/dashboard/appointments/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            {isDoctor ? "Schedule Appointment" : "Book Appointment"}
          </Button>
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by patient name or appointment number..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="cancelled">Cancelled</TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedTab} className="mt-6">
          {filteredAppointments.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No appointments found</h3>
                <p className="text-muted-foreground">
                  {selectedTab === "upcoming"
                    ? "You don't have any upcoming appointments."
                    : "No appointments match your search."}
                </p>
                <Link href="/dashboard/appointments/new" className="mt-4">
                  <Button>Book an Appointment</Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {filteredAppointments.map((appointment) => (
                <Card key={appointment.id}>
                  <CardContent className="p-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                          <Calendar className="h-6 w-6 text-primary" />
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">
                              {isDoctor
                                ? appointment.patient.user.full_name
                                : appointment.doctor.user.full_name}
                            </h3>
                            <Badge className={getStatusColor(appointment.status)}>
                              {appointment.status.replace("_", " ")}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {appointment.appointment_number} · {appointment.appointment_type.replace("_", " ")}
                          </p>
                          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {formatDate(appointment.appointment_date)}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
                            </span>
                            <span className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              {appointment.clinic.name}
                            </span>
                          </div>
                          {appointment.reason && (
                            <p className="text-sm mt-2">
                              <span className="font-medium">Reason:</span> {appointment.reason}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {["scheduled", "confirmed"].includes(appointment.status) && (
                          <>
                            {isDoctor && (
                              <Button variant="outline" size="sm">
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Check In
                              </Button>
                            )}
                            <Button variant="outline" size="sm">
                              <RefreshCw className="h-4 w-4 mr-1" />
                              Reschedule
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-red-500 hover:text-red-600"
                              onClick={() => {
                                setSelectedAppointment(appointment);
                                setCancelDialogOpen(true);
                              }}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Cancel
                            </Button>
                          </>
                        )}
                        {appointment.status === "checked_in" && isDoctor && (
                          <Button size="sm">
                            Start Consultation
                          </Button>
                        )}
                        <Link href={`/dashboard/appointments/${appointment.id}`}>
                          <Button variant="ghost" size="sm">
                            View Details
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Cancel Dialog */}
      <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Appointment</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel this appointment? This action cannot be undone.
              The {isDoctor ? "patient" : "doctor"} will be notified via WhatsApp.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelDialogOpen(false)}>
              Keep Appointment
            </Button>
            <Button variant="destructive" onClick={handleCancelAppointment}>
              Cancel Appointment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
