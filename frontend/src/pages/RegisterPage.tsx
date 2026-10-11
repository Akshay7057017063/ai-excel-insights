import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import ErrorMessage from '../components/ui/ErrorMessage'
import { BarChart3, Mail, Lock, User, ArrowRight, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'

const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  terms: z.literal(true, {
    errorMap: () => ({ message: 'You must accept the terms of service' }),
  }),
})

type RegisterFormValues = z.infer<typeof registerSchema>

export const RegisterPage: React.FC = () => {
  const { register: registerAuth } = useAuth()
  const navigate = useNavigate()
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  })

  const passwordValue = watch('password') || ''

  const getPasswordStrength = (pwd: string) => {
    if (!pwd) return { label: 'Empty', color: 'bg-gray-200', pct: 0 }
    if (pwd.length < 6) return { label: 'Weak', color: 'bg-red-500', pct: 25 }
    if (pwd.length < 10) return { label: 'Medium', color: 'bg-amber-500', pct: 60 }
    return { label: 'Strong', color: 'bg-emerald-500', pct: 100 }
  }

  const strength = getPasswordStrength(passwordValue)

  const onSubmit = async (values: RegisterFormValues) => {
    setErrorMessage(null)
    try {
      await registerAuth(values.name, values.email, values.password)
      toast.success('Account created successfully!')
      navigate('/upload')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Registration failed. Please check details or try another email.'
      setErrorMessage(msg)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center gap-2.5 font-bold text-xl text-gray-900 mb-6">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <BarChart3 className="w-5 h-5" />
          </div>
          <span>DataPulse<span className="text-blue-600">AI</span></span>
        </Link>
        <h2 className="text-2xl font-bold tracking-tight text-gray-900">
          Create your free account
        </h2>
        <p className="mt-2 text-xs text-gray-500">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-500">
            Sign in here
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-8 px-6 shadow-sm rounded-2xl border border-gray-200/80 sm:px-10">
          {errorMessage && (
            <div className="mb-6">
              <ErrorMessage message={errorMessage} />
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  {...register('name')}
                  placeholder="Jane Doe"
                  className={`w-full pl-10 pr-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.name ? 'border-red-300 bg-red-50/20' : 'border-gray-300'
                  }`}
                />
              </div>
              {errors.name && (
                <p className="text-xs text-red-600 mt-1">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  {...register('email')}
                  placeholder="jane@company.com"
                  className={`w-full pl-10 pr-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.email ? 'border-red-300 bg-red-50/20' : 'border-gray-300'
                  }`}
                />
              </div>
              {errors.email && (
                <p className="text-xs text-red-600 mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  {...register('password')}
                  placeholder="Min. 8 characters"
                  className={`w-full pl-10 pr-3.5 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.password ? 'border-red-300 bg-red-50/20' : 'border-gray-300'
                  }`}
                />
              </div>

              {/* Password strength indicator */}
              {passwordValue && (
                <div className="mt-2 space-y-1">
                  <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${strength.color}`}
                      style={{ width: `${strength.pct}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-400">
                    <span>Strength: {strength.label}</span>
                    <span>Use 8+ characters with numbers</span>
                  </div>
                </div>
              )}

              {errors.password && (
                <p className="text-xs text-red-600 mt-1">{errors.password.message}</p>
              )}
            </div>

            <div className="pt-2">
              <label className="flex items-start gap-2.5 text-xs text-gray-600 cursor-pointer">
                <input
                  type="checkbox"
                  {...register('terms')}
                  className="mt-0.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span>
                  I agree to the Terms of Service and Privacy Policy. My uploaded datasets will remain confidential.
                </span>
              </label>
              {errors.terms && (
                <p className="text-xs text-red-600 mt-1">{errors.terms.message}</p>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              loading={isSubmitting}
              className="w-full py-2.5 rounded-xl mt-3"
            >
              <span>Create Account</span>
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-100 flex items-center justify-center gap-2 text-xs text-gray-500">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>256-bit secure processing</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
