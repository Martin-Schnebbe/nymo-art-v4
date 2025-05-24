import { TextField } from '@mui/material';

interface PromptInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
}

const PromptInput = ({ value, onChange }: PromptInputProps) => {
  return (
    <TextField
      fullWidth
      multiline
      rows={4}
      name="prompt"
      label="Describe your vision"
      placeholder="A serene mountain landscape at golden hour with misty clouds..."
      value={value}
      onChange={onChange}
      required
      sx={{ 
        mb: 3,
        '& .MuiOutlinedInput-root': {
          borderRadius: 3,
        }
      }}
      variant="outlined"
    />
  );
};

export default PromptInput;
