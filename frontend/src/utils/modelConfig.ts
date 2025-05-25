/**
 * Model configuration and style management utilities
 */

export interface ModelConfig {
  name: string;
  styles: string[];
  defaultStyle: string;
  supportedDimensions: Array<{ width: number; height: number }>;
  defaultDimensions: { width: number; height: number };
  features: {
    alchemy?: boolean;
    ultra?: boolean;
    upscale?: boolean;
    enhance_prompt?: boolean;
    negative_prompt?: boolean;
    photoreal_version?: boolean;
    model_type?: boolean;
    seed?: boolean;
  };
}

// Phoenix model configuration
export const PHOENIX_CONFIG: ModelConfig = {
  name: 'Phoenix',
  styles: [
    "3D Render", "Bokeh", "Cinematic", "Cinematic Concept", "Creative", "Dynamic", 
    "Fashion", "Graphic Design Pop Art", "Graphic Design Vector", "HDR", "Illustration", 
    "Macro", "Minimalist", "Moody", "None", "Portrait", "Pro B&W photography", 
    "Pro color photography", "Pro film photography", "Portrait Fashion", "Ray Traced", 
    "Sketch (B&W)", "Sketch (Color)", "Stock Photo", "Vibrant"
  ],
  defaultStyle: 'Dynamic',
  supportedDimensions: [
    { width: 512, height: 512 },
    { width: 768, height: 768 },
    { width: 1024, height: 1024 },
    { width: 1536, height: 1536 },
    { width: 832, height: 1216 },
    { width: 1216, height: 832 },
    { width: 1344, height: 768 },
    { width: 768, height: 1344 }
  ],
  defaultDimensions: { width: 1024, height: 1024 },
  features: {
    alchemy: true,
    upscale: true,
    enhance_prompt: true,
    negative_prompt: true
  }
};

// FLUX model configuration
export const FLUX_CONFIG: ModelConfig = {
  name: 'FLUX',
  styles: [
    "3D Render", "Acrylic", "Anime General", "Creative", "Dynamic", "Fashion", 
    "Game Concept", "Graphic Design 3D", "Illustration", "None", "Portrait", 
    "Portrait Cinematic", "Ray Traced", "Stock Photo", "Watercolor"
  ],
  defaultStyle: 'Dynamic',
  supportedDimensions: [
    { width: 512, height: 512 },
    { width: 768, height: 768 },
    { width: 1024, height: 1024 },
    { width: 1536, height: 1536 },
    { width: 832, height: 1216 },
    { width: 1216, height: 832 }
  ],
  defaultDimensions: { width: 1024, height: 1024 },
  features: {
    ultra: true,
    enhance_prompt: true,
    negative_prompt: true,
    model_type: true,
    seed: true
  }
};

// PhotoReal model configuration
export const PHOTOREAL_CONFIG: ModelConfig = {
  name: 'PhotoReal',
  styles: [
    "BOKEH", "CINEMATIC", "CINEMATIC_CLOSEUP", "CREATIVE", "FASHION", "FILM", 
    "FOOD", "HDR", "LONG_EXPOSURE", "MACRO", "MINIMALISTIC", "MONOCHROME", 
    "MOODY", "NEUTRAL", "PORTRAIT", "RETRO", "STOCK_PHOTO", "VIBRANT", "UNPROCESSED"
  ],
  defaultStyle: 'CINEMATIC',
  supportedDimensions: [
    { width: 512, height: 512 },
    { width: 768, height: 768 },
    { width: 1024, height: 1024 },
    { width: 1536, height: 1536 }
  ],
  defaultDimensions: { width: 1024, height: 1024 },
  features: {
    enhance_prompt: true,
    negative_prompt: true,
    photoreal_version: true
  }
};

// PhotoReal v1 specific styles
export const PHOTOREAL_V1_STYLES = ["CINEMATIC", "CREATIVE", "VIBRANT"];

/**
 * Get model configuration by name
 */
export const getModelConfig = (modelName: 'phoenix' | 'flux' | 'photoreal'): ModelConfig => {
  switch (modelName) {
    case 'phoenix':
      return PHOENIX_CONFIG;
    case 'flux':
      return FLUX_CONFIG;
    case 'photoreal':
      return PHOTOREAL_CONFIG;
    default:
      return PHOENIX_CONFIG;
  }
};

/**
 * Get available styles for a model
 */
export const getAvailableStyles = (
  modelName: 'phoenix' | 'flux' | 'photoreal', 
  photorealVersion?: 'v1' | 'v2'
): string[] => {
  if (modelName === 'photoreal' && photorealVersion === 'v1') {
    return PHOTOREAL_V1_STYLES;
  }
  
  const config = getModelConfig(modelName);
  return config.styles;
};

/**
 * Check if a model supports a specific feature
 */
export const modelSupportsFeature = (
  modelName: 'phoenix' | 'flux' | 'photoreal', 
  feature: keyof ModelConfig['features']
): boolean => {
  const config = getModelConfig(modelName);
  return !!config.features[feature];
};

/**
 * Get default values for a model
 */
export const getModelDefaults = (modelName: 'phoenix' | 'flux' | 'photoreal') => {
  const config = getModelConfig(modelName);
  
  return {
    style: config.defaultStyle,
    width: config.defaultDimensions.width,
    height: config.defaultDimensions.height,
    num_images: 1,
    contrast: 3.5,
    enhance_prompt: false,
    negative_prompt: '',
    
    // Model-specific defaults
    ...(modelName === 'phoenix' && {
      alchemy: true,
      upscale: false,
      upscale_strength: 0.35
    }),
    
    ...(modelName === 'flux' && {
      model_type: 'flux_precision' as const,
      ultra: false,
      enhance_prompt_instruction: '',
      seed: undefined
    }),
    
    ...(modelName === 'photoreal' && {
      photoreal_version: 'v2' as const,
      model_id: 'aa77f04e-3eec-4034-9c07-d0f619684628',
      photoreal_strength: undefined
    })
  };
};
