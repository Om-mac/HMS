import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Healthcare Management System",
  description: "A high-security, automated Healthcare Management System specializing in seamless appointment logistics, bidirectional WhatsApp communication, and inter-hospital patient data portability.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: "#363636",
                color: "#fff",
              },
              success: {
                duration: 3000,
                style: {
                  background: "#22c55e",
                },
              },
              error: {
                duration: 5000,
                style: {
                  background: "#ef4444",
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}
