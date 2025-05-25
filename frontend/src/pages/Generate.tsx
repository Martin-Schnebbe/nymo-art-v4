import { useState } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Image as ImageIcon,
} from '@mui/icons-material';

import ModelSelector from '../components/ModelSelector';
import PromptInput from '../components/PromptInput';
import DimensionsSelector from '../components/DimensionsSelector';
import ModelFilters from '../components/ModelFilters';
import ImageGallery from '../components/ImageGallery';
import { useFormData } from '../hooks/useFormData';

import { generateImages, validateGenerationParams } from '../services/imageGenerationService';
import { downloadImage } from '../utils/imageUtils';

const Generate = () => {
  const [selectedModel, setSelectedModel] = useState<'phoenix' | 'flux' | 'photoreal'>('phoenix');
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { 
    formData, 
    handleInputChange, 
    handleSelectChange
  } = useFormData(selectedModel);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Validate parameters first
      const validation = validateGenerationParams(selectedModel, formData);
      if (!validation.isValid) {
        setError(validation.errors.join(', '));
        return;
      }

      // Generate images using unified service
      const result = await generateImages(selectedModel, formData);
      
      // Set the base64 images for display
      setImages(result.images);
      
    } catch (err) {
      console.error('Generation error:', err);
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadImage = (imageData: string, index: number) => {
    downloadImage(imageData, index);
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

                {/* Model Filters */}
                <ModelFilters
                  selectedModel={selectedModel}
                  formData={formData}
                  handleInputChange={handleInputChange}
                  handleSelectChange={handleSelectChange}
                />

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
            onDownload={handleDownloadImage} 
          />
        </Box>
      </Box>
    </Container>
  );
};

export default Generate;
