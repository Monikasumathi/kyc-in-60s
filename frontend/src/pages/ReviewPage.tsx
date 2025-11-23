import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { CheckCircle, XCircle, ArrowLeft, AlertCircle, FileText, User, Shield, Image as ImageIcon } from 'lucide-react'
import { kycApi, ApplicationStatus } from '../services/api'

export default function ReviewPage() {
  const { applicationId } = useParams<{ applicationId: string }>()
  const navigate = useNavigate()
  const [application, setApplication] = useState<ApplicationStatus | null>(null)
  const [auditTrail, setAuditTrail] = useState<any>(null)
  const [reviewerId, setReviewerId] = useState('')
  const [notes, setNotes] = useState('')
  const [decision, setDecision] = useState<'approved' | 'rejected' | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      if (!applicationId) return

      try {
        const [appData, auditData] = await Promise.all([
          kycApi.getStatus(applicationId),
          kycApi.getAuditTrail(applicationId),
        ])
        setApplication(appData)
        setAuditTrail(auditData)
      } catch (err) {
        console.error('Failed to fetch data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [applicationId])

  const handleSubmitReview = async () => {
    if (!reviewerId || !notes || !decision || !applicationId) {
      alert('Please fill in all fields')
      return
    }

    setSubmitting(true)
    try {
      await kycApi.submitReview({
        application_id: applicationId,
        reviewer_id: reviewerId,
        decision,
        notes,
      })
      alert('Review submitted successfully!')
      navigate('/admin')
    } catch (err: any) {
      alert('Failed to submit review: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading application...</p>
        </div>
      </div>
    )
  }

  if (!application) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="card max-w-md">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Application Not Found</h2>
            <Link to="/admin" className="btn btn-primary">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const extractedData = application.risk_assessment?.factors || {}
  const riskAssessment = application.risk_assessment

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Application Review</h1>
              <p className="text-gray-600 font-mono text-sm">{applicationId}</p>
            </div>
            <Link to="/admin" className="inline-flex items-center text-gray-600 hover:text-primary-600 transition-colors">
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column: Application Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Risk Assessment */}
            <div className="card">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                Risk Assessment
              </h2>
              
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Risk Level</p>
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      riskAssessment?.risk_level === 'low'
                        ? 'bg-green-100 text-green-800'
                        : riskAssessment?.risk_level === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {riskAssessment?.risk_level || 'N/A'}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Risk Score</p>
                  <p className="text-2xl font-bold">
                    {riskAssessment?.score ? (riskAssessment.score * 100).toFixed(1) : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Confidence</p>
                  <p className="text-2xl font-bold">
                    {riskAssessment?.confidence ? (riskAssessment.confidence * 100).toFixed(1) + '%' : 'N/A'}
                  </p>
                </div>
              </div>

              {riskAssessment?.reason_codes && riskAssessment.reason_codes.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-2">Risk Factors</p>
                  <div className="flex flex-wrap gap-2">
                    {riskAssessment.reason_codes.map((code: string, index: number) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-red-50 text-red-700 text-sm rounded border border-red-200"
                      >
                        {code.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm font-semibold text-blue-900 mb-2">Component Scores</p>
                <div className="space-y-2">
                  {Object.entries(extractedData).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex justify-between items-center text-sm">
                      <span className="text-blue-800 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="font-mono font-semibold text-blue-900">
                        {typeof value === 'number' ? (value * 100).toFixed(1) + '%' : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Extracted Data */}
            <div className="card">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <User className="w-5 h-5 mr-2" />
                Extracted Information
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                {Object.entries((application as any).extracted_data || {}).map(([key, field]: [string, any]) => (
                  <div key={key}>
                    <p className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</p>
                    <p className="font-semibold">{field.value || 'N/A'}</p>
                    <p className="text-xs text-gray-500">
                      Confidence: {field.confidence ? (field.confidence * 100).toFixed(1) + '%' : 'N/A'}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quality Checks */}
            {(application as any).quality_checks && (
              <div className="card">
                <h2 className="text-xl font-semibold mb-4 flex items-center">
                  <ImageIcon className="w-5 h-5 mr-2" />
                  Image Quality Checks
                </h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Overall Quality</span>
                    {(application as any).quality_checks.is_acceptable ? (
                      <span className="flex items-center text-green-600">
                        <CheckCircle className="w-5 h-5 mr-1" />
                        Acceptable
                      </span>
                    ) : (
                      <span className="flex items-center text-red-600">
                        <XCircle className="w-5 h-5 mr-1" />
                        Issues Found
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Blur Score</p>
                      <p className="font-semibold">{(application as any).quality_checks.blur_score?.toFixed(1)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Glare Score</p>
                      <p className="font-semibold">{(application as any).quality_checks.glare_score?.toFixed(1)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Crop Score</p>
                      <p className="font-semibold">{((application as any).quality_checks.crop_score * 100)?.toFixed(1)}%</p>
                    </div>
                  </div>

                  {(application as any).quality_checks.issues?.length > 0 && (
                    <div className="p-3 bg-yellow-50 rounded border border-yellow-200">
                      <p className="text-sm font-semibold text-yellow-900 mb-1">Issues</p>
                      <ul className="text-sm text-yellow-800 space-y-1">
                        {(application as any).quality_checks.issues.map((issue: string, i: number) => (
                          <li key={i}>• {issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Audit Trail */}
            {auditTrail && (
              <div className="card">
                <h2 className="text-xl font-semibold mb-4 flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Audit Trail
                </h2>
                <div className="space-y-3">
                  {auditTrail.timeline?.map((event: any, index: number) => (
                    <div key={index} className="flex items-start border-l-2 border-gray-300 pl-4 py-2">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{event.action.replace(/_/g, ' ')}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(event.timestamp).toLocaleString()}
                        </p>
                        {event.outcome && (
                          <p className="text-sm text-gray-700 mt-1">Outcome: {event.outcome}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Review Form */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <h2 className="text-xl font-semibold mb-6">Submit Review</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Reviewer ID
                  </label>
                  <input
                    type="text"
                    value={reviewerId}
                    onChange={(e) => setReviewerId(e.target.value)}
                    placeholder="Your reviewer ID"
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Decision
                  </label>
                  <div className="space-y-2">
                    <button
                      onClick={() => setDecision('approved')}
                      className={`w-full flex items-center justify-center px-4 py-3 rounded-lg border-2 transition-all ${
                        decision === 'approved'
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : 'border-gray-200 hover:border-green-300'
                      }`}
                    >
                      <CheckCircle className="w-5 h-5 mr-2" />
                      Approve Application
                    </button>
                    <button
                      onClick={() => setDecision('rejected')}
                      className={`w-full flex items-center justify-center px-4 py-3 rounded-lg border-2 transition-all ${
                        decision === 'rejected'
                          ? 'border-red-500 bg-red-50 text-red-700'
                          : 'border-gray-200 hover:border-red-300'
                      }`}
                    >
                      <XCircle className="w-5 h-5 mr-2" />
                      Reject Application
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Review Notes
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Provide detailed notes about your decision..."
                    rows={6}
                    className="input"
                  />
                </div>

                <button
                  onClick={handleSubmitReview}
                  disabled={!reviewerId || !notes || !decision || submitting}
                  className="btn btn-primary w-full"
                >
                  {submitting ? 'Submitting...' : 'Submit Review'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

