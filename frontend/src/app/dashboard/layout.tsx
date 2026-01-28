"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/stores/auth-store";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Activity,
  LayoutDashboard, 
  Calendar, 
  Users, 
  FileText, 
  Settings, 
  LogOut,
  Bell,
  Menu,
  X,
  Stethoscope,
  Building2,
  ClipboardList,
  Share2
} from "lucide-react";
import { useState } from "react";
import { getInitials } from "@/lib/utils";

const navigation = {
  doctor: [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Appointments", href: "/dashboard/appointments", icon: Calendar },
    { name: "Patients", href: "/dashboard/patients", icon: Users },
    { name: "EMR", href: "/dashboard/emr", icon: FileText },
    { name: "Live Queue", href: "/dashboard/queue", icon: ClipboardList },
    { name: "Transfers", href: "/dashboard/transfers", icon: Share2 },
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
  ],
  patient: [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Appointments", href: "/dashboard/appointments", icon: Calendar },
    { name: "My Records", href: "/dashboard/records", icon: FileText },
    { name: "Find Doctors", href: "/dashboard/doctors", icon: Stethoscope },
    { name: "Clinics", href: "/dashboard/clinics", icon: Building2 },
    { name: "Transfers", href: "/dashboard/transfers", icon: Share2 },
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
  ],
  admin: [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Users", href: "/dashboard/users", icon: Users },
    { name: "Clinics", href: "/dashboard/clinics", icon: Building2 },
    { name: "Doctors", href: "/dashboard/doctors", icon: Stethoscope },
    { name: "Reports", href: "/dashboard/reports", icon: FileText },
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
  ],
  staff: [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Appointments", href: "/dashboard/appointments", icon: Calendar },
    { name: "Patients", href: "/dashboard/patients", icon: Users },
    { name: "Live Queue", href: "/dashboard/queue", icon: ClipboardList },
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
  ],
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, logout, fetchUser, isLoading } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      fetchUser().catch(() => {
        router.push("/login");
      });
    }
  }, [isAuthenticated, fetchUser, router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const userNavigation = navigation[user.role] || navigation.patient;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div
        className={cn(
          "fixed inset-0 z-50 bg-black/50 lg:hidden",
          sidebarOpen ? "block" : "hidden"
        )}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-white border-r transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:inset-auto",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-4 py-5 border-b">
            <Link href="/dashboard" className="flex items-center gap-2">
              <Activity className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold text-primary">HMS</span>
            </Link>
            <button
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {userNavigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t">
            <div className="flex items-center gap-3 mb-4">
              <Avatar>
                <AvatarImage src="" />
                <AvatarFallback>{getInitials(user.full_name || user.email)}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user.full_name}</p>
                <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
              </div>
            </div>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-40 bg-white border-b">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="flex-1" />

            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" />
              </Button>
              <Avatar className="h-8 w-8">
                <AvatarImage src="" />
                <AvatarFallback className="text-xs">
                  {getInitials(user.full_name || user.email)}
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
