import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Grid,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Save,
  Refresh,
  Security,
  Notifications,
  Palette,
  Language,
  Delete,
  Edit,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Settings: React.FC = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: false,
      security: true,
    },
    appearance: {
      theme: 'light',
      language: 'en',
    },
    security: {
      twoFactor: false,
      sessionTimeout: 30,
      logLevel: 'info',
    },
  });
  const [changePassword, setChangePassword] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [showChangePassword, setShowChangePassword] = useState(false);

  const handleSettingChange = (category: string, setting: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [setting]: value,
      },
    }));
  };

  const handleSaveSettings = () => {
    // Here you would typically save to the backend
    toast.success('Settings saved successfully!');
  };

  const handleChangePassword = () => {
    if (changePassword.newPassword !== changePassword.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (changePassword.newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    // Here you would typically call the backend API
    toast.success('Password changed successfully!');
    setShowChangePassword(false);
    setChangePassword({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    });
  };

  const SettingCard = ({ title, icon, children }: any) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {icon}
            <Typography variant="h6" sx={{ ml: 1 }}>
              {title}
            </Typography>
          </Box>
          {children}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage your account settings and preferences.
      </Typography>

      <Grid container spacing={3}>
        {/* User Information */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="User Information"
            icon={<Security color="primary" />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Username"
                  value={user?.username || ''}
                  disabled
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Role"
                  value={user?.role || ''}
                  disabled
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  onClick={() => setShowChangePassword(true)}
                  startIcon={<Edit />}
                >
                  Change Password
                </Button>
              </Grid>
            </Grid>
          </SettingCard>
        </Grid>

        {/* Notifications */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Notifications"
            icon={<Notifications color="primary" />}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.email}
                    onChange={(e) => handleSettingChange('notifications', 'email', e.target.checked)}
                  />
                }
                label="Email Notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.push}
                    onChange={(e) => handleSettingChange('notifications', 'push', e.target.checked)}
                  />
                }
                label="Push Notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.security}
                    onChange={(e) => handleSettingChange('notifications', 'security', e.target.checked)}
                  />
                }
                label="Security Alerts"
              />
            </Box>
          </SettingCard>
        </Grid>

        {/* Appearance */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Appearance"
            icon={<Palette color="primary" />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  select
                  label="Theme"
                  value={settings.appearance.theme}
                  onChange={(e) => handleSettingChange('appearance', 'theme', e.target.value)}
                  SelectProps={{ native: true }}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  select
                  label="Language"
                  value={settings.appearance.language}
                  onChange={(e) => handleSettingChange('appearance', 'language', e.target.value)}
                  SelectProps={{ native: true }}
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </TextField>
              </Grid>
            </Grid>
          </SettingCard>
        </Grid>

        {/* Security Settings */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Security"
            icon={<Security color="primary" />}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.security.twoFactor}
                    onChange={(e) => handleSettingChange('security', 'twoFactor', e.target.checked)}
                  />
                }
                label="Two-Factor Authentication"
              />
              <TextField
                fullWidth
                label="Session Timeout (minutes)"
                type="number"
                value={settings.security.sessionTimeout}
                onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
              />
              <TextField
                fullWidth
                select
                label="Log Level"
                value={settings.security.logLevel}
                onChange={(e) => handleSettingChange('security', 'logLevel', e.target.value)}
                SelectProps={{ native: true }}
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </TextField>
            </Box>
          </SettingCard>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <SettingCard
            title="System Status"
            icon={<Refresh color="primary" />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip label="Online" color="success" />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    AI Model
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip label="Active" color="success" />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Security Monitoring
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip label="Connected" color="success" />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Database
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip label="Stable" color="success" />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    WebSocket
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </SettingCard>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <SettingCard
            title="Recent Activity"
            icon={<Refresh color="primary" />}
          >
            <List>
              <ListItem>
                <ListItemText
                  primary="Password changed"
                  secondary="2 hours ago"
                />
                <Chip label="Security" size="small" color="info" />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Settings updated"
                  secondary="1 day ago"
                />
                <Chip label="General" size="small" color="default" />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Login from new device"
                  secondary="3 days ago"
                />
                <Chip label="Security" size="small" color="warning" />
              </ListItem>
            </List>
          </SettingCard>
        </Grid>
      </Grid>

      {/* Save Button */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          startIcon={<Save />}
          onClick={handleSaveSettings}
          size="large"
        >
          Save Settings
        </Button>
      </Box>

      {/* Change Password Dialog */}
      <Dialog open={showChangePassword} onClose={() => setShowChangePassword(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Current Password"
                type="password"
                value={changePassword.currentPassword}
                onChange={(e) => setChangePassword(prev => ({ ...prev, currentPassword: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="New Password"
                type="password"
                value={changePassword.newPassword}
                onChange={(e) => setChangePassword(prev => ({ ...prev, newPassword: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Confirm New Password"
                type="password"
                value={changePassword.confirmPassword}
                onChange={(e) => setChangePassword(prev => ({ ...prev, confirmPassword: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowChangePassword(false)}>Cancel</Button>
          <Button onClick={handleChangePassword} variant="contained">
            Change Password
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;