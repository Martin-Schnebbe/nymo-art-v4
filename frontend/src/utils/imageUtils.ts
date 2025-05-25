/**
 * Image utility functions for frontend components
 */

/**
 * Convert image URL to base64 for display
 */
export const convertImageUrlToBase64 = async (url: string): Promise<string> => {
  try {
    const fullUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`;
    const response = await fetch(fullUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch image: ${response.status}`);
    }
    
    const blob = await response.blob();
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        resolve(base64.split(',')[1]);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (err) {
    console.error('Error fetching image:', err);
    throw err;
  }
};

/**
 * Convert multiple image URLs to base64
 */
export const convertImageUrlsToBase64 = async (urls: string[]): Promise<string[]> => {
  const imagePromises = urls.map(convertImageUrlToBase64);
  return Promise.all(imagePromises);
};

/**
 * Download image as file
 */
export const downloadImage = (imageData: string, index?: number, prefix = 'nymo-art'): void => {
  const link = document.createElement('a');
  link.href = `data:image/png;base64,${imageData}`;
  const timestamp = Date.now();
  const suffix = index !== undefined ? `-${index + 1}` : '';
  link.download = `${prefix}-${timestamp}${suffix}.png`;
  link.click();
};

/**
 * Get responsive grid size for image gallery
 */
export const getImageGridSize = (imageCount: number) => {
  if (imageCount === 1) {
    return { xs: 12, sm: 12, md: 12 };
  } else if (imageCount === 2) {
    return { xs: 12, sm: 6, md: 6 };
  } else if (imageCount === 3) {
    return { xs: 12, sm: 6, md: 4 };
  } else if (imageCount === 4) {
    return { xs: 12, sm: 6, md: 3 };
  } else if (imageCount <= 6) {
    return { xs: 12, sm: 6, md: 4 };
  } else if (imageCount <= 8) {
    return { xs: 12, sm: 6, md: 3 };
  } else {
    return { xs: 12, sm: 4, md: 3 };
  }
};
