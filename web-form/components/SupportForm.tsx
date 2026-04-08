'use client';
import React, { useState } from 'react';

const CATEGORIES = [
  { value: 'general', label: 'General Question' },
  { value: 'technical', label: 'Technical Support' },
  { value: 'billing', label: 'Billing Inquiry' },
  { value: 'bug_report', label: 'Bug Report' },
  { value: 'feedback', label: 'Feedback' }
];

const PRIORITIES = [
  { value: 'low', label: 'Low - Not urgent' },
  { value: 'medium', label: 'Medium - Need help soon' },
  { value: 'high', label: 'High - Urgent issue' }
];

export default function SupportForm({ apiEndpoint = 'http://localhost:8000/support/submit' }: { apiEndpoint?: string }) {
  const [formData, setFormData] = useState({
    name: '', email: '', subject: '', category: 'general', priority: 'medium', message: ''
  });
  const [status, setStatus] = useState('idle');
  const [ticketId, setTicketId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    if (formData.name.trim().length < 2) { setError('Please enter your full name'); return false; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) { setError('Please enter a valid email'); return false; }
    if (formData.subject.trim().length < 5) { setError('Subject must be at least 5 characters'); return false; }
    if (formData.message.trim().length < 10) { setError('Please describe your issue in more detail'); return false; }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validateForm()) return;
    setStatus('submitting');
    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Submission failed');
      }
      const data = await response.json();
      setTicketId(data.ticket_id);
      setStatus('success');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
    }
  };

  if (status === 'success') {
    return (
      <div className="max-w-2xl mx-auto p-8 bg-white rounded-2xl shadow-lg text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Request Submitted!</h2>
        <p className="text-gray-600 mb-4">Our AI support team will respond within 5 minutes.</p>
        <div className="bg-gray-50 rounded-xl p-4 mb-6">
          <p className="text-sm text-gray-500 mb-1">Your Ticket ID</p>
          <p className="text-lg font-mono font-bold text-gray-900">{ticketId}</p>
        </div>
        <button
          onClick={() => {
            setStatus('idle');
            setFormData({ name: '', email: '', subject: '', category: 'general', priority: 'medium', message: '' });
          }}
          className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
        >
          Submit Another Request
        </button>
      </div>
    );
  }

  const btnClass = status === 'submitting'
    ? 'w-full py-4 px-6 rounded-xl font-semibold text-white bg-gray-400 cursor-not-allowed'
    : 'w-full py-4 px-6 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-700 hover:shadow-lg transition-all';

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-2xl shadow-lg">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Contact Support</h1>
        <p className="text-gray-600">Get help from our AI-powered support team. Usually responds within 5 minutes.</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name *</label>
            <input
              type="text" name="name" value={formData.name} onChange={handleChange} required
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="John Doe"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Email Address *</label>
            <input
              type="email" name="email" value={formData.email} onChange={handleChange} required
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder="john@company.com"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Subject *</label>
          <input
            type="text" name="subject" value={formData.subject} onChange={handleChange} required
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            placeholder="Brief description of your issue"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Category *</label>
            <select
              name="category" value={formData.category} onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition bg-white"
            >
              {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Priority</label>
            <select
              name="priority" value={formData.priority} onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition bg-white"
            >
              {PRIORITIES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">How can we help? *</label>
          <textarea
            name="message" value={formData.message} onChange={handleChange} required rows={5}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition resize-none"
            placeholder="Please describe your issue or question in detail..."
          />
          <p className="mt-1 text-xs text-gray-400">{formData.message.length}/1000 characters</p>
        </div>

        <button type="submit" disabled={status === 'submitting'} className={btnClass}>
          {status === 'submitting' ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Submitting...
            </span>
          ) : 'Submit Support Request'}
        </button>
      </form>
    </div>
  );
}
