import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface FluxParams {
  prompt: string;
  width: number;
  height: number;
  num_images: number;
  model_type: 'flux_speed' | 'flux_precision';
  style?: string;
  contrast: number;
  enhance_prompt: boolean;
  enhance_prompt_instruction?: string;
  negative_prompt?: string;
  ultra: boolean;
  seed?: number;
}

export interface FluxResponse {
  generation_id: string;
  status: string;
  num_images: number;
  image_urls: string[];
  metadata: Record<string, any>;
  cost_estimate?: number;
}

export const generateFlux = async (params: FluxParams): Promise<FluxResponse> => {
  try {
    console.log('Sending FLUX request:', params);
    
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/generations/flux`,
      params,
      {
        timeout: 120000, // 2 minutes timeout
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    console.log('FLUX response:', response.data);
    return response.data;
  } catch (error) {
    console.error('FLUX generation error:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with error status
        const errorMessage = error.response.data?.error || error.response.data?.detail || 'Server error';
        throw new Error(`Generation failed: ${errorMessage}`);
      } else if (error.request) {
        // Request made but no response received
        throw new Error('Network error: Could not connect to the server');
      } else {
        // Something else happened
        throw new Error(`Request error: ${error.message}`);
      }
    }
    
    throw new Error('An unexpected error occurred');
  }
};
