import { ChatLayout } from "@/components/chat/ChatLayout";
import { ThreatCard } from "@/components/chat/ThreatCard";


export default function Home() {
  return (
    <ChatLayout>
      {/* Welcome Message */}
      <div className="brutal-box p-6 md:p-8 max-w-3xl mx-auto shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]">
        <h1 className="text-3xl md:text-5xl font-bold mb-4 uppercase tracking-tighter flex items-center gap-3">
          <span className="bg-brand-primary text-black px-2 py-1">SYS</span>
          Siap Analisa.
        </h1>
        <p className="text-lg md:text-xl font-mono text-gray-700 dark:text-gray-300 mb-6">
          Sistem deteksi ancaman cyber. Upload file APK atau masukkan URL mencurigakan.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border-2 border-black dark:border-white p-4 hover:bg-gray-100 dark:hover:bg-[#222] transition-colors cursor-pointer group md:[&:nth-child(odd):last-child]:col-span-2">
            <div className="font-bold text-lg mb-1 group-hover:text-brand-primary transition-colors">📱 Cek APK</div>
            <div className="text-sm font-mono text-gray-500">Analisa malware, pencurian OTP, dan izin akses.</div>
          </div>
          <div className="border-2 border-black dark:border-white p-4 hover:bg-gray-100 dark:hover:bg-[#222] transition-colors cursor-pointer group md:[&:nth-child(odd):last-child]:col-span-2">
            <div className="font-bold text-lg mb-1 group-hover:text-brand-primary transition-colors">🔗 Cek Link</div>
            <div className="text-sm font-mono text-gray-500">Deteksi web phishing dan penipuan online.</div>
          </div>
          <div className="border-2 border-black dark:border-white p-4 hover:bg-gray-100 dark:hover:bg-[#222] transition-colors cursor-pointer group md:[&:nth-child(odd):last-child]:col-span-2">
            <div className="font-bold text-lg mb-1 group-hover:text-brand-primary transition-colors">🔎 Analisa File</div>
            <div className="text-sm font-mono text-gray-500">Analisa mendalam file PDF atau dokumen mencurigakan lainnya.</div>
          </div>
        </div>
      </div>

      {/* Mock Threat Card Demonstration */}
      <div className="max-w-4xl mx-auto mt-12 opacity-50 hover:opacity-100 transition-opacity">
        <div className="text-xs font-mono mb-2">PREVIEW: HASIL ANALISA</div>
        <ThreatCard
          data={{
            status: "BERBAHAYA",
            target: "Undangan_Pernikahan_Digital.apk",
            type: "APK",
            analysis_report: "[ANALISA OTOMATIS]\nAplikasi ini meminta izin untuk membaca dan menerima SMS (READ_SMS, RECEIVE_SMS) serta mengakses internet secara bersamaan. Ini adalah indikasi kuat pencurian kode OTP.\n\nTindakan: DILARANG INSTALL."
          }}
        />
      </div>
    </ChatLayout>
  );
}
