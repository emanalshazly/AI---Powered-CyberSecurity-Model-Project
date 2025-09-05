import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Pagination,
  Grid,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security,
  Warning,
  Error,
  CheckCircle,
  Refresh,
  Visibility,
  Block,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface SecurityEvent {
  id: number;
  event_type: string;
  description: string;
  severity: string;
  ip_address: string;
  timestamp: string;
  resolved: boolean;
}

const SecurityMonitor: React.FC = () => {
  const [page, setPage] = useState(1);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  const { data: eventsData, isLoading, refetch } = useQuery(
    ['security-events', page],
    async () => {
      const response = await axios.get('/security/events', {
        params: { page, per_page: 50 },
      });
      return response.data;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const { data: metricsData } = useQuery(
    'security-metrics',
    async () => {
      const response = await axios.get('/security/metrics');
      return response.data;
    },
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <Error />;
      case 'medium':
        return <Warning />;
      case 'low':
        return <CheckCircle />;
      default:
        return <Security />;
    }
  };

  const getEventTypeColor = (eventType: string) => {
    if (eventType.includes('malicious') || eventType.includes('attack')) {
      return 'error';
    } else if (eventType.includes('suspicious') || eventType.includes('unauthorized')) {
      return 'warning';
    } else {
      return 'info';
    }
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleRefresh = () => {
    refetch();
  };

  const handleViewDetails = (event: SecurityEvent) => {
    setSelectedEvent(event);
  };

  const handleResolveEvent = async (eventId: number) => {
    try {
      await axios.patch(`/security/events/${eventId}/resolve`);
      refetch();
    } catch (error) {
      console.error('Failed to resolve event:', error);
    }
  };

  // Generate mock data for charts
  const generateChartData = () => {
    const data = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        events: Math.floor(Math.random() * 10),
        threats: Math.floor(Math.random() * 5),
        blocked: Math.floor(Math.random() * 8),
      });
    }
    return data;
  };

  const chartData = generateChartData();

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Security Monitor
        </Typography>
        <IconButton onClick={handleRefresh} disabled={isLoading}>
          <Refresh />
        </IconButton>
      </Box>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Real-time security monitoring and threat analysis dashboard.
      </Typography>

      {/* Security Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Security sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography variant="h6">Total Events</Typography>
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                  {eventsData?.total || 0}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Error sx={{ color: 'error.main', mr: 1 }} />
                  <Typography variant="h6">High Severity</Typography>
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                  {eventsData?.events?.filter((e: SecurityEvent) => e.severity === 'high').length || 0}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Warning sx={{ color: 'warning.main', mr: 1 }} />
                  <Typography variant="h6">Medium Severity</Typography>
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                  {eventsData?.events?.filter((e: SecurityEvent) => e.severity === 'medium').length || 0}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CheckCircle sx={{ color: 'success.main', mr: 1 }} />
                  <Typography variant="h6">Resolved</Typography>
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                  {eventsData?.events?.filter((e: SecurityEvent) => e.resolved).length || 0}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Security Trends Chart */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Events Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="events" stroke="#2563eb" strokeWidth={2} />
                    <Line type="monotone" dataKey="threats" stroke="#dc2626" strokeWidth={2} />
                    <Line type="monotone" dataKey="blocked" stroke="#16a34a" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Event Types
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { name: 'Malicious', value: 5 },
                    { name: 'Suspicious', value: 12 },
                    { name: 'Unauthorized', value: 8 },
                    { name: 'Failed Login', value: 15 },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="value" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Security Events Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Security Events
            </Typography>
            <TableContainer component={Paper} elevation={0}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Event Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>IP Address</TableCell>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={7} sx={{ textAlign: 'center', py: 4 }}>
                        <Typography>Loading...</Typography>
                      </TableCell>
                    </TableRow>
                  ) : eventsData?.events?.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} sx={{ textAlign: 'center', py: 4 }}>
                        <Typography color="text.secondary">No security events found</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    eventsData?.events?.map((event: SecurityEvent) => (
                      <TableRow key={event.id}>
                        <TableCell>
                          <Chip
                            label={event.event_type.replace('_', ' ').toUpperCase()}
                            color={getEventTypeColor(event.event_type)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {event.description}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={event.severity}
                            color={getSeverityColor(event.severity)}
                            icon={getSeverityIcon(event.severity)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {event.ip_address}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(event.timestamp).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={event.resolved ? 'Resolved' : 'Open'}
                            color={event.resolved ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                onClick={() => handleViewDetails(event)}
                              >
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            {!event.resolved && (
                              <Tooltip title="Mark as Resolved">
                                <IconButton
                                  size="small"
                                  onClick={() => handleResolveEvent(event.id)}
                                >
                                  <CheckCircle />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            {eventsData?.pages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination
                  count={eventsData.pages}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                />
              </Box>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Event Details Dialog */}
      {selectedEvent && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Event Details
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Event Type
                  </Typography>
                  <Chip
                    label={selectedEvent.event_type.replace('_', ' ').toUpperCase()}
                    color={getEventTypeColor(selectedEvent.event_type)}
                    sx={{ mt: 0.5 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Severity
                  </Typography>
                  <Chip
                    label={selectedEvent.severity}
                    color={getSeverityColor(selectedEvent.severity)}
                    icon={getSeverityIcon(selectedEvent.severity)}
                    sx={{ mt: 0.5 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Description
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 0.5 }}>
                    {selectedEvent.description}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    IP Address
                  </Typography>
                  <Typography variant="body1" sx={{ fontFamily: 'monospace', mt: 0.5 }}>
                    {selectedEvent.ip_address}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 0.5 }}>
                    {new Date(selectedEvent.timestamp).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={selectedEvent.resolved ? 'Resolved' : 'Open'}
                    color={selectedEvent.resolved ? 'success' : 'warning'}
                    sx={{ mt: 0.5 }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </Box>
  );
};

export default SecurityMonitor;