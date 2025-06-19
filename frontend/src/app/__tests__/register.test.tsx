import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import RegisterPage from '../register/page';
import { render as customRender } from '../../__tests__/test-utils';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock the AuthContext
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(() => ({
    register: jest.fn(),
    user: null,
    loading: false,
  })),
}));

describe('RegisterPage', () => {
  const mockPush = jest.fn();
  const mockRegister = jest.fn();

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
      register: mockRegister,
      user: null,
      loading: false,
    }));
  });

  it('renders the registration form', () => {
    render(<RegisterPage />);
    
    expect(screen.getByLabelText(/이름/)).toBeInTheDocument();
    expect(screen.getByLabelText(/이메일/)).toBeInTheDocument();
    expect(screen.getByLabelText(/비밀번호/)).toBeInTheDocument();
    expect(screen.getByLabelText(/비밀번호 확인/)).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /회원가입/ })).toBeInTheDocument();
    expect(screen.getByText(/이미 계정이 있으신가요/)).toBeInTheDocument();
  });

  it('shows validation errors for empty form submission', async () => {
    render(<RegisterPage />);
    
    // Submit the form without filling in any fields
    fireEvent.click(screen.getByRole('button', { name: /회원가입/ }));
    
    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText('모든 필수 항목을 입력해주세요.')).toBeInTheDocument();
    });
  });

  it('shows password mismatch error', async () => {
    render(<RegisterPage />);
    
    // Fill in the form with mismatched passwords
    fireEvent.change(screen.getByLabelText(/이름/), {
      target: { value: 'Test User' },
    });
    
    fireEvent.change(screen.getByLabelText(/이메일/), {
      target: { value: 'test@example.com' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호/), {
      target: { value: 'password123' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호 확인/), {
      target: { value: 'differentpassword' },
    });
    
    // Check the terms checkbox
    fireEvent.click(screen.getByRole('checkbox'));
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /회원가입/ }));
    
    // Check for password mismatch error
    await waitFor(() => {
      expect(screen.getByText('비밀번호가 일치하지 않습니다.')).toBeInTheDocument();
    });
  });

  it('shows terms not agreed error', async () => {
    render(<RegisterPage />);
    
    // Fill in the form but don't check the terms checkbox
    fireEvent.change(screen.getByLabelText(/이름/), {
      target: { value: 'Test User' },
    });
    
    fireEvent.change(screen.getByLabelText(/이메일/), {
      target: { value: 'test@example.com' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호/), {
      target: { value: 'password123' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호 확인/), {
      target: { value: 'password123' },
    });
    
    // Submit the form without checking the terms checkbox
    fireEvent.click(screen.getByRole('button', { name: /회원가입/ }));
    
    // Check for terms not agreed error
    await waitFor(() => {
      expect(screen.getByText('이용약관 및 개인정보 처리방침에 동의해주세요.')).toBeInTheDocument();
    });
  });

  it('submits the form with valid data', async () => {
    // Mock successful registration
    mockRegister.mockResolvedValueOnce({ error: null });
    
    render(<RegisterPage />);
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/이름/), {
      target: { value: 'Test User' },
    });
    
    fireEvent.change(screen.getByLabelText(/이메일/), {
      target: { value: 'test@example.com' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호/), {
      target: { value: 'Password123!' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호 확인/), {
      target: { value: 'Password123!' },
    });
    
    // Check the terms checkbox
    fireEvent.click(screen.getByRole('checkbox'));
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /회원가입/ }));
    
    // Check that register was called with the correct data
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith(
        'test@example.com',
        'Password123!',
        'Test User'
      );
    });
  });

  it('shows an error message when registration fails', async () => {
    // Mock failed registration
    const errorMessage = '이미 가입된 이메일 주소입니다.';
    mockRegister.mockResolvedValueOnce({ 
      error: { message: 'User already registered' } 
    });
    
    render(<RegisterPage />);
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/이름/), {
      target: { value: 'Test User' },
    });
    
    fireEvent.change(screen.getByLabelText(/이메일/), {
      target: { value: 'existing@example.com' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호/), {
      target: { value: 'Password123!' },
    });
    
    fireEvent.change(screen.getByLabelText(/비밀번호 확인/), {
      target: { value: 'Password123!' },
    });
    
    // Check the terms checkbox
    fireEvent.click(screen.getByRole('checkbox'));
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /회원가입/ }));
    
    // Check that the error message is displayed
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('redirects to dashboard if already logged in', async () => {
    // Mock user being already logged in
    require('@/contexts/AuthContext').useAuth.mockImplementationOnce(() => ({
      register: mockRegister,
      user: { email: 'test@example.com' },
      loading: false,
    }));
    
    render(<RegisterPage />);
    
    // Check that we were redirected
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows loading state', () => {
    // Mock loading state
    require('@/contexts/AuthContext').useAuth.mockImplementationOnce(() => ({
      register: mockRegister,
      user: null,
      loading: true,
    }));
    
    render(<RegisterPage />);
    
    // Check that loading spinner is shown
    expect(screen.getByText('처리 중입니다...')).toBeInTheDocument();
  });
});
