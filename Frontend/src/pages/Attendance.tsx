// ─── Attendance Page ─────────────────────────────────────────────────────────
// Lets the logged-in employee mark check-in, check-out,
// and view their personal late-arrival history.

import { useState, useEffect } from "react";
import { markAttendance, checkout, getMyLateMark } from "../api/attendance";
import { getErrorMessage } from "../utils/helpers";
import { CheckCircle, XCircle, Clock, AlertTriangle } from "lucide-react";

// Shape of each late-arrival record returned by the API
interface LateRecord {
  date: string;
  check_in: string;
  late_by: string;
}

export default function Attendance() {
  // Success or error message shown after check-in / check-out
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Tracks which button is currently loading ('checkin' | 'checkout' | null)
  const [loading, setLoading] = useState<"checkin" | "checkout" | null>(null);

  // Late-arrival records for this employee
  const [lateRecords, setLateRecords] = useState<LateRecord[]>([]);
  const [lateThreshold, setLateThreshold] = useState("");

  // Fetch late records once when the page loads
  useEffect(() => {
    getMyLateMark()
      .then((res) => {
        setLateRecords(res.data.records);
        setLateThreshold(res.data.late_threshold);
      })
      .catch(() => {}); // silently ignore — data is non-critical
  }, []);

  // Handles both check-in and check-out actions
  const handleAction = async (action: "checkin" | "checkout") => {
    setMessage("");
    setError("");
    setLoading(action);

    try {
      const response =
        action === "checkin" ? await markAttendance() : await checkout();

      // Build a user-friendly success message
      const { message: msg, hours_worked, overtime_hours } = response.data;
      const extra = hours_worked
        ? ` — ${hours_worked}h worked, ${overtime_hours}h overtime`
        : "";
      setMessage(msg + extra);
    } catch (err) {
      setError(getErrorMessage(err, "Action failed"));
    } finally {
      setLoading(null);
    }
  };
  const formatLateBy = (lateBy: string): string => {
    const total = parseInt(lateBy, 10);
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    const parts: string[] = [];
    if (h > 0) parts.push(`${h}h`);
    if (m > 0) parts.push(`${m}m`);
    if (s > 0) parts.push(`${s}s`);
    return parts.length ? parts.join(" ") : "< 1s";
  };
  // Today's date formatted for the page header
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Attendance</h1>
        <p className="text-gray-500 text-sm mt-1">{today}</p>
      </div>

      {/* Check-in / Check-out card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <Clock size={18} className="text-blue-500" />
          Today's Actions
        </h2>

        {/* Success alert */}
        {message && (
          <div className="flex items-start gap-2 bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-3 text-sm mb-4">
            <CheckCircle size={16} className="mt-0.5 shrink-0" />
            {message}
          </div>
        )}

        {/* Error alert */}
        {error && (
          <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm mb-4">
            <XCircle size={16} className="mt-0.5 shrink-0" />
            {error}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => handleAction("checkin")}
            disabled={loading !== null}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-medium py-3 rounded-lg transition-colors text-sm"
          >
            {loading === "checkin" ? "Marking..." : "Mark Check-In"}
          </button>

          <button
            onClick={() => handleAction("checkout")}
            disabled={loading !== null}
            className="flex-1 bg-gray-700 hover:bg-gray-800 disabled:opacity-60 text-white font-medium py-3 rounded-lg transition-colors text-sm"
          >
            {loading === "checkout" ? "Checking out..." : "Check Out"}
          </button>
        </div>
      </div>

      {/* Late arrival history card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="font-semibold text-gray-700 mb-1 flex items-center gap-2">
          <AlertTriangle size={18} className="text-yellow-500" />
          Late Arrivals
        </h2>

        {lateThreshold && (
          <p className="text-xs text-gray-400 mb-4">
            Threshold: {lateThreshold}
          </p>
        )}

        {lateRecords.length === 0 ? (
          <p className="text-sm text-gray-400">No late records. Great job!</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th className="pb-2 font-medium">Date</th>
                  <th className="pb-2 font-medium">Check-In</th>
                  <th className="pb-2 font-medium">Late By</th>
                </tr>
              </thead>
              <tbody>
                {lateRecords.map((record, index) => (
                  <tr
                    key={index}
                    className="border-b border-gray-50 last:border-0"
                  >
                    <td className="py-2">{record.date}</td>
                    <td className="py-2">
                      {new Date(record.check_in).toLocaleTimeString()}
                    </td>
                    <td className="py-2 text-red-500">
                      {formatLateBy(record.late_by)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
