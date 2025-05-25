import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

export interface BatchJob {
  id: string;
  prompt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  imageCount?: number;
  error?: string;
}

export interface BatchConfig {
  model: 'phoenix' | 'flux' | 'photoreal';
  num_images: number;
  width: number;
  height: number;
  style?: string;
  contrast?: number;
  alchemy?: boolean;
  enhance_prompt?: boolean;
  negative_prompt?: string;
  ultra?: boolean;
  upscale?: boolean;
  upscale_strength?: number;
  photoreal_version?: string;
  photoreal_strength?: number;
  // Additional model-specific fields
  model_type?: string;
  enhance_prompt_instruction?: string;
  seed?: number;
  model_id?: string;
}

export interface BatchStatus {
  id: string;
  status: 'starting' | 'processing' | 'completed' | 'failed' | 'cancelled';
  total_jobs: number;
  completed: number;
  failed: number;
  progress: number;
  start_time: string;
  end_time?: string;
  duration?: number;
  error?: string;
  message?: string; // <-- add this line
  jobs?: {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
}

/**
 * Upload CSV file and extract prompts
 */
export async function uploadCSV(file: File): Promise<{ prompts: Array<{ id: string; prompt: string }>; count: number }> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_BASE}/batch/upload-csv`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.success) {
      return {
        prompts: response.data.prompts,
        count: response.data.count,
      };
    } else {
      throw new Error('Failed to upload CSV');
    }
  } catch (error) {
    console.error('CSV upload error:', error);
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to upload CSV');
    }
    throw new Error('Network error during CSV upload');
  }
}

/**
 * Start batch processing
 */
export async function startBatchProcessing(
  prompts: Array<{ id: string; prompt: string }>,
  config: BatchConfig
): Promise<{ batch_id: string; total_jobs: number }> {
  try {
    const response = await axios.post(`${API_BASE}/batch/start`, {
      prompts,
      config,
    });

    if (response.data.success) {
      return {
        batch_id: response.data.batch_id,
        total_jobs: response.data.total_jobs,
      };
    } else {
      throw new Error('Failed to start batch processing');
    }
  } catch (error) {
    console.error('Batch start error:', error);
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to start batch processing');
    }
    throw new Error('Network error during batch start');
  }
}

/**
 * Get batch processing status
 */
export async function getBatchStatus(batchId: string): Promise<BatchStatus> {
  try {
    const response = await axios.get(`${API_BASE}/batch/status/${batchId}`);
    return response.data;
  } catch (error) {
    console.error('Batch status error:', error);
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to get batch status');
    }
    throw new Error('Network error during status check');
  }
}

/**
 * Cancel batch processing
 */
export async function cancelBatch(batchId: string): Promise<void> {
  try {
    const response = await axios.delete(`${API_BASE}/batch/${batchId}`);
    if (!response.data.success) {
      throw new Error('Failed to cancel batch');
    }
  } catch (error) {
    console.error('Batch cancel error:', error);
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to cancel batch');
    }
    throw new Error('Network error during batch cancellation');
  }
}

/**
 * List active batches
 */
export async function listActiveBatches(): Promise<BatchStatus[]> {
  try {
    const response = await axios.get(`${API_BASE}/batch/`);
    return response.data.batches;
  } catch (error) {
    console.error('List batches error:', error);
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to list batches');
    }
    throw new Error('Network error during batch listing');
  }
}

/**
 * Download batch results (placeholder for now)
 */
export async function downloadBatchResults(batchId: string): Promise<{ output_directory: string }> {
  try {
    const response = await axios.get(`${API_BASE}/batch/${batchId}/download`);
    return response.data;
  } catch (error) {
    console.error('Batch download error:', error);
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail || 'Failed to download batch results');
    }
    throw new Error('Network error during batch download');
  }
}
