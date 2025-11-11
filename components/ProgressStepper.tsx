'use client';

import { Check } from 'lucide-react';

interface Step {
  id: number;
  title: string;
}

interface ProgressStepperProps {
  steps: Step[];
  currentStep: number;
}

export default function ProgressStepper({ steps, currentStep }: ProgressStepperProps) {
  return (
    <div className="w-full py-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            <div className="flex flex-col items-center flex-1">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                  step.id < currentStep
                    ? 'bg-black border-black text-white'
                    : step.id === currentStep
                    ? 'border-black text-black'
                    : 'border-neutral-300 text-neutral-300'
                }`}
              >
                {step.id < currentStep ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <span className="font-medium">{step.id}</span>
                )}
              </div>
              <span
                className={`mt-2 text-xs md:text-sm font-medium ${
                  step.id <= currentStep ? 'text-black' : 'text-neutral-400'
                }`}
              >
                {step.title}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`h-0.5 flex-1 mx-2 transition-colors ${
                  step.id < currentStep ? 'bg-black' : 'bg-neutral-300'
                }`}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
