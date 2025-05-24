import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

interface ModelSelectorProps {
  selectedModel: 'phoenix' | 'flux' | 'photoreal';
  onModelChange: (model: 'phoenix' | 'flux' | 'photoreal') => void;
}

const ModelSelector = ({ selectedModel, onModelChange }: ModelSelectorProps) => {
  return (
    <FormControl fullWidth sx={{ mb: 3 }}>
      <InputLabel>AI Model</InputLabel>
      <Select
        name="model"
        value={selectedModel}
        onChange={(e) => onModelChange(e.target.value as 'phoenix' | 'flux' | 'photoreal')}
        label="AI Model"
        sx={{
          borderRadius: 3,
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
          }
        }}
      >
        <MenuItem value="phoenix">Leonardo Phoenix - Premium Quality</MenuItem>
        <MenuItem value="flux">Leonardo FLUX - Speed & Precision</MenuItem>
        <MenuItem value="photoreal">Leonardo PhotoReal - Photorealistic</MenuItem>
      </Select>
    </FormControl>
  );
};

export default ModelSelector;
