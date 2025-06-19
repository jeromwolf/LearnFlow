import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import LoginPage from '../login/page';
import { render as customRender } from '../../__tests__/test-utils';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock the AuthContext
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(() => ({
    login: jest.fn(),
    user: null,
    loading: false,
  })),
}));

describe('LoginPage', () => {
  const mockPush = jest.fn();
  const mockLogin = jest.fn();

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Mock useRouter
    (useRouter as jest.Mock).mockImplementation(() => ({
      push: mockPush,
    }));
    
    // Mock useSearchParams
    (useSearchParams as jest.Mock).mockImplementation(() => ({
      get: jest.fn().mockReturnValue(null),
    }));
    
    // Mock useAuth
    require('@/contexts/AuthContext').useAuth.mockImplementation(() => ({
      login: mockLogin,
      user: null,
      loading: false,
    }));
  });

  it('renders the login form', () => {
    render(<LoginPage />);
    
    expect(screen.getByLabelText(/이메일/)).toBeInTheDocument();
    expect(screen.getByLabelText(/비밀번호/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /로그인/ })).toBeInTheDocument();
    expect(screen.getByText(/계정이 없으신가요/)).toBeInTheDocument();
  });

  it('shows validation errors', async () => {
    render(<LoginPage />);
    
    // Submit the form without filling in any fields
    fireEvent.click(screen.getByRole('button', { name: /로그인/ }));
    
    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText('이메일과 비밀번호를 모두 입력해주세요.')).toBeInTheDocument();
    });
  });

  it('submits the form with valid data', async () => {
    // Mock successful login
    mockLogin.mockResolvedValueOnce({ error: null });
    
    render(<LoginPage />);
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/이메일/), {
      target: { value: 'test@example.com' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호/), {
      target: { value: 'password123' },
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /로그인/ }));
    
    // Check that login was called with the correct data
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('shows an error message when login fails', async () => {
    // Mock failed login
    const errorMessage = '이메일 또는 비밀번호가 올바르지 않습니다.';
    mockLogin.mockResolvedValueOnce({ 
      error: { message: 'Invalid login credentials' } 
    });
    
    render(<LoginPage />);
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/이메일/), {
      target: { value: 'test@example.com' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호/), {
      target: { value: 'wrongpassword' },
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /로그인/ }));
    
    // Check that the error message is displayed
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('redirects to dashboard if already logged in', async () => {
    // Mock user being already logged in
    require('@/contexts/AuthContext').useAuth.mockImplementationOnce(() => ({
      login: mockLogin,
      user: { email: 'test@example.com' },
      loading: false,
    }));
    
    render(<LoginPage />);
    
    // Check that we were redirected
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows loading state', () => {
    // Mock loading state
    require('@/contexts/AuthContext').useAuth.mockImplementationOnce(() => ({
      login: mockLogin,
      user: null,
      loading: true,
    }));
    
    render(<LoginPage />);
    
    // Check that loading spinner is shown
    expect(screen.getByText('로그인 중입니다...')).toBeInTheDocument();
  });
});
