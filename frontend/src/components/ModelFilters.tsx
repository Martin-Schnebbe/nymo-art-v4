import React from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, TextField } from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import type { ChangeEvent } from 'react';
import { getModelConfig, getAvailableStyles } from '../utils/modelConfig';

interface ModelFiltersProps {
  selectedModel: 'phoenix' | 'flux' | 'photoreal';
  formData: Record<string, any>;
  handleInputChange: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleSelectChange: (name: string) => (e: SelectChangeEvent<any>) => void;
}

const ModelFilters: React.FC<ModelFiltersProps> = ({ selectedModel, formData, handleInputChange, handleSelectChange }) => {
  const config = getModelConfig(selectedModel);
  
  // Get available styles based on model and version
  const getStyles = () => {
    if (selectedModel === 'photoreal') {
      return getAvailableStyles(selectedModel, formData.photoreal_version);
    }
    return config.styles;
  };
  
  const availableStyles = getStyles();
  
  return (
    <Box display="flex" flexDirection="column" gap={2}>
      {/* Style */}
      <FormControl fullWidth size="small">
        <InputLabel>Style</InputLabel>
        <Select name="style" value={formData.style} onChange={handleSelectChange('style')} label="Style">
          {availableStyles.map(style => <MenuItem key={style} value={style}>{style}</MenuItem>)}
        </Select>
      </FormControl>
      {/* Contrast */}
      <FormControl fullWidth size="small">
        <InputLabel>Contrast</InputLabel>
        <Select name="contrast" value={formData.contrast} onChange={handleSelectChange('contrast')} label="Contrast">
          <MenuItem value={1.0}>1.0</MenuItem>
          <MenuItem value={1.3}>1.3</MenuItem>
          <MenuItem value={1.8}>1.8</MenuItem>
          <MenuItem value={2.5}>2.5</MenuItem>
          <MenuItem value={3.0}>3.0</MenuItem>
          <MenuItem value={3.5}>3.5</MenuItem>
          <MenuItem value={4.0}>4.0</MenuItem>
          <MenuItem value={4.5}>4.5</MenuItem>
        </Select>
      </FormControl>
      {/* Dynamic features */}
      {config.features.alchemy && (
        <FormControl fullWidth size="small">
          <InputLabel>Alchemy</InputLabel>
          <Select name="alchemy" value={String(formData.alchemy)} onChange={handleSelectChange('alchemy')} label="Alchemy">
            <MenuItem value="true">Enabled</MenuItem>
            <MenuItem value="false">Disabled</MenuItem>
          </Select>
        </FormControl>
      )}
      {config.features.upscale && (
        <>
          <FormControl fullWidth size="small">
            <InputLabel>Upscale</InputLabel>
            <Select name="upscale" value={String(formData.upscale)} onChange={handleSelectChange('upscale')} label="Upscale">
              <MenuItem value="true">Enabled</MenuItem>
              <MenuItem value="false">Disabled</MenuItem>
            </Select>
          </FormControl>
          {formData.upscale && (
            <FormControl fullWidth size="small">
              <InputLabel>Upscale Strength</InputLabel>
              <Select name="upscale_strength" value={formData.upscale_strength} onChange={handleSelectChange('upscale_strength')} label="Upscale Strength">
                <MenuItem value={0.1}>0.1 - Subtle</MenuItem>
                <MenuItem value={0.35}>0.35 - Default</MenuItem>
                <MenuItem value={0.75}>0.75 - Strong</MenuItem>
                <MenuItem value={1.0}>1.0 - Maximum</MenuItem>
              </Select>
            </FormControl>
          )}
        </>
      )}
      {config.features.enhance_prompt && (
        <FormControl fullWidth size="small">
          <InputLabel>Enhance Prompt</InputLabel>
          <Select name="enhance_prompt" value={String(formData.enhance_prompt)} onChange={handleSelectChange('enhance_prompt')} label="Enhance Prompt">
            <MenuItem value="true">Enabled</MenuItem>
            <MenuItem value="false">Disabled</MenuItem>
          </Select>
        </FormControl>
      )}
      {config.features.ultra && (
        <FormControl fullWidth size="small">
          <InputLabel>Ultra Mode</InputLabel>
          <Select name="ultra" value={String(formData.ultra)} onChange={handleSelectChange('ultra')} label="Ultra Mode">
            <MenuItem value="true">Enabled</MenuItem>
            <MenuItem value="false">Disabled</MenuItem>
          </Select>
        </FormControl>
      )}
      {config.features.enhance_prompt_instruction && (
        <TextField 
          fullWidth 
          size="small" 
          name="enhance_prompt_instruction" 
          label="Enhance Prompt Instruction" 
          value={formData.enhance_prompt_instruction || ''} 
          onChange={handleInputChange}
          helperText="Custom instruction for prompt enhancement"
        />
      )}
      {config.features.model_type && (
        <FormControl fullWidth size="small">
          <InputLabel>Model Type</InputLabel>
          <Select name="model_type" value={formData.model_type} onChange={handleSelectChange('model_type')} label="Model Type">
            <MenuItem value="flux_speed">FLUX Speed</MenuItem>
            <MenuItem value="flux_precision">FLUX Precision</MenuItem>
          </Select>
        </FormControl>
      )}
      {config.features.seed && (
        <TextField 
          fullWidth 
          size="small" 
          name="seed" 
          type="number" 
          label="Seed" 
          inputProps={{ min: 0, max: 2147483638, step: 1 }} 
          value={formData.seed ?? ''} 
          onChange={handleInputChange}
          helperText="Seed for reproducible generation (optional)"
        />
      )}
      {config.features.photoreal_version && (
        <>
          <FormControl fullWidth size="small">
            <InputLabel>PhotoReal Version</InputLabel>
            <Select name="photoreal_version" value={formData.photoreal_version} onChange={handleSelectChange('photoreal_version')} label="PhotoReal Version">
              <MenuItem value="v1">Version 1</MenuItem>
              <MenuItem value="v2">Version 2</MenuItem>
            </Select>
          </FormControl>
          {formData.photoreal_version === 'v1' && (
            <TextField fullWidth size="small" name="photoreal_strength" type="number" label="Strength" inputProps={{ step:0.1, min:0.1, max:1.0 }} value={formData.photoreal_strength ?? ''} onChange={handleInputChange} />
          )}
          {formData.photoreal_version === 'v2' && (
            <TextField 
              fullWidth 
              size="small" 
              name="model_id" 
              label="Model ID (optional)" 
              value={formData.model_id || ''} 
              onChange={handleInputChange}
              helperText="Leave empty to use default PhotoReal v2 model"
            />
          )}
        </>
      )}
      {config.features.negative_prompt && (
        <TextField fullWidth size="small" multiline rows={2} name="negative_prompt" label="Negative Prompt" value={formData.negative_prompt} onChange={handleInputChange} />
      )}
    </Box>
  );
};

export default ModelFilters;
