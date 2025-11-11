import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-neutral-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-xl">B</span>
              </div>
              <span className="text-xl font-bold">Bolt.new</span>
            </div>
            <p className="text-neutral-400 text-sm">
              Unlock access to warehouse robots without upfront capital. Lease cutting-edge automation equipment and scale your operations.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Equipment</h3>
            <ul className="space-y-2 text-sm text-neutral-400">
              <li><Link href="/robots?category=amr" className="hover:text-white transition-colors">AMRs</Link></li>
              <li><Link href="/robots?category=drones" className="hover:text-white transition-colors">Drones</Link></li>
              <li><Link href="/robots?category=arms" className="hover:text-white transition-colors">Robotic Arms</Link></li>
              <li><Link href="/robots?category=agv" className="hover:text-white transition-colors">AGVs</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Industries</h3>
            <ul className="space-y-2 text-sm text-neutral-400">
              <li><Link href="/industries?sector=logistics" className="hover:text-white transition-colors">Logistics</Link></li>
              <li><Link href="/industries?sector=agriculture" className="hover:text-white transition-colors">Agriculture</Link></li>
              <li><Link href="/industries?sector=manufacturing" className="hover:text-white transition-colors">Manufacturing</Link></li>
              <li><Link href="/industries?sector=retail" className="hover:text-white transition-colors">Retail</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2 text-sm text-neutral-400">
              <li><Link href="/dealers" className="hover:text-white transition-colors">Find a Dealer</Link></li>
              <li><Link href="/prequalify" className="hover:text-white transition-colors">Get Prequalified</Link></li>
              <li><a href="mailto:contact@bolt.new" className="hover:text-white transition-colors">Contact Sales</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-neutral-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-neutral-400">
          <p>&copy; 2025 Bolt.new. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
