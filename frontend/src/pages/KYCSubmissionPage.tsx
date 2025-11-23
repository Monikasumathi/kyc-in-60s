import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Camera, CheckCircle, AlertCircle, Loader2, ArrowLeft } from 'lucide-react'
import { kycApi } from '../services/api'
import { Link } from 'react-router-dom'

export default function KYCSubmissionPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [customerId, setCustomerId] = useState('')
  const [document, setDocument] = useState<File | null>(null)
  const [selfie, setSelfie] = useState<File | null>(null)
  const [documentPreview, setDocumentPreview] = useState<string | null>(null)
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDocumentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setDocument(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setDocumentPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSelfieChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelfie(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setSelfiePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async () => {
    if (!customerId || !document || !selfie) {
      setError('Please complete all steps')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await kycApi.submitKYC(customerId, document, selfie)
      navigate(`/status/${response.application_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit KYC application')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link to="/" className="inline-flex items-center text-gray-600 hover:text-primary-600 transition-colors">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Home
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">KYC Verification</h1>
          <p className="text-gray-600">Complete your identity verification in 3 simple steps</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-center space-x-4">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    step >= s
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {step > s ? <CheckCircle className="w-6 h-6" /> : s}
                </div>
                {s < 3 && (
                  <div
                    className={`w-16 h-1 mx-2 ${
                      step > s ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-4 space-x-16">
            <span className={step >= 1 ? 'text-primary-600 font-medium' : 'text-gray-500'}>
              Customer ID
            </span>
            <span className={step >= 2 ? 'text-primary-600 font-medium' : 'text-gray-500'}>
              Document
            </span>
            <span className={step >= 3 ? 'text-primary-600 font-medium' : 'text-gray-500'}>
              Selfie
            </span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="w-5 h-5 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Step 1: Customer ID */}
        {step === 1 && (
          <div className="card max-w-md mx-auto">
            <h2 className="text-xl font-semibold mb-4">Enter Your Customer ID</h2>
            <p className="text-gray-600 mb-6">
              This is the unique identifier provided by your financial institution.
            </p>
            <input
              type="text"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              placeholder="e.g., CUST-123456"
              className="input mb-6"
            />
            <button
              onClick={() => setStep(2)}
              disabled={!customerId}
              className="btn btn-primary w-full"
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 2: Document Upload */}
        {step === 2 && (
          <div className="card max-w-md mx-auto">
            <h2 className="text-xl font-semibold mb-4">Upload Your ID Document</h2>
            <p className="text-gray-600 mb-6">
              Please upload a clear photo of your ID card, passport, or driver's license.
            </p>
            
            <div className="mb-6">
              <label className="block cursor-pointer">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleDocumentChange}
                  className="hidden"
                />
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
                  {documentPreview ? (
                    <img src={documentPreview} alt="Document preview" className="max-h-64 mx-auto rounded" />
                  ) : (
                    <>
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">Click to upload or drag and drop</p>
                      <p className="text-sm text-gray-500 mt-2">PNG, JPG up to 10MB</p>
                    </>
                  )}
                </div>
              </label>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h4 className="font-medium text-blue-900 mb-2">📸 Tips for a great photo:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Ensure good lighting without glare</li>
                <li>• Document should be clearly visible and in focus</li>
                <li>• All four corners should be visible</li>
                <li>• Text should be readable</li>
              </ul>
            </div>

            <div className="flex space-x-3">
              <button onClick={() => setStep(1)} className="btn btn-secondary flex-1">
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={!document}
                className="btn btn-primary flex-1"
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Selfie */}
        {step === 3 && (
          <div className="card max-w-md mx-auto">
            <h2 className="text-xl font-semibold mb-4">Take a Selfie</h2>
            <p className="text-gray-600 mb-6">
              Take a clear selfie to verify your identity matches the document.
            </p>
            
            <div className="mb-6">
              <label className="block cursor-pointer">
                <input
                  type="file"
                  accept="image/*"
                  capture="user"
                  onChange={handleSelfieChange}
                  className="hidden"
                />
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
                  {selfiePreview ? (
                    <img src={selfiePreview} alt="Selfie preview" className="max-h-64 mx-auto rounded" />
                  ) : (
                    <>
                      <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">Click to take a selfie</p>
                      <p className="text-sm text-gray-500 mt-2">Make sure your face is clearly visible</p>
                    </>
                  )}
                </div>
              </label>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h4 className="font-medium text-blue-900 mb-2">🤳 Selfie guidelines:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Look directly at the camera</li>
                <li>• Remove sunglasses and hats</li>
                <li>• Ensure face is well-lit and in focus</li>
                <li>• No one else should be in the photo</li>
              </ul>
            </div>

            <div className="flex space-x-3">
              <button onClick={() => setStep(2)} className="btn btn-secondary flex-1">
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!selfie || loading}
                className="btn btn-primary flex-1 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Submit Application'
                )}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

