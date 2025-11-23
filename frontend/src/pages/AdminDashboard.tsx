import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, CheckCircle, XCircle, Clock, TrendingUp, ArrowLeft, Eye } from 'lucide-react'
import { kycApi, Statistics } from '../services/api'

interface PendingApplication {
  id: string
  customer_id: string
  status: string
  created_at: string
  risk_assessment: any
  extracted_data: any
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<Statistics | null>(null)
  const [pendingApps, setPendingApps] = useState<PendingApplication[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, pendingData] = await Promise.all([
          kycApi.getStatistics(),
          kycApi.getPendingApplications(),
        ])
        setStats(statsData)
        setPendingApps(pendingData.applications || [])
      } catch (err) {
        console.error('Failed to fetch data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">KYC Application Management</p>
            </div>
            <Link to="/" className="inline-flex items-center text-gray-600 hover:text-primary-600 transition-colors">
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Home
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600">Total Applications</p>
              <Users className="w-5 h-5 text-gray-400" />
            </div>
            <p className="text-3xl font-bold">{stats?.total_applications || 0}</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600">Approved</p>
              <CheckCircle className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-green-600">{stats?.approved || 0}</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600">Under Review</p>
              <Clock className="w-5 h-5 text-yellow-500" />
            </div>
            <p className="text-3xl font-bold text-yellow-600">{stats?.under_review || 0}</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600">Rejected</p>
              <XCircle className="w-5 h-5 text-red-500" />
            </div>
            <p className="text-3xl font-bold text-red-600">{stats?.rejected || 0}</p>
          </div>
        </div>

        {/* Automation Statistics */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Auto-Approval Rate</h3>
              <TrendingUp className="w-5 h-5 text-primary-600" />
            </div>
            <div className="flex items-end">
              <p className="text-4xl font-bold text-primary-600">
                {stats?.auto_approval_rate.toFixed(1) || 0}%
              </p>
              <p className="text-gray-600 ml-2 mb-1">of applications</p>
            </div>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full"
                style={{ width: `${stats?.auto_approval_rate || 0}%` }}
              ></div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Manual Review Rate</h3>
              <Eye className="w-5 h-5 text-yellow-600" />
            </div>
            <div className="flex items-end">
              <p className="text-4xl font-bold text-yellow-600">
                {stats?.manual_review_rate.toFixed(1) || 0}%
              </p>
              <p className="text-gray-600 ml-2 mb-1">require review</p>
            </div>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div
                className="bg-yellow-600 h-2 rounded-full"
                style={{ width: `${stats?.manual_review_rate || 0}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Pending Applications Table */}
        <div className="card">
          <h2 className="text-xl font-bold mb-6">Pending Manual Review</h2>
          
          {pendingApps.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <p className="text-xl font-semibold text-gray-900 mb-2">All Caught Up!</p>
              <p className="text-gray-600">No applications pending review at this time.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Application ID</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Customer ID</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Submitted</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Risk Level</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingApps.map((app) => (
                    <tr key={app.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4">
                        <span className="font-mono text-sm">{app.id.slice(0, 8)}...</span>
                      </td>
                      <td className="py-4 px-4 text-gray-700">{app.customer_id}</td>
                      <td className="py-4 px-4 text-gray-600 text-sm">
                        {new Date(app.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-4 px-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            app.risk_assessment?.risk_level === 'low'
                              ? 'bg-green-100 text-green-800'
                              : app.risk_assessment?.risk_level === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {app.risk_assessment?.risk_level || 'N/A'}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-700">
                        {app.extracted_data?.full_name?.value || 'N/A'}
                      </td>
                      <td className="py-4 px-4">
                        <Link
                          to={`/admin/review/${app.id}`}
                          className="inline-flex items-center px-3 py-1.5 bg-primary-600 text-white text-sm font-medium rounded hover:bg-primary-700 transition-colors"
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          Review
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

