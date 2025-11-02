import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowLeft, Phone, Mail, MessageSquare, AlertCircle, CheckCircle, Clock, Sparkles, TrendingUp, User, Zap, ArrowRight, ArrowUp, ArrowDown, X } from 'lucide-react';

export default function FollowUpBrain() {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [intentShift, setIntentShift] = useState(null);
  const [actions, setActions] = useState([]);
  const [touchpoints, setTouchpoints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [sentEmail, setSentEmail] = useState(null);

  // Load leads on mount
  useEffect(() => {
    loadLeads();
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

  const loadTouchpoints = async (leadId) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/leads/${leadId}/touchpoints`);
      setTouchpoints(response.data.touchpoints || []);
    } catch (error) {
      console.error('Error loading touchpoints:', error);
    }
  };

  const loadActions = async (leadId) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/leads/${leadId}/actions`);
      setActions(response.data.actions || []);
    } catch (error) {
      console.error('Error loading actions:', error);
    }
  };

  const analyzeTranscript = async () => {
    if (!selectedLead || !transcript.trim()) {
      showToastNotification('Please select a lead and enter a transcript', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/leads/${selectedLead.id}/touchpoint`,
        {
          type: 'call',
          direction: 'inbound',
          content: transcript
        }
      );

      setAnalysis(response.data.analysis);
      setIntentShift(response.data.intent_shift);
      const recommendedActions = response.data.recommended_actions;
      setActions(recommendedActions);
      setTranscript(''); // Clear transcript
      
      // Reload touchpoints
      await loadTouchpoints(selectedLead.id);
      
      // Show success notification
      showToastNotification('✅ Transcript analyzed successfully!', 'success');

      // Auto-execute email and call actions
      await autoExecuteActions(recommendedActions);
      
    } catch (error) {
      console.error('Error analyzing transcript:', error);
      showToastNotification('❌ Error analyzing transcript. Please try again.', 'error');
    }
    setLoading(false);
  };

  const autoExecuteActions = async (actions) => {
    // Filter for email and call actions
    const autoExecuteTypes = ['email', 'call'];
    const actionsToExecute = actions.filter(action => 
      autoExecuteTypes.includes(action.action_type) && action.status === 'pending'
    );

    if (actionsToExecute.length === 0) return;

    // Find email action to display
    const emailAction = actionsToExecute.find(a => a.action_type === 'email');

    // Execute each action automatically
    for (const action of actionsToExecute) {
      try {
        await axios.post(`http://localhost:8000/api/followup/${action.id}/execute`);
        console.log(`✅ Auto-executed ${action.action_type} action`);
      } catch (error) {
        console.error(`❌ Error auto-executing ${action.action_type}:`, error);
      }
    }

    // Reload actions to show updated status
    if (selectedLead) {
      await loadActions(selectedLead.id);
    }

    // Show email modal if email was sent
    if (emailAction) {
      setSentEmail({
        to: selectedLead.email,
        content: emailAction.content,
        lead: selectedLead.full_name
      });
      setShowEmailModal(true);
    }

    // Show notification about auto-executed actions
    const executedTypes = actionsToExecute.map(a => a.action_type).join(' & ');
    showToastNotification(`🚀 Auto-executed: ${executedTypes}`, 'success');
  };

  const executeAction = async (actionId) => {
    setExecuting(actionId);
    try {
      await axios.post(`http://localhost:8000/api/followup/${actionId}/execute`);
      showToastNotification('✅ Action executed successfully!', 'success');
      
      // Reload actions to update status
      if (selectedLead) {
        await loadActions(selectedLead.id);
      }
    } catch (error) {
      console.error('Error executing action:', error);
      showToastNotification('❌ Error executing action. Please try again.', 'error');
    }
    setExecuting(null);
  };

  const selectLead = (lead) => {
    setSelectedLead(lead);
    setAnalysis(null);
    setIntentShift(null);
    setActions([]);
    loadTouchpoints(lead.id);
    loadActions(lead.id);
  };

  const useSampleTranscript = () => {
    setTranscript(`Agent: Hi Kinjal, this is Alex from Solisa Insurance. How are you today?

Kinjal: Hi Alex. I'm okay, just really busy right now.

Agent: I understand. I wanted to follow up on the quote we sent you last week for auto insurance. Did you have a chance to review it?

Kinjal: Yeah, I looked at it. Honestly, it seems a bit expensive compared to what I'm paying now with Geico.

Agent: I hear you on the price. Can I ask what you're currently paying with Geico?

Kinjal: About $180 a month.

Agent: And our quote was $220, correct?

Kinjal: Yeah, that's the one. That's $40 more per month. I don't know if I can justify that right now.

Agent: That's fair. The difference is that our policy includes accident forgiveness and a lower deductible. With Geico, if you have an accident, your rates could go up significantly.

Kinjal: Hmm, I didn't think about that. But still, $40 a month is $480 a year. That's a lot.

Agent: Absolutely, I get it. Let me ask - have you had any accidents or tickets in the past few years?

Kinjal: No, actually I have a clean record.

Agent: That's great! You know what, let me see if I can get you a better rate. Can I call you back tomorrow with a revised quote?

Kinjal: Um, maybe. I'm really busy this week. Can I think about it and call you back?

Agent: Of course! No pressure at all. I'll send you an email with some additional information about the accident forgiveness benefit. Sound good?

Kinjal: Yeah, that works. Thanks Alex.

Agent: Thank you Kinjal, talk soon!`);
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-800 border-green-200';
      case 'negative': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getActionIcon = (type) => {
    switch (type) {
      case 'sms': return <MessageSquare className="w-5 h-5" />;
      case 'email': return <Mail className="w-5 h-5" />;
      case 'call': return <Phone className="w-5 h-5" />;
      case 'escalate': return <AlertCircle className="w-5 h-5" />;
      default: return <Clock className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Background Decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <a href="/" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-6 font-medium transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </a>
          
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-500 rounded-2xl flex items-center justify-center shadow-xl">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-blue-500 bg-clip-text text-transparent">
                AI Assistant
              </h1>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Lead Selection */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-blue-100">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Select Lead</h2>
            </div>
            
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {leads.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="mb-2">No leads yet</p>
                  <p className="text-sm">Create leads in Phase 1 first</p>
                </div>
              ) : (
                leads.map((lead) => (
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
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                        {lead.insurance_type}
                      </span>
                      {lead.current_provider && (
                        <span className="text-xs text-gray-500">
                          {lead.current_provider}
                        </span>
                      )}
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Middle & Right: Transcript Upload and Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Section */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-blue-100">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2">
                  <Phone className="w-5 h-5 text-blue-600" />
                  <h2 className="text-xl font-semibold text-gray-900">Upload Call Transcript</h2>
                </div>
                <button
                  onClick={useSampleTranscript}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  Use Sample Transcript
                </button>
              </div>

              {selectedLead && (
                <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                      {selectedLead.full_name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">{selectedLead.full_name}</div>
                      <div className="text-sm text-gray-600">{selectedLead.email} • {selectedLead.phone}</div>
                    </div>
                  </div>
                </div>
              )}

              <textarea
                placeholder="Paste call transcript here..."
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                className="w-full p-4 border-2 border-gray-200 rounded-xl h-64 mb-4 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all resize-none"
              />

              <button
                onClick={analyzeTranscript}
                disabled={loading || !selectedLead}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-4 rounded-xl hover:from-blue-700 hover:to-blue-600 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed font-semibold text-lg shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Analyzing with AI...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Analyze with AI
                  </>
                )}
              </button>
            </div>

            {/* Intent Shift Alert */}
            {intentShift && intentShift.shift_detected && (
              <div className={`rounded-2xl shadow-xl p-6 border-2 animate-fade-in ${
                intentShift.shift_type === 'positive' ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300' :
                intentShift.shift_type === 'negative' ? 'bg-gradient-to-r from-red-50 to-orange-50 border-red-300' :
                'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-300'
              }`}>
                <div className="flex items-start gap-3">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    intentShift.shift_type === 'positive' ? 'bg-green-100' :
                    intentShift.shift_type === 'negative' ? 'bg-red-100' :
                    'bg-blue-100'
                  }`}>
                    {intentShift.shift_type === 'positive' ? <ArrowUp className="w-6 h-6 text-green-600" /> :
                     intentShift.shift_type === 'negative' ? <ArrowDown className="w-6 h-6 text-red-600" /> :
                     <ArrowRight className="w-6 h-6 text-blue-600" />}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Intent Shift Detected!</h3>
                    <p className={`text-sm font-semibold mb-2 ${
                      intentShift.shift_type === 'positive' ? 'text-green-700' :
                      intentShift.shift_type === 'negative' ? 'text-red-700' :
                      'text-blue-700'
                    }`}>
                      {intentShift.message}
                    </p>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-600">Previous:</span>
                        <span className="px-3 py-1 bg-white rounded-lg font-semibold text-gray-700 border border-gray-300">
                          {intentShift.previous_intent}
                        </span>
                      </div>
                      <ArrowRight className="w-4 h-4 text-gray-400" />
                      <div className="flex items-center gap-2">
                        <span className="text-gray-600">Current:</span>
                        <span className={`px-3 py-1 rounded-lg font-semibold border ${
                          intentShift.shift_type === 'positive' ? 'bg-green-100 text-green-800 border-green-300' :
                          intentShift.shift_type === 'negative' ? 'bg-red-100 text-red-800 border-red-300' :
                          'bg-blue-100 text-blue-800 border-blue-300'
                        }`}>
                          {intentShift.current_intent}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Analysis Results */}
            {analysis && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-blue-100 animate-fade-in">
                {/* Header */}
                <div className="flex items-center gap-3 mb-8 pb-4 border-b border-gray-200">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-500 rounded-xl flex items-center justify-center shadow-md">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">AI Analysis</h2>
                    <p className="text-sm text-gray-500">Conversation insights and metrics</p>
                  </div>
                </div>

                {/* Metrics Grid - 4 columns */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                  {/* Sentiment */}
                  <div className="relative group">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-5 rounded-xl border-2 border-blue-200 hover:border-blue-400 transition-all hover:shadow-lg">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs uppercase tracking-wide text-gray-600 font-semibold">Sentiment</span>
                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                      </div>
                      <div className={`px-4 py-2 rounded-lg text-base font-bold border-2 text-center ${getSentimentColor(analysis.sentiment)}`}>
                        {analysis.sentiment}
                      </div>
                    </div>
                  </div>

                  {/* Intent */}
                  <div className="relative group">
                    <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-5 rounded-xl border-2 border-indigo-200 hover:border-indigo-400 transition-all hover:shadow-lg">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs uppercase tracking-wide text-gray-600 font-semibold">Client's Intent</span>
                        <div className="w-2 h-2 rounded-full bg-indigo-500"></div>
                      </div>
                      <div className="px-4 py-2 rounded-lg text-base font-bold bg-indigo-100 text-indigo-800 border-2 border-indigo-300 text-center">
                        {analysis.intent?.replace(/_/g, ' ')}
                      </div>
                    </div>
                  </div>

                  {/* Urgency */}
                  <div className="relative group">
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-5 rounded-xl border-2 border-purple-200 hover:border-purple-400 transition-all hover:shadow-lg">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs uppercase tracking-wide text-gray-600 font-semibold">Urgency</span>
                        <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                      </div>
                      <div className="px-4 py-2 rounded-lg text-base font-bold bg-purple-100 text-purple-800 border-2 border-purple-300 text-center">
                        {analysis.urgency}
                      </div>
                    </div>
                  </div>

                  {/* Objections Count */}
                  <div className="relative group">
                    <div className="bg-gradient-to-br from-red-50 to-red-100 p-5 rounded-xl border-2 border-red-200 hover:border-red-400 transition-all hover:shadow-lg">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs uppercase tracking-wide text-gray-600 font-semibold">Objections</span>
                        <div className="w-2 h-2 rounded-full bg-red-500"></div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-red-700">{analysis.objections?.length || 0}</div>
                        <div className="text-xs text-red-600 font-medium mt-1">found</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Detailed Sections */}
                <div className="space-y-4">
                  {/* Objections Detail */}
                  {analysis.objections && analysis.objections.length > 0 && (
                    <div className="bg-gradient-to-r from-red-50 to-orange-50 p-5 rounded-xl border-2 border-red-200">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                          <AlertCircle className="w-5 h-5 text-red-600" />
                        </div>
                        <h3 className="font-bold text-red-800 text-lg">Objections Detected</h3>
                      </div>
                      <div className="grid grid-cols-2 gap-3 mt-4">
                        {analysis.objections.map((obj, i) => (
                          <div key={i} className="flex items-start gap-2 bg-white p-3 rounded-lg border border-red-200">
                            <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                              <span className="text-xs font-bold text-red-700">{i + 1}</span>
                            </div>
                            <span className="text-sm text-gray-800 font-medium">{obj}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Key Points */}
                  {analysis.key_points && analysis.key_points.length > 0 && (
                    <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-5 rounded-xl border-2 border-blue-200">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Sparkles className="w-5 h-5 text-blue-600" />
                        </div>
                        <h3 className="font-bold text-blue-800 text-lg">Key Points</h3>
                      </div>
                      <div className="space-y-2 mt-4">
                        {analysis.key_points.map((point, i) => (
                          <div key={i} className="flex items-start gap-3 bg-white p-3 rounded-lg border border-blue-200">
                            <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-gray-800">{point}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Recommended Actions */}
            {actions.length > 0 && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-blue-100 animate-fade-in">
                <div className="flex items-center gap-2 mb-6">
                  <Zap className="w-5 h-5 text-blue-600" />
                  <h2 className="text-xl font-semibold text-gray-900">Recommended Actions</h2>
                </div>

                <div className="space-y-4">
                  {actions.map((action) => (
                    <div key={action.id} className="border-l-4 border-blue-500 bg-gradient-to-r from-blue-50 to-white p-5 rounded-r-xl shadow-md">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            {getActionIcon(action.action_type)}
                          </div>
                          <div>
                            <span className="font-semibold text-lg text-gray-900 uppercase">
                              {action.action_type}
                            </span>
                            <div className="flex items-center gap-2 mt-1">
                              <span className={`px-2 py-1 text-xs rounded-lg font-semibold border ${getPriorityColor(action.priority)}`}>
                                {action.priority} priority
                              </span>
                              {action.status === 'completed' && (
                                <span className="px-2 py-1 text-xs rounded-lg font-semibold bg-green-100 text-green-800 border border-green-200 flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3" />
                                  Completed
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                      </div>

                      <p className="text-sm text-gray-600 mb-3 italic pl-13">{action.reasoning}</p>

                      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                        <pre className="whitespace-pre-wrap text-sm text-gray-800">{action.content}</pre>
                      </div>

                      {action.timing && (
                        <div className="mt-3 flex items-center gap-2 text-xs text-gray-500 pl-13">
                          <Clock className="w-3 h-3" />
                          Timing: <span className="font-medium">{action.timing}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

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

      {/* Email Sent Modal */}
      {showEmailModal && sentEmail && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                    <Mail className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">Email Sent Successfully!</h3>
                    <p className="text-green-100 text-sm mt-1">Follow-up email delivered to {sentEmail.lead}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowEmailModal(false)}
                  className="w-10 h-10 hover:bg-white/20 rounded-lg transition-colors flex items-center justify-center"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Email Details */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
              {/* To */}
              <div className="mb-4">
                <label className="text-xs uppercase tracking-wide text-gray-500 font-semibold mb-2 block">To:</label>
                <div className="bg-gray-50 px-4 py-3 rounded-lg border border-gray-200">
                  <p className="text-gray-900 font-medium">{sentEmail.to}</p>
                </div>
              </div>

              {/* Subject */}
              <div className="mb-4">
                <label className="text-xs uppercase tracking-wide text-gray-500 font-semibold mb-2 block">Subject:</label>
                <div className="bg-gray-50 px-4 py-3 rounded-lg border border-gray-200">
                  <p className="text-gray-900 font-medium">Follow-up: Auto Insurance Quote</p>
                </div>
              </div>

              {/* Body */}
              <div className="mb-4">
                <label className="text-xs uppercase tracking-wide text-gray-500 font-semibold mb-2 block">Message:</label>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-5 rounded-xl border-2 border-blue-200">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans leading-relaxed">{sentEmail.content}</pre>
                </div>
              </div>

              {/* Success Badge */}
              <div className="flex items-center justify-center gap-2 mt-6 p-4 bg-green-50 rounded-xl border-2 border-green-200">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-green-800 font-semibold">Email delivered successfully</span>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 p-4 bg-gray-50">
              <button
                onClick={() => setShowEmailModal(false)}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-600 transition-all shadow-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
