import { Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';

interface PhoenixSettingsProps {
  formData: any;
  onChange: (e: any) => void;
  onSelectChange?: (name: string) => (event: any) => void;
}

const PhoenixSettings = ({ formData, onChange }: PhoenixSettingsProps) => {
  return (
    <>
      <Box display="flex" gap={2}>
        <FormControl fullWidth size="small">
          <InputLabel>Alchemy</InputLabel>
          <Select
            name="alchemy"
            value={formData.alchemy ? 'true' : 'false'}
            onChange={onChange}
            label="Alchemy"
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
        <FormControl fullWidth size="small">
          <InputLabel>Upscale</InputLabel>
          <Select
            name="upscale"
            value={formData.upscale ? 'true' : 'false'}
            onChange={onChange}
            label="Upscale"
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
        {formData.upscale && (
          <FormControl fullWidth size="small">
            <InputLabel>Upscale Strength</InputLabel>
            <Select
              name="upscale_strength"
              value={formData.upscale_strength}
              onChange={onChange}
              label="Upscale Strength"
              sx={{
                borderRadius: 2,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            >
              <MenuItem value={0.1}>0.1 - Subtle</MenuItem>
              <MenuItem value={0.25}>0.25 - Light</MenuItem>
              <MenuItem value={0.35}>0.35 - Default</MenuItem>
              <MenuItem value={0.5}>0.5 - Medium</MenuItem>
              <MenuItem value={0.75}>0.75 - Strong</MenuItem>
              <MenuItem value={1.0}>1.0 - Maximum</MenuItem>
            </Select>
          </FormControl>
        )}
      </Box>
    </>
  );
};

export default PhoenixSettings;
