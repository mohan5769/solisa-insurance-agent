import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowLeft, Heart, TrendingUp, Baby, Home, Car, Briefcase, Calendar, MessageSquare, CheckCircle, Clock, AlertCircle, X, Send } from 'lucide-react';

export default function LifelineRetention() {
  const [activeTab, setActiveTab] = useState('life_events'); // 'life_events' or 'occasions'
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [lifeEvents, setLifeEvents] = useState([]);
  const [occasions, setOccasions] = useState([]);
  const [policyHealth, setPolicyHealth] = useState(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [showResponseModal, setShowResponseModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [selectedOccasion, setSelectedOccasion] = useState(null);
  const [customerResponse, setCustomerResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  useEffect(() => {
    loadLeads();
    loadAllLifeEvents();
    loadOccasions();
  }, []);

  const showToastNotification = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 5000);
  };

  const loadLeads = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/leads');
      setLeads(response.data);
    } catch (error) {
      console.error('Error loading leads:', error);
    }
  };

  const loadAllLifeEvents = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/life-events');
      setLifeEvents(response.data.life_events || []);
    } catch (error) {
      console.error('Error loading life events:', error);
    }
  };

  const loadPolicyHealth = async (leadId) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/leads/${leadId}/policy-health`);
      setPolicyHealth(response.data.policy_health);
    } catch (error) {
      console.error('Error loading policy health:', error);
    }
  };

  const selectLead = (lead) => {
    setSelectedLead(lead);
    loadPolicyHealth(lead.id);
  };

  const triggerLifeEvent = async (eventType) => {
    if (!selectedLead) {
      showToastNotification('Please select a lead first', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/leads/${selectedLead.id}/life-event`,
        {
          event_type: eventType,
          event_date: new Date().toISOString(),
          description: `${eventType.replace('_', ' ')} detected`,
          source: 'manual'
        }
      );

      showToastNotification(`✅ Life event triggered! SMS sent to ${selectedLead.full_name}`, 'success');
      setShowEventModal(false);
      loadAllLifeEvents();
      loadPolicyHealth(selectedLead.id);
    } catch (error) {
      console.error('Error triggering life event:', error);
      showToastNotification('❌ Error triggering life event', 'error');
    }
    setLoading(false);
  };

  const respondToEvent = async () => {
    if (!customerResponse.trim()) {
      showToastNotification('Please enter a response', 'error');
      return;
    }

    setLoading(true);
    try {
      // Determine if it's a life event or occasion
      const isLifeEvent = selectedEvent && !selectedOccasion;
      const endpoint = isLifeEvent 
        ? `http://localhost:8000/api/life-events/${selectedEvent.id}/respond`
        : `http://localhost:8000/api/occasions/${selectedOccasion.id}/respond`;
      
      const response = await axios.post(endpoint, {
        response_text: customerResponse
      });

      const updatedHealth = response.data.policy_health;
      const outcome = response.data.response_analysis?.outcome || response.data.outcome;
      
      // Immediately update policy health from response
      if (updatedHealth) {
        setPolicyHealth(updatedHealth);
      }
      
      // Show outcome-specific messages
      if (outcome === 'converted' || outcome === 'accepted') {
        showToastNotification(`🎉 Success! Policy health improved to ${updatedHealth?.health_score || 'N/A'}`, 'success');
      } else if (outcome === 'declined') {
        showToastNotification(`⚠️ Customer declined. Policy health: ${updatedHealth?.health_score || 'N/A'}`, 'warning');
      } else {
        showToastNotification(`📊 Response processed! Outcome: ${outcome}`, 'success');
      }
      
      setShowResponseModal(false);
      setCustomerResponse('');
      setSelectedEvent(null);
      setSelectedOccasion(null);
      loadAllLifeEvents();
      loadOccasions();
    } catch (error) {
      console.error('Error responding:', error);
      showToastNotification('❌ Error processing response', 'error');
    }
    setLoading(false);
  };

  const triggerOccasion = async (occasionType) => {
    if (!selectedLead) {
      showToastNotification('Please select a lead first', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/leads/${selectedLead.id}/occasion`,
        {
          occasion_type: occasionType,
          occasion_date: new Date().toISOString(),
          description: `${occasionType.replace('_', ' ')} celebration`
        }
      );

      showToastNotification(`🎉 Occasion triggered! Message sent to ${selectedLead.full_name}`, 'success');
      loadOccasions();
    } catch (error) {
      console.error('Error triggering occasion:', error);
      showToastNotification('❌ Error triggering occasion', 'error');
    }
    setLoading(false);
  };

  const loadOccasions = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/occasions');
      setOccasions(response.data.occasions || []);
    } catch (error) {
      console.error('Error loading occasions:', error);
    }
  };

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'new_baby': return <Baby className="w-5 h-5" />;
      case 'home_purchase': return <Home className="w-5 h-5" />;
      case 'teen_driver': return <Car className="w-5 h-5" />;
      case 'job_change': return <Briefcase className="w-5 h-5" />;
      default: return <Calendar className="w-5 h-5" />;
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getChurnRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'high': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getOutcomeColor = (outcome) => {
    switch (outcome) {
      case 'converted': return 'bg-green-100 text-green-800 border-green-300';
      case 'declined': return 'bg-red-100 text-red-800 border-red-300';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Background Decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      </div>

      {/* Enhanced Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                <Heart className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Lifeline Retention Agent
                </h1>
              </div>
            </div>
            <a href="/" className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Dashboard
            </a>
          </div>
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Lead Selection & Policy Health */}
            <div className="lg:col-span-4 space-y-6">
            {/* Lead Selection */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-blue-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Customer</h2>
              
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {leads.map((lead) => (
                  <button
                    key={lead.id}
                    onClick={() => selectLead(lead)}
                    className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                      selectedLead?.id === lead.id
                        ? 'border-blue-500 bg-blue-50 shadow-md'
                        : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
                    }`}
                  >
                    <div className="font-semibold text-gray-900">{lead.full_name}</div>
                    <div className="text-sm text-gray-600 mt-1">{lead.email}</div>
                    <div className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium mt-2 inline-block">
                      {lead.insurance_type}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Policy Health Score */}
            {policyHealth && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-blue-100 animate-fade-in">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  <h2 className="text-xl font-semibold text-gray-900">Policy Health</h2>
                </div>

                {/* Health Score Gauge */}
                <div className="text-center mb-6">
                  <div className={`text-6xl font-bold ${getHealthScoreColor(policyHealth.health_score)}`}>
                    {policyHealth.health_score}
                  </div>
                  <div className="text-sm text-gray-600 mt-2">Health Score</div>
                </div>

                {/* Churn Risk */}
                <div className="mb-4">
                  <label className="text-xs uppercase tracking-wide text-gray-600 font-semibold mb-2 block">Churn Risk</label>
                  <div className={`px-4 py-2 rounded-lg font-semibold text-center border-2 ${getChurnRiskColor(policyHealth.churn_risk)}`}>
                    {policyHealth.churn_risk?.toUpperCase()}
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Engagement</div>
                    <div className="text-lg font-bold text-blue-600">{policyHealth.engagement_score || 0}</div>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Satisfaction</div>
                    <div className="text-lg font-bold text-green-600">{policyHealth.satisfaction_score || 0}</div>
                  </div>
                  <div className="bg-purple-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Usage</div>
                    <div className="text-lg font-bold text-purple-600">{policyHealth.usage_score || 0}</div>
                  </div>
                  <div className="bg-orange-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Payment</div>
                    <div className="text-lg font-bold text-orange-600">{policyHealth.payment_score || 0}</div>
                  </div>
                </div>

                {/* Predicted Churn */}
                {policyHealth.days_to_predicted_churn && (
                  <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
                    <div className="flex items-center gap-2 text-red-700">
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-sm font-semibold">
                        Predicted churn in {policyHealth.days_to_predicted_churn} days
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

            {/* Right: Life Events & Actions */}
            <div className="lg:col-span-8 space-y-6">
            {/* Tab Selector */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-2 border border-gray-200">
              <div className="flex gap-2">
                <button
                  onClick={() => setActiveTab('life_events')}
                  className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all ${
                    activeTab === 'life_events'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Life Events
                </button>
                <button
                  onClick={() => setActiveTab('occasions')}
                  className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all ${
                    activeTab === 'occasions'
                      ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  Occasions
                </button>
              </div>
            </div>

            {/* Trigger Life Event */}
            {activeTab === 'life_events' && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-blue-100">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Trigger Life Event</h2>
              
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => triggerLifeEvent('new_baby')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-pink-50 to-pink-100 border-2 border-pink-200 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Baby className="w-6 h-6 text-pink-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">New Baby</div>
                    <div className="text-xs text-gray-600">Umbrella insurance</div>
                  </div>
                </button>

                <button
                  onClick={() => triggerLifeEvent('home_reno')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                >
                  <Home className="w-6 h-6 text-green-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Home Reno</div>
                    <div className="text-xs text-gray-600">Flood coverage</div>
                  </div>
                </button>

                <button
                  onClick={() => triggerLifeEvent('teen_driver')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Car className="w-6 h-6 text-blue-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Teen Driver</div>
                    <div className="text-xs text-gray-600">Auto upgrade</div>
                  </div>
                </button>

                <button
                  onClick={() => triggerLifeEvent('job_change')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-50 to-purple-100 border-2 border-purple-200 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Briefcase className="w-6 h-6 text-purple-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Job Change</div>
                    <div className="text-xs text-gray-600">Policy review</div>
                  </div>
                </button>
              </div>
            </div>
            )}

            {/* Trigger Occasions */}
            {activeTab === 'occasions' && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-purple-100">
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-purple-600" />
                  Trigger Occasion
                </h2>
              
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => triggerOccasion('policy_anniversary')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-50 to-purple-100 border-2 border-purple-200 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Calendar className="w-6 h-6 text-purple-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Policy Anniversary</div>
                    <div className="text-xs text-gray-600">$50 off renewal</div>
                  </div>
                </button>

                <button
                  onClick={() => triggerOccasion('birthday')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-pink-50 to-pink-100 border-2 border-pink-200 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Heart className="w-6 h-6 text-pink-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Birthday</div>
                    <div className="text-xs text-gray-600">Free roadside assist</div>
                  </div>
                </button>

                <button
                  onClick={() => triggerOccasion('usage_based_savings')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-green-50 to-green-100 border-2 border-green-200 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Car className="w-6 h-6 text-green-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Usage Savings</div>
                    <div className="text-xs text-gray-600">Save $340/yr</div>
                  </div>
                </button>

                <button
                  onClick={() => triggerOccasion('policy_renewal')}
                  disabled={!selectedLead || loading}
                  className="flex items-center gap-3 p-4 bg-gradient-to-r from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Policy Renewal</div>
                    <div className="text-xs text-gray-600">Review coverage</div>
                  </div>
                </button>
              </div>
            </div>
            )}

            {/* Life Events List */}
            {activeTab === 'life_events' && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-blue-100">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Life Events</h2>
              
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {lifeEvents.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No life events yet</p>
                    <p className="text-sm mt-2">Trigger an event above to get started</p>
                  </div>
                ) : (
                  lifeEvents.map((event) => (
                    <div key={event.id} className="border-l-4 border-blue-500 bg-gradient-to-r from-blue-50 to-white p-5 rounded-r-xl shadow-md">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            {getEventIcon(event.event_type)}
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">{event.lead_name}</div>
                            <div className="text-sm text-gray-600">{event.event_type.replace('_', ' ')}</div>
                          </div>
                        </div>
                        <div className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getOutcomeColor(event.outcome)}`}>
                          {event.outcome || 'pending'}
                        </div>
                      </div>

                      {event.action_content && (
                        <div className="bg-white p-3 rounded-lg border border-gray-200 mb-3">
                          <div className="text-xs text-gray-500 mb-1">SMS Sent:</div>
                          <div className="text-sm text-gray-800">{event.action_content}</div>
                        </div>
                      )}

                      {event.customer_response && (
                        <div className="bg-green-50 p-3 rounded-lg border border-green-200 mb-3">
                          <div className="text-xs text-green-700 mb-1">Customer Response:</div>
                          <div className="text-sm text-gray-800">{event.customer_response}</div>
                        </div>
                      )}

                      {event.recommended_product && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <span>Product: <strong>{event.recommended_product}</strong></span>
                          {event.estimated_value && (
                            <span className="text-green-600 font-semibold">+${event.estimated_value}/mo</span>
                          )}
                        </div>
                      )}

                      {event.outcome === 'pending' && event.action_taken && (
                        <button
                          onClick={() => {
                            setSelectedEvent(event);
                            setShowResponseModal(true);
                          }}
                          className="mt-3 w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white px-4 py-2 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-600 transition-all flex items-center justify-center gap-2"
                        >
                          <MessageSquare className="w-4 h-4" />
                          Simulate Customer Response
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
            )}

            {/* Occasions List */}
            {activeTab === 'occasions' && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-purple-100">
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-purple-600" />
                  Recent Occasions
                </h2>
              
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {occasions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No occasions yet</p>
                    <p className="text-sm mt-2">Trigger an occasion above to get started</p>
                  </div>
                ) : (
                  occasions.map((occasion) => (
                    <div key={occasion.id} className="border-l-4 border-purple-500 bg-gradient-to-r from-purple-50 to-white p-5 rounded-r-xl shadow-md">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">{occasion.lead_name}</div>
                            <div className="text-sm text-gray-600">{occasion.occasion_type.replace('_', ' ')}</div>
                          </div>
                        </div>
                        <div className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getOutcomeColor(occasion.outcome)}`}>
                          {occasion.outcome || 'pending'}
                        </div>
                      </div>

                      {occasion.action_content && (
                        <div className="bg-white p-3 rounded-lg border border-gray-200 mb-3">
                          <div className="text-xs text-gray-500 mb-1">Message Sent:</div>
                          <div className="text-sm text-gray-800">{occasion.action_content}</div>
                        </div>
                      )}

                      {occasion.customer_response && (
                        <div className="bg-green-50 p-3 rounded-lg border border-green-200 mb-3">
                          <div className="text-xs text-green-700 mb-1">Customer Response:</div>
                          <div className="text-sm text-gray-800">{occasion.customer_response}</div>
                        </div>
                      )}

                      {occasion.offer_description && (
                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                          <span>Offer: <strong>{occasion.offer_description}</strong></span>
                          {occasion.offer_value > 0 && (
                            <span className="text-green-600 font-semibold">${occasion.offer_value}</span>
                          )}
                        </div>
                      )}

                      {occasion.outcome === 'pending' && occasion.action_taken && (
                        <button
                          onClick={() => {
                            setSelectedOccasion(occasion);
                            setSelectedEvent(null);
                            setShowResponseModal(true);
                          }}
                          className="mt-3 w-full bg-gradient-to-r from-purple-600 to-purple-500 text-white px-4 py-2 rounded-lg font-semibold hover:from-purple-700 hover:to-purple-600 transition-all flex items-center justify-center gap-2"
                        >
                          <MessageSquare className="w-4 h-4" />
                          Simulate Customer Response
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
            )}
            </div>
          </div>
        </div>
      </div>

      {/* Customer Response Modal */}
      {showResponseModal && (selectedEvent || selectedOccasion) && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full">
            <div className="bg-gradient-to-r from-blue-600 to-blue-500 p-6 text-white rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold">Customer Response</h3>
                <button
                  onClick={() => setShowResponseModal(false)}
                  className="w-8 h-8 hover:bg-white/20 rounded-lg transition-colors flex items-center justify-center"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Simulate {(selectedEvent?.lead_name || selectedOccasion?.lead_name)}'s Response:
                </label>
                <textarea
                  value={customerResponse}
                  onChange={(e) => setCustomerResponse(e.target.value)}
                  placeholder="e.g., Yes let's do it! or Tell me more or No thanks"
                  className="w-full p-4 border-2 border-gray-200 rounded-xl h-32 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowResponseModal(false)}
                  className="flex-1 px-4 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={respondToEvent}
                  disabled={loading || !customerResponse.trim()}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-blue-500 text-white px-4 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-600 disabled:from-gray-400 disabled:to-gray-400 transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Send Response
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed top-4 right-4 z-50 animate-fade-in">
          <div className={`flex items-center gap-3 px-6 py-4 rounded-xl shadow-2xl border-2 ${
            toastType === 'success' 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300' 
              : 'bg-gradient-to-r from-red-50 to-orange-50 border-red-300'
          }`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              toastType === 'success' ? 'bg-green-100' : 'bg-red-100'
            }`}>
              {toastType === 'success' ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-600" />
              )}
            </div>
            <p className={`font-semibold ${
              toastType === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {toastMessage}
            </p>
            <button
              onClick={() => setShowToast(false)}
              className="ml-2 hover:opacity-70 transition-opacity"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
