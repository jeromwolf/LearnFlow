import React from 'react';
import { render, screen } from '@testing-library/react';

test('renders a button', () => {
  console.log('Button test is running');
  render(<button>Click me</button>);
  const button = screen.getByText(/click me/i);
  expect(button).toBeInTheDocument();
});
