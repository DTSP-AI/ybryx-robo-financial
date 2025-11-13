import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface RobotCardProps {
  id: string;
  name: string;
  manufacturer: string;
  category: string;
  description: string;
  payload?: string;
  autonomyLevel?: string;
  leaseFrom: string;
  imageUrl?: string;
}

export default function RobotCard({
  id,
  name,
  manufacturer,
  category,
  description,
  payload,
  autonomyLevel,
  leaseFrom,
  imageUrl,
}: RobotCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="h-48 bg-neutral-100 flex items-center justify-center">
        {imageUrl ? (
          <img src={imageUrl} alt={name} className="w-full h-full object-cover" />
        ) : (
          <div className="text-neutral-400 text-6xl">🤖</div>
        )}
      </div>
      <CardHeader>
        <div className="flex justify-between items-start mb-2">
          <Badge variant="secondary">{category}</Badge>
          {autonomyLevel && <Badge variant="outline">{autonomyLevel}</Badge>}
        </div>
        <CardTitle className="text-xl">{name}</CardTitle>
        <CardDescription className="text-sm text-neutral-600">{manufacturer}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-neutral-700 mb-4">{description}</p>
        {payload && (
          <div className="text-sm">
            <span className="font-medium">Payload:</span> {payload}
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-between items-center">
        <div>
          <p className="text-xs text-neutral-500">Lease from</p>
          <p className="text-lg font-bold">{leaseFrom}/mo</p>
        </div>
        <Link href={`/robots/${id}`}>
          <Button variant="outline">Learn More</Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
