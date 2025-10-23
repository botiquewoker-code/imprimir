"use client";

import { motion } from "framer-motion";
import { Home, FileText, Settings, UploadCloud, HelpCircle } from "lucide-react";

const menuItems = [
  { name: "Inicio", icon: Home },
  { name: "Mis Archivos", icon: FileText },
  { name: "Subir", icon: UploadCloud },
  { name: "Ajustes", icon: Settings },
  { name: "Ayuda", icon: HelpCircle },
];

export default function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -120, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed left-0 top-0 h-screen w-20 md:w-56 
                 bg-white/60 backdrop-blur-xl border-r border-white/30 
                 shadow-lg flex flex-col items-center md:items-start 
                 py-6 px-3 md:px-6 z-20"
    >
      {/* Logo */}
      <motion.h1
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-extrabold text-xl text-transparent bg-clip-text 
                   bg-gradient-to-r from-green-500 via-blue-500 to-orange-400 
                   mb-10 md:ml-2"
      >
        PrintPDF
      </motion.h1>

      {/* Menú */}
      <nav className="flex flex-col gap-6 w-full">
        {menuItems.map(({ name, icon: Icon }) => (
          <motion.button
            key={name}
            whileHover={{ scale: 1.1, x: 5 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-3 text-gray-700 font-medium 
                       hover:text-blue-600 transition-colors"
          >
            <Icon className="text-green-500 md:text-blue-500" size={24} />
            <span className="hidden md:block">{name}</span>
          </motion.button>
        ))}
      </nav>

      {/* Footer */}
      <div className="mt-auto text-xs text-gray-500 md:ml-1">
        © {new Date().getFullYear()} PrintPDF
      </div>
    </motion.aside>
  );
}
