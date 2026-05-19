import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "FindMe RS",
  description: "Personalised product recommendations powered by hybrid ML",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-200 py-6 mt-12 text-center text-sm text-gray-500">
          FindMe RS &middot; hybrid recommendation engine
        </footer>
      </body>
    </html>
  );
}
