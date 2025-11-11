import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle2, Mail, Phone, Calendar } from 'lucide-react';

export default function ThankYouPage() {
  return (
    <div className="min-h-screen bg-neutral-50">
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <CheckCircle2 className="w-12 h-12 text-green-600" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Application Submitted Successfully
          </h1>
          <p className="text-xl text-neutral-600">
            Thank you for choosing Bolt.new. Your prequalification application is being reviewed.
          </p>
        </div>

        <Card className="mb-8">
          <CardContent className="pt-6">
            <h2 className="text-2xl font-bold mb-6">What Happens Next?</h2>
            <div className="space-y-6">
              <div className="flex items-start">
                <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                  <span className="text-white font-bold">1</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Application Review</h3>
                  <p className="text-neutral-600">
                    Our team will review your application and perform a soft credit check within the next 1-2 business days.
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                  <span className="text-white font-bold">2</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Prequalification Decision</h3>
                  <p className="text-neutral-600">
                    You will receive an email with your prequalification status and available lease terms.
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                  <span className="text-white font-bold">3</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Connect with a Dealer</h3>
                  <p className="text-neutral-600">
                    We will connect you with an authorized dealer in your area to finalize equipment selection and delivery.
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                  <span className="text-white font-bold">4</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">Equipment Deployment</h3>
                  <p className="text-neutral-600">
                    Once approved, your equipment can be deployed within 2-4 weeks depending on availability.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card>
            <CardContent className="pt-6 text-center">
              <Mail className="w-8 h-8 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Check Your Email</h3>
              <p className="text-sm text-neutral-600">
                A confirmation has been sent to your email address
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 text-center">
              <Phone className="w-8 h-8 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Questions?</h3>
              <p className="text-sm text-neutral-600">
                Call us at <br />
                <a href="tel:18005550123" className="text-black font-medium hover:underline">
                  (800) 555-0123
                </a>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 text-center">
              <Calendar className="w-8 h-8 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Expected Response</h3>
              <p className="text-sm text-neutral-600">
                1-2 business days for prequalification decision
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="text-center space-y-4">
          <p className="text-neutral-600">
            While you wait, explore our equipment catalog and learn more about robotics solutions
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/robots">
              <Button variant="outline" className="border-black w-full sm:w-auto">
                Browse Equipment
              </Button>
            </Link>
            <Link href="/industries">
              <Button variant="outline" className="border-black w-full sm:w-auto">
                Explore Industries
              </Button>
            </Link>
            <Link href="/">
              <Button className="bg-black hover:bg-neutral-800 w-full sm:w-auto">
                Return Home
              </Button>
            </Link>
          </div>
        </div>

        <div className="mt-12 bg-black text-white p-8 rounded-lg text-center">
          <h3 className="text-2xl font-bold mb-4">
            Need Immediate Assistance?
          </h3>
          <p className="text-neutral-300 mb-6">
            Book a 15-minute consultation with our robotics specialists to discuss your specific needs
          </p>
          <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-black">
            Schedule Consultation
          </Button>
        </div>
      </section>
    </div>
  );
}
