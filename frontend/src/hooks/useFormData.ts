import { useState, useEffect } from 'react';
import { getModelDefaults, getAvailableStyles } from '../utils/modelConfig';
import { 
  handleInputChange as createInputHandler, 
  handleSelectChange as createSelectHandler, 
  type FormData 
} from '../utils/parameterUtils';

export { type FormData } from '../utils/parameterUtils';

export const useFormData = (selectedModel: 'phoenix' | 'flux' | 'photoreal') => {
  const [formData, setFormData] = useState<FormData>(() => ({
    prompt: '',
    ...getModelDefaults(selectedModel)
  } as FormData));

  // Reset form data when model changes or photoreal version changes
  useEffect(() => {
    const currentStyles = getAvailableStyles(selectedModel, formData.photoreal_version);
    const currentStyle = formData.style;
    
    if (!currentStyles.includes(currentStyle)) {
      const defaults = getModelDefaults(selectedModel);
      setFormData(prev => ({
        ...prev,
        style: defaults.style
      }));
    }
  }, [selectedModel, formData.photoreal_version]);

  // Create handlers using utility functions
  const handleInputChange = createInputHandler(setFormData);
  const handleSelectChange = createSelectHandler(setFormData);

  const getAvailableStylesForModel = () => {
    return getAvailableStyles(selectedModel, formData.photoreal_version);
  };

  return {
    formData,
    setFormData,
    handleInputChange,
    handleSelectChange,
    getAvailableStyles: getAvailableStylesForModel
  };
};
