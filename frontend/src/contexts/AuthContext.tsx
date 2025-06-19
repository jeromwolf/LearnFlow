'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { User, Session, AuthError } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';

interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  updated_at?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  session: Session | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  register: (email: string, password: string, fullName: string) => Promise<{ error: AuthError | null }>;
  logout: () => Promise<{ error: AuthError | null }>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  updateProfile: (updates: Partial<UserProfile>) => Promise<{ error: AuthError | null }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Login with email and password
  const login = async (email: string, password: string) => {
    setError(null);
    const { data, error: signInError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (signInError) {
      setError(signInError.message);
      return { error: signInError };
    }

    if (data?.user) {
      const { data: userData, error: profileError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', data.user.id)
        .single();

      if (profileError) {
        setError(profileError.message);
        return { error: profileError };
      }

      setUser({
        id: data.user.id,
        email: data.user.email || '',
        full_name: userData?.full_name || '',
        avatar_url: userData?.avatar_url,
      });
      
      setSession(data.session);
      router.push('/dashboard');
    }

    return { error: null };
  };

  // Register new user
  const register = async (email: string, password: string, fullName: string) => {
    setError(null);
    
    // Create user in Auth
    const { data: authData, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    });

    if (signUpError) {
      setError(signUpError.message);
      return { error: signUpError };
    }

    // Create user profile in public.profiles table
    if (authData.user) {
      const { error: profileError } = await supabase
        .from('profiles')
        .insert([
          { 
            id: authData.user.id, 
            email,
            full_name: fullName,
          },
        ]);

      if (profileError) {
        setError(profileError.message);
        return { error: profileError };
      }

      setUser({
        id: authData.user.id,
        email,
        full_name: fullName,
      });
      
      setSession(authData.session);
      router.push('/dashboard');
    }

    return { error: null };
  };

  // Logout
  const logout = async () => {
    setError(null);
    const { error: signOutError } = await supabase.auth.signOut();
    
    if (signOutError) {
      setError(signOutError.message);
      return { error: signOutError };
    }
    
    setUser(null);
    setSession(null);
    router.push('/login');
    return { error: null };
  };

  // Password reset
  const resetPassword = async (email: string) => {
    setError(null);
    const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });

    if (resetError) {
      setError(resetError.message);
    }
    
    return { error: resetError };
  };

  // Update user profile
  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!user) return { error: new Error('User not authenticated') as AuthError };
    
    setError(null);
    const { error: updateError } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', user.id);

    if (updateError) {
      setError(updateError.message);
      return { error: updateError };
    }

    setUser(prev => (prev ? { ...prev, ...updates } : null));
    return { error: null };
  };

  // Check active sessions and set the user
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (session?.user) {
          const { data: userData, error } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', session.user.id)
            .single();

          if (error) {
            console.error('Error fetching user profile:', error);
            setError(error.message);
            return;
          }

          setUser({
            id: session.user.id,
            email: session.user.email || '',
            full_name: userData?.full_name || '',
            avatar_url: userData?.avatar_url,
          });
          setSession(session);
        } else {
          setUser(null);
          setSession(null);
        }
        setLoading(false);
      }
    );

    // Check the current user when the app loads
    const getUser = async () => {
      const { data: { user }, error } = await supabase.auth.getUser();
      
      if (user) {
        const { data: userData, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single();

        if (profileError) {
          console.error('Error fetching user profile:', profileError);
          setError(profileError.message);
          setLoading(false);
          return;
        }

        setUser({
          id: user.id,
          email: user.email || '',
          full_name: userData?.full_name || '',
          avatar_url: userData?.avatar_url,
        });
        
        // Get session
        const { data: { session } } = await supabase.auth.getSession();
        setSession(session);
      }
      setLoading(false);
    };

    getUser();

    // Cleanup subscription on unmount
    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  const value = {
    user,
    session,
    loading,
    error,
    login,
    register,
    logout,
    resetPassword,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Helper hook to protect routes
export function useRequireAuth(redirectUrl = '/login') {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push(redirectUrl);
    }
  }, [user, loading, router, redirectUrl]);

  return { user, loading };
};
