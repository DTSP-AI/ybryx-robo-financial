'use client';

import { useState } from 'react';
import DealerCard from '@/components/DealerCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, MapPin } from 'lucide-react';

const dealers = [
  {
    id: '1',
    name: 'RoboTech Solutions',
    coverage: 'California, Nevada, Arizona',
    address: '1234 Innovation Dr, San Francisco, CA 94105',
    phone: '(415) 555-0123',
    email: 'sales@robotechsolutions.com',
    specialties: ['AMRs', 'AGVs', 'Warehouse Automation'],
    zipCodes: ['94105', '94102', '89101', '85001'],
  },
  {
    id: '2',
    name: 'AgriBot Distributors',
    coverage: 'Midwest States',
    address: '5678 Harvest Ln, Des Moines, IA 50309',
    phone: '(515) 555-0456',
    email: 'info@agribotdist.com',
    specialties: ['Agricultural Drones', 'Crop Monitoring', 'Precision Spraying'],
    zipCodes: ['50309', '68101', '64101', '55401'],
  },
  {
    id: '3',
    name: 'Industrial Automation Partners',
    coverage: 'Northeast Corridor',
    address: '9012 Manufacturing Way, Newark, NJ 07102',
    phone: '(973) 555-0789',
    email: 'contact@indautopartners.com',
    specialties: ['Robotic Arms', 'Manufacturing', 'Assembly Lines'],
    zipCodes: ['07102', '10001', '19102', '02101'],
  },
  {
    id: '4',
    name: 'Urban Delivery Robotics',
    coverage: 'Major Metropolitan Areas',
    address: '3456 Tech Park Blvd, Austin, TX 78701',
    phone: '(512) 555-0234',
    email: 'hello@urbandeliveryrobotics.com',
    specialties: ['Last-Mile Delivery', 'Autonomous Vehicles', 'Urban Logistics'],
    zipCodes: ['78701', '90001', '60601', '98101'],
  },
  {
    id: '5',
    name: 'Construction Tech Systems',
    coverage: 'Southern States',
    address: '7890 Builder Ave, Atlanta, GA 30303',
    phone: '(404) 555-0567',
    email: 'sales@constructiontech.com',
    specialties: ['Survey Drones', 'Site Monitoring', 'Construction Safety'],
    zipCodes: ['30303', '33101', '28201', '37201'],
  },
  {
    id: '6',
    name: 'Retail Robotics Group',
    coverage: 'National Coverage',
    address: '2345 Commerce St, Chicago, IL 60601',
    phone: '(312) 555-0890',
    email: 'info@retailroboticsgroup.com',
    specialties: ['Floor Cleaners', 'Inventory Scanners', 'Retail Automation'],
    zipCodes: ['60601', '10001', '90001', '75201', '98101'],
  },
];

export default function DealersPage() {
  const [zipCode, setZipCode] = useState('');
  const [filteredDealers, setFilteredDealers] = useState(dealers);
  const [searchPerformed, setSearchPerformed] = useState(false);

  const handleSearch = () => {
    if (!zipCode.trim()) {
      setFilteredDealers(dealers);
      setSearchPerformed(false);
      return;
    }

    const results = dealers.filter((dealer) =>
      dealer.zipCodes.some((zip) => zip.startsWith(zipCode.trim()))
    );
    setFilteredDealers(results);
    setSearchPerformed(true);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <section className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Find an Authorized Dealer
          </h1>
          <p className="text-xl text-neutral-600">
            Work with certified partners who understand your industry and can help you select the right equipment
          </p>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white p-8 rounded-lg shadow-sm mb-12">
          <div className="max-w-2xl mx-auto">
            <label className="block text-lg font-semibold mb-4">
              Search by ZIP Code
            </label>
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="Enter your ZIP code"
                  value={zipCode}
                  onChange={(e) => setZipCode(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-10"
                  maxLength={5}
                />
              </div>
              <Button
                onClick={handleSearch}
                className="bg-black hover:bg-neutral-800"
              >
                <Search className="w-5 h-5 mr-2" />
                Search
              </Button>
            </div>
          </div>
        </div>

        {searchPerformed && filteredDealers.length === 0 && (
          <div className="bg-white p-8 rounded-lg shadow-sm text-center mb-12">
            <p className="text-xl text-neutral-600 mb-4">
              No dealers found in your area for ZIP code: {zipCode}
            </p>
            <p className="text-neutral-600">
              Try a nearby ZIP code or contact our sales team for assistance.
            </p>
            <Button
              onClick={() => {
                setZipCode('');
                setFilteredDealers(dealers);
                setSearchPerformed(false);
              }}
              variant="outline"
              className="mt-4"
            >
              View All Dealers
            </Button>
          </div>
        )}

        <div className="mb-6">
          <h2 className="text-2xl font-bold">
            {searchPerformed
              ? `${filteredDealers.length} Dealer${filteredDealers.length !== 1 ? 's' : ''} Found`
              : 'All Authorized Dealers'}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDealers.map((dealer) => (
            <DealerCard key={dealer.id} {...dealer} />
          ))}
        </div>
      </section>

      <section className="bg-black text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Interested in Becoming a Dealer?
          </h2>
          <p className="text-xl text-neutral-300 mb-8 max-w-3xl mx-auto">
            Join our network of certified partners and help businesses access cutting-edge robotics equipment
          </p>
          <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-black">
            Partner With Us
          </Button>
        </div>
      </section>
    </div>
  );
}
