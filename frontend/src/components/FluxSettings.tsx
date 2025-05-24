import { Box, FormControl, InputLabel, Select, MenuItem, TextField } from '@mui/material';

interface FluxSettingsProps {
  formData: any;
  onChange: (e: any) => void;
  onSelectChange: (name: string) => (event: any) => void;
}

const FluxSettings = ({ formData, onChange, onSelectChange }: FluxSettingsProps) => {
  return (
    <>
      <Box display="flex" gap={2}>
        <FormControl fullWidth size="small">
          <InputLabel>Model Type</InputLabel>
          <Select
            name="model_type"
            value={formData.model_type}
            onChange={onSelectChange('model_type')}
            label="Model Type"
            sx={{
              borderRadius: 2,
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          >
            <MenuItem value="flux_speed">FLUX Speed</MenuItem>
            <MenuItem value="flux_precision">FLUX Precision</MenuItem>
          </Select>
        </FormControl>
        <FormControl fullWidth size="small">
          <InputLabel>Enhance Prompt</InputLabel>
          <Select
            name="enhance_prompt"
            value={formData.enhance_prompt ? 'true' : 'false'}
            onChange={onChange}
            label="Enhance Prompt"
            sx={{
              borderRadius: 2,
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          >
            <MenuItem value="true">Enabled</MenuItem>
            <MenuItem value="false">Disabled</MenuItem>
          </Select>
        </FormControl>
      </Box>
      <Box display="flex" gap={2}>
        <TextField
          fullWidth
          size="small"
          name="enhance_prompt_instruction"
          label="Enhance Prompt Instruction"
          value={formData.enhance_prompt_instruction}
          onChange={onChange}
          placeholder="Custom instructions for prompt enhancement"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            }
          }}
        />
        <TextField
          fullWidth
          size="small"
          name="seed"
          label="Seed (Optional)"
          type="number"
          value={formData.seed || ''}
          onChange={onChange}
          placeholder="Random seed for reproducible results"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            }
          }}
        />
      </Box>
    </>
  );
};

export default FluxSettings;
