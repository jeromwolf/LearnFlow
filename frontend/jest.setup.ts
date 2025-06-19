import '@testing-library/jest-dom';

// Mock Next.js router
const mockRouter = {
  route: '/',
  pathname: '',
  query: {},
  asPath: '',
  push: jest.fn(),
  replace: jest.fn(),
  reload: jest.fn(),
  back: jest.fn(),
  prefetch: jest.fn(),
  beforePopState: jest.fn(),
  events: {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
  },
};

// Mock Next.js router and navigation
jest.mock('next/navigation', () => ({
  useRouter: () => mockRouter,
  useSearchParams: () => ({
    get: jest.fn().mockReturnValue(null),
  }),
  usePathname: () => '/',
  useParams: () => ({}),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Polyfill TextEncoder/TextDecoder for Jest
import { TextEncoder, TextDecoder } from 'util';

global.TextEncoder = TextEncoder;
// Node's TextDecoder is slightly different from the browser's
global.TextDecoder = TextDecoder as unknown as typeof global.TextDecoder;
