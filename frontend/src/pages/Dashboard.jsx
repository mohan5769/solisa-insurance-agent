import { useState, useEffect } from 'react'
import axios from 'axios'
import { Users, MessageSquare, Mail, Calendar, TrendingUp, X, Eye, CheckCircle } from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [leads, setLeads] = useState([])
  const [selectedLead, setSelectedLead] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    try {
      const [statsRes, leadsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/stats'),
        axios.get('http://localhost:8000/api/leads')
      ])
      setStats(statsRes.data)
      setLeads(leadsRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleViewDetails = (lead) => {
    setSelectedLead(lead)
    setShowModal(true)
  }

  const handleSimulateBooking = async (leadId) => {
    try {
      await axios.post(`http://localhost:8000/api/leads/${leadId}/book`)
      fetchData() // Refresh data
      alert('Meeting booked successfully!')
    } catch (error) {
      console.error('Error booking meeting:', error)
      alert('Error booking meeting')
    }
  }

  const getTimeAgo = (timestamp) => {
    if (!timestamp) return 'N/A'
    const date = new Date(timestamp)
    const seconds = Math.floor((new Date() - date) / 1000)
    
    if (seconds < 60) return `${seconds}s ago`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Monitor your AI SDR performance in real-time</p>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <Users className="w-8 h-8 text-primary-500" />
                <span className="text-2xl font-bold text-gray-900">{stats.total_leads}</span>
              </div>
              <p className="text-sm text-gray-600 font-medium">Total Leads</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <MessageSquare className="w-8 h-8 text-secondary-500" />
                <span className="text-2xl font-bold text-gray-900">{stats.sms_sent}</span>
              </div>
              <p className="text-sm text-gray-600 font-medium">SMS Sent</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <Mail className="w-8 h-8 text-purple-500" />
                <span className="text-2xl font-bold text-gray-900">{stats.emails_sent}</span>
              </div>
              <p className="text-sm text-gray-600 font-medium">Emails Sent</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <Calendar className="w-8 h-8 text-yellow-500" />
                <span className="text-2xl font-bold text-gray-900">{stats.meetings_booked}</span>
              </div>
              <p className="text-sm text-gray-600 font-medium">Meetings Booked</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="w-8 h-8 text-red-500" />
                <span className="text-2xl font-bold text-gray-900">{stats.conversion_rate}%</span>
              </div>
              <p className="text-sm text-gray-600 font-medium">Conversion Rate</p>
            </div>
          </div>
        )}

        {/* Leads Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Recent Leads</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Lead Info
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Insurance Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {leads.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                      No leads yet. Submit a lead from the landing page to get started!
                    </td>
                  </tr>
                ) : (
                  leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-gray-900">{lead.full_name}</div>
                          <div className="text-sm text-gray-500">{lead.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                          {lead.insurance_type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col space-y-1">
                          {lead.sms_sent && (
                            <span className="inline-flex items-center text-xs text-secondary-600">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              SMS
                            </span>
                          )}
                          {lead.email_sent && (
                            <span className="inline-flex items-center text-xs text-purple-600">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Email
                            </span>
                          )}
                          {lead.booking_confirmed && (
                            <span className="inline-flex items-center text-xs text-yellow-600">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Booked
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {getTimeAgo(lead.created_at)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleViewDetails(lead)}
                            className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </button>
                          {!lead.booking_confirmed && (
                            <button
                              onClick={() => handleSimulateBooking(lead.id)}
                              className="inline-flex items-center px-3 py-1 border border-transparent rounded-md text-sm font-medium text-white bg-secondary-600 hover:bg-secondary-700"
                            >
                              <Calendar className="w-4 h-4 mr-1" />
                              Book
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Lead Details Modal */}
      {showModal && selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-2xl font-bold text-gray-900">Lead Details</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Contact Info */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Contact Information</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Full Name</p>
                    <p className="font-medium">{selectedLead.full_name}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Email</p>
                    <p className="font-medium">{selectedLead.email}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Phone</p>
                    <p className="font-medium">{selectedLead.phone}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Insurance Type</p>
                    <p className="font-medium">{selectedLead.insurance_type}</p>
                  </div>
                </div>
              </div>

              {/* Enriched Data */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Enriched Profile</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Life Stage</p>
                    <p className="font-medium">{selectedLead.life_stage || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Age Range</p>
                    <p className="font-medium">{selectedLead.estimated_age_range || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Current Provider</p>
                    <p className="font-medium">{selectedLead.current_provider || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Renewal Date</p>
                    <p className="font-medium">{selectedLead.renewal_date || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Estimated Savings</p>
                    <p className="font-medium text-secondary-600">
                      ${selectedLead.estimated_savings || 0}/year
                    </p>
                  </div>
                </div>
                
                {selectedLead.pain_points && selectedLead.pain_points.length > 0 && (
                  <div className="mt-4">
                    <p className="text-gray-500 mb-2">Pain Points</p>
                    <ul className="list-disc list-inside space-y-1">
                      {selectedLead.pain_points.map((point, index) => (
                        <li key={index} className="text-sm text-gray-700">{point}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Communication Timeline */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Communication Timeline</h3>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">Lead Created</p>
                      <p className="text-xs text-gray-500">{getTimeAgo(selectedLead.created_at)}</p>
                    </div>
                  </div>

                  {selectedLead.sms_sent && (
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-2 h-2 bg-secondary-500 rounded-full mt-2 mr-3"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">SMS Sent</p>
                        <p className="text-xs text-gray-500">{getTimeAgo(selectedLead.sms_sent_at)}</p>
                        {selectedLead.sms_content && (
                          <p className="text-sm text-gray-600 mt-1 bg-gray-50 p-2 rounded">
                            {selectedLead.sms_content}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {selectedLead.email_sent && (
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Email Sent</p>
                        <p className="text-xs text-gray-500">{getTimeAgo(selectedLead.email_sent_at)}</p>
                        {selectedLead.email_subject && (
                          <div className="mt-1 bg-gray-50 p-2 rounded">
                            <p className="text-sm font-medium text-gray-700">
                              Subject: {selectedLead.email_subject}
                            </p>
                            {selectedLead.email_content && (
                              <p className="text-xs text-gray-600 mt-1 whitespace-pre-wrap">
                                {selectedLead.email_content.substring(0, 200)}...
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {selectedLead.booking_confirmed && (
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Meeting Booked</p>
                        <p className="text-xs text-gray-500">{getTimeAgo(selectedLead.booking_confirmed_at)}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => setShowModal(false)}
                className="w-full bg-primary-600 text-white py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
