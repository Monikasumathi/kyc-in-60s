import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { CheckCircle, XCircle, Clock, AlertCircle, Loader2, ArrowLeft, FileText, Sparkles, Bot } from 'lucide-react'
import { kycApi, ApplicationStatus } from '../services/api'

export default function StatusPage() {
  const { applicationId } = useParams<{ applicationId: string }>()
  const [status, setStatus] = useState<ApplicationStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      if (!applicationId) return
      
      try {
        const data = await kycApi.getStatus(applicationId)
        setStatus(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch application status')
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
    // Poll for updates every 10 seconds if under review
    const interval = setInterval(fetchStatus, 10000)
    return () => clearInterval(interval)
  }, [applicationId])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading application status...</p>
        </div>
      </div>
    )
  }

  if (error || !status) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 flex items-center justify-center">
        <div className="card max-w-md">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Error</h2>
            <p className="text-gray-600 mb-6">{error || 'Application not found'}</p>
            <Link to="/" className="btn btn-primary">
              Return to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'approved':
        return <CheckCircle className="w-20 h-20 text-green-500" />
      case 'rejected':
        return <XCircle className="w-20 h-20 text-red-500" />
      case 'under_review':
        return <Clock className="w-20 h-20 text-yellow-500 animate-pulse-slow" />
      default:
        return <Clock className="w-20 h-20 text-blue-500" />
    }
  }

  const getStatusMessage = () => {
    switch (status.status) {
      case 'approved':
        return {
          title: 'Application Approved! 🎉',
          message: 'Your KYC verification is complete. Your account is now active.',
          color: 'green',
        }
      case 'rejected':
        return {
          title: 'Application Rejected',
          message: 'Unfortunately, we couldn\'t verify your identity at this time.',
          color: 'red',
        }
      case 'under_review':
        return {
          title: 'Under Review',
          message: 'Our team is reviewing your application. You\'ll hear from us within 24 hours.',
          color: 'yellow',
        }
      default:
        return {
          title: 'Processing',
          message: 'Your application is being processed.',
          color: 'blue',
        }
    }
  }

  const statusInfo = getStatusMessage()
  const riskAssessment = status.risk_assessment

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
        {/* Status Card */}
        <div className="card text-center mb-8">
          <div className="mb-6">{getStatusIcon()}</div>
          <h1 className={`text-3xl font-bold mb-2 text-${statusInfo.color}-600`}>
            {statusInfo.title}
          </h1>
          <p className="text-xl text-gray-600 mb-6">{statusInfo.message}</p>
          
          <div className="inline-block bg-gray-100 rounded-lg px-6 py-3">
            <p className="text-sm text-gray-600">Application ID</p>
            <p className="font-mono font-semibold">{applicationId}</p>
          </div>
        </div>

        {/* Timeline */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Application Timeline
          </h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="w-3 h-3 bg-green-500 rounded-full mt-1.5 mr-4"></div>
              <div className="flex-1">
                <p className="font-medium">Application Submitted</p>
                <p className="text-sm text-gray-600">
                  {new Date(status.created_at).toLocaleString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className={`w-3 h-3 rounded-full mt-1.5 mr-4 ${
                status.status === 'approved' || status.status === 'rejected' 
                  ? 'bg-green-500' 
                  : 'bg-yellow-500 animate-pulse'
              }`}></div>
              <div className="flex-1">
                <p className="font-medium">
                  {status.status === 'under_review' ? 'Under Review' : 'Review Complete'}
                </p>
                <p className="text-sm text-gray-600">
                  {status.status === 'under_review' 
                    ? 'In progress...' 
                    : new Date(status.updated_at).toLocaleString()
                  }
                </p>
              </div>
            </div>

            {(status.status === 'approved' || status.status === 'rejected') && (
              <div className="flex items-start">
                <div className="w-3 h-3 bg-green-500 rounded-full mt-1.5 mr-4"></div>
                <div className="flex-1">
                  <p className="font-medium">Decision Made</p>
                  <p className="text-sm text-gray-600">
                    Status: <span className="font-semibold capitalize">{status.status}</span>
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* AI Agent Insights - NEW! */}
        {(status as any).ai_agent_insights && (
          <div className="card mb-8 bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
            <div className="flex items-center mb-4">
              <Bot className="w-6 h-6 text-purple-600 mr-2" />
              <h2 className="text-xl font-semibold text-purple-900">AI Agent Analysis</h2>
              <Sparkles className="w-5 h-5 text-yellow-500 ml-2" />
            </div>
            
            <div className="bg-white rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-purple-700">
                  Agent Recommendation: {(status as any).ai_agent_insights.recommendation}
                </span>
                <span className="text-sm font-semibold text-purple-900">
                  Confidence: {((status as any).ai_agent_insights.confidence * 100).toFixed(0)}%
                </span>
              </div>
              
              {/* Risk Summary from Risk Intelligence Agent */}
              {(status as any).ai_agent_insights.risk_summary && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">🔍 Risk Analysis:</h3>
                  <div className="prose prose-sm max-w-none">
                    <div className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-3 rounded border border-gray-200">
                      {(status as any).ai_agent_insights.risk_summary}
                    </div>
                  </div>
                </div>
              )}
              
              {/* Customer Message from CX Agent */}
              {(status as any).ai_agent_insights.customer_message && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">💬 Message for You:</h3>
                  <div className="prose prose-sm max-w-none">
                    <div className="whitespace-pre-wrap text-sm text-gray-700 bg-blue-50 p-3 rounded border border-blue-200">
                      {(status as any).ai_agent_insights.customer_message}
                    </div>
                  </div>
                </div>
              )}
              
              {/* Next Steps */}
              {(status as any).ai_agent_insights.next_steps && (
                <div className="mb-2">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">📋 Next Steps:</h3>
                  <div className="text-sm text-gray-600 bg-green-50 p-3 rounded border border-green-200">
                    {(status as any).ai_agent_insights.next_steps}
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex items-center text-xs text-purple-600">
              <span>✓ Analyzed by: {(status as any).ai_agent_insights.agents_used?.join(' & ')}</span>
            </div>
          </div>
        )}

        {/* Risk Assessment Details */}
        {riskAssessment && (
          <div className="card mb-8">
            <h2 className="text-xl font-semibold mb-4">Verification Details</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Risk Level</p>
                <p className="font-semibold capitalize flex items-center">
                  <span className={`w-3 h-3 rounded-full mr-2 ${
                    riskAssessment.risk_level === 'low' ? 'bg-green-500' :
                    riskAssessment.risk_level === 'medium' ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}></span>
                  {riskAssessment.risk_level}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Confidence Score</p>
                <p className="font-semibold">
                  {(riskAssessment.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {riskAssessment.reason_codes && riskAssessment.reason_codes.length > 0 && (
              <div className="mt-6">
                <p className="text-sm text-gray-600 mb-2">Assessment Factors</p>
                <div className="flex flex-wrap gap-2">
                  {riskAssessment.reason_codes.map((code: string, index: number) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                    >
                      {code.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Next Steps */}
        {status.status === 'approved' && (
          <div className="card bg-green-50 border-green-200">
            <h3 className="font-semibold text-green-900 mb-3">🎉 Next Steps</h3>
            <ul className="space-y-2 text-green-800">
              <li>• Your account is now active and ready to use</li>
              <li>• Check your email for welcome information</li>
              <li>• You can now access all banking services</li>
            </ul>
          </div>
        )}

        {status.status === 'under_review' && (
          <div className="card bg-yellow-50 border-yellow-200">
            <h3 className="font-semibold text-yellow-900 mb-3">⏳ What's Next?</h3>
            <ul className="space-y-2 text-yellow-800">
              <li>• Our team is carefully reviewing your application</li>
              <li>• This typically takes up to 24 hours</li>
              <li>• We may contact you if we need additional information</li>
              <li>• You'll receive an email once the review is complete</li>
            </ul>
          </div>
        )}

        {status.reviewer_notes && (
          <div className="card bg-blue-50 border-blue-200 mt-6">
            <h3 className="font-semibold text-blue-900 mb-2">Reviewer Notes</h3>
            <p className="text-blue-800">{status.reviewer_notes}</p>
          </div>
        )}
      </main>
    </div>
  )
}

