import axios from 'axios';

export interface PhoenixParams {
  prompt: string;
  width: number;
  height: number;
  num_images: number;
  style?: string;
  contrast?: number;
  alchemy?: boolean;
  enhance_prompt?: boolean;
  ultra?: boolean;
  negative_prompt?: string;
  upscale?: boolean;
  upscale_strength?: number;
}

export interface PhoenixResponse {
  generation_id: string;
  status: string;
  num_images: number;
  image_urls: string[];
  metadata: any;
  cost_estimate: number;
}

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 Minuten Timeout für Bildgenerierung
});

export async function generatePhoenix(params: PhoenixParams): Promise<PhoenixResponse> {
  try {
    console.log('Sending request to backend:', params);
    const resp = await api.post('/api/v1/generations/phoenix', params);
    console.log('Backend response:', resp.data);
    return resp.data;
  } catch (error) {
    console.error('API Error:', error);
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      throw new Error(`Generation failed: ${message}`);
    }
    throw error;
  }
}
