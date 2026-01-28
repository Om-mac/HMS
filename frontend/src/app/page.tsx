import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Calendar, 
  Users, 
  FileText, 
  Shield, 
  MessageSquare, 
  ArrowRight,
  Activity,
  Building2
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold text-primary">HMS</span>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="#features" className="text-sm text-muted-foreground hover:text-foreground">
              Features
            </Link>
            <Link href="#security" className="text-sm text-muted-foreground hover:text-foreground">
              Security
            </Link>
            <Link href="#contact" className="text-sm text-muted-foreground hover:text-foreground">
              Contact
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
          Healthcare Management
          <span className="text-primary"> Reimagined</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
          A high-security, automated Healthcare Management System with seamless 
          appointment logistics, bidirectional WhatsApp communication, and 
          inter-hospital patient data portability.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register">
            <Button size="lg" className="gap-2">
              Start Free Trial <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="#features">
            <Button size="lg" variant="outline">
              Learn More
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader>
              <Calendar className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Smart Appointments</CardTitle>
              <CardDescription>
                Automated scheduling with WhatsApp notifications and waitlist management
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <MessageSquare className="h-10 w-10 text-green-600 mb-2" />
              <CardTitle>WhatsApp Integration</CardTitle>
              <CardDescription>
                Bidirectional communication for confirmations, reminders, and rescheduling
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <FileText className="h-10 w-10 text-purple-600 mb-2" />
              <CardTitle>Universal Patient Vault</CardTitle>
              <CardDescription>
                Complete EMR with QR-ID, dental odontogram, and multimedia history
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Building2 className="h-10 w-10 text-orange-600 mb-2" />
              <CardTitle>Federated Transfer</CardTitle>
              <CardDescription>
                Secure patient data portability between hospitals with permission-based access
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* Security Section */}
      <section id="security" className="bg-primary/5 py-20">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center gap-12">
            <div className="flex-1">
              <Shield className="h-16 w-16 text-primary mb-6" />
              <h2 className="text-3xl font-bold mb-4">HIPAA Compliant Security</h2>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-primary rounded-full" />
                  AES-256 encryption for all sensitive data
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-primary rounded-full" />
                  Signed S3 URLs with 10-minute expiry
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-primary rounded-full" />
                  Comprehensive audit logging
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-primary rounded-full" />
                  Role-based access control
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-primary rounded-full" />
                  JWT authentication with refresh tokens
                </li>
              </ul>
            </div>
            <div className="flex-1">
              <Card className="p-8">
                <CardHeader>
                  <Users className="h-10 w-10 text-primary mb-2" />
                  <CardTitle>Doctor&apos;s Command Center</CardTitle>
                  <CardDescription>
                    Real-time dashboard with live queue management, ambient scribing, 
                    and image annotation for X-rays
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/dashboard">
                    <Button className="w-full">Access Dashboard</Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Activity className="h-6 w-6 text-primary" />
              <span className="font-bold text-primary">HMS</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Healthcare Management System. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
