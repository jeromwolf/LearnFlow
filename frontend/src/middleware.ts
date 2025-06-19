import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  const { pathname } = request.nextUrl;

  // 로그인/회원가입 페이지는 인증된 사용자가 접근하면 대시보드로 리다이렉트
  const isAuthPage = pathname.startsWith('/login') || pathname.startsWith('/register');
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // 보호된 페이지 목록
  const protectedPaths = ['/dashboard', '/profile', '/settings'];
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));

  // 보호된 페이지에 접근 시 토큰이 없으면 로그인 페이지로 리다이렉트
  if (isProtectedPath && !token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('from', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
