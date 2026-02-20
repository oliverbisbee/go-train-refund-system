import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const getRoutes = () => api.get('/routes');
export const getStops = (routeId: string) => api.get(`/stops?route_id=${routeId}`);
export const getTrains = (routeId: string, day: string, origin: string, dest: string) =>
  api.get(`/trains?route_id=${routeId}&day=${day}&origin_stop=${origin}&destination_stop=${dest}`);
export const createSubscription = (data: any) => api.post('/subscriptions', data);
export const getDelayedTrains = () => api.get('/delayed_trains');
export const generateEmail = (delayEventId: string) => api.post('/generate_email', { delay_event_id: delayEventId });