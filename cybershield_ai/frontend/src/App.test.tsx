import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders CyberShield AI', () => {
  render(<App />);
  const linkElement = screen.getByText(/CyberShield AI/i);
  expect(linkElement).toBeInTheDocument();
});