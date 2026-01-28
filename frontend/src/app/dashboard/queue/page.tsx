"use client";

import { useState, useEffect } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Users,
  Clock,
  CheckCircle,
  ArrowRight,
  Bell,
  SkipForward,
  Play,
  RefreshCw
} from "lucide-react";
import { getInitials, getStatusColor, formatTime } from "@/lib/utils";

// Mock queue data
const mockQueueItems = [
  {
    id: "1",
    position: 1,
    patient: { user: { full_name: "Sarah Johnson" }, patient_id: "HMS-ABC123" },
    appointment: {
      start_time: "09:00",
      appointment_type: "consultation",
    },
    status: "in_consultation",
    estimated_wait_time: 0,
    check_in_time: "08:45",
    called_at: "09:02",
  },
  {
    id: "2",
    position: 2,
    patient: { user: { full_name: "Michael Chen" }, patient_id: "HMS-DEF456" },
    appointment: {
      start_time: "09:30",
      appointment_type: "follow_up",
    },
    status: "waiting",
    estimated_wait_time: 15,
    check_in_time: "09:20",
    called_at: null,
  },
  {
    id: "3",
    position: 3,
    patient: { user: { full_name: "Emily Davis" }, patient_id: "HMS-GHI789" },
    appointment: {
      start_time: "10:00",
      appointment_type: "procedure",
    },
    status: "waiting",
    estimated_wait_time: 35,
    check_in_time: "09:45",
    called_at: null,
  },
  {
    id: "4",
    position: 4,
    patient: { user: { full_name: "Robert Brown" }, patient_id: "HMS-JKL012" },
    appointment: {
      start_time: "10:30",
      appointment_type: "consultation",
    },
    status: "waiting",
    estimated_wait_time: 55,
    check_in_time: "10:15",
    called_at: null,
  },
];

export default function LiveQueuePage() {
  const { user } = useAuthStore();
  const [queue, setQueue] = useState(mockQueueItems);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const currentPatient = queue.find((item) => item.status === "in_consultation");
  const waitingPatients = queue.filter((item) => item.status === "waiting");

  const handleCallNext = () => {
    setQueue((prev) => {
      const updated = [...prev];
      // Mark current as completed
      const currentIndex = updated.findIndex((item) => item.status === "in_consultation");
      if (currentIndex !== -1) {
        updated[currentIndex].status = "completed";
      }
      // Call next waiting patient
      const nextIndex = updated.findIndex((item) => item.status === "waiting");
      if (nextIndex !== -1) {
        updated[nextIndex].status = "called";
        updated[nextIndex].called_at = new Date().toISOString();
      }
      return updated;
    });
  };

  const handleStartConsultation = (id: string) => {
    setQueue((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, status: "in_consultation" } : item
      )
    );
  };

  const handleSkipPatient = (id: string) => {
    setQueue((prev) => {
      const updated = prev.map((item) =>
        item.id === id ? { ...item, status: "skipped" } : item
      );
      // Reorder positions
      return updated;
    });
  };

  const handleNotifyPatient = (id: string) => {
    // In real app, this would send a WhatsApp notification
    console.log("Notifying patient:", id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Live Queue</h1>
          <p className="text-muted-foreground">
            Real-time patient queue management
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Current Time</p>
            <p className="text-2xl font-bold">
              {currentTime.toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          </div>
          <Button variant="outline" size="icon">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">In Queue</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{waitingPatients.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Wait Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">~20 min</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {queue.filter((item) => item.status === "completed").length}
            </div>
          </CardContent>
        </Card>
        <Card className="bg-primary text-primary-foreground">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Skipped</CardTitle>
            <SkipForward className="h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {queue.filter((item) => item.status === "skipped").length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Current Patient */}
      {currentPatient && (
        <Card className="border-primary border-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-primary">Currently Consulting</CardTitle>
                <CardDescription>In progress</CardDescription>
              </div>
              <Badge className="bg-green-100 text-green-800 animate-pulse">
                <span className="mr-1 h-2 w-2 rounded-full bg-green-500 inline-block" />
                Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Avatar className="h-16 w-16">
                  <AvatarFallback className="text-lg">
                    {getInitials(currentPatient.patient.user.full_name)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-xl font-semibold">
                    {currentPatient.patient.user.full_name}
                  </h3>
                  <p className="text-muted-foreground">
                    {currentPatient.patient.patient_id} · {currentPatient.appointment.appointment_type}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Scheduled: {formatTime(currentPatient.appointment.start_time)}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline">View EMR</Button>
                <Button onClick={handleCallNext}>
                  Complete & Call Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Waiting Queue */}
      <Card>
        <CardHeader>
          <CardTitle>Waiting Queue</CardTitle>
          <CardDescription>
            {waitingPatients.length} patients waiting
          </CardDescription>
        </CardHeader>
        <CardContent>
          {waitingPatients.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No patients currently waiting</p>
            </div>
          ) : (
            <div className="space-y-4">
              {waitingPatients.map((item, index) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 bg-muted/50 rounded-lg"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary">
                      {index + 1}
                    </div>
                    <Avatar>
                      <AvatarFallback>
                        {getInitials(item.patient.user.full_name)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h4 className="font-medium">{item.patient.user.full_name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {item.patient.patient_id} · {item.appointment.appointment_type}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Scheduled: {formatTime(item.appointment.start_time)} · Check-in: {item.check_in_time}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">Est. Wait</p>
                      <p className="text-lg font-bold text-primary">
                        ~{item.estimated_wait_time} min
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => handleNotifyPatient(item.id)}
                        title="Send WhatsApp Notification"
                      >
                        <Bell className="h-4 w-4" />
                      </Button>
                      {index === 0 && !currentPatient && (
                        <Button
                          size="sm"
                          onClick={() => handleStartConsultation(item.id)}
                        >
                          <Play className="h-4 w-4 mr-1" />
                          Start
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => handleSkipPatient(item.id)}
                        title="Skip Patient"
                      >
                        <SkipForward className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
