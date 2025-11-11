'use client';

import { Button } from '@/components/ui/button';
import IndustryTile from '@/components/IndustryTile';
import RobotCard from '@/components/RobotCard';
import Link from 'next/link';
import { Warehouse, Tractor, Factory, Truck, Building2, ShoppingCart, ArrowRight, CheckCircle2 } from 'lucide-react';

const industries = [
  {
    title: 'Logistics & Warehousing',
    description: 'Automate order fulfillment and reduce labor costs by up to 40%',
    icon: Warehouse,
    slug: 'logistics',
    useCases: ['Order picking and sorting', 'Pallet movement', 'Inventory management'],
  },
  {
    title: 'Agriculture',
    description: 'Deploy autonomous equipment that works 24/7 across your acreage',
    icon: Tractor,
    slug: 'agriculture',
    useCases: ['Crop monitoring and spraying', 'Harvesting automation', 'Livestock management'],
  },
  {
    title: 'Manufacturing',
    description: 'Increase production throughput with precision robotic arms',
    icon: Factory,
    slug: 'manufacturing',
    useCases: ['Assembly line automation', 'Quality inspection', 'Material handling'],
  },
  {
    title: 'Last-Mile Delivery',
    description: 'Cut delivery costs with autonomous ground and aerial vehicles',
    icon: Truck,
    slug: 'delivery',
    useCases: ['Package delivery', 'Route optimization', 'Customer notifications'],
  },
  {
    title: 'Construction',
    description: 'Survey sites, monitor progress, and transport materials autonomously',
    icon: Building2,
    slug: 'construction',
    useCases: ['Site surveying', 'Material transport', 'Safety monitoring'],
  },
  {
    title: 'Retail',
    description: 'Enhance customer experience with automated inventory and cleaning',
    icon: ShoppingCart,
    slug: 'retail',
    useCases: ['Inventory scanning', 'Floor cleaning', 'Customer assistance'],
  },
];

const featuredRobots = [
  {
    id: '1',
    name: 'Mobile Shelf AMR',
    manufacturer: 'Locus Robotics',
    category: 'AMR',
    description: 'Autonomous mobile robot that brings shelves directly to workers, reducing walk time by 70%',
    payload: '500 lbs',
    autonomyLevel: 'Level 4',
    leaseFrom: '$1,299',
  },
  {
    id: '2',
    name: 'Heavy Duty Pallet Bot',
    manufacturer: 'Fetch Robotics',
    category: 'AGV',
    description: 'Industrial-grade pallet mover for high-volume warehouse operations',
    payload: '3,000 lbs',
    autonomyLevel: 'Level 4',
    leaseFrom: '$2,499',
  },
  {
    id: '3',
    name: 'Agricultural Spray Drone',
    manufacturer: 'DJI Agras',
    category: 'Drone',
    description: 'Cover 40 acres per hour with precision crop spraying and monitoring',
    payload: '10 gallons',
    autonomyLevel: 'Level 3',
    leaseFrom: '$899',
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      <section className="relative bg-gradient-to-br from-neutral-900 via-black to-neutral-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                Access Industrial Robots Without the Capital Burden
              </h1>
              <p className="text-xl text-neutral-300 mb-8">
                Unlock cutting-edge automation equipment through flexible leasing. Prequalify in minutes with no hard credit pull.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/prequalify">
                  <Button size="lg" className="bg-white text-black hover:bg-neutral-200 w-full sm:w-auto">
                    Get Prequalified
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link href="/robots">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-black w-full sm:w-auto">
                    Browse Equipment
                  </Button>
                </Link>
              </div>
              <div className="mt-8 flex flex-wrap gap-6">
                <div className="flex items-center">
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  <span className="text-sm">No upfront capital</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  <span className="text-sm">Flexible terms</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  <span className="text-sm">Fast approval</span>
                </div>
              </div>
            </div>
            <div className="relative h-96 md:h-full flex items-center justify-center">
              <div className="text-9xl opacity-20">🤖</div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Built for Every Industry
            </h2>
            <p className="text-xl text-neutral-600 max-w-3xl mx-auto">
              Whether you run a warehouse, farm, or factory, robotics equipment pays for itself through labor savings and increased throughput.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {industries.map((industry) => (
              <IndustryTile key={industry.slug} {...industry} />
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Featured Equipment
            </h2>
            <p className="text-xl text-neutral-600">
              Explore autonomous fleets that pay for themselves in 6 months
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredRobots.map((robot) => (
              <RobotCard key={robot.id} {...robot} />
            ))}
          </div>
          <div className="text-center mt-12">
            <Link href="/robots">
              <Button size="lg" variant="outline" className="border-black">
                View Full Catalog
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="py-20 bg-black text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-5xl font-bold mb-6">
                Why Choose Leasing Over Buying?
              </h2>
              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                    <span className="text-black font-bold text-xl">1</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Preserve Working Capital</h3>
                    <p className="text-neutral-300">
                      Deploy robots without tying up $50K-$500K in equipment purchases. Keep cash for growth.
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                    <span className="text-black font-bold text-xl">2</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Stay Current with Technology</h3>
                    <p className="text-neutral-300">
                      Upgrade to newer models as technology advances without obsolescence risk.
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                    <span className="text-black font-bold text-xl">3</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Tax Advantages</h3>
                    <p className="text-neutral-300">
                      Lease payments are typically 100% tax deductible as operating expenses.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white text-black p-8 rounded-lg">
              <h3 className="text-2xl font-bold mb-6">Ready to Get Started?</h3>
              <p className="text-neutral-700 mb-6">
                See what you qualify for in minutes. No impact to your credit score during prequalification.
              </p>
              <Link href="/prequalify">
                <Button size="lg" className="w-full bg-black hover:bg-neutral-800">
                  Start Prequalification
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <p className="text-sm text-neutral-500 mt-4 text-center">
                Join 1,200+ businesses already leasing with Bolt.new
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Find Authorized Dealers Near You
            </h2>
            <p className="text-xl text-neutral-600 mb-8">
              Work with certified partners who understand your industry
            </p>
            <Link href="/dealers">
              <Button size="lg" className="bg-black hover:bg-neutral-800">
                Search Dealers
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
