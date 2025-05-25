/**
 * Parameter handling utilities for form data
 */

import type { SelectChangeEvent } from '@mui/material';

export interface BaseFormData {
  prompt: string;
  width: number;
  height: number;
  num_images: number;
  style: string;
  contrast: number;
  enhance_prompt: boolean;
  negative_prompt: string;
}

export interface PhoenixFormData extends BaseFormData {
  alchemy: boolean;
  ultra: boolean;
  upscale: boolean;
  upscale_strength: number;
}

export interface FluxFormData extends BaseFormData {
  model_type: 'flux_speed' | 'flux_precision';
  enhance_prompt_instruction: string;
  ultra: boolean;
  seed?: number;
}

export interface PhotoRealFormData extends BaseFormData {
  photoreal_version: 'v1' | 'v2';
  model_id: string;
  photoreal_strength?: number;
}

export type FormData = PhoenixFormData & FluxFormData & PhotoRealFormData;

/**
 * Handle input change with proper type conversion
 */
export const handleInputChange = (
  setFormData: (data: FormData | ((prev: FormData) => FormData)) => void
) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
  const { name, value } = e.target;
  
  let processedValue: any = value;
  
  // Handle numeric fields
  if (['width', 'height', 'num_images', 'seed'].includes(name)) {
    processedValue = parseInt(value) || 0;
  } else if (['contrast', 'upscale_strength', 'photoreal_strength'].includes(name)) {
    processedValue = parseFloat(value);
  } else if (['alchemy', 'enhance_prompt', 'upscale', 'ultra'].includes(name)) {
    processedValue = value === 'true';
  }
  
  setFormData(prev => ({
    ...prev,
    [name]: processedValue
  }));
};

/**
 * Handle select change with proper type conversion
 */
export const handleSelectChange = (
  setFormData: (data: FormData | ((prev: FormData) => FormData)) => void
) => (name: string) => (event: SelectChangeEvent<string | number>) => {
  const value = event.target.value;
  
  let processedValue: any = value;
  
  // Handle numeric fields
  if (['width', 'height', 'num_images', 'seed'].includes(name)) {
    processedValue = typeof value === 'string' ? parseInt(value) : value;
  } else if (['contrast', 'upscale_strength', 'photoreal_strength'].includes(name)) {
    processedValue = typeof value === 'string' ? parseFloat(value) : value;
  }
  
  setFormData(prev => ({
    ...prev,
    [name]: processedValue
  }));
};

/**
 * Create parameter object for Phoenix API
 */
export const createPhoenixParams = (formData: FormData) => ({
  prompt: formData.prompt,
  width: formData.width,
  height: formData.height,
  num_images: formData.num_images,
  style: formData.style,
  contrast: formData.contrast,
  alchemy: formData.alchemy,
  enhance_prompt: formData.enhance_prompt,
  ultra: formData.ultra,
  negative_prompt: formData.negative_prompt,
  upscale: formData.upscale,
  upscale_strength: formData.upscale_strength,
});

/**
 * Create parameter object for FLUX API
 */
export const createFluxParams = (formData: FormData) => ({
  prompt: formData.prompt,
  width: formData.width,
  height: formData.height,
  num_images: formData.num_images,
  model_type: formData.model_type,
  style: formData.style,
  contrast: formData.contrast,
  enhance_prompt: formData.enhance_prompt,
  enhance_prompt_instruction: formData.enhance_prompt_instruction,
  negative_prompt: formData.negative_prompt,
  ultra: formData.ultra,
  seed: formData.seed,
});

/**
 * Create parameter object for PhotoReal API
 */
export const createPhotoRealParams = (formData: FormData) => ({
  prompt: formData.prompt,
  width: formData.width,
  height: formData.height,
  num_images: formData.num_images,
  photoreal_version: formData.photoreal_version,
  model_id: formData.photoreal_version === 'v2' && formData.model_id?.trim() ? formData.model_id : undefined,
  style: formData.style,
  contrast: formData.contrast,
  photoreal_strength: formData.photoreal_version === 'v1' ? formData.photoreal_strength : undefined,
  enhance_prompt: formData.enhance_prompt,
  negative_prompt: formData.negative_prompt,
});

/**
 * Create batch configuration from form data
 */
export const createBatchConfig = (
  formData: FormData, 
  selectedModel: 'phoenix' | 'flux' | 'photoreal'
) => ({
  model: selectedModel,
  num_images: formData.num_images,
  width: formData.width,
  height: formData.height,
  style: formData.style,
  contrast: formData.contrast,
  enhance_prompt: formData.enhance_prompt,
  negative_prompt: formData.negative_prompt,
  
  // Model-specific parameters
  ...(selectedModel === 'phoenix' && {
    alchemy: formData.alchemy,
    ultra: formData.ultra,
    upscale: formData.upscale,
    upscale_strength: formData.upscale_strength,
  }),
  
  ...(selectedModel === 'flux' && {
    model_type: formData.model_type,
    ultra: formData.ultra,
    enhance_prompt_instruction: formData.enhance_prompt_instruction,
    seed: formData.seed,
  }),
  
  ...(selectedModel === 'photoreal' && {
    photoreal_version: formData.photoreal_version,
    model_id: formData.model_id,
    photoreal_strength: formData.photoreal_strength,
  })
});
