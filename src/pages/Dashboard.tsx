import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Security,
  Send,
  History,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useSocket } from '../contexts/SocketContext';

const Dashboard: React.FC = () => {
  const { lastCommand, securityAlerts } = useSocket();

  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading } = useQuery(
    'dashboard-stats',
    async () => {
      const response = await axios.get('/dashboard/stats');
      return response.data;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

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

  const StatCard = ({ title, value, icon, color, trend }: any) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                backgroundColor: `${color}.light`,
                color: `${color}.main`,
                mr: 2,
              }}
            >
              {icon}
            </Box>
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          </Box>
          <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
            {value}
          </Typography>
          {trend && (
            <Typography variant="body2" color="text.secondary">
              {trend}
            </Typography>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Real-time monitoring of the Metro Door Security System
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Commands"
            value={stats?.totalCommands || 0}
            icon={<Send />}
            color="primary"
            trend="+12% from last hour"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Valid Commands"
            value={stats?.validCommands || 0}
            icon={<CheckCircle />}
            color="success"
            trend="98.5% success rate"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Suspicious Commands"
            value={stats?.suspiciousCommands || 0}
            icon={<Warning />}
            color="warning"
            trend="+3 from last hour"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Malicious Commands"
            value={stats?.maliciousCommands || 0}
            icon={<Error />}
            color="error"
            trend="Blocked successfully"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Last Command */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Last Command Processed
                </Typography>
                {lastCommand ? (
                  <Box>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      <strong>Command:</strong> {lastCommand.command}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <Chip
                        label={lastCommand.classification}
                        color={getClassificationColor(lastCommand.classification)}
                        icon={getClassificationIcon(lastCommand.classification)}
                        size="small"
                      />
                      <Chip
                        label={`Risk: ${(lastCommand.risk_score * 100).toFixed(1)}%`}
                        color={lastCommand.risk_score > 0.7 ? 'error' : lastCommand.risk_score > 0.3 ? 'warning' : 'success'}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(lastCommand.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No commands processed yet
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Security Alerts */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Security Alerts
                </Typography>
                {securityAlerts.length > 0 ? (
                  <Box>
                    {securityAlerts.slice(0, 5).map((alert, index) => (
                      <Paper
                        key={index}
                        sx={{
                          p: 2,
                          mb: 1,
                          backgroundColor: 'error.light',
                          color: 'error.contrastText',
                        }}
                      >
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {alert.type.replace('_', ' ').toUpperCase()}
                        </Typography>
                        <Typography variant="caption">
                          {new Date(alert.timestamp).toLocaleString()}
                        </Typography>
                      </Paper>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No recent security alerts
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Status
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">AI Model Status</Typography>
                    <Chip label="Online" color="success" size="small" />
                  </Box>
                  <LinearProgress variant="determinate" value={100} color="success" />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Security Monitoring</Typography>
                    <Chip label="Active" color="success" size="small" />
                  </Box>
                  <LinearProgress variant="determinate" value={100} color="success" />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Database Connection</Typography>
                    <Chip label="Connected" color="success" size="small" />
                  </Box>
                  <LinearProgress variant="determinate" value={100} color="success" />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;