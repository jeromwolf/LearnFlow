import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AuthProvider, useAuth } from '../AuthContext';

// Simple test component that uses the auth context
const TestComponent = () => {
  const { user } = useAuth();
  return (
    <div>
      <div data-testid="user-email">{user?.email || 'No user'}</div>
    </div>
  );
};

describe('AuthContext Simple Test', () => {
  it('should render without errors', () => {
    // This is a simple test to check if the AuthProvider can be rendered
    // without throwing any errors
    expect(() => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
    }).not.toThrow();
  });

  it('should initially have no user', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByTestId('user-email')).toHaveTextContent('No user');
  });
});
