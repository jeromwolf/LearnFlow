import React, { ReactNode } from 'react';
import { render, screen, fireEvent, waitFor, renderHook, act } from '@testing-library/react';

// First, mock the supabase module
jest.mock('@/lib/supabase', () => {
  const mockSignInWithPassword = jest.fn();
  const mockSignUp = jest.fn();
  const mockSignOut = jest.fn();
  const mockGetUser = jest.fn();
  
  return {
    supabase: {
      auth: {
        signInWithPassword: mockSignInWithPassword,
        signUp: mockSignUp,
        signOut: mockSignOut,
        onAuthStateChange: (callback: (event: string, session: { user: { id: string; email: string } | null } | null) => void) => {
          // Simulate auth state change with null user initially
          callback('SIGNED_OUT', null);
          return {
            data: { subscription: { unsubscribe: jest.fn() } }
          };
        },
        getUser: mockGetUser,
      },
      from: jest.fn().mockReturnThis(),
      select: jest.fn().mockReturnThis(),
      eq: jest.fn().mockReturnThis(),
      single: jest.fn().mockResolvedValue({ data: null, error: null }),
    },
    // Export the mocks for use in tests
    __mocks__: {
      mockSignInWithPassword,
      mockSignUp,
      mockSignOut,
      mockGetUser,
    }
  };
});

// Now import the module and get the mocks
const { supabase } = require('@/lib/supabase');
const { 
  mockSignInWithPassword, 
  mockSignUp, 
  mockSignOut, 
  mockGetUser 
} = require('@/lib/supabase').__mocks__;

// Then import the components we're testing
import { useAuth, AuthProvider } from '../AuthContext';
import { render as customRender } from '../../__tests__/test-utils';

const TestComponent = () => {
  const { user, login, register, logout } = useAuth();
  const [error, setError] = React.useState('');

  const handleLogin = async () => {
    try {
      await login('test@example.com', 'password');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleRegister = async () => {
    try {
      await register('test@example.com', 'password', 'Test User');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div>
      <div data-testid="user-email">{user?.email || 'No user'}</div>
      {error && <div data-testid="error">{error}</div>}
      <button onClick={handleLogin} data-testid="login-button">
        Login
      </button>
      <button onClick={handleRegister} data-testid="register-button">
        Register
      </button>
      <button onClick={handleLogout} data-testid="logout-button">
        Logout
      </button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('should provide auth context', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }: { children: ReactNode }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initial auth state to be set
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(typeof result.current.login).toBe('function');
    expect(typeof result.current.register).toBe('function');
    expect(typeof result.current.logout).toBe('function');
  });

  it('should handle login successfully', async () => {
    // Mock successful login
    const mockUser = { id: '123', email: 'test@example.com' };
    mockSignInWithPassword.mockResolvedValueOnce({
      data: { user: mockUser },
      error: null,
    });

    customRender(<TestComponent />);

    await act(async () => {
      fireEvent.click(screen.getByTestId('login-button'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
      expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    });
  });

  it('should handle login error', async () => {
    // Mock login error
    const errorMessage = 'Invalid login credentials';
    mockSignInWithPassword.mockRejectedValueOnce(new Error(errorMessage));

    customRender(<TestComponent />);

    await act(async () => {
      fireEvent.click(screen.getByTestId('login-button'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
    });
  });

  it('should handle registration successfully', async () => {
    // Mock successful registration
    const mockUser = { id: '123', email: 'test@example.com' };
    mockSignUp.mockResolvedValueOnce({
      data: { user: mockUser },
      error: null,
    });

    customRender(<TestComponent />);

    await act(async () => {
      fireEvent.click(screen.getByTestId('register-button'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
      expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    });
  });

  it('should handle logout', async () => {
    // Mock successful logout
    mockSignOut.mockResolvedValueOnce({ error: null });

    customRender(<TestComponent />, {
      authProviderProps: {
        initialUser: { email: 'test@example.com', id: '123' },
      },
    });

    // Should show user email initially
    expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');

    // Click logout
    await act(async () => {
      fireEvent.click(screen.getByTestId('logout-button'));
    });

    // Should show 'No user' after logout
    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('No user');
      expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    });
  });
});
