import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface PhotoRealParams {
  prompt: string;
  width: number;
  height: number;
  num_images: number;
  photoreal_version: 'v1' | 'v2';
  model_id?: string;
  style: string;
  contrast: number;
  photoreal_strength?: number;
  enhance_prompt: boolean;
  negative_prompt?: string;
}

export interface PhotoRealResponse {
  generation_id: string;
  status: string;
  num_images: number;
  image_urls: string[];
  metadata: Record<string, any>;
  cost_estimate?: number;
}

export const generatePhotoReal = async (params: PhotoRealParams): Promise<PhotoRealResponse> => {
  try {
    console.log('Sending PhotoReal request:', params);
    
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/generations/photoreal`,
      params,
      {
        timeout: 120000, // 2 minutes timeout
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    console.log('PhotoReal response:', response.data);
    return response.data;
  } catch (error) {
    console.error('PhotoReal generation error:', error);
    
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
    
    throw error;
  }
};

// PhotoReal Model IDs for v2
export const PHOTOREAL_V2_MODELS = {
  'Leonardo Kino XL': 'aa77f04e-3eec-4034-9c07-d0f619684628',
  'Leonardo Diffusion XL': 'b24e16ff-06e3-43eb-8d33-4416c2d75876',
  'Leonardo Vision XL': '5c232a9e-9061-4777-980a-ddc8e65647c6',
} as const;

// PhotoReal v1 Styles (limited set)
export const PHOTOREAL_V1_STYLES = [
  'CINEMATIC',
  'CREATIVE', 
  'VIBRANT'
] as const;

// PhotoReal v2 Styles (full set)
export const PHOTOREAL_V2_STYLES = [
  'BOKEH',
  'CINEMATIC',
  'CINEMATIC_CLOSEUP',
  'CREATIVE',
  'FASHION',
  'FILM',
  'FOOD',
  'HDR',
  'LONG_EXPOSURE',
  'MACRO',
  'MINIMALISTIC',
  'MONOCHROME',
  'MOODY',
  'NEUTRAL',
  'PORTRAIT',
  'RETRO',
  'STOCK_PHOTO',
  'VIBRANT',
  'UNPROCESSED'
] as const;

export type PhotoRealV1Style = typeof PHOTOREAL_V1_STYLES[number];
export type PhotoRealV2Style = typeof PHOTOREAL_V2_STYLES[number];
export type PhotoRealModel = keyof typeof PHOTOREAL_V2_MODELS;
