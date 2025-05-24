import { AppBar, Toolbar, Typography, Box, Avatar, Chip, Tabs, Tab } from '@mui/material';
import { AutoAwesome as AutoAwesomeIcon, Image as ImageIcon, BatchPrediction as BatchIcon } from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();
  
  const currentTab = location.pathname === '/batch' ? 1 : 0;

  return (
    <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'background.paper/80', backdropFilter: 'blur(20px)' }}>
      <Toolbar>
        <Avatar
          sx={{ 
            width: 32, 
            height: 32, 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            mr: 2 
          }}
        >
          <Typography variant="h6" sx={{ fontSize: '14px', fontWeight: 'bold', color: 'white' }}>
            N
          </Typography>
        </Avatar>
        <Typography variant="h6" sx={{ flexGrow: 1, color: 'text.primary', fontWeight: 600 }}>
          Nymo Art Studio
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Tabs 
            value={currentTab} 
            indicatorColor="primary"
            textColor="primary"
            sx={{ minHeight: 'auto' }}
          >
            <Tab 
              label="Generate" 
              icon={<ImageIcon />}
              iconPosition="start"
              component={Link} 
              to="/" 
              sx={{ 
                minHeight: 'auto', 
                py: 1,
                textTransform: 'none',
                fontWeight: 500
              }}
            />
            <Tab 
              label="Batch Processing" 
              icon={<BatchIcon />}
              iconPosition="start"
              component={Link} 
              to="/batch" 
              sx={{ 
                minHeight: 'auto', 
                py: 1,
                textTransform: 'none',
                fontWeight: 500
              }}
            />
          </Tabs>
          
          <Chip 
            icon={<AutoAwesomeIcon />} 
            label="AI Powered" 
            size="small" 
            sx={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              fontWeight: 500
            }}
          />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;
