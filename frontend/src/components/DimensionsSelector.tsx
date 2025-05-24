import { Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';

interface DimensionsSelectorProps {
  width: number;
  height: number;
  onWidthChange: (event: SelectChangeEvent<string | number>) => void;
  onHeightChange: (event: SelectChangeEvent<string | number>) => void;
}

const DimensionsSelector = ({ width, height, onWidthChange, onHeightChange }: DimensionsSelectorProps) => {
  const dimensions = [512, 768, 1024, 1536];

  return (
    <Box display="flex" gap={2} sx={{ mb: 3 }}>
      <FormControl fullWidth>
        <InputLabel>Width</InputLabel>
        <Select
          name="width"
          value={width}
          onChange={onWidthChange}
          label="Width"
          sx={{
            borderRadius: 3,
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
            }
          }}
        >
          {dimensions.map(dim => (
            <MenuItem key={dim} value={dim}>{dim}px</MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <FormControl fullWidth>
        <InputLabel>Height</InputLabel>
        <Select
          name="height"
          value={height}
          onChange={onHeightChange}
          label="Height"
          sx={{
            borderRadius: 3,
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
            }
          }}
        >
          {dimensions.map(dim => (
            <MenuItem key={dim} value={dim}>{dim}px</MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default DimensionsSelector;
