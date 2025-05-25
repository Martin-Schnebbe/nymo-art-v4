import { useState, useRef } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  AppBar,
  Toolbar,
  Avatar,
  Alert,
  CircularProgress,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import {
  Upload as UploadIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  AutoAwesome as AutoAwesomeIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import * as batchClient from '../services/batchClient';
import type { BatchJob, BatchConfig } from '../services/batchClient';

const BatchProcess = () => {
  // Stepper state
  const [activeStep, setActiveStep] = useState(0);
  
  // CSV Upload state
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvData, setCsvData] = useState<string[]>([]);
  const [csvError, setCsvError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Batch configuration
  const [batchConfig, setBatchConfig] = useState<BatchConfig>({
    model: 'phoenix',
    num_images: 1,
    width: 1024,
    height: 1024,
    style: 'Dynamic',
    contrast: 3.5,
    alchemy: true,
    enhance_prompt: false,
    negative_prompt: '',
    ultra: false,
    upscale: false,
    upscale_strength: 0.35,
    photoreal_version: 'v2',
    photoreal_strength: 0.35,
  });

  // Processing state
  const [batchId, setBatchId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [jobs, setJobs] = useState<BatchJob[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [processingError, setProcessingError] = useState<string | null>(null);

  // Style options for each model
  const PHOENIX_STYLES = [
    "3D Render", "Bokeh", "Cinematic", "Cinematic Concept", "Creative", "Dynamic", 
    "Fashion", "Graphic Design Pop Art", "Graphic Design Vector", "HDR", "Illustration", 
    "Macro", "Minimalist", "Moody", "None", "Portrait", "Pro B&W photography", 
    "Pro color photography", "Pro film photography", "Portrait Fashion", "Ray Traced", 
    "Sketch (B&W)", "Sketch (Color)", "Stock Photo", "Vibrant"
  ];

  const FLUX_STYLES = [
    "3D Render", "Acrylic", "Anime General", "Creative", "Dynamic", "Fashion", 
    "Game Concept", "Graphic Design 3D", "Illustration", "None", "Portrait", 
    "Portrait Cinematic", "Ray Traced", "Stock Photo", "Watercolor"
  ];

  const PHOTOREAL_STYLES = {
    v1: ["CINEMATIC", "CREATIVE", "VIBRANT"],
    v2: [
      "BOKEH", "CINEMATIC", "CINEMATIC_CLOSEUP", "CREATIVE", "FASHION", "FILM", 
      "FOOD", "HDR", "LONG_EXPOSURE", "MACRO", "MINIMALISTIC", "MONOCHROME", 
      "MOODY", "NEUTRAL", "PORTRAIT", "RETRO", "STOCK_PHOTO", "VIBRANT", "UNPROCESSED"
    ]
  };

  // Handle CSV file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setCsvError('Please upload a valid CSV file');
      return;
    }

    setCsvFile(file);
    setCsvError(null);

    // Read and parse CSV
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const lines = text.split('\n').filter(line => line.trim());
        
        if (lines.length < 2) {
          setCsvError('CSV must contain at least a header and one data row');
          return;
        }

        const header = lines[0].toLowerCase().trim();
        if (!header.includes('prompt')) {
          setCsvError('CSV must contain a "prompt" column');
          return;
        }

        // Extract prompts (assuming simple CSV with just prompts)
        const prompts = lines.slice(1).map(line => {
          // Remove quotes and clean up
          return line.trim().replace(/^"/, '').replace(/"$/, '');
        }).filter(prompt => prompt.length > 0);

        if (prompts.length === 0) {
          setCsvError('No valid prompts found in CSV');
          return;
        }

        setCsvData(prompts);
        
        // Create initial job list
        const initialJobs: BatchJob[] = prompts.map((prompt, index) => ({
          id: `job_${String(index + 1).padStart(3, '0')}`,
          prompt,
          status: 'pending'
        }));
        setJobs(initialJobs);

      } catch (error) {
        setCsvError('Error parsing CSV file');
        console.error('CSV parsing error:', error);
      }
    };

    reader.readAsText(file);
  };

  // Handle form changes
  const handleConfigChange = (field: keyof BatchConfig) => (
    event: SelectChangeEvent<any> | React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value;
    setBatchConfig(prev => ({
      ...prev,
      [field]: field === 'num_images' || field === 'width' || field === 'height' || field === 'contrast' || field === 'photoreal_strength'
        ? Number(value)
        : field === 'alchemy' || field === 'enhance_prompt' || field === 'ultra'
        ? value === 'true'
        : value
    }));
  };

  // Start batch processing
  const startBatchProcessing = async () => {
    if (jobs.length === 0 || !csvFile) return;
    
    setIsProcessing(true);
    setIsPaused(false);
    setProcessingError(null);
    setActiveStep(2); // Move to processing step

    try {
      // Upload CSV first
      const csvResponse = await batchClient.uploadCSV(csvFile);
      console.log('CSV uploaded:', csvResponse);

      // Start batch processing with the prompts
      const batchResponse = await batchClient.startBatchProcessing(csvResponse.prompts, batchConfig);
      setBatchId(batchResponse.batch_id);
      console.log('Batch started:', batchResponse);

      // Start polling for status updates
      startStatusPolling(batchResponse.batch_id);
      
    } catch (error) {
      setProcessingError('Error starting batch processing');
      setIsProcessing(false);
      console.error('Batch processing error:', error);
    }
  };

  // Poll batch status
  const startStatusPolling = (batchId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await batchClient.getBatchStatus(batchId);
        
        // Update overall progress
        setOverallProgress(status.progress || 0);
        
        // Update jobs status based on the counts from the backend
        if (status.jobs) {
          // Update job statuses based on backend counts
          // This is a simplified approach - in reality you'd want more detailed job tracking
          setJobs(prev => {
            const updated = [...prev];
            let completedCount = 0;
            let failedCount = 0;
            let processingCount = 0;
            
            for (let i = 0; i < updated.length; i++) {
              if (completedCount < status.jobs!.completed && updated[i].status !== 'completed') {
                updated[i] = { ...updated[i], status: 'completed', imageCount: batchConfig.num_images };
                completedCount++;
              } else if (failedCount < status.jobs!.failed && updated[i].status !== 'failed' && updated[i].status !== 'completed') {
                updated[i] = { ...updated[i], status: 'failed', error: 'Processing failed' };
                failedCount++;
              } else if (processingCount < status.jobs!.processing && updated[i].status === 'pending') {
                updated[i] = { ...updated[i], status: 'processing' };
                processingCount++;
              }
            }
            
            return updated;
          });
        }
        
        // Check if batch is complete
        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
          setIsProcessing(false);
          clearInterval(pollInterval);
          
          if (status.status === 'failed') {
            setProcessingError(status.error || 'Batch processing failed');
          }
        }
        
      } catch (error) {
        console.error('Error polling batch status:', error);
        // Continue polling unless it's a critical error
      }
    }, 2000); // Poll every 2 seconds

    // Store interval reference for cleanup
    return pollInterval;
  };

  // Pause/Resume processing (Note: Backend may not support pause/resume)
  const togglePause = () => {
    setIsPaused(prev => !prev);
    // TODO: Implement pause/resume API calls if backend supports it
  };

  // Stop processing
  const stopProcessing = async () => {
    if (batchId) {
      try {
        await batchClient.cancelBatch(batchId);
      } catch (error) {
        console.error('Error cancelling batch:', error);
      }
    }
    
    setIsProcessing(false);
    setIsPaused(false);
    setBatchId(null);
    // Reset jobs to pending
    setJobs(prev => prev.map(job => 
      job.status === 'processing' ? { ...job, status: 'pending' } : job
    ));
    setOverallProgress(0);
  };

  // Download batch results
  const downloadResults = async () => {
    if (!batchId) return;
    
    try {
      const result = await batchClient.downloadBatchResults(batchId);
      // For now, just log the output directory
      // In a real app, you might trigger a file download or show a link
      console.log('Batch results available at:', result.output_directory);
      alert(`Batch results saved to: ${result.output_directory}`);
    } catch (error) {
      console.error('Error downloading results:', error);
      setProcessingError('Error downloading batch results');
    }
  };

  // Get status counts
  const statusCounts = {
    pending: jobs.filter(job => job.status === 'pending').length,
    processing: jobs.filter(job => job.status === 'processing').length,
    completed: jobs.filter(job => job.status === 'completed').length,
    failed: jobs.filter(job => job.status === 'failed').length,
  };

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'background.paper/80', backdropFilter: 'blur(20px)' }}>
        <Toolbar>
          <Avatar
            sx={{ 
              width: 32, 
              height: 32, 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              mr: 2 
            }}
          >
            <Typography variant="h6" sx={{ fontSize: '14px', fontWeight: 'bold', color: 'white' }}>
              N
            </Typography>
          </Avatar>
          <Typography variant="h6" sx={{ flexGrow: 1, color: 'text.primary', fontWeight: 600 }}>
            Nymo Art Studio - Batch Processing
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button 
              component={Link} 
              to="/" 
              variant="outlined" 
              size="small"
              sx={{ borderRadius: 2 }}
            >
              Single Generation
            </Button>
            <Chip 
              icon={<AutoAwesomeIcon />} 
              label="Batch Mode" 
              size="small" 
              sx={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                fontWeight: 500
              }}
            />
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" flexDirection={{ xs: 'column', lg: 'row' }} gap={4}>
          {/* Left Side - Stepper and Controls */}
          <Box flex={1}>
            <Card 
              elevation={0} 
              sx={{ 
                background: 'rgba(255, 255, 255, 0.8)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: 3,
                mb: 3
              }}
            >
              <CardContent sx={{ p: 4 }}>
                <Stepper activeStep={activeStep} orientation="vertical">
                  {/* Step 1: Upload CSV */}
                  <Step>
                    <StepLabel>
                      <Typography variant="h6">Upload CSV File</Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography color="text.secondary" sx={{ mb: 3 }}>
                        Upload a CSV file with prompts. The file should have a "prompt" column containing your image descriptions.
                      </Typography>
                      
                      <Box sx={{ mb: 3 }}>
                        <input
                          type="file"
                          accept=".csv"
                          onChange={handleFileUpload}
                          ref={fileInputRef}
                          style={{ display: 'none' }}
                        />
                        <Button
                          variant="outlined"
                          startIcon={<UploadIcon />}
                          onClick={() => fileInputRef.current?.click()}
                          sx={{ borderRadius: 2 }}
                        >
                          Choose CSV File
                        </Button>
                        {csvFile && (
                          <Chip
                            icon={<FileIcon />}
                            label={csvFile.name}
                            sx={{ ml: 2 }}
                            color="primary"
                          />
                        )}
                      </Box>

                      {csvError && (
                        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                          {csvError}
                        </Alert>
                      )}

                      {csvData.length > 0 && (
                        <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
                          Successfully loaded {csvData.length} prompts from CSV
                        </Alert>
                      )}

                      <Box sx={{ mb: 2 }}>
                        <Button
                          variant="contained"
                          onClick={() => setActiveStep(1)}
                          disabled={csvData.length === 0}
                          sx={{ borderRadius: 2 }}
                        >
                          Continue
                        </Button>
                      </Box>
                    </StepContent>
                  </Step>

                  {/* Step 2: Configure Settings */}
                  <Step>
                    <StepLabel>
                      <Typography variant="h6">Configure Generation Settings</Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography color="text.secondary" sx={{ mb: 3 }}>
                        Configure the image generation settings that will be applied to all prompts in your batch.
                      </Typography>

                      <Box display="flex" flexDirection="column" gap={3}>
                        {/* Model Selection */}
                        <FormControl fullWidth>
                          <InputLabel>AI Model</InputLabel>
                          <Select
                            value={batchConfig.model}
                            onChange={handleConfigChange('model')}
                            label="AI Model"
                            sx={{ borderRadius: 2 }}
                          >
                            <MenuItem value="phoenix">Leonardo Phoenix</MenuItem>
                            <MenuItem value="flux">Leonardo FLUX</MenuItem>
                            <MenuItem value="photoreal">Leonardo PhotoReal</MenuItem>
                          </Select>
                        </FormControl>

                        {/* Basic Settings */}
                        <Box display="flex" gap={2}>
                          <FormControl fullWidth>
                            <InputLabel>Images per Prompt</InputLabel>
                            <Select
                              value={batchConfig.num_images}
                              onChange={handleConfigChange('num_images')}
                              label="Images per Prompt"
                              sx={{ borderRadius: 2 }}
                            >
                              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                                <MenuItem key={num} value={num}>{num}</MenuItem>
                              ))}
                            </Select>
                          </FormControl>

                          <FormControl fullWidth>
                            <InputLabel>Dimensions</InputLabel>
                            <Select
                              value={`${batchConfig.width}x${batchConfig.height}`}
                              onChange={(e) => {
                                const [width, height] = e.target.value.split('x').map(Number);
                                setBatchConfig(prev => ({ ...prev, width, height }));
                              }}
                              label="Dimensions"
                              sx={{ borderRadius: 2 }}
                            >
                              <MenuItem value="512x512">512 × 512</MenuItem>
                              <MenuItem value="768x768">768 × 768</MenuItem>
                              <MenuItem value="1024x1024">1024 × 1024</MenuItem>
                              <MenuItem value="1536x1536">1536 × 1536</MenuItem>
                            </Select>
                          </FormControl>
                        </Box>

                        {/* Advanced Settings */}
                        <Accordion sx={{ borderRadius: 2 }}>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box display="flex" alignItems="center">
                              <SettingsIcon sx={{ mr: 2, color: 'text.secondary' }} />
                              <Typography fontWeight="500">Advanced Settings</Typography>
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Box display="flex" flexDirection="column" gap={2}>
                              {/* Style Selection */}
                              <FormControl fullWidth size="small">
                                <InputLabel>Style</InputLabel>
                                <Select
                                  value={batchConfig.style}
                                  onChange={handleConfigChange('style')}
                                  label="Style"
                                  sx={{ borderRadius: 2 }}
                                >
                                  {(() => {
                                    let styles: string[] = [];
                                    if (batchConfig.model === 'phoenix') {
                                      styles = PHOENIX_STYLES;
                                    } else if (batchConfig.model === 'flux') {
                                      styles = FLUX_STYLES;
                                    } else if (batchConfig.model === 'photoreal') {
                                      styles = PHOTOREAL_STYLES[batchConfig.photoreal_version as 'v1' | 'v2'];
                                    }
                                    
                                    return styles.map((style) => (
                                      <MenuItem key={style} value={style}>
                                        {style}
                                      </MenuItem>
                                    ));
                                  })()}
                                </Select>
                              </FormControl>

                              {/* Model-specific settings would go here */}
                              {/* Similar to the Generate.tsx component */}
                            </Box>
                          </AccordionDetails>
                        </Accordion>
                      </Box>

                      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                        <Button
                          onClick={() => setActiveStep(0)}
                          sx={{ borderRadius: 2 }}
                        >
                          Back
                        </Button>
                        <Button
                          variant="contained"
                          onClick={() => setActiveStep(2)}
                          sx={{ borderRadius: 2 }}
                        >
                          Start Processing
                        </Button>
                      </Box>
                    </StepContent>
                  </Step>

                  {/* Step 3: Process Batch */}
                  <Step>
                    <StepLabel>
                      <Typography variant="h6">Batch Processing</Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography color="text.secondary" sx={{ mb: 3 }}>
                        Monitor the progress of your batch generation. You can pause or stop the process at any time.
                      </Typography>

                      {/* Progress Overview */}
                      <Box sx={{ mb: 3 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            Overall Progress
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {Math.round(overallProgress)}%
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={overallProgress} 
                          sx={{ borderRadius: 1, height: 8 }}
                        />
                      </Box>

                      {/* Status Summary */}
                      <Box display="flex" gap={2} sx={{ mb: 3 }}>
                        <Chip 
                          label={`${statusCounts.pending} Pending`} 
                          color="default" 
                          size="small"
                        />
                        <Chip 
                          label={`${statusCounts.processing} Processing`} 
                          color="primary" 
                          size="small"
                        />
                        <Chip 
                          label={`${statusCounts.completed} Completed`} 
                          color="success" 
                          size="small"
                        />
                        {statusCounts.failed > 0 && (
                          <Chip 
                            label={`${statusCounts.failed} Failed`} 
                            color="error" 
                            size="small"
                          />
                        )}
                      </Box>

                      {/* Control Buttons */}
                      <Box display="flex" gap={2} sx={{ mb: 3 }}>
                        {!isProcessing ? (
                          <>
                            <Button
                              variant="contained"
                              startIcon={<PlayArrowIcon />}
                              onClick={startBatchProcessing}
                              disabled={jobs.length === 0}
                              sx={{ borderRadius: 2 }}
                            >
                              Start Processing
                            </Button>
                            {batchId && statusCounts.completed > 0 && (
                              <Button
                                variant="outlined"
                                startIcon={<DownloadIcon />}
                                onClick={downloadResults}
                                sx={{ borderRadius: 2 }}
                              >
                                Download Results
                              </Button>
                            )}
                          </>
                        ) : (
                          <>
                            <Button
                              variant="outlined"
                              startIcon={isPaused ? <PlayArrowIcon /> : <PauseIcon />}
                              onClick={togglePause}
                              sx={{ borderRadius: 2 }}
                            >
                              {isPaused ? 'Resume' : 'Pause'}
                            </Button>
                            <Button
                              variant="outlined"
                              startIcon={<StopIcon />}
                              onClick={stopProcessing}
                              color="error"
                              sx={{ borderRadius: 2 }}
                            >
                              Stop
                            </Button>
                          </>
                        )}
                      </Box>

                      {processingError && (
                        <Alert severity="error" sx={{ borderRadius: 2 }}>
                          {processingError}
                        </Alert>
                      )}
                    </StepContent>
                  </Step>
                </Stepper>
              </CardContent>
            </Card>
          </Box>

          {/* Right Side - Job Status */}
          <Box flex={1}>
            <Card 
              elevation={0} 
              sx={{ 
                background: 'rgba(255, 255, 255, 0.8)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: 3
              }}
            >
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                  <FileIcon sx={{ mr: 2, color: 'text.secondary' }} />
                  Batch Jobs ({jobs.length})
                </Typography>

                {jobs.length > 0 ? (
                  <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Prompt</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Images</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {jobs.map((job) => (
                          <TableRow key={job.id}>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                {job.id}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  maxWidth: 200, 
                                  overflow: 'hidden', 
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                {job.prompt}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                size="small"
                                label={job.status}
                                color={
                                  job.status === 'completed' ? 'success' :
                                  job.status === 'processing' ? 'primary' :
                                  job.status === 'failed' ? 'error' : 'default'
                                }
                                icon={
                                  job.status === 'completed' ? <CheckCircleIcon /> :
                                  job.status === 'processing' ? <CircularProgress size={16} /> :
                                  job.status === 'failed' ? <ErrorIcon /> : undefined
                                }
                              />
                            </TableCell>
                            <TableCell>
                              {job.imageCount ? `${job.imageCount} images` : '-'}
                            </TableCell>
                            <TableCell>
                              {job.status === 'completed' && (
                                <Tooltip title="Download Images">
                                  <IconButton size="small">
                                    <DownloadIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Paper 
                    elevation={0}
                    sx={{ 
                      p: 4, 
                      textAlign: 'center',
                      background: 'rgba(248, 250, 252, 0.8)',
                      borderRadius: 2
                    }}
                  >
                    <FileIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                    <Typography color="text.secondary">
                      Upload a CSV file to see batch jobs here
                    </Typography>
                  </Paper>
                )}
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default BatchProcess;
