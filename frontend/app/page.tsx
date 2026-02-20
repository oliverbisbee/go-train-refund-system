'use client';

import { useEffect, useState } from 'react';
import { getDelayedTrains } from '@/lib/api';

interface DelayEvent {
  id: string;
  trip_id: string;
  route_id: string;
  origin_stop_id: string;
  destination_stop_id: string;
  scheduled_departure: string;
  delay_seconds: number;
  trip_completed: boolean;
  email_generated: boolean;
}

export default function Dashboard() {
  const [delayedTrains, setDelayedTrains] = useState<DelayEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDelayedTrains();
    // Poll every 60 seconds
    const interval = setInterval(fetchDelayedTrains, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchDelayedTrains = async () => {
    try {
      const response = await getDelayedTrains();
      setDelayedTrains(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch delayed trains');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-xl">Loading delayed trains...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-gray-900">
          🚂 GO Train Delay Dashboard
        </h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">
            Currently Delayed Trains (Lakeshore West)
          </h2>

          {delayedTrains.length === 0 ? (
            <p className="text-gray-600">No delayed trains at the moment ✅</p>
          ) : (
            <div className="space-y-4">
              {delayedTrains.map((train) => (
                <div
                  key={train.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-lg">
                        {train.origin_stop_id} → {train.destination_stop_id}
                      </p>
                      <p className="text-gray-600">
                        Scheduled: {new Date(train.scheduled_departure).toLocaleTimeString()}
                      </p>
                      <p className="text-red-600 font-semibold">
                        Delay: {Math.floor(train.delay_seconds / 60)} minutes
                      </p>
                    </div>
                    <div>
                      {train.email_generated ? (
                        <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                          Email Generated ✓
                        </span>
                      ) : (
                        <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                          Eligible for Refund
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mt-8 text-center">
          <a
            href="/subscribe"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-block"
          >
            Subscribe to Train Alerts
          </a>
        </div>
      </div>
    </div>
  );
}