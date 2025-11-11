'use client';

import { useState } from 'react';
import RobotCard from '@/components/RobotCard';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

const robots = [
  {
    id: '1',
    name: 'Mobile Shelf AMR',
    manufacturer: 'Locus Robotics',
    category: 'AMR',
    description: 'Autonomous mobile robot that brings shelves directly to workers, reducing walk time by 70%',
    payload: '500 lbs',
    autonomyLevel: 'Level 4',
    leaseFrom: '$1,299',
    useCase: 'logistics',
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
    useCase: 'logistics',
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
    useCase: 'agriculture',
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
    useCase: 'manufacturing',
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
    useCase: 'logistics',
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
    useCase: 'delivery',
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
    useCase: 'construction',
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
    useCase: 'retail',
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
    useCase: 'manufacturing',
  },
];

export default function RobotsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [useCaseFilter, setUseCaseFilter] = useState('all');

  const filteredRobots = robots.filter((robot) => {
    const matchesSearch =
      robot.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      robot.manufacturer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      robot.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || robot.category === categoryFilter;
    const matchesUseCase = useCaseFilter === 'all' || robot.useCase === useCaseFilter;

    return matchesSearch && matchesCategory && matchesUseCase;
  });

  return (
    <div className="min-h-screen bg-neutral-50">
      <section className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Equipment Catalog
          </h1>
          <p className="text-xl text-neutral-600">
            Browse our complete selection of autonomous robots and equipment available for lease
          </p>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="Search by name, manufacturer, or description..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="AMR">AMR</SelectItem>
                <SelectItem value="AGV">AGV</SelectItem>
                <SelectItem value="Drone">Drone</SelectItem>
                <SelectItem value="Robotic Arm">Robotic Arm</SelectItem>
              </SelectContent>
            </Select>
            <Select value={useCaseFilter} onValueChange={setUseCaseFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Use Case" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Use Cases</SelectItem>
                <SelectItem value="logistics">Logistics</SelectItem>
                <SelectItem value="agriculture">Agriculture</SelectItem>
                <SelectItem value="manufacturing">Manufacturing</SelectItem>
                <SelectItem value="delivery">Delivery</SelectItem>
                <SelectItem value="construction">Construction</SelectItem>
                <SelectItem value="retail">Retail</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="mb-6">
          <p className="text-neutral-600">
            Showing <span className="font-semibold">{filteredRobots.length}</span> of{' '}
            <span className="font-semibold">{robots.length}</span> robots
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredRobots.map((robot) => (
            <RobotCard key={robot.id} {...robot} />
          ))}
        </div>

        {filteredRobots.length === 0 && (
          <div className="text-center py-12">
            <p className="text-xl text-neutral-600">
              No robots found matching your criteria. Try adjusting your filters.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
