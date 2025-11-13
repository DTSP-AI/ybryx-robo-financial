'use client';

import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-neutral-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">Y</span>
            </div>
            <span className="text-xl font-bold text-black">Ybryx Capital</span>
          </Link>

          <div className="hidden md:flex items-center space-x-8">
            <Link href="/robots" className="text-neutral-700 hover:text-black transition-colors font-medium">
              Equipment
            </Link>
            <Link href="/industries" className="text-neutral-700 hover:text-black transition-colors font-medium">
              Industries
            </Link>
            <Link href="/dealers" className="text-neutral-700 hover:text-black transition-colors font-medium">
              Dealers
            </Link>
            <Link href="/prequalify">
              <Button className="bg-black hover:bg-neutral-800">
                Get Prequalified
              </Button>
            </Link>
          </div>

          <button
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-neutral-200">
            <div className="flex flex-col space-y-4">
              <Link
                href="/robots"
                className="text-neutral-700 hover:text-black transition-colors font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                Equipment
              </Link>
              <Link
                href="/industries"
                className="text-neutral-700 hover:text-black transition-colors font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                Industries
              </Link>
              <Link
                href="/dealers"
                className="text-neutral-700 hover:text-black transition-colors font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                Dealers
              </Link>
              <Link href="/prequalify" onClick={() => setMobileMenuOpen(false)}>
                <Button className="w-full bg-black hover:bg-neutral-800">
                  Get Prequalified
                </Button>
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
