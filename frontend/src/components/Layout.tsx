import { Box } from '@mui/material';
import Navigation from './Navigation';
import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      <Navigation />
      <main>
        {children}
      </main>
    </Box>
  );
};

export default Layout;
