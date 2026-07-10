import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EMOS – Enterprise Memory OS",
  description: "Turn your meetings into permanent organizational memory.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-gray-50">
          {/* Navigation Bar */}
          <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-blue-600">EMOS</span>
              <span className="text-sm text-gray-500 hidden sm:inline-block">
                Enterprise Memory OS
              </span>
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <a href="/dashboard" className="text-gray-600 hover:text-blue-600 transition">
                Dashboard
              </a>
              <a href="/workspace" className="text-gray-600 hover:text-blue-600 transition">
                Workspace
              </a>
              <a href="/chat" className="text-gray-600 hover:text-blue-600 transition">
                AI Chat
              </a>
            </div>
          </nav>

          {/* Page Content */}
          <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}