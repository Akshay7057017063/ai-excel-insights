import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { billingAPI } from '../services/api'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { CheckCircle2, ChevronDown, Sparkles, HelpCircle, Shield, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'

export const PricingPage: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null)
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: '₹0',
      period: 'forever',
      description: 'Test the power of automated spreadsheet insights.',
      popular: false,
      features: [
        '3 automated reports per month',
        'Up to 10 MB per spreadsheet',
        'Up to 10,000 rows',
        'Automatic KPI cards & charts',
        'Summary anomaly detection',
        'Community support',
      ],
      buttonText: 'Get Started Free',
      buttonVariant: 'secondary' as const,
    },
    {
      id: 'single',
      name: 'Single Report',
      price: '₹149',
      period: 'one-time purchase',
      description: 'One-off in-depth analysis for an immediate presentation.',
      popular: false,
      features: [
        '1 comprehensive analysis report',
        'Up to 50 MB spreadsheet',
        'Up to 250,000 rows',
        'Full executive PDF export',
        'AI Analyst chat (10 questions)',
        'Clean CSV data download',
      ],
      buttonText: 'Buy 1 Report',
      buttonVariant: 'secondary' as const,
    },
    {
      id: 'pro',
      name: 'Pro',
      price: '₹999',
      period: 'per month',
      description: 'For business analysts, finance teams, and founders.',
      popular: true,
      features: [
        'Unlimited reports per month',
        'Up to 50 MB per spreadsheet',
        'Up to 500,000 rows',
        'Unlimited AI Analyst questions',
        'Full executive PDF & CSV exports',
        'Priority data processing speed',
        'Email & chat support',
      ],
      buttonText: 'Subscribe to Pro',
      buttonVariant: 'primary' as const,
    },
    {
      id: 'business',
      name: 'Business',
      price: '₹3,499',
      period: 'per month',
      description: 'For organizations with multi-department reporting needs.',
      popular: false,
      features: [
        'Everything in Pro plan',
        'Up to 200 MB per file',
        'Up to 2,000,000 rows',
        'Custom corporate branding on PDFs',
        'Multiple team member seats',
        'Dedicated onboarding session',
        '99.9% uptime SLA',
      ],
      buttonText: 'Contact & Upgrade',
      buttonVariant: 'secondary' as const,
    },
  ]

  const billingFaqs = [
    {
      q: 'How does billing work in Indian Rupees (INR)?',
      a: 'All prices are listed in Indian Rupees (₹). Recurring subscriptions renew on a monthly basis, and you can cancel anytime with a single click.',
    },
    {
      q: 'What happens if I exceed the file size limit?',
      a: 'Free accounts support files up to 10 MB. Pro and Business accounts accept larger spreadsheets up to 50 MB and 200 MB respectively.',
    },
    {
      q: 'Can I purchase a single report without subscribing?',
      a: 'Yes! The Single Report option allows you to run a deep analysis on a single dataset for ₹149 without any recurring monthly charges.',
    },
    {
      q: 'Do you offer refunds?',
      a: 'If our system is unable to process your spreadsheet or generate insights properly, reach out to our team for a prompt refund.',
    },
  ]

  const handleSelectPlan = async (planId: string) => {
    if (!isAuthenticated) {
      toast('Please create an account or sign in to continue.', { icon: '👋' })
      navigate('/register')
      return
    }

    if (planId === 'free') {
      navigate('/upload')
      return
    }

    setLoadingPlan(planId)
    try {
      const res = await billingAPI.checkout(planId)
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url
      } else {
        toast.success(`Plan request received. Proceeding to checkout.`)
      }
    } catch {
      toast.error('Unable to initiate checkout right now. Please try again shortly.')
    } finally {
      setLoadingPlan(null)
    }
  }

  return (
    <div className="py-8 max-w-6xl mx-auto px-4 sm:px-6">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <Badge variant="info" className="mb-3">
          Flexible Pricing
        </Badge>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">
          Choose the right plan for your workflow
        </h1>
        <p className="mt-3 text-base text-gray-600">
          Transparent pricing in Indian Rupees. Instant setup with no hidden charges.
        </p>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`bg-white rounded-2xl p-6 flex flex-col justify-between transition-all relative ${
              plan.popular
                ? 'border-2 border-blue-600 shadow-xl scale-[1.02] ring-4 ring-blue-500/10'
                : 'border border-gray-200 shadow-sm hover:border-gray-300'
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow">
                Recommended
              </div>
            )}

            <div>
              <h3 className="text-lg font-bold text-gray-900">{plan.name}</h3>
              <p className="text-xs text-gray-500 mt-1 min-h-[32px]">{plan.description}</p>

              <div className="mt-5 mb-6">
                <span className="text-3xl font-extrabold text-gray-900">{plan.price}</span>
                <span className="text-xs text-gray-500 font-medium ml-1">/ {plan.period}</span>
              </div>

              <div className="border-t border-gray-100 pt-5 mb-6">
                <p className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-3">
                  Included Features:
                </p>
                <ul className="space-y-2.5 text-xs text-gray-600">
                  {plan.features.map((feat, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <Button
              variant={plan.buttonVariant}
              onClick={() => handleSelectPlan(plan.id)}
              loading={loadingPlan === plan.id}
              className="w-full text-xs font-semibold py-2.5 rounded-xl shadow-sm"
            >
              <span>{plan.buttonText}</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </div>
        ))}
      </div>

      {/* Security & Guarantee Note */}
      <div className="bg-gray-50 rounded-2xl border border-gray-200/80 p-6 flex flex-col sm:flex-row items-center justify-between gap-4 mb-16">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center flex-shrink-0">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Encrypted Payments & Data Guarantee</h4>
            <p className="text-xs text-gray-500 mt-0.5">
              Processed via verified payment gateways. Cancel anytime without penalty.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500 font-medium">
          <span>UPI</span> • <span>Net Banking</span> • <span>Cards</span>
        </div>
      </div>

      {/* Billing FAQ */}
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h3 className="text-2xl font-bold text-gray-900">Billing & Subscription Questions</h3>
        </div>

        <div className="space-y-3">
          {billingFaqs.map((faq, index) => {
            const isOpen = openFaq === index
            return (
              <div
                key={index}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden"
              >
                <button
                  onClick={() => setOpenFaq(isOpen ? null : index)}
                  className="w-full p-4 text-left flex items-center justify-between font-semibold text-sm text-gray-900 hover:text-blue-600"
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    className={`w-4 h-4 text-gray-400 transition-transform ${
                      isOpen ? 'rotate-180 text-blue-600' : ''
                    }`}
                  />
                </button>
                {isOpen && (
                  <div className="px-4 pb-4 pt-1 text-xs text-gray-600 leading-relaxed border-t border-gray-50">
                    {faq.a}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default PricingPage
