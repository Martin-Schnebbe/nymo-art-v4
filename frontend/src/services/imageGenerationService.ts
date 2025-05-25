/**
 * Unified image generation service
 */

import { generatePhoenix } from './phoenixClient';
import { generateFlux } from './fluxClient';
import { generatePhotoReal } from './photorealClient';
import { createPhoenixParams, createFluxParams, createPhotoRealParams, type FormData } from '../utils/parameterUtils';
import { convertImageUrlsToBase64 } from '../utils/imageUtils';

export interface GenerationResult {
  generation_id: string;
  status: string;
  num_images: number;
  image_urls: string[];
  images: string[]; // base64 images for display
  metadata: Record<string, any>;
  cost_estimate?: number;
}

export interface GenerationError extends Error {
  code?: string;
  details?: any;
}

/**
 * Generate images using the specified model
 */
export const generateImages = async (
  selectedModel: 'phoenix' | 'flux' | 'photoreal',
  formData: FormData
): Promise<GenerationResult> => {
  try {
    let result;
    
    // Generate images based on selected model
    if (selectedModel === 'phoenix') {
      const phoenixParams = createPhoenixParams(formData);
      result = await generatePhoenix(phoenixParams);
    } else if (selectedModel === 'flux') {
      const fluxParams = createFluxParams(formData);
      result = await generateFlux(fluxParams);
    } else if (selectedModel === 'photoreal') {
      const photorealParams = createPhotoRealParams(formData);
      result = await generatePhotoReal(photorealParams);
    } else {
      throw new Error(`Unsupported model: ${selectedModel}`);
    }
    
    // Convert image URLs to base64 for display
    if (result && result.image_urls && result.image_urls.length > 0) {
      const base64Images = await convertImageUrlsToBase64(result.image_urls);
      
      return {
        ...result,
        images: base64Images
      };
    } else {
      throw new Error('No images were generated');
    }
    
  } catch (err) {
    console.error('Generation error:', err);
    
    const error = new Error(
      err instanceof Error ? err.message : 'Something went wrong'
    ) as GenerationError;
    
    if (err instanceof Error) {
      error.code = 'GENERATION_ERROR';
      error.details = err;
    }
    
    throw error;
  }
};

/**
 * Validate form data before generation
 */
export const validateGenerationParams = (
  selectedModel: 'phoenix' | 'flux' | 'photoreal',
  formData: FormData
): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  // Common validation
  if (!formData.prompt || !formData.prompt.trim()) {
    errors.push('Prompt is required');
  }
  
  if (formData.prompt && formData.prompt.length > 1000) {
    errors.push('Prompt must be less than 1000 characters');
  }
  
  if (formData.num_images < 1 || formData.num_images > 10) {
    errors.push('Number of images must be between 1 and 10');
  }
  
  if (formData.contrast < 1 || formData.contrast > 5) {
    errors.push('Contrast must be between 1 and 5');
  }
  
  // Model-specific validation
  if (selectedModel === 'phoenix') {
    if (formData.upscale_strength < 0 || formData.upscale_strength > 1) {
      errors.push('Upscale strength must be between 0 and 1');
    }
  }
  
  if (selectedModel === 'flux') {
    if (formData.seed !== undefined && (formData.seed < 0 || formData.seed > 2147483647)) {
      errors.push('Seed must be between 0 and 2147483647');
    }
  }
  
  if (selectedModel === 'photoreal') {
    if (formData.photoreal_version === 'v1' && formData.photoreal_strength !== undefined) {
      if (formData.photoreal_strength < 0 || formData.photoreal_strength > 1) {
        errors.push('PhotoReal strength must be between 0 and 1');
      }
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};
