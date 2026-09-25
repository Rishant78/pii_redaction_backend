import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Header } from '../components/Header';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'PII Redaction Tool',
  description: 'Enterprise Document Protection',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-white antialiased text-zinc-950">
      <body className={`${inter.className} min-h-screen flex flex-col relative`}>
        {/* Subtle top gradient bar for premium feel */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-zinc-200 via-zinc-400 to-zinc-200" />
        
        <Header />
        
        <div className="flex-1 flex flex-col relative z-10">
          {children}
        </div>

        <footer className="w-full border-t border-zinc-200 bg-white/50 backdrop-blur-sm mt-auto z-10">
          <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between text-xs text-zinc-500 font-medium">
            <p>PII Redaction Tool</p>
            <p>Documents are processed locally by the configured redaction service.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
