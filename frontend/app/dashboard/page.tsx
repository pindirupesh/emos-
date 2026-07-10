"use client";

import { useState, useEffect } from "react";
import { AlertCircle, Clock, Calendar, CheckCircle } from "lucide-react";

const USER_ID = 1;

interface DashboardData {
  user_name: string;
  stats: {
    pending: number;
    overdue: number;
    done: number;
    total: number;
  };
  pending_commitments: Array<{ id: number; task: string; deadline: string | null }>;
  overdue_commitments: Array<{ id: number; task: string; deadline: string | null }>;
  recent_meetings: Array<{ id: number; title: string; date: string }>;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/meetings/dashboard/${USER_ID}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Dashboard fetch error:", err);
        setError("Could not load dashboard data. Is the backend running?");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
        <p className="text-red-700 mt-2">{error}</p>
        <p className="text-sm text-red-500 mt-1">
          Make sure your backend is running on http://localhost:8000
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center text-gray-500 py-12">
        No data available. Upload a meeting to get started!
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Daily AI Brief */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">Good Morning, {data.user_name}! ☀️</h1>
            <p className="text-blue-100 mt-1">Here's your organizational memory snapshot</p>
          </div>
          <div className="bg-white/20 rounded-full px-4 py-2 text-sm font-medium backdrop-blur-sm">
            {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <span className="text-blue-100 text-sm">Total</span>
              <span className="text-2xl font-bold">{data.stats.total}</span>
            </div>
            <p className="text-blue-200 text-xs">All commitments</p>
          </div>
          <div className="bg-yellow-500/20 rounded-xl p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <span className="text-yellow-100 text-sm">Pending</span>
              <span className="text-2xl font-bold">{data.stats.pending}</span>
            </div>
            <p className="text-yellow-200 text-xs">Waiting on you</p>
          </div>
          <div className="bg-red-500/20 rounded-xl p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <span className="text-red-100 text-sm">Overdue</span>
              <span className="text-2xl font-bold">{data.stats.overdue}</span>
            </div>
            <p className="text-red-200 text-xs">Requires attention</p>
          </div>
          <div className="bg-green-500/20 rounded-xl p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <span className="text-green-100 text-sm">Done</span>
              <span className="text-2xl font-bold">{data.stats.done}</span>
            </div>
            <p className="text-green-200 text-xs">Completed</p>
          </div>
        </div>
      </div>

      {/* Pending & Overdue */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-gray-800">
            <Clock className="h-5 w-5 text-yellow-500" />
            Pending Tasks
          </h2>
          {data.pending_commitments.length === 0 ? (
            <p className="text-gray-400 text-sm mt-3">No pending tasks. Good job! 🎉</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {data.pending_commitments.map((c) => (
                <li key={c.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">{c.task}</span>
                  <span className="text-xs text-gray-400">
                    {c.deadline ? new Date(c.deadline).toLocaleDateString() : "No deadline"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-gray-800">
            <AlertCircle className="h-5 w-5 text-red-500" />
            Overdue Commitments
          </h2>
          {data.overdue_commitments.length === 0 ? (
            <p className="text-gray-400 text-sm mt-3">No overdue commitments! ✅</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {data.overdue_commitments.map((c) => (
                <li key={c.id} className="flex items-center justify-between p-3 bg-red-50 border border-red-100 rounded-lg">
                  <span className="text-sm text-red-700">{c.task}</span>
                  <span className="text-xs text-red-500 font-medium">
                    {c.deadline ? `Due: ${new Date(c.deadline).toLocaleDateString()}` : "No deadline"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Recent Meetings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-semibold flex items-center gap-2 text-gray-800 mb-3">
          <Calendar className="h-5 w-5 text-blue-500" />
          Recent Meetings
        </h2>
        {data.recent_meetings.length === 0 ? (
          <p className="text-gray-400 text-sm">No meetings uploaded yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {data.recent_meetings.map((m) => (
              <div key={m.id} className="p-3 bg-gray-50 rounded-lg flex items-center justify-between">
                <span className="text-sm text-gray-700">{m.title}</span>
                <span className="text-xs text-gray-400">
                  {new Date(m.date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        )}
        <div className="mt-4 text-right">
          <a href="/workspace" className="text-sm text-blue-600 hover:underline">
            View all meetings →
          </a>
        </div>
      </div>
    </div>
  );
}