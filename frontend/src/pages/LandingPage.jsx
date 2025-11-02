import { useState } from 'react'
import axios from 'axios'
import { Sparkles, Shield, Zap, Mail, MessageSquare, Calendar, CheckCircle2, Loader2, ArrowRight, TrendingUp } from 'lucide-react'

export default function LandingPage() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    insurance_type: 'Auto',
    current_provider: ''
  })
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showTimeline, setShowTimeline] = useState(false)
  const [timelineEvents, setTimelineEvents] = useState([])
  const [showSuccess, setShowSuccess] = useState(false)
  const [leadData, setLeadData] = useState(null)

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const addTimelineEvent = (event, delay = 0) => {
    setTimeout(() => {
      setTimelineEvents(prev => [...prev, event])
    }, delay)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setShowTimeline(true)
    setTimelineEvents([])

    // Add timeline events with delays
    addTimelineEvent({ text: '📝 Form submitted', time: 'Just now', icon: CheckCircle2 }, 0)
    addTimelineEvent({ text: '🔍 Enriching lead data...', time: '0.5s', icon: Sparkles }, 500)
    addTimelineEvent({ text: '🤖 AI analyzing your profile...', time: '1.0s', icon: Zap }, 1000)
    addTimelineEvent({ text: '📱 Generating personalized SMS...', time: '1.5s', icon: MessageSquare }, 1500)
    addTimelineEvent({ text: '📧 Crafting personalized email...', time: '2.0s', icon: Mail }, 2000)

    try {
      const response = await axios.post('http://localhost:8000/api/leads', formData)
      
      addTimelineEvent({ text: '✅ SMS sent successfully!', time: '2.5s', icon: CheckCircle2 }, 2500)
      addTimelineEvent({ text: '✅ Email sent successfully!', time: '3.0s', icon: CheckCircle2 }, 3000)
      addTimelineEvent({ text: '🎉 All done! Check your inbox.', time: '3.5s', icon: CheckCircle2 }, 3500)

      setTimeout(() => {
        setLeadData(response.data)
        setShowSuccess(true)
        setIsSubmitting(false)
      }, 4000)

    } catch (error) {
      console.error('Error submitting form:', error)
      addTimelineEvent({ text: '❌ Error: ' + (error.response?.data?.detail || 'Something went wrong'), time: 'Error', icon: CheckCircle2 }, 2500)
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background Decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold mb-6">
              <Sparkles className="w-4 h-4" />
              AI-Powered Insurance Outreach
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Insurance That
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-blue-400"> Actually Cares</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
              Experience the future of insurance with AI-powered personalization. 
              Get instant quotes, personalized recommendations, and seamless communication.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-blue-100 hover:shadow-xl transition-all hover:-translate-y-1">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Instant AI Analysis</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Our AI analyzes your profile in seconds to find the perfect coverage for your life stage.
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-blue-100 hover:shadow-xl transition-all hover:-translate-y-1">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                <MessageSquare className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Personalized Outreach</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Receive tailored SMS and email with quotes designed specifically for you.
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-blue-100 hover:shadow-xl transition-all hover:-translate-y-1">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Better Coverage</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Save an average of $704/year while getting superior protection.
              </p>
            </div>
          </div>

          {/* Main Content - Form and Timeline */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Side - Form */}
            <div className="bg-white rounded-3xl shadow-2xl p-8 border border-blue-100">
              <div className="mb-6">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Get Your Free Quote</h2>
                <p className="text-gray-600">Fill out the form below and see our AI in action</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Full Name */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all"
                    placeholder="John Smith"
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all"
                    placeholder="john@example.com"
                  />
                </div>

                {/* Phone */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>

                {/* Insurance Type */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Insurance Type
                  </label>
                  <select
                    name="insurance_type"
                    value={formData.insurance_type}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all bg-white"
                  >
                    <option value="Auto">Auto Insurance</option>
                    <option value="Home">Home Insurance</option>
                    <option value="Life">Life Insurance</option>
                    <option value="Health">Health Insurance</option>
                  </select>
                </div>

                {/* Current Provider */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Current Provider (Optional)
                  </label>
                  <input
                    type="text"
                    name="current_provider"
                    value={formData.current_provider}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all"
                    placeholder="Geico, State Farm, etc."
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-blue-600 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 group"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      Get My Free Quote
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </form>

              {/* Trust Indicators */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>No spam</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>Instant quotes</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>AI-powered</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Side - Timeline */}
            <div className="space-y-6">
              {/* Timeline Card */}
              {showTimeline && (
                <div className="bg-white rounded-3xl shadow-2xl p-8 border border-blue-100">
                  <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                    Real-Time Progress
                  </h3>
                  
                  <div className="space-y-4">
                    {timelineEvents.map((event, index) => (
                      <div
                        key={index}
                        className="flex items-start gap-4 animate-fade-in"
                      >
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                        </div>
                        <div className="flex-1">
                          <p className="text-gray-900 font-medium">{event.text}</p>
                          <p className="text-sm text-gray-500">{event.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Success Card */}
              {showSuccess && leadData && (
                <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-3xl shadow-2xl p-8 border-2 border-green-200 animate-fade-in">
                  <div className="text-center mb-6">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <CheckCircle2 className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">Success! 🎉</h3>
                    <p className="text-gray-600">Your personalized quote is on its way!</p>
                  </div>

                  <div className="space-y-4">
                    <div className="bg-white rounded-xl p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <MessageSquare className="w-5 h-5 text-blue-600" />
                        <span className="font-semibold text-gray-900">SMS Sent</span>
                      </div>
                      <p className="text-sm text-gray-600 pl-8">
                        Check your phone for a personalized message
                      </p>
                    </div>

                    <div className="bg-white rounded-xl p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <Mail className="w-5 h-5 text-blue-600" />
                        <span className="font-semibold text-gray-900">Email Sent</span>
                      </div>
                      <p className="text-sm text-gray-600 pl-8">
                        Detailed quote sent to {leadData.email}
                      </p>
                    </div>

                    <div className="bg-white rounded-xl p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <Calendar className="w-5 h-5 text-blue-600" />
                        <span className="font-semibold text-gray-900">Book a Call</span>
                      </div>
                      <p className="text-sm text-gray-600 pl-8 mb-3">
                        Schedule a call to discuss your options
                      </p>
                      <a
                        href={leadData.calendly_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold text-center hover:bg-blue-700 transition-colors"
                      >
                        Schedule Now
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {/* Info Card */}
              {!showTimeline && (
                <div className="bg-gradient-to-br from-blue-600 to-blue-500 rounded-3xl shadow-2xl p-8 text-white">
                  <h3 className="text-2xl font-bold mb-4">Why Choose Solisa?</h3>
                  <ul className="space-y-4">
                    <li className="flex items-start gap-3">
                      <CheckCircle2 className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold">AI-Powered Matching</p>
                        <p className="text-blue-100 text-sm">Find the perfect coverage for your unique situation</p>
                      </div>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle2 className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold">Instant Personalization</p>
                        <p className="text-blue-100 text-sm">Get quotes tailored to your life stage and needs</p>
                      </div>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle2 className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold">Average $704/year Savings</p>
                        <p className="text-blue-100 text-sm">Most customers save significantly on their premiums</p>
                      </div>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle2 className="w-6 h-6 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold">24/7 Support</p>
                        <p className="text-blue-100 text-sm">Our AI and human team are always here to help</p>
                      </div>
                    </li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">10k+</div>
              <div className="text-gray-600">Happy Customers</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">$704</div>
              <div className="text-gray-600">Avg. Yearly Savings</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">98%</div>
              <div className="text-gray-600">Satisfaction Rate</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">24/7</div>
              <div className="text-gray-600">AI Support</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
