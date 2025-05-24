import { Box, FormControl, InputLabel, Select, MenuItem, TextField } from '@mui/material';

interface PhotoRealSettingsProps {
  formData: any;
  onChange: (e: any) => void;
  onSelectChange: (name: string) => (event: any) => void;
}

const PhotoRealSettings = ({ formData, onChange, onSelectChange }: PhotoRealSettingsProps) => {
  return (
    <>
      <Box display="flex" gap={2}>
        <FormControl fullWidth size="small">
          <InputLabel>PhotoReal Version</InputLabel>
          <Select
            name="photoreal_version"
            value={formData.photoreal_version}
            onChange={onSelectChange('photoreal_version')}
            label="PhotoReal Version"
            sx={{
              borderRadius: 2,
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          >
            <MenuItem value="v1">Version 1</MenuItem>
            <MenuItem value="v2">Version 2</MenuItem>
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
          name="model_id"
          label="Model ID"
          value={formData.model_id}
          onChange={onChange}
          placeholder="PhotoReal model identifier"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            }
          }}
        />
        <TextField
          fullWidth
          size="small"
          name="photoreal_strength"
          label="Strength (Optional)"
          type="number"
          value={formData.photoreal_strength || ''}
          onChange={onChange}
          placeholder="PhotoReal strength (0.1-1.0)"
          inputProps={{
            step: 0.1,
            min: 0.1,
            max: 1.0
          }}
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

export default PhotoRealSettings;
