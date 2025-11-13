import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MapPin, Phone, Mail } from 'lucide-react';

interface DealerCardProps {
  name: string;
  coverage: string;
  address: string;
  phone: string;
  email: string;
  specialties: string[];
}

export default function DealerCard({
  name,
  coverage,
  address,
  phone,
  email,
  specialties,
}: DealerCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{name}</CardTitle>
        <CardDescription className="flex items-center">
          <MapPin className="w-4 h-4 mr-1" />
          {coverage}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-neutral-700 mb-2">Specialties</p>
            <div className="flex flex-wrap gap-2">
              {specialties.map((specialty, index) => (
                <span
                  key={index}
                  className="text-xs bg-neutral-100 px-2 py-1 rounded"
                >
                  {specialty}
                </span>
              ))}
            </div>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex items-center text-neutral-600">
              <MapPin className="w-4 h-4 mr-2" />
              {address}
            </div>
            <div className="flex items-center text-neutral-600">
              <Phone className="w-4 h-4 mr-2" />
              <a href={`tel:${phone}`} className="hover:text-black">{phone}</a>
            </div>
            <div className="flex items-center text-neutral-600">
              <Mail className="w-4 h-4 mr-2" />
              <a href={`mailto:${email}`} className="hover:text-black">{email}</a>
            </div>
          </div>

          <Button className="w-full bg-black hover:bg-neutral-800">
            Contact Dealer
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
