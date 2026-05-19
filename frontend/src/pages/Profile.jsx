import { useState, useEffect } from 'react';
import { useAuth } from '../services/useAuth';
import Toast from '../components/Toast';

export default function Profile() {
  const { user, updateProfile } = useAuth();
  const [formData, setFormData] = useState({ full_name: '', avatar_url: '', bio: '' });
  const [status, setStatus] = useState({ loading: false, message: null, type: 'info' });

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        avatar_url: user.avatar_url || '',
        bio: user.bio || '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, message: null, type: 'info' });

    try {
      await updateProfile(formData);
      setStatus({ loading: false, message: 'Profile updated successfully.', type: 'success' });
    } catch (err) {
      setStatus({ loading: false, message: err.response?.data?.detail || 'Failed to update profile.', type: 'error' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 py-10">
      <div className="mx-auto max-w-3xl rounded-[2rem] bg-white/95 p-8 shadow-2xl shadow-slate-200 backdrop-blur-xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Your Profile</h1>
          <p className="mt-2 text-slate-600">Update your user details and account preferences.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-slate-700">Full Name</label>
              <input
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
                placeholder="Jane Doe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Avatar URL</label>
              <input
                name="avatar_url"
                value={formData.avatar_url}
                onChange={handleChange}
                className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
                placeholder="https://..."
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700">Bio</label>
            <textarea
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
              rows="5"
              placeholder="Tell us a bit about yourself"
            />
          </div>

          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm text-slate-600">Signed in as</p>
              <p className="font-medium text-slate-900">{user?.email}</p>
            </div>
            <button
              type="submit"
              disabled={status.loading}
              className="rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:opacity-60"
            >
              {status.loading ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </form>

        {status.message && <Toast message={status.message} type={status.type} />}
      </div>
    </div>
  );
}
