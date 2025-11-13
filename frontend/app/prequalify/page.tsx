'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ProgressStepper from '@/components/ProgressStepper';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';

const steps = [
  { id: 1, title: 'Business Info' },
  { id: 2, title: 'Equipment Needs' },
  { id: 3, title: 'Financials' },
  { id: 4, title: 'Review & Submit' },
];

const equipment = [
  { id: '1', name: 'Mobile Shelf AMR', category: 'AMR' },
  { id: '2', name: 'Heavy Duty Pallet Bot', category: 'AGV' },
  { id: '3', name: 'Agricultural Spray Drone', category: 'Drone' },
  { id: '4', name: 'Precision Welding Arm', category: 'Robotic Arm' },
  { id: '5', name: 'Warehouse Inventory Scanner', category: 'AMR' },
  { id: '6', name: 'Last-Mile Delivery Bot', category: 'AGV' },
  { id: '7', name: 'Construction Site Surveyor', category: 'Drone' },
  { id: '8', name: 'Retail Floor Cleaner', category: 'AMR' },
  { id: '9', name: 'Pick and Place Arm', category: 'Robotic Arm' },
];

export default function PrequalifyPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    businessName: '',
    businessType: '',
    industry: '',
    email: '',
    phone: '',
    selectedEquipment: [] as string[],
    quantity: '1',
    annualRevenue: '',
    businessAge: '',
    creditRating: '',
    consent: false,
  });

  const updateFormData = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const toggleEquipment = (equipmentId: string) => {
    setFormData((prev) => ({
      ...prev,
      selectedEquipment: prev.selectedEquipment.includes(equipmentId)
        ? prev.selectedEquipment.filter((id) => id !== equipmentId)
        : [...prev.selectedEquipment, equipmentId],
    }));
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return (
          formData.businessName &&
          formData.businessType &&
          formData.industry &&
          formData.email &&
          formData.phone
        );
      case 2:
        return formData.selectedEquipment.length > 0 && formData.quantity;
      case 3:
        return formData.annualRevenue && formData.businessAge && formData.creditRating;
      case 4:
        return formData.consent;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (canProceed() && currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!canProceed()) return;

    console.log('Submitting form:', formData);
    router.push('/thank-you');
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <section className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Equipment Lease Prequalification
          </h1>
          <p className="text-xl text-neutral-600">
            Get prequalified in minutes with no impact to your credit score
          </p>
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ProgressStepper steps={steps} currentStep={currentStep} />

        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-2xl">{steps[currentStep - 1].title}</CardTitle>
            <CardDescription>
              {currentStep === 1 && 'Tell us about your business'}
              {currentStep === 2 && 'Select the equipment you need'}
              {currentStep === 3 && 'Provide financial information'}
              {currentStep === 4 && 'Review and submit your application'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <Label htmlFor="businessName">Business Name</Label>
                  <Input
                    id="businessName"
                    value={formData.businessName}
                    onChange={(e) => updateFormData('businessName', e.target.value)}
                    placeholder="Enter your business name"
                  />
                </div>
                <div>
                  <Label htmlFor="businessType">Business Type</Label>
                  <Select
                    value={formData.businessType}
                    onValueChange={(value) => updateFormData('businessType', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select business type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="llc">LLC</SelectItem>
                      <SelectItem value="corporation">Corporation</SelectItem>
                      <SelectItem value="partnership">Partnership</SelectItem>
                      <SelectItem value="sole-proprietor">Sole Proprietor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="industry">Industry</Label>
                  <Select
                    value={formData.industry}
                    onValueChange={(value) => updateFormData('industry', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your industry" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="logistics">Logistics & Warehousing</SelectItem>
                      <SelectItem value="agriculture">Agriculture</SelectItem>
                      <SelectItem value="manufacturing">Manufacturing</SelectItem>
                      <SelectItem value="delivery">Last-Mile Delivery</SelectItem>
                      <SelectItem value="construction">Construction</SelectItem>
                      <SelectItem value="retail">Retail</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => updateFormData('email', e.target.value)}
                    placeholder="your.email@company.com"
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => updateFormData('phone', e.target.value)}
                    placeholder="(555) 123-4567"
                  />
                </div>
              </div>
            )}

            {currentStep === 2 && (
              <div className="space-y-6">
                <div>
                  <Label className="text-base mb-4 block">
                    Select Equipment (choose one or more)
                  </Label>
                  <div className="space-y-3">
                    {equipment.map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-neutral-50 cursor-pointer"
                        onClick={() => toggleEquipment(item.id)}
                      >
                        <Checkbox
                          checked={formData.selectedEquipment.includes(item.id)}
                          onCheckedChange={() => toggleEquipment(item.id)}
                        />
                        <div className="flex-1">
                          <p className="font-medium">{item.name}</p>
                          <p className="text-sm text-neutral-600">{item.category}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <Label htmlFor="quantity">Quantity Needed</Label>
                  <Select
                    value={formData.quantity}
                    onValueChange={(value) => updateFormData('quantity', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select quantity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 unit</SelectItem>
                      <SelectItem value="2-5">2-5 units</SelectItem>
                      <SelectItem value="6-10">6-10 units</SelectItem>
                      <SelectItem value="11-20">11-20 units</SelectItem>
                      <SelectItem value="20+">20+ units</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {currentStep === 3 && (
              <div className="space-y-6">
                <div>
                  <Label htmlFor="annualRevenue">Annual Revenue</Label>
                  <Select
                    value={formData.annualRevenue}
                    onValueChange={(value) => updateFormData('annualRevenue', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select revenue range" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0-500k">$0 - $500K</SelectItem>
                      <SelectItem value="500k-1m">$500K - $1M</SelectItem>
                      <SelectItem value="1m-5m">$1M - $5M</SelectItem>
                      <SelectItem value="5m-10m">$5M - $10M</SelectItem>
                      <SelectItem value="10m+">$10M+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="businessAge">Business Age</Label>
                  <Select
                    value={formData.businessAge}
                    onValueChange={(value) => updateFormData('businessAge', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select business age" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0-1">Less than 1 year</SelectItem>
                      <SelectItem value="1-2">1-2 years</SelectItem>
                      <SelectItem value="2-5">2-5 years</SelectItem>
                      <SelectItem value="5+">5+ years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="creditRating">Estimated Credit Rating</Label>
                  <Select
                    value={formData.creditRating}
                    onValueChange={(value) => updateFormData('creditRating', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select credit rating" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="excellent">Excellent (750+)</SelectItem>
                      <SelectItem value="good">Good (700-749)</SelectItem>
                      <SelectItem value="fair">Fair (650-699)</SelectItem>
                      <SelectItem value="poor">Poor (below 650)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-900">
                    <CheckCircle2 className="w-4 h-4 inline mr-2" />
                    This is a soft inquiry and will not impact your credit score
                  </p>
                </div>
              </div>
            )}

            {currentStep === 4 && (
              <div className="space-y-6">
                <div className="bg-neutral-50 p-6 rounded-lg space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Business Information</h3>
                    <p className="text-sm text-neutral-600">
                      {formData.businessName} • {formData.businessType} • {formData.industry}
                    </p>
                    <p className="text-sm text-neutral-600">
                      {formData.email} • {formData.phone}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">Equipment Selection</h3>
                    <p className="text-sm text-neutral-600">
                      {formData.selectedEquipment.length} equipment type(s) selected • Quantity: {formData.quantity}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">Financial Details</h3>
                    <p className="text-sm text-neutral-600">
                      Annual Revenue: {formData.annualRevenue} • Business Age: {formData.businessAge}
                    </p>
                    <p className="text-sm text-neutral-600">
                      Credit Rating: {formData.creditRating}
                    </p>
                  </div>
                </div>

                <div className="border rounded-lg p-4 space-y-4">
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="consent"
                      checked={formData.consent}
                      onCheckedChange={(checked) => updateFormData('consent', checked as boolean)}
                    />
                    <label htmlFor="consent" className="text-sm leading-relaxed cursor-pointer">
                      I authorize Ybryx Capital and its lending partners to perform a soft credit inquiry and contact me regarding my equipment lease application. I understand this will not affect my credit score and I consent to receive communications via phone, email, and SMS.
                    </label>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-900">
                    <CheckCircle2 className="w-4 h-4 inline mr-2" />
                    You will receive a prequalification decision within 1-2 business days
                  </p>
                </div>
              </div>
            )}

            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                onClick={handleBack}
                disabled={currentStep === 1}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              {currentStep < 4 ? (
                <Button
                  onClick={handleNext}
                  disabled={!canProceed()}
                  className="bg-black hover:bg-neutral-800"
                >
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={!canProceed()}
                  className="bg-black hover:bg-neutral-800"
                >
                  Submit Application
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
