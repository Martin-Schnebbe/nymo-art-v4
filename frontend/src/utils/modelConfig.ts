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
    enhance_prompt_instruction?: boolean;
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
    negative_prompt: true,
    ultra: true
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
    enhance_prompt_instruction: true,
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
      upscale_strength: 0.35,
      ultra: false
    }),
    
    ...(modelName === 'flux' && {
      model_type: 'flux_precision' as const,
      ultra: false,
      enhance_prompt_instruction: '',
      seed: undefined
    }),
    
    ...(modelName === 'photoreal' && {
      photoreal_version: 'v2' as const,
      model_id: '', // Empty by default, backend will set default if needed
      photoreal_strength: undefined
    })
  };
};

// FLUX Style UUID mapping (from Leonardo API documentation)
export const FLUX_STYLE_UUIDS: Record<string, string> = {
  "3D Render": "debdf72a-91a4-467b-bf61-cc02bdeb69c6",
  "Acrylic": "3cbb655a-7ca4-463f-b697-8a03ad67327c",
  "Anime General": "b2a54a51-230b-4d4f-ad4e-8409bf58645f",
  "Creative": "6fedbf1f-4a17-45ec-84fb-92fe524a29ef",
  "Dynamic": "111dc692-d470-4eec-b791-3475abac4c46",
  "Fashion": "594c4a08-a522-4e0e-b7ff-e4dac4b6b622",
  "Game Concept": "09d2b5b5-d7c5-4c02-905d-9f84051640f4",
  "Graphic Design 3D": "7d7c2bc5-4b12-4ac3-81a9-630057e9e89f",
  "Illustration": "645e4195-f63d-4715-a3f2-3fb1e6eb8c70",
  "None": "556c1ee5-ec38-42e8-955a-1e82dad0ffa1",
  "Portrait": "8e2bc543-6ee2-45f9-bcd9-594b6ce84dcd",
  "Portrait Cinematic": "4edb03c9-8a26-4041-9d01-f85b5d4abd71",
  "Ray Traced": "b504f83c-3326-4947-82e1-7fe9e839ec0f",
  "Stock Photo": "5bdc3f2a-1be6-4d1c-8e77-992a30824a2c",
  "Watercolor": "1db308ce-c7ad-4d10-96fd-592fa6b75cc4"
};

// Phoenix Style UUID mapping (from Leonardo API documentation)
export const PHOENIX_STYLE_UUIDS: Record<string, string> = {
  "3D Render": "debdf72a-91a4-467b-bf61-cc02bdeb69c6",
  "Bokeh": "9fdc5e8c-4d13-49b4-9ce6-5a74cbb19177",
  "Cinematic": "a5632c7c-ddbb-4e2f-ba34-8456ab3ac436",
  "Cinematic Concept": "33abbb99-03b9-4dd7-9761-ee98650b2c88",
  "Creative": "6fedbf1f-4a17-45ec-84fb-92fe524a29ef",
  "Dynamic": "111dc692-d470-4eec-b791-3475abac4c46",
  "Fashion": "594c4a08-a522-4e0e-b7ff-e4dac4b6b622",
  "Graphic Design Pop Art": "2e74ec31-f3a4-4825-b08b-2894f6d13941",
  "Graphic Design Vector": "1fbb6a68-9319-44d2-8d56-2957ca0ece6a",
  "HDR": "97c20e5c-1af6-4d42-b227-54d03d8f0727",
  "Illustration": "645e4195-f63d-4715-a3f2-3fb1e6eb8c70",
  "Macro": "30c1d34f-e3a9-479a-b56f-c018bbc9c02a",
  "Minimalist": "cadc8cd6-7838-4c99-b645-df76be8ba8d8",
  "Moody": "621e1c9a-6319-4bee-a12d-ae40659162fa",
  "None": "556c1ee5-ec38-42e8-955a-1e82dad0ffa1",
  "Portrait": "8e2bc543-6ee2-45f9-bcd9-594b6ce84dcd",
  "Pro B&W photography": "22a9a7d2-2166-4d86-80ff-22e2643adbcf",
  "Pro color photography": "7c3f932b-a572-47cb-9b9b-f20211e63b5b",
  "Pro film photography": "581ba6d6-5aac-4492-bebe-54c424a0d46e",
  "Portrait Fashion": "0d34f8e1-46d4-428f-8ddd-4b11811fa7c9",
  "Ray Traced": "b504f83c-3326-4947-82e1-7fe9e839ec0f",
  "Sketch (B&W)": "be8c6b58-739c-4d44-b9c1-b032ed308b61",
  "Sketch (Color)": "093accc3-7633-4ffd-82da-d34000dfc0d6",
  "Stock Photo": "5bdc3f2a-1be6-4d1c-8e77-992a30824a2c",
  "Vibrant": "dee282d3-891f-4f73-ba02-7f8131e5541b"
};

// FLUX model IDs
export const FLUX_MODEL_IDS = {
  flux_speed: "1dd50843-d653-4516-a8e3-f0238ee453ff", // Flux Schnell
  flux_precision: "b2614463-296c-462a-9586-aafdb8f00e36" // Flux Dev
};

/**
 * Get FLUX style UUID from style name
 */
export const getFluxStyleUUID = (styleName: string): string | undefined => {
  return FLUX_STYLE_UUIDS[styleName];
};

/**
 * Get FLUX model ID from model type
 */
export const getFluxModelId = (modelType: 'flux_speed' | 'flux_precision'): string => {
  return FLUX_MODEL_IDS[modelType];
};

// Phoenix model ID
export const PHOENIX_MODEL_ID = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"; // Leonardo Phoenix 1.0

/**
 * Get Phoenix style UUID from style name
 */
export const getPhoenixStyleUUID = (styleName: string): string | undefined => {
  return PHOENIX_STYLE_UUIDS[styleName];
};
