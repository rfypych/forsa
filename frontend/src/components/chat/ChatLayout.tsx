"use client";

import { useState, useEffect } from "react";
import { Menu, Plus, X, Search, Moon, Sun, Upload, Send } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

export function ChatLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true); // Default to dark as requested

  useEffect(() => {
    // Apply dark mode initially
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  return (
    <div className="flex h-screen overflow-hidden bg-bg-light dark:bg-bg-dark text-text-light dark:text-text-dark font-sans selection:bg-brand-primary selection:text-black">
      {/* Mobile Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-sm"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={{ x: "-100%" }}
        animate={{ x: sidebarOpen ? 0 : "-100%" }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className={cn(
          "fixed md:static inset-y-0 left-0 z-50 w-72 bg-white dark:bg-[#111] border-r-[3px] border-black dark:border-white flex flex-col md:translate-x-0 transition-transform duration-300",
          "md:!transform-none" // Override framer-motion on desktop
        )}
      >
        <div className="p-4 border-b-[3px] border-black dark:border-white flex items-center justify-between bg-brand-primary dark:bg-brand-primary text-black">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-black flex items-center justify-center">
              <div className="w-3 h-3 border-2 border-brand-primary"></div>
            </div>
            <h1 className="font-mono font-bold text-xl tracking-tighter">FORSA_</h1>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="md:hidden">
            <X className="hover:scale-110 transition-transform" />
          </button>
        </div>

        <div className="p-4">
          <button className="w-full brutal-button flex items-center justify-center gap-2 bg-[#f0f0f0] dark:bg-[#222] hover:bg-brand-primary dark:hover:bg-brand-primary hover:text-black transition-colors">
            <Plus size={18} />
            <span>ANALISA BARU</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <div className="text-xs font-mono text-gray-500 mb-2">RIWAYAT (MOCK)</div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-3 border-2 border-black dark:border-white hover:bg-gray-100 dark:hover:bg-[#222] cursor-pointer transition-colors group relative">
              <div className="font-bold text-sm truncate group-hover:text-brand-primary transition-colors">
                Analisa_APK_{i}.apk
              </div>
              <div className="text-xs text-gray-500 mt-1 font-mono">12:3{i} PM</div>
              {/* Decor */}
              <div className="absolute top-0 right-0 w-2 h-2 bg-black dark:bg-white hidden group-hover:block" />
            </div>
          ))}
        </div>

        <div className="p-4 border-t-[3px] border-black dark:border-white flex justify-between items-center bg-gray-50 dark:bg-[#151515]">
          <div className="text-xs font-mono flex flex-col">
            <span>SYS: ONLINE</span>
            <span className="text-brand-primary">V 1.0.0</span>
          </div>
          <button onClick={toggleTheme} className="p-2 brutal-border bg-white dark:bg-black hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors">
            {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Mobile Header */}
        <header className="md:hidden p-4 border-b-[3px] border-black dark:border-white flex items-center gap-3 bg-white dark:bg-[#111] z-10">
          <button onClick={() => setSidebarOpen(true)} className="p-1">
            <Menu />
          </button>
          <div className="font-mono font-bold">FORSA_TERMINAL</div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 pb-32">
          {children}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-bg-light dark:from-bg-dark via-bg-light/90 dark:via-bg-dark/90 to-transparent">
          <div className="max-w-4xl mx-auto flex gap-2">
            <button className="brutal-button !px-3 bg-white dark:bg-[#222] flex-shrink-0" title="Upload File">
              <Upload size={20} />
            </button>
            <div className="relative flex-1 group">
              <input
                type="text"
                placeholder="Masukkan URL, teks, atau drop file APK..."
                className="w-full brutal-input bg-white dark:bg-[#222]"
              />
              <div className="absolute right-0 top-0 bottom-0 w-3 bg-black dark:bg-white hidden group-focus-within:block" />
            </div>
            <button className="brutal-button !px-4 bg-brand-primary text-black flex-shrink-0 flex items-center gap-2">
              <span className="hidden sm:inline">KIRIM</span>
              <Send size={18} />
            </button>
          </div>
          <div className="text-center mt-2 text-[10px] font-mono text-gray-500">
            For Internal Police Use Only • Confidential Data Processing
          </div>
        </div>
      </main>
    </div>
  );
}
