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
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search,
  Refresh,
  CheckCircle,
  Warning,
  Error,
  Visibility,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import axios from 'axios';

interface CommandHistoryItem {
  id: number;
  command: string;
  classification: string;
  risk_score: number;
  timestamp: string;
}

const CommandHistory: React.FC = () => {
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCommand, setSelectedCommand] = useState<CommandHistoryItem | null>(null);

  const { data: historyData, isLoading, refetch } = useQuery(
    ['command-history', page, searchTerm],
    async () => {
      const response = await axios.get('/commands/history', {
        params: { page, per_page: 20, search: searchTerm },
      });
      return response.data;
    },
    {
      keepPreviousData: true,
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

  const getRiskColor = (riskScore: number) => {
    if (riskScore > 0.7) return 'error';
    if (riskScore > 0.3) return 'warning';
    return 'success';
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(1);
  };

  const handleRefresh = () => {
    refetch();
  };

  const handleViewDetails = (command: CommandHistoryItem) => {
    setSelectedCommand(command);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Command History
        </Typography>
        <IconButton onClick={handleRefresh} disabled={isLoading}>
          <Refresh />
        </IconButton>
      </Box>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        View and analyze all processed commands with their security classifications.
      </Typography>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search commands..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      {/* Command History Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Command</TableCell>
                  <TableCell>Classification</TableCell>
                  <TableCell>Risk Score</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={5} sx={{ textAlign: 'center', py: 4 }}>
                      <Typography>Loading...</Typography>
                    </TableCell>
                  </TableRow>
                ) : historyData?.commands?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} sx={{ textAlign: 'center', py: 4 }}>
                      <Typography color="text.secondary">No commands found</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  historyData?.commands?.map((command: CommandHistoryItem) => (
                    <motion.tr
                      key={command.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            fontFamily: 'monospace',
                            backgroundColor: 'grey.100',
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {command.command}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={command.classification}
                          color={getClassificationColor(command.classification)}
                          icon={getClassificationIcon(command.classification)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${(command.risk_score * 100).toFixed(1)}%`}
                          color={getRiskColor(command.risk_score)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(command.timestamp).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(command)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </motion.tr>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          {historyData?.pages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={historyData.pages}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Command Details Dialog */}
      {selectedCommand && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Command Details
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  ID: {selectedCommand.id}
                </Typography>
                <IconButton onClick={() => setSelectedCommand(null)}>
                  <Refresh />
                </IconButton>
              </Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Command
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      fontFamily: 'monospace',
                      backgroundColor: 'grey.100',
                      p: 1,
                      borderRadius: 1,
                      wordBreak: 'break-all',
                    }}
                  >
                    {selectedCommand.command}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Classification
                  </Typography>
                  <Chip
                    label={selectedCommand.classification}
                    color={getClassificationColor(selectedCommand.classification)}
                    icon={getClassificationIcon(selectedCommand.classification)}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Risk Score
                  </Typography>
                  <Typography variant="h6" color={getRiskColor(selectedCommand.risk_score) + '.main'}>
                    {(selectedCommand.risk_score * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedCommand.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </Box>
  );
};

export default CommandHistory;