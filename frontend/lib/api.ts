const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ScoreResponse {
  prospect_id?: string;
  score: number;
  tier: 'Hot' | 'Warm' | 'Cold' | 'Frozen' | 'Ignore';
  probability: number;
  confidence?: number;
  recommended_action: string;
  predicted_at: string;
  model_mode: string;
  lead_source?: string;
  country?: string;
  city?: string;
  specialization?: string;
  [key: string]: any;
}

export interface BatchUploadResponse {
  message: string;
  total_leads: number;
  scored_successfully: number;
  errors: string[];
  results: ScoreResponse[];
}

export interface AnalyticsSummary {
  total_leads_scored: number;
  hot_count: number;
  warm_count: number;
  cold_count: number;
  frozen_count: number;
  average_score: number;
  top_sources: any[];
  top_specializations: any[];
  top_cities: any[];
  model_mode: string;
}

/**
 * Health check
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Network response was not ok');
    return await res.json();
  } catch (error) {
    console.error('API Health Check failed:', error);
    return { status: 'down' };
  }
}

/**
 * Score a single lead
 */
export async function scoreLead(data: any): Promise<ScoreResponse> {
  const res = await fetch(`${API_BASE_URL}/api/score/single`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || 'Failed to score lead');
  }
  
  return res.json();
}

/**
 * Get Analytics Summary
 */
export async function getAnalytics(): Promise<AnalyticsSummary> {
  const res = await fetch(`${API_BASE_URL}/api/analytics/summary`);
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}

/**
 * Upload CSV for batch scoring
 */
export async function uploadBatchCsv(file: File): Promise<BatchUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_BASE_URL}/api/score/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || 'Failed to process batch upload');
  }
  
  return res.json();
}
