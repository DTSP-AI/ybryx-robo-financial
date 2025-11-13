import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';

interface IndustryTileProps {
  title: string;
  description: string;
  icon: LucideIcon;
  slug: string;
  useCases: string[];
}

export default function IndustryTile({
  title,
  description,
  icon: Icon,
  slug,
  useCases,
}: IndustryTileProps) {
  return (
    <Link href={`/industries?sector=${slug}`}>
      <Card className="h-full hover:shadow-lg transition-all hover:scale-105 cursor-pointer">
        <CardHeader>
          <div className="w-12 h-12 bg-black rounded-lg flex items-center justify-center mb-4">
            <Icon className="w-6 h-6 text-white" />
          </div>
          <CardTitle className="text-xl">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm font-medium text-neutral-700">Common Use Cases:</p>
            <ul className="space-y-1">
              {useCases.slice(0, 3).map((useCase, index) => (
                <li key={index} className="text-sm text-neutral-600 flex items-start">
                  <span className="mr-2">•</span>
                  <span>{useCase}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
