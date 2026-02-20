'use client';

import { useState } from 'react';
import { createSubscription, getStops, getTrains } from '@/lib/api';

export default function Subscribe() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    day_of_week: '',
    route_id: '01',
    origin_stop_id: '',
    destination_stop_id: '',
    scheduled_departure_time: '',
    scheduled_arrival_time: '',
    email: '',
  });
  const [stops, setStops] = useState<any[]>([]);
  const [trains, setTrains] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  const handleDaySelect = async (day: string) => {
    setFormData({ ...formData, day_of_week: day });
    // Fetch stops
    const response = await getStops('01');
    setStops(response.data);
    setStep(2);
  };

  const handleStopsSelect = async () => {
    if (!formData.origin_stop_id || !formData.destination_stop_id) {
      alert('Please select both origin and destination');
      return;
    }
    setLoading(true);
    try {
      const response = await getTrains(
        formData.route_id,
        formData.day_of_week,
        formData.origin_stop_id,
        formData.destination_stop_id
      );
      setTrains(response.data);
      setStep(3);
    } catch (error) {
      alert('Failed to fetch trains');
    }
    setLoading(false);
  };

  const handleTrainSelect = (train: any) => {
    setFormData({
      ...formData,
      scheduled_departure_time: train.departure_time,
      scheduled_arrival_time: train.arrival_time,
    });
    setStep(4);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createSubscription(formData);
      alert('Subscription created! (Email verification would happen here)');
      window.location.href = '/';
    } catch (error) {
      alert('Failed to create subscription');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold mb-6">Subscribe to Train Alerts</h1>

        {/* Step 1: Day Selection */}
        {step === 1 && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Select Day of Week</h2>
            <div className="grid grid-cols-2 gap-4">
              {days.map((day) => (
                <button
                  key={day}
                  onClick={() => handleDaySelect(day)}
                  className="bg-blue-100 hover:bg-blue-200 p-4 rounded-lg capitalize"
                >
                  {day}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Stop Selection */}
        {step === 2 && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Select Stops</h2>
            <div className="space-y-4">
              <div>
                <label className="block mb-2 font-medium">Origin</label>
                <select
                  className="w-full p-2 border rounded"
                  value={formData.origin_stop_id}
                  onChange={(e) => setFormData({ ...formData, origin_stop_id: e.target.value })}
                >
                  <option value="">Select origin</option>
                  {stops.map((stop) => (
                    <option key={stop.stop_id} value={stop.stop_id}>
                      {stop.stop_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block mb-2 font-medium">Destination</label>
                <select
                  className="w-full p-2 border rounded"
                  value={formData.destination_stop_id}
                  onChange={(e) => setFormData({ ...formData, destination_stop_id: e.target.value })}
                >
                  <option value="">Select destination</option>
                  {stops.map((stop) => (
                    <option key={stop.stop_id} value={stop.stop_id}>
                      {stop.stop_name}
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={handleStopsSelect}
                className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Next'}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Train Selection */}
        {step === 3 && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Select Your Train</h2>
            <div className="space-y-4">
              {trains.map((train) => (
                <button
                  key={train.trip_id}
                  onClick={() => handleTrainSelect(train)}
                  className="w-full bg-gray-100 hover:bg-gray-200 p-4 rounded-lg text-left"
                >
                  <p className="font-semibold">Departure: {train.departure_time}</p>
                  <p>Arrival: {train.arrival_time}</p>
                  <p className="text-sm text-gray-600">Duration: {train.duration_minutes} min</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Email Entry */}
        {step === 4 && (
          <form onSubmit={handleSubmit}>
            <h2 className="text-xl font-semibold mb-4">Enter Your Email</h2>
            <input
              type="email"
              className="w-full p-3 border rounded mb-4"
              placeholder="your@email.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
            <button
              type="submit"
              className="w-full bg-green-600 text-white p-3 rounded-lg hover:bg-green-700"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Complete Subscription'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}