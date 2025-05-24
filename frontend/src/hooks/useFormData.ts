import { useState, useEffect } from 'react';
import type { SelectChangeEvent } from '@mui/material';

export interface FormData {
  prompt: string;
  width: number;
  height: number;
  num_images: number;
  style: string;
  contrast: number;
  enhance_prompt: boolean;
  negative_prompt: string;
  ultra: boolean;
  // Phoenix-specific
  alchemy: boolean;
  upscale: boolean;
  upscale_strength: number;
  // FLUX-specific
  model_type: 'flux_speed' | 'flux_precision';
  enhance_prompt_instruction: string;
  seed?: number;
  // PhotoReal-specific
  photoreal_version: 'v1' | 'v2';
  model_id: string;
  photoreal_strength?: number;
}

export const useFormData = (selectedModel: 'phoenix' | 'flux' | 'photoreal') => {
  const [formData, setFormData] = useState<FormData>({
    prompt: '',
    width: 1024,
    height: 1024,
    num_images: 1,
    style: 'Dynamic',
    contrast: 3.5,
    enhance_prompt: false,
    negative_prompt: '',
    ultra: false,
    // Phoenix-specific
    alchemy: true,
    upscale: false,
    upscale_strength: 0.35,
    // FLUX-specific
    model_type: 'flux_precision',
    enhance_prompt_instruction: '',
    seed: undefined,
    // PhotoReal-specific
    photoreal_version: 'v2',
    model_id: 'aa77f04e-3eec-4034-9c07-d0f619684628',
    photoreal_strength: undefined,
  });

  // Style constants
  const PHOENIX_STYLES = [
    "3D Render", "Bokeh", "Cinematic", "Cinematic Concept", "Creative", "Dynamic", 
    "Fashion", "Graphic Design Pop Art", "Graphic Design Vector", "HDR", "Illustration", 
    "Macro", "Minimalist", "Moody", "None", "Portrait", "Pro B&W photography", 
    "Pro color photography", "Pro film photography", "Portrait Fashion", "Ray Traced", 
    "Sketch (B&W)", "Sketch (Color)", "Stock Photo", "Vibrant"
  ];

  const FLUX_STYLES = [
    "3D Render", "Acrylic", "Anime General", "Creative", "Dynamic", "Fashion", 
    "Game Concept", "Graphic Design 3D", "Illustration", "None", "Portrait", 
    "Portrait Cinematic", "Ray Traced", "Stock Photo", "Watercolor"
  ];

  const PHOTOREAL_STYLES = {
    v1: ["CINEMATIC", "CREATIVE", "VIBRANT"],
    v2: [
      "BOKEH", "CINEMATIC", "CINEMATIC_CLOSEUP", "CREATIVE", "FASHION", "FILM", 
      "FOOD", "HDR", "LONG_EXPOSURE", "MACRO", "MINIMALISTIC", "MONOCHROME", 
      "MOODY", "NEUTRAL", "PORTRAIT", "RETRO", "STOCK_PHOTO", "VIBRANT", "UNPROCESSED"
    ]
  };

  // Reset style when model changes
  useEffect(() => {
    let currentStyles: string[] = [];
    
    if (selectedModel === 'phoenix') {
      currentStyles = PHOENIX_STYLES;
    } else if (selectedModel === 'flux') {
      currentStyles = FLUX_STYLES;
    } else if (selectedModel === 'photoreal') {
      currentStyles = PHOTOREAL_STYLES[formData.photoreal_version];
    }
    
    const currentStyle = formData.style;
    
    if (!currentStyles.includes(currentStyle)) {
      const defaultStyle = selectedModel === 'photoreal' ? 'CINEMATIC' : 'Dynamic';
      setFormData(prev => ({
        ...prev,
        style: defaultStyle
      }));
    }
  }, [selectedModel, formData.photoreal_version]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | any) => {
    const { name, value } = e.target;
    
    let processedValue = value;
    
    if (name === 'width' || name === 'height' || name === 'num_images' || name === 'seed') {
      processedValue = parseInt(value) || 0;
    } else if (name === 'contrast' || name === 'upscale_strength') {
      processedValue = parseFloat(value);
    } else if (name === 'alchemy' || name === 'enhance_prompt' || name === 'upscale' || name === 'ultra') {
      processedValue = value === 'true';
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: processedValue
    }));
  };

  const handleSelectChange = (name: string) => (event: SelectChangeEvent<string | number>) => {
    const value = event.target.value;
    
    setFormData(prev => {
      let processedValue = value;
      
      if (name === 'width' || name === 'height' || name === 'num_images' || name === 'seed') {
        processedValue = typeof value === 'string' ? parseInt(value) : value;
      } else if (name === 'contrast' || name === 'upscale_strength') {
        processedValue = typeof value === 'string' ? parseFloat(value) : value;
      }
      
      return {
        ...prev,
        [name]: processedValue
      };
    });
  };

  const getAvailableStyles = () => {
    if (selectedModel === 'phoenix') {
      return PHOENIX_STYLES;
    } else if (selectedModel === 'flux') {
      return FLUX_STYLES;
    } else if (selectedModel === 'photoreal') {
      return PHOTOREAL_STYLES[formData.photoreal_version];
    }
    return [];
  };

  return {
    formData,
    setFormData,
    handleInputChange,
    handleSelectChange,
    getAvailableStyles
  };
};
