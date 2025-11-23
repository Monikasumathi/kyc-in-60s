import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface KYCSubmissionResponse {
  application_id: string
  status: string
  message: string
  next_steps: string[]
  decision?: any
  estimated_time?: string
}

export interface ApplicationStatus {
  application_id: string
  status: string
  created_at: string
  updated_at: string
  risk_assessment: any
  decision: any
  reviewer_notes?: string
}

export interface ReviewDecision {
  application_id: string
  reviewer_id: string
  decision: 'approved' | 'rejected'
  notes: string
}

export interface Statistics {
  total_applications: number
  approved: number
  rejected: number
  under_review: number
  auto_approval_rate: number
  manual_review_rate: number
}

export const kycApi = {
  // Submit KYC application
  submitKYC: async (
    customerId: string,
    document: File,
    selfie: File
  ): Promise<KYCSubmissionResponse> => {
    const formData = new FormData()
    formData.append('customer_id', customerId)
    formData.append('document', document)
    formData.append('selfie', selfie)

    const response = await api.post('/api/kyc/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Get application status
  getStatus: async (applicationId: string): Promise<ApplicationStatus> => {
    const response = await api.get(`/api/kyc/status/${applicationId}`)
    return response.data
  },

  // Get audit trail
  getAuditTrail: async (applicationId: string) => {
    const response = await api.get(`/api/kyc/audit/${applicationId}`)
    return response.data
  },

  // Get pending applications
  getPendingApplications: async (skip = 0, limit = 50) => {
    const response = await api.get('/api/kyc/pending', {
      params: { skip, limit },
    })
    return response.data
  },

  // Submit review decision
  submitReview: async (review: ReviewDecision) => {
    const response = await api.post('/api/kyc/review', review)
    return response.data
  },

  // Get statistics
  getStatistics: async (): Promise<Statistics> => {
    const response = await api.get('/api/stats')
    return response.data
  },
}

export default api

