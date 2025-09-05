import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Chip,
  Paper,
  Alert,
  CircularProgress,
  IconButton,
} from '@mui/material';
import {
  Send,
  PlayArrow,
  Stop,
  Warning,
  CheckCircle,
  Error,
  Refresh,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

interface CommandResult {
  command: string;
  classification: string;
  risk_score: number;
  timestamp: string;
}

const CommandCenter: React.FC = () => {
  const [customCommand, setCustomCommand] = useState('');
  const [lastResult, setLastResult] = useState<CommandResult | null>(null);
  const [doorState, setDoorState] = useState<'open' | 'closed'>('closed');

  const classifyCommand = useMutation(
    async (command: string) => {
      const response = await axios.post('/classify', { command });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setLastResult(data);
        
        // Update door state for valid commands
        if (data.classification.includes('Valid') && data.classification.includes('Normal')) {
          if (data.command === 'open_door') {
            setDoorState('open');
          } else if (data.command === 'close_door') {
            setDoorState('closed');
          }
        }

        // Show toast based on classification
        if (data.classification.includes('Malicious')) {
          toast.error('Malicious command detected and blocked!');
        } else if (data.classification.includes('Suspicious')) {
          toast.warning('Suspicious command detected');
        } else {
          toast.success('Command processed successfully');
        }
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Command processing failed');
      },
    }
  );

  const handlePredefinedCommand = (command: string) => {
    classifyCommand.mutate(command);
  };

  const handleCustomCommand = () => {
    if (!customCommand.trim()) {
      toast.error('Please enter a command');
      return;
    }
    classifyCommand.mutate(customCommand.trim());
    setCustomCommand('');
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleCustomCommand();
    }
  };

  const getClassificationColor = (classification: string) => {
    if (classification.includes('Valid') && classification.includes('Normal')) {
      return 'success';
    } else if (classification.includes('Suspicious')) {
      return 'warning';
    } else {
      return 'error';
    }
  };

  const getClassificationIcon = (classification: string) => {
    if (classification.includes('Valid') && classification.includes('Normal')) {
      return <CheckCircle />;
    } else if (classification.includes('Suspicious')) {
      return <Warning />;
    } else {
      return <Error />;
    }
  };

  const predefinedCommands = [
    { command: 'open_door', label: 'Open Door', color: 'primary' },
    { command: 'close_door', label: 'Close Door', color: 'secondary' },
    { command: 'emergency_stop', label: 'Emergency Stop', color: 'error' },
  ];

  const exampleCommands = [
    'door pls',
    'hack override system',
    'open door now',
    'system shutdown',
    'emergency_stop',
    'close_door',
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Command Center
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Send commands to the metro door system. All commands are analyzed by AI for security threats.
      </Typography>

      <Grid container spacing={3}>
        {/* Door Visualization */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card elevation={3}>
              <CardContent sx={{ textAlign: 'center', p: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Metro Door Status
                </Typography>
                <Box
                  sx={{
                    position: 'relative',
                    width: 200,
                    height: 300,
                    margin: '0 auto',
                    perspective: '1000px',
                  }}
                >
                  <Box
                    className={`door ${doorState}`}
                    sx={{
                      position: 'relative',
                      width: '100%',
                      height: '100%',
                      transformStyle: 'preserve-3d',
                      transition: 'transform 0.5s ease-in-out',
                      transform: doorState === 'open' ? 'rotateY(-90deg)' : 'rotateY(0deg)',
                    }}
                  >
                    <Box
                      className="door-panel left"
                      sx={{
                        position: 'absolute',
                        left: 0,
                        width: '50%',
                        height: '100%',
                        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                        border: '2px solid #1d4ed8',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <Box
                      className="door-panel right"
                      sx={{
                        position: 'absolute',
                        right: 0,
                        width: '50%',
                        height: '100%',
                        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                        border: '2px solid #1d4ed8',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <Box
                      className="door-frame"
                      sx={{
                        position: 'absolute',
                        top: -4,
                        left: -4,
                        right: -4,
                        bottom: -4,
                        border: '4px solid #0ea5e9',
                        borderRadius: 1,
                      }}
                    />
                  </Box>
                </Box>
                <Typography variant="h6" sx={{ mt: 2 }}>
                  Door: {doorState.toUpperCase()}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Command Controls */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Send Commands
                </Typography>

                {/* Predefined Commands */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Predefined Commands
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {predefinedCommands.map((cmd) => (
                      <Button
                        key={cmd.command}
                        variant="outlined"
                        color={cmd.color as any}
                        startIcon={<Send />}
                        onClick={() => handlePredefinedCommand(cmd.command)}
                        disabled={classifyCommand.isLoading}
                        sx={{ mb: 1 }}
                      >
                        {cmd.label}
                      </Button>
                    ))}
                  </Box>
                </Box>

                {/* Custom Command Input */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Custom Command
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      fullWidth
                      placeholder="Enter custom command..."
                      value={customCommand}
                      onChange={(e) => setCustomCommand(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={classifyCommand.isLoading}
                    />
                    <Button
                      variant="contained"
                      onClick={handleCustomCommand}
                      disabled={classifyCommand.isLoading || !customCommand.trim()}
                      startIcon={classifyCommand.isLoading ? <CircularProgress size={20} /> : <Send />}
                    >
                      Send
                    </Button>
                  </Box>
                </Box>

                {/* Example Commands */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Try these examples:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {exampleCommands.map((cmd) => (
                      <Chip
                        key={cmd}
                        label={cmd}
                        variant="outlined"
                        size="small"
                        onClick={() => setCustomCommand(cmd)}
                        sx={{ cursor: 'pointer' }}
                      />
                    ))}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Last Command Result */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card elevation={3}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Last Command Result
                  </Typography>
                  <IconButton
                    onClick={() => setLastResult(null)}
                    size="small"
                  >
                    <Refresh />
                  </IconButton>
                </Box>

                <AnimatePresence>
                  {lastResult ? (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Paper
                        sx={{
                          p: 3,
                          backgroundColor: 'grey.50',
                          border: '1px solid',
                          borderColor: 'grey.200',
                        }}
                      >
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">
                              Command
                            </Typography>
                            <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                              {lastResult.command}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">
                              Classification
                            </Typography>
                            <Chip
                              label={lastResult.classification}
                              color={getClassificationColor(lastResult.classification)}
                              icon={getClassificationIcon(lastResult.classification)}
                              sx={{ mt: 0.5 }}
                            />
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">
                              Risk Score
                            </Typography>
                            <Typography variant="body1">
                              {(lastResult.risk_score * 100).toFixed(1)}%
                            </Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">
                              Timestamp
                            </Typography>
                            <Typography variant="body1">
                              {new Date(lastResult.timestamp).toLocaleString()}
                            </Typography>
                          </Grid>
                        </Grid>
                      </Paper>
                    </motion.div>
                  ) : (
                    <Alert severity="info">
                      No commands processed yet. Send a command to see the result here.
                    </Alert>
                  )}
                </AnimatePresence>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CommandCenter;