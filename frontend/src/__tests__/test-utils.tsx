import React, { ReactElement, ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import { AuthProvider } from '@/contexts/AuthContext';

interface AuthProviderProps {
  children: ReactNode;
  initialUser?: any;
  initialLoading?: boolean;
}

type CustomRenderOptions = RenderOptions & {
  authProviderProps?: Omit<AuthProviderProps, 'children'>;
};

const customRender = (
  ui: ReactElement,
  {
    authProviderProps = {},
    ...renderOptions
  }: CustomRenderOptions = {}
) => {
  const Wrapper: React.FC<{ children: ReactNode }> = ({ children }) => (
    <AuthProvider {...authProviderProps}>
      {children}
    </AuthProvider>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

export * from '@testing-library/react';
export { customRender as render };
