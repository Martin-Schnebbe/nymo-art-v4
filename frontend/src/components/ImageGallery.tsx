import { 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  CardMedia, 
  CardActions, 
  IconButton, 
  Tooltip,
  Paper,
  Box
} from '@mui/material';
import { Download as DownloadIcon, Image as ImageIcon } from '@mui/icons-material';

interface ImageGalleryProps {
  images: string[];
  onDownload: (imageData: string, index: number) => void;
}

const ImageGallery = ({ images, onDownload }: ImageGalleryProps) => {
  if (images.length === 0) {
    return (
      <Paper 
        elevation={0}
        sx={{ 
          p: 8, 
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: 3
        }}
      >
        <Box
          sx={{
            width: 80,
            height: 80,
            background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
            borderRadius: 3,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 3
          }}
        >
          <ImageIcon sx={{ fontSize: 40, color: 'text.secondary' }} />
        </Box>
        <Typography variant="h5" fontWeight="600" mb={2}>
          Ready to create
        </Typography>
        <Typography color="text.secondary" mb={4}>
          Enter a prompt and click generate to see your AI-created images appear here.
        </Typography>
        <Box display="flex" justifyContent="center" gap={1}>
          {[0, 1, 2].map((i) => (
            <Box
              key={i}
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: `rgba(100, 116, 139, ${0.3 - i * 0.1})`
              }}
            />
          ))}
        </Box>
      </Paper>
    );
  }

  return (
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
        <Typography variant="h5" fontWeight="600" mb={3}>
          Generated Images ({images.length})
        </Typography>
        <Grid container spacing={2}>
          {images.map((image, index) => {
            // Responsive grid logic
            let gridSize;
            if (images.length === 1) {
              gridSize = { xs: 12, sm: 12, md: 12 };
            } else if (images.length === 2) {
              gridSize = { xs: 12, sm: 6, md: 6 };
            } else if (images.length === 3) {
              gridSize = { xs: 12, sm: 6, md: 4 };
            } else if (images.length === 4) {
              gridSize = { xs: 12, sm: 6, md: 3 };
            } else if (images.length <= 6) {
              gridSize = { xs: 12, sm: 6, md: 4 };
            } else if (images.length <= 8) {
              gridSize = { xs: 12, sm: 6, md: 3 };
            } else {
              gridSize = { xs: 12, sm: 4, md: 3 };
            }
            
            return (
              <Grid key={index} size={gridSize}>
                <Card 
                  elevation={2}
                  sx={{ 
                    borderRadius: 3,
                    overflow: 'hidden',
                    transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
                    }
                  }}
                >
                  <CardMedia
                    component="img"
                    image={`data:image/png;base64,${image}`}
                    alt={`Generated image ${index + 1}`}
                    sx={{ 
                      aspectRatio: '1/1',
                      objectFit: 'cover',
                      width: '100%',
                      height: 'auto',
                      maxWidth: '100%',
                      display: 'block'
                    }}
                  />
                  <CardActions sx={{ justifyContent: 'center', p: 2 }}>
                    <Tooltip title="Download Image">
                      <IconButton 
                        onClick={() => onDownload(image, index)}
                        sx={{ 
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                          }
                        }}
                      >
                        <DownloadIcon />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ImageGallery;
