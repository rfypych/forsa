import type { Metadata } from "next";
import { Inter, Space_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const spaceMono = Space_Mono({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-space-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FORSA - Forensic Search & Analysis",
  description: "Asisten Keamanan Siber Resmi Polri",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="id"
      className={`${inter.variable} ${spaceMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-bg-light dark:bg-bg-dark text-text-light dark:text-text-dark font-sans transition-colors duration-300">
        {children}
      </body>
    </html>
  );
}
