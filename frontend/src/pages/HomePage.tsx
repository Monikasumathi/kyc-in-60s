import { Link } from 'react-router-dom'
import { Shield, Zap, Eye, Lock, CheckCircle, Clock } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Shield className="w-8 h-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">KYC in 60s</h1>
            </div>
            <nav className="flex space-x-4">
              <Link to="/admin" className="text-gray-600 hover:text-primary-600 transition-colors">
                Admin Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full mb-6">
            <Zap className="w-4 h-4" />
            <span className="text-sm font-medium">AI-Powered Identity Verification</span>
          </div>
          
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Complete Your KYC
            <br />
            <span className="text-primary-600">in Under 60 Seconds</span>
          </h2>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Experience the future of customer onboarding with our AI-powered KYC solution. 
            Fast, secure, and compliant verification with instant approval for low-risk customers.
          </p>
          
          <Link
            to="/submit"
            className="inline-flex items-center px-8 py-4 bg-primary-600 text-white text-lg font-medium rounded-xl hover:bg-primary-700 transition-all transform hover:scale-105 shadow-lg"
          >
            Start Verification Now
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="card text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 text-primary-600 rounded-full mb-4">
              <Zap className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
            <p className="text-gray-600">
              Auto-approval for low-risk customers in under 60 seconds. No waiting, no hassle.
            </p>
          </div>

          <div className="card text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 text-primary-600 rounded-full mb-4">
              <Eye className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI-Powered Verification</h3>
            <p className="text-gray-600">
              Advanced OCR, face matching, and risk assessment powered by machine learning.
            </p>
          </div>

          <div className="card text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 text-primary-600 rounded-full mb-4">
              <Lock className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Secure & Compliant</h3>
            <p className="text-gray-600">
              Bank-grade security with complete audit trails and regulatory compliance.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="card mb-16">
          <h3 className="text-2xl font-bold text-center mb-8">How It Works</h3>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                1
              </div>
              <h4 className="font-semibold mb-2">Upload Document</h4>
              <p className="text-sm text-gray-600">Take a photo of your ID card or passport</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                2
              </div>
              <h4 className="font-semibold mb-2">Take Selfie</h4>
              <p className="text-sm text-gray-600">Capture a clear selfie for identity verification</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                3
              </div>
              <h4 className="font-semibold mb-2">AI Analysis</h4>
              <p className="text-sm text-gray-600">Our AI verifies your identity in real-time</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                4
              </div>
              <h4 className="font-semibold mb-2">Instant Decision</h4>
              <p className="text-sm text-gray-600">Get approved instantly or within 24 hours</p>
            </div>
          </div>
        </div>

        {/* Key Benefits */}
        <div className="grid md:grid-cols-2 gap-8">
          <div className="card">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <CheckCircle className="w-6 h-6 text-green-500 mr-2" />
              For Customers
            </h3>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                Complete verification from your phone in under a minute
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                Real-time feedback if document quality needs improvement
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                Instant approval for straightforward cases
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                Transparent status updates throughout the process
              </li>
            </ul>
          </div>

          <div className="card">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <Clock className="w-6 h-6 text-primary-500 mr-2" />
              For Financial Institutions
            </h3>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-start">
                <span className="text-primary-500 mr-2">✓</span>
                Reduce manual review workload by up to 80%
              </li>
              <li className="flex items-start">
                <span className="text-primary-500 mr-2">✓</span>
                Explainable AI decisions with full audit trails
              </li>
              <li className="flex items-start">
                <span className="text-primary-500 mr-2">✓</span>
                Automated risk scoring and fraud detection
              </li>
              <li className="flex items-start">
                <span className="text-primary-500 mr-2">✓</span>
                Regulatory compliance with tamper-evident logs
              </li>
            </ul>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            Built for the Future of Banking Hackathon 2025
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Secure • Compliant • AI-Powered
          </p>
        </div>
      </footer>
    </div>
  )
}

