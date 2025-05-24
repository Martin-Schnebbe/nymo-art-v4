import { useState } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Image as ImageIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

import ModelSelector from '../components/ModelSelector';
import PromptInput from '../components/PromptInput';
import DimensionsSelector from '../components/DimensionsSelector';
import PhoenixSettings from '../components/PhoenixSettings';
import FluxSettings from '../components/FluxSettings';
import PhotoRealSettings from '../components/PhotoRealSettings';
import ImageGallery from '../components/ImageGallery';
import { useFormData } from '../hooks/useFormData';

import { generatePhoenix, type PhoenixParams } from '../services/phoenixClient';
import { generateFlux, type FluxParams } from '../services/fluxClient';
import { generatePhotoReal, type PhotoRealParams } from '../services/photorealClient';

const Generate = () => {
  const [selectedModel, setSelectedModel] = useState<'phoenix' | 'flux' | 'photoreal'>('phoenix');
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { 
    formData, 
    handleInputChange, 
    handleSelectChange, 
    getAvailableStyles 
  } = useFormData(selectedModel);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      let result;
      
      if (selectedModel === 'phoenix') {
        const phoenixParams: PhoenixParams = {
          prompt: formData.prompt,
          width: formData.width,
          height: formData.height,
          num_images: formData.num_images,
          style: formData.style,
          contrast: formData.contrast,
          alchemy: formData.alchemy,
          enhance_prompt: formData.enhance_prompt,
          negative_prompt: formData.negative_prompt,
          upscale: formData.upscale,
          upscale_strength: formData.upscale_strength,
        };
        result = await generatePhoenix(phoenixParams);
      } else if (selectedModel === 'flux') {
        const fluxParams: FluxParams = {
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
        };
        result = await generateFlux(fluxParams);
      } else if (selectedModel === 'photoreal') {
        const photorealParams: PhotoRealParams = {
          prompt: formData.prompt,
          width: formData.width,
          height: formData.height,
          num_images: formData.num_images,
          photoreal_version: formData.photoreal_version,
          model_id: formData.photoreal_version === 'v2' ? formData.model_id : undefined,
          style: formData.style,
          contrast: formData.contrast,
          photoreal_strength: formData.photoreal_version === 'v1' ? formData.photoreal_strength : undefined,
          enhance_prompt: formData.enhance_prompt,
          negative_prompt: formData.negative_prompt,
        };
        result = await generatePhotoReal(photorealParams);
      }
      
      // Convert image URLs to base64 for display
      if (result && result.image_urls && result.image_urls.length > 0) {
        const imagePromises = result.image_urls.map(async (url) => {
          try {
            const fullUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`;
            const response = await fetch(fullUrl);
            if (!response.ok) {
              throw new Error(`Failed to fetch image: ${response.status}`);
            }
            
            const blob = await response.blob();
            return new Promise<string>((resolve, reject) => {
              const reader = new FileReader();
              reader.onloadend = () => {
                const base64 = reader.result as string;
                resolve(base64.split(',')[1]);
              };
              reader.onerror = reject;
              reader.readAsDataURL(blob);
            });
          } catch (err) {
            console.error('Error fetching image:', err);
            throw err;
          }
        });
        
        const base64Images = await Promise.all(imagePromises);
        setImages(base64Images);
      } else {
        setError('No images were generated');
      }
    } catch (err) {
      console.error('Generation error:', err);
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = (imageData: string, index: number) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${imageData}`;
    link.download = `nymo-art-${Date.now()}-${index + 1}.png`;
    link.click();
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box display="flex" flexDirection={{ xs: 'column', lg: 'row' }} gap={4}>
        {/* Left Side - Controls */}
        <Box flex={1}>
          <Card 
            elevation={0} 
            sx={{ 
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: 3
            }}
          >
            <CardContent sx={{ p: 4 }}>
              <Box display="flex" alignItems="center" mb={3}>
                <ImageIcon sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h5" fontWeight="600">
                  Create Your Image
                </Typography>
              </Box>
              
              <Box component="form" onSubmit={handleSubmit}>
                <ModelSelector 
                  selectedModel={selectedModel} 
                  onModelChange={setSelectedModel} 
                />
                
                <PromptInput 
                  value={formData.prompt}
                  onChange={handleInputChange}
                />
                
                <DimensionsSelector
                  width={formData.width}
                  height={formData.height}
                  onWidthChange={handleSelectChange('width')}
                  onHeightChange={handleSelectChange('height')}
                />

                {/* Advanced Settings */}
                <Accordion 
                  sx={{ 
                    mb: 3, 
                    background: 'rgba(248, 250, 252, 0.8)',
                    border: '1px solid rgba(226, 232, 240, 0.5)',
                    borderRadius: 3,
                    '&:before': { display: 'none' },
                    '& .MuiAccordionSummary-root': {
                      borderRadius: 3,
                    },
                    '& .MuiAccordionDetails-root': {
                      borderRadius: '0 0 12px 12px',
                    }
                  }}
                >
                  <AccordionSummary 
                    expandIcon={<ExpandMoreIcon />}
                    sx={{ borderRadius: 3 }}
                  >
                    <Box display="flex" alignItems="center">
                      <SettingsIcon sx={{ mr: 2, color: 'text.secondary' }} />
                      <Typography fontWeight="500">Advanced Settings</Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails sx={{ pt: 2, pb: 3 }}>
                    <Box display="flex" flexDirection="column" gap={3}>
                      {/* Basic Settings Row */}
                      <Box display="flex" gap={2}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Images</InputLabel>
                          <Select
                            name="num_images"
                            value={formData.num_images}
                            onChange={handleSelectChange('num_images')}
                            label="Images"
                            sx={{ borderRadius: 2 }}
                          >
                            {[1,2,3,4,5,6,7,8,9,10].map(num => (
                              <MenuItem key={num} value={num}>{num} image{num > 1 ? 's' : ''}</MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                        
                        <FormControl fullWidth size="small">
                          <InputLabel>Style</InputLabel>
                          <Select
                            name="style"
                            value={formData.style || 'Dynamic'}
                            onChange={handleInputChange}
                            label="Style"
                            sx={{ borderRadius: 2 }}
                          >
                            {getAvailableStyles().map((style) => (
                              <MenuItem key={style} value={style}>
                                {style}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                        
                        <FormControl fullWidth size="small">
                          <InputLabel>Contrast</InputLabel>
                          <Select
                            name="contrast"
                            value={formData.contrast}
                            onChange={handleSelectChange('contrast')}
                            label="Contrast"
                            sx={{ borderRadius: 2 }}
                          >
                            <MenuItem value={1.0}>1.0 - Subtle</MenuItem>
                            <MenuItem value={1.3}>1.3 - Light</MenuItem>
                            <MenuItem value={1.8}>1.8 - Moderate</MenuItem>
                            <MenuItem value={2.5}>2.5 - Medium</MenuItem>
                            <MenuItem value={3.0}>3.0 - Enhanced</MenuItem>
                            <MenuItem value={3.5}>3.5 - Strong</MenuItem>
                            <MenuItem value={4.0}>4.0 - Bold</MenuItem>
                            <MenuItem value={4.5}>4.5 - Maximum</MenuItem>
                          </Select>
                        </FormControl>
                      </Box>
                      
                      {/* Model-specific settings */}
                      {selectedModel === 'phoenix' && (
                        <PhoenixSettings 
                          formData={formData} 
                          onChange={handleInputChange}
                        />
                      )}
                      
                      {selectedModel === 'flux' && (
                        <FluxSettings 
                          formData={formData} 
                          onChange={handleInputChange}
                          onSelectChange={handleSelectChange}
                        />
                      )}
                      
                      {selectedModel === 'photoreal' && (
                        <PhotoRealSettings 
                          formData={formData} 
                          onChange={handleInputChange}
                          onSelectChange={handleSelectChange}
                        />
                      )}
                      
                      {/* Negative Prompt */}
                      <TextField
                        fullWidth
                        size="small"
                        multiline
                        rows={2}
                        name="negative_prompt"
                        label="Negative Prompt (Optional)"
                        placeholder="blurry, low quality, distorted..."
                        value={formData.negative_prompt || ''}
                        onChange={handleInputChange}
                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                      />
                    </Box>
                  </AccordionDetails>
                </Accordion>

                {/* Generate Button */}
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading || !formData.prompt.trim()}
                  sx={{ 
                    py: 2, 
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    fontWeight: 600,
                    fontSize: '1.1rem',
                    mt: 1
                  }}
                >
                  {loading ? (
                    <Box display="flex" alignItems="center" gap={2}>
                      <CircularProgress size={20} color="inherit" />
                      <span>Generating...</span>
                    </Box>
                  ) : (
                    'Generate Images'
                  )}
                </Button>
              </Box>

              {/* Error Message */}
              {error && (
                <Alert severity="error" sx={{ mt: 3, borderRadius: 3 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Right Side - Results */}
        <Box flex={1}>
          <ImageGallery 
            images={images} 
            onDownload={downloadImage} 
          />
        </Box>
      </Box>
    </Container>
  );
};

export default Generate;
