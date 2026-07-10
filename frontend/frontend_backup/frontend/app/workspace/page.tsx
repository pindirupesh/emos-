"use client";

import { useState, useEffect, useRef } from "react";
import { Upload, FileText, Loader2 } from "lucide-react";

const USER_ID = 1;

interface Meeting {
  id: number;
  title: string;
  summary: string;
  meeting_date: string;
}

export default function WorkspacePage() {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loadingMeetings, setLoadingMeetings] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ✅ FIXED: useEffect instead of useState
  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    setLoadingMeetings(true);
    try {
      const res = await fetch(`http://localhost:8000/meetings/dashboard/${USER_ID}`);
      if (res.ok) {
        const data = await res.json();
        if (data.recent_meetings) {
          setMeetings(data.recent_meetings);
        }
      }
    } catch (e) {
      console.error("Failed to fetch meetings", e);
    } finally {
      setLoadingMeetings(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title) {
      setUploadStatus({ type: "error", message: "Please enter a title and select a file." });
      return;
    }

    setUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append("user_id", String(USER_ID));
    formData.append("title", title);
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/meetings/upload", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setUploadStatus({ type: "success", message: `✅ Meeting "${title}" uploaded successfully!` });
        setTitle("");
        setFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        fetchMeetings();
      } else {
        const errorText = await res.text();
        setUploadStatus({ type: "error", message: `❌ Upload failed: ${errorText}` });
      }
    } catch (err) {
      setUploadStatus({ type: "error", message: "❌ Network error. Is the backend running?" });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Upload className="h-6 w-6 text-blue-600" />
          Meeting Workspace
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Upload a meeting transcript to extract commitments, decisions, and action items.
        </p>

        <form onSubmit={handleUpload} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Meeting Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Sprint Planning - Week 5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Transcript File (.txt)
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              required
            />
            <p className="text-xs text-gray-400 mt-1">Upload a plain text file of your meeting transcript.</p>
          </div>

          <button
            type="submit"
            disabled={uploading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition disabled:opacity-50 flex items-center gap-2"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Upload & Process
              </>
            )}
          </button>
        </form>

        {uploadStatus && (
          <div
            className={`mt-4 p-3 rounded-lg ${
              uploadStatus.type === "success"
                ? "bg-green-50 border border-green-200 text-green-700"
                : "bg-red-50 border border-red-200 text-red-700"
            }`}
          >
            {uploadStatus.message}
          </div>
        )}
      </div>

      {/* Meeting List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />
          Your Meetings
        </h2>

        {loadingMeetings ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>
        ) : meetings.length === 0 ? (
          <p className="text-gray-400 text-sm mt-3">
            No meetings uploaded yet. Upload your first meeting above!
          </p>
        ) : (
          <div className="mt-3 space-y-3">
            {meetings.map((m) => (
              <div key={m.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-gray-800">{m.title}</h3>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{m.summary || "No summary available"}</p>
                  </div>
                  <span className="text-xs text-gray-400 whitespace-nowrap">
                    {new Date(m.meeting_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}