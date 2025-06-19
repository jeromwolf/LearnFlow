// Mock Supabase client
export const supabase = {
  auth: {
    signInWithPassword: jest.fn().mockResolvedValue({ data: { user: { id: 'test-user-id', email: 'test@example.com' } }, error: null }),
    signUp: jest.fn().mockResolvedValue({ data: { user: { id: 'new-user-id', email: 'test@example.com' } }, error: null }),
    signOut: jest.fn().mockResolvedValue({ error: null }),
    onAuthStateChange: jest.fn().mockImplementation((callback) => {
      // Simulate auth state change
      callback({ event: 'SIGNED_IN', session: { user: { id: 'test-user-id', email: 'test@example.com' } } });
      return { data: { subscription: { unsubscribe: jest.fn() } } };
    }),
    getUser: jest.fn().mockResolvedValue({ data: { user: { id: 'test-user-id', email: 'test@example.com' } }, error: null }),
  },
  from: jest.fn().mockReturnThis(),
  select: jest.fn().mockReturnThis(),
  eq: jest.fn().mockReturnThis(),
  single: jest.fn().mockResolvedValue({ data: null, error: null }),
};

export default supabase;
