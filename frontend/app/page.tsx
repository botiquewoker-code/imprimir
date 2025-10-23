"use client";
import Sidebar from "../components/Sidebar";
import { motion } from "framer-motion";
import { Upload, FileText, Download } from "lucide-react";
import { useDropzone } from "react-dropzone";
import { useState, useEffect } from "react";
import { PDFDocument } from "pdf-lib";
import { saveAs } from "file-saver"

let pdfjsLib: any = null;

type Mode = "compress" | "jpg" | "docx";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [outputUrl, setOutputUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<Mode>("compress");

  // ✅ Cargar pdfjs-dist solo en el cliente (evita errores en Next.js 14)
  useEffect(() => {
    (async () => {
      if (typeof window !== "undefined") {
        const pdfjsModule = await import("pdfjs-dist/build/pdf");
        pdfjsModule.GlobalWorkerOptions.workerSrc =
          "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js";
        pdfjsLib = pdfjsModule;
      }
    })();
  }, []);

  const onDrop = (acceptedFiles: File[]) => {
    setFile(acceptedFiles[0]);
    setOutputUrl(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
  });

  // 🧩 COMPRESIÓN PDF
  const compressPDF = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdfDoc = await PDFDocument.load(arrayBuffer);
      const compressed = await pdfDoc.save({ useObjectStreams: true });
      const blob = new Blob([compressed], { type: "application/pdf" });
      setOutputUrl(URL.createObjectURL(blob));
    } finally {
      setLoading(false);
    }
  };

  // 🖼️ CONVERTIR PDF → JPG
  const convertToJPG = async () => {
    if (!file || !pdfjsLib) return;
    setLoading(true);
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      const page = await pdf.getPage(1);
      const viewport = page.getViewport({ scale: 2 });
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d")!;
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      await page.render({ canvasContext: ctx, viewport }).promise;

      canvas.toBlob((blob) => {
        if (blob) {
          saveAs(blob, "converted_page.jpg");
          setOutputUrl(URL.createObjectURL(blob));
        }
      }, "image/jpeg");
    } finally {
      setLoading(false);
    }
  };

  // 📝 CONVERTIR PDF → DOCX (simulado)
  const convertToDocx = async () => {
    if (!file) return;
    setLoading(true);
    setTimeout(() => {
      const blob = new Blob(["Archivo convertido a Word"], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      saveAs(blob, "converted.docx");
      setOutputUrl(URL.createObjectURL(blob));
      setLoading(false);
    }, 1500);
  };

  const handleProcess = () => {
    if (mode === "compress") compressPDF();
    if (mode === "jpg") convertToJPG();
    if (mode === "docx") convertToDocx();
  };

  return (
    <main className="animated-bg min-h-screen flex flex-col items-center justify-center text-gray-800">
      {/* ENCABEZADO */}
      <motion.header
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center py-10"
      >
        <h1 className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-green-500 via-blue-500 to-orange-400 drop-shadow-lg">
          PrintPDF PRO
        </h1>
        <p className="mt-3 text-gray-600 text-lg">
          Convierte y comprime tus archivos en segundos ⚡
        </p>
      </motion.header>

      {/* PESTAÑAS */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setMode("compress")}
          className={`btn ${mode === "compress" ? "opacity-100" : "opacity-50"}`}
        >
          Comprimir PDF
        </button>
        <button
          onClick={() => setMode("jpg")}
          className={`btn from-blue-500 to-cyan-400 ${
            mode === "jpg" ? "opacity-100" : "opacity-50"
          }`}
        >
          PDF a JPG
        </button>
        <button
          onClick={() => setMode("docx")}
          className={`btn from-amber-500 to-orange-400 ${
            mode === "docx" ? "opacity-100" : "opacity-50"
          }`}
        >
          PDF a Word
        </button>
      </div>

      {/* ZONA DE SUBIDA */}
      <motion.div
        {...getRootProps()}
        className={`card w-96 text-center cursor-pointer shadow-smooth transition-smooth ${
          isDragActive ? "border-green-400 bg-green-50" : ""
        }`}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.98 }}
      >
        <input {...getInputProps()} />
        {file ? (
          <div>
            <FileText className="mx-auto text-green-500" size={48} />
            <p className="mt-3 font-medium">{file.name}</p>
          </div>
        ) : (
          <div>
            <Upload className="mx-auto text-gray-500" size={48} />
            <p className="mt-3 text-gray-700">
              Arrastra tu PDF aquí o haz clic para seleccionarlo
            </p>
          </div>
        )}
      </motion.div>

      {/* BOTÓN PRINCIPAL */}
      {file && !outputUrl && (
        <motion.button
          className="btn mt-8 float"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleProcess}
          disabled={loading}
        >
          {loading ? "Procesando..." : "Procesar archivo"}
        </motion.button>
      )}

      {/* DESCARGA */}
      {outputUrl && (
        <motion.a
          href={outputUrl}
          download={`resultado_${file?.name}`}
          className="btn mt-8 float bg-gradient-to-r from-lime-500 to-emerald-400"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Download className="inline-block mr-2" size={20} />
          Descargar resultado
        </motion.a>
      )}

      <footer className="mt-10 text-sm text-gray-600">
        © {new Date().getFullYear()} PrintPDF PRO — Inteligente, fluido y rápido 💫
      </footer>
    </main>
  );
}
