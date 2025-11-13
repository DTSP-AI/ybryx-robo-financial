'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import IndustryTile from '@/components/IndustryTile';
import RobotCard from '@/components/RobotCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Warehouse, Tractor, Factory, Truck, Building2, ShoppingCart, TrendingUp, DollarSign, Users } from 'lucide-react';

const industries = [
  {
    title: 'Logistics & Warehousing',
    description: 'Automate order fulfillment and reduce labor costs by up to 40%',
    icon: Warehouse,
    slug: 'logistics',
    useCases: [
      'Order picking and sorting',
      'Pallet movement and transport',
      'Inventory management and scanning',
      'Goods-to-person automation',
      'Cross-docking operations',
    ],
    benefits: [
      { label: 'Labor Cost Reduction', value: '40%' },
      { label: 'Throughput Increase', value: '2-3x' },
      { label: 'Picking Accuracy', value: '99.9%' },
    ],
    robots: ['1', '2', '5'],
  },
  {
    title: 'Agriculture',
    description: 'Deploy autonomous equipment that works 24/7 across your acreage',
    icon: Tractor,
    slug: 'agriculture',
    useCases: [
      'Crop monitoring and health assessment',
      'Precision spraying and fertilization',
      'Harvesting automation',
      'Livestock monitoring',
      'Field mapping and planning',
    ],
    benefits: [
      { label: 'Coverage Area', value: '40 acres/hr' },
      { label: 'Chemical Savings', value: '30%' },
      { label: 'Crop Yield Increase', value: '15%' },
    ],
    robots: ['3'],
  },
  {
    title: 'Manufacturing',
    description: 'Increase production throughput with precision robotic arms',
    icon: Factory,
    slug: 'manufacturing',
    useCases: [
      'Assembly line automation',
      'Quality inspection and testing',
      'Material handling',
      'Welding and fabrication',
      'Packaging operations',
    ],
    benefits: [
      { label: 'Production Increase', value: '50%' },
      { label: 'Defect Reduction', value: '85%' },
      { label: 'ROI Timeline', value: '8-12 months' },
    ],
    robots: ['4', '9'],
  },
  {
    title: 'Last-Mile Delivery',
    description: 'Cut delivery costs with autonomous ground and aerial vehicles',
    icon: Truck,
    slug: 'delivery',
    useCases: [
      'Package delivery within 3-mile radius',
      'Route optimization',
      'Customer notifications',
      'Contactless delivery',
      'Return pickups',
    ],
    benefits: [
      { label: 'Cost per Delivery', value: '$1-2' },
      { label: 'Delivery Speed', value: '30 min' },
      { label: 'Carbon Reduction', value: '90%' },
    ],
    robots: ['6'],
  },
  {
    title: 'Construction',
    description: 'Survey sites, monitor progress, and transport materials autonomously',
    icon: Building2,
    slug: 'construction',
    useCases: [
      'Site surveying and mapping',
      'Progress monitoring',
      'Safety inspections',
      'Material transport',
      '3D modeling and BIM integration',
    ],
    benefits: [
      { label: 'Survey Time', value: '10x faster' },
      { label: 'Safety Incidents', value: '-60%' },
      { label: 'Project Delays', value: '-25%' },
    ],
    robots: ['7'],
  },
  {
    title: 'Retail',
    description: 'Enhance customer experience with automated inventory and cleaning',
    icon: ShoppingCart,
    slug: 'retail',
    useCases: [
      'Inventory scanning and tracking',
      'Floor cleaning and maintenance',
      'Customer assistance',
      'Shelf monitoring',
      'Stock-out detection',
    ],
    benefits: [
      { label: 'Inventory Accuracy', value: '99%' },
      { label: 'Labor Savings', value: '35%' },
      { label: 'Customer Satisfaction', value: '+20%' },
    ],
    robots: ['8'],
  },
];

const allRobots = [
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
  {
    id: '4',
    name: 'Precision Welding Arm',
    manufacturer: 'ABB Robotics',
    category: 'Robotic Arm',
    description: 'Six-axis robotic arm for high-precision welding and assembly tasks',
    payload: '15 lbs',
    autonomyLevel: 'Level 5',
    leaseFrom: '$1,799',
  },
  {
    id: '5',
    name: 'Warehouse Inventory Scanner',
    manufacturer: 'Boston Dynamics',
    category: 'AMR',
    description: 'Autonomous robot that scans and tracks inventory across large warehouse facilities',
    payload: '50 lbs',
    autonomyLevel: 'Level 4',
    leaseFrom: '$1,599',
  },
  {
    id: '6',
    name: 'Last-Mile Delivery Bot',
    manufacturer: 'Starship Technologies',
    category: 'AGV',
    description: 'Autonomous ground vehicle for urban delivery within 3-mile radius',
    payload: '20 lbs',
    autonomyLevel: 'Level 4',
    leaseFrom: '$699',
  },
  {
    id: '7',
    name: 'Construction Site Surveyor',
    manufacturer: 'Skydio',
    category: 'Drone',
    description: 'High-resolution drone for automated site surveys and progress tracking',
    payload: '5 lbs',
    autonomyLevel: 'Level 4',
    leaseFrom: '$1,099',
  },
  {
    id: '8',
    name: 'Retail Floor Cleaner',
    manufacturer: 'Brain Corp',
    category: 'AMR',
    description: 'Autonomous floor scrubber for retail and commercial spaces',
    payload: 'N/A',
    autonomyLevel: 'Level 4',
    leaseFrom: '$799',
  },
  {
    id: '9',
    name: 'Pick and Place Arm',
    manufacturer: 'Universal Robots',
    category: 'Robotic Arm',
    description: 'Collaborative robot arm for packaging and material handling',
    payload: '22 lbs',
    autonomyLevel: 'Level 5',
    leaseFrom: '$1,499',
  },
];

export default function IndustriesPage() {
  const searchParams = useSearchParams();
  const [selectedIndustry, setSelectedIndustry] = useState<string | null>(null);

  useEffect(() => {
    const sector = searchParams.get('sector');
    if (sector) {
      setSelectedIndustry(sector);
    }
  }, [searchParams]);

  const industry = selectedIndustry
    ? industries.find((ind) => ind.slug === selectedIndustry)
    : null;

  const industryRobots = industry
    ? allRobots.filter((robot) => industry.robots.includes(robot.id))
    : [];

  return (
    <div className="min-h-screen bg-neutral-50">
      <section className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {selectedIndustry ? industry?.title : 'Industries We Serve'}
          </h1>
          <p className="text-xl text-neutral-600">
            {selectedIndustry
              ? industry?.description
              : 'Discover how robotics equipment transforms operations across diverse sectors'}
          </p>
        </div>
      </section>

      {!selectedIndustry ? (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {industries.map((industry) => (
              <IndustryTile key={industry.slug} {...industry} />
            ))}
          </div>
        </section>
      ) : (
        industry && (
          <>
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <h2 className="text-3xl font-bold mb-8">Key Performance Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                {industry.benefits.map((benefit, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <CardTitle className="text-sm text-neutral-600 font-medium">
                        {benefit.label}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-4xl font-bold">{benefit.value}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <h2 className="text-3xl font-bold mb-8">Common Use Cases</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
                {industry.useCases.map((useCase, index) => (
                  <Card key={index}>
                    <CardContent className="pt-6">
                      <div className="flex items-start">
                        <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                          <span className="text-white font-bold text-sm">{index + 1}</span>
                        </div>
                        <p className="text-lg">{useCase}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <h2 className="text-3xl font-bold mb-8">Recommended Equipment</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {industryRobots.map((robot) => (
                  <RobotCard key={robot.id} {...robot} />
                ))}
              </div>
            </section>
          </>
        )
      )}
    </div>
  );
}
