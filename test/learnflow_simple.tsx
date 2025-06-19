import React, { useState } from 'react';
import { Search, Play, Star, Users, Clock, ChevronRight, BookOpen, Code, Palette, TrendingUp, Award, Heart, Menu, X } from 'lucide-react';

const HomePage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const featuredCourses = [
    {
      id: 1,
      title: "React 완벽 마스터: 초급부터 고급까지",
      instructor: "김개발",
      image: "/api/placeholder/300/200",
      price: "89,000원",
      originalPrice: "129,000원",
      rating: 4.8,
      students: 1245,
      duration: "12시간",
      level: "초급"
    },
    {
      id: 2,
      title: "디지털 마케팅 실무: SNS부터 퍼포먼스까지",
      instructor: "박마케터",
      image: "/api/placeholder/300/200",
      price: "75,000원",
      originalPrice: "99,000원",
      rating: 4.9,
      students: 892,
      duration: "8시간",
      level: "중급"
    },
    {
      id: 3,
      title: "UI/UX 디자인 실무: 피그마로 완성하는 앱 디자인",
      instructor: "이디자이너",
      image: "/api/placeholder/300/200",
      price: "65,000원",
      originalPrice: "89,000원",
      rating: 4.7,
      students: 756,
      duration: "10시간",
      level: "초급"
    },
    {
      id: 4,
      title: "데이터 분석 입문: 파이썬으로 시작하는 데이터 사이언스",
      instructor: "최데이터",
      image: "/api/placeholder/300/200",
      price: "95,000원",
      originalPrice: "139,000원",
      rating: 4.6,
      students: 623,
      duration: "15시간",
      level: "초급"
    }
  ];

  const categories = [
    { name: "프로그래밍", icon: Code, color: "bg-blue-100 text-blue-600" },
    { name: "디자인", icon: Palette, color: "bg-purple-100 text-purple-600" },
    { name: "마케팅", icon: TrendingUp, color: "bg-green-100 text-green-600" },
    { name: "비즈니스", icon: Award, color: "bg-orange-100 text-orange-600" },
    { name: "자기계발", icon: Heart, color: "bg-pink-100 text-pink-600" },
    { name: "기타", icon: BookOpen, color: "bg-gray-100 text-gray-600" }
  ];

  const stats = [
    { label: "수강생", value: "10,000+", icon: Users },
    { label: "강의", value: "500+", icon: BookOpen },
    { label: "강사", value: "150+", icon: Award },
    { label: "완료율", value: "92%", icon: TrendingUp }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">LF</span>
              </div>
              <span className="text-xl font-bold text-gray-900">LearnFlow</span>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors">강의</a>
              <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors">카테고리</a>
              <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors">강사 지원</a>
            </nav>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-700 hover:text-blue-600 transition-colors"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>

            {/* Auth Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              <button className="text-gray-700 hover:text-blue-600 font-medium transition-colors">로그인</button>
              <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105">
                회원가입
              </button>
            </div>
          </div>
          
          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden border-t border-gray-100 bg-white">
              <div className="px-4 py-6 space-y-4">
                <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium transition-colors">강의</a>
                <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium transition-colors">카테고리</a>
                <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium transition-colors">강사 지원</a>
                <div className="pt-4 border-t border-gray-100 space-y-3">
                  <button className="block w-full text-left text-gray-700 hover:text-blue-600 font-medium transition-colors">로그인</button>
                  <button className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-medium text-center">
                    회원가입
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-indigo-900 via-blue-800 to-purple-900 text-white py-24 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-10 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white bg-opacity-10 backdrop-blur-sm rounded-full text-sm font-medium mb-6 border border-white border-opacity-20">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
              새로운 강의가 매주 업데이트됩니다
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="block">자연스러운 학습의 흐름</span>
              <span className="block mt-2">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-orange-400 to-pink-400">
                  LearnFlow
                </span>
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl mb-10 text-blue-100 max-w-4xl mx-auto leading-relaxed">
              <span className="font-semibold text-white">실무 전문가들이 직접 가르치는</span> 온라인 강의로
              <br />
              <span className="text-yellow-300">당신의 커리어를 한 단계 더 성장</span>시켜보세요
            </p>
            
            {/* Search Bar */}
            <div className="max-w-2xl mx-auto mb-10">
              <div className="relative bg-white bg-opacity-10 backdrop-blur-xl border border-white border-opacity-20 rounded-2xl p-1">
                <div className="flex items-center">
                  <Search className="absolute left-6 text-white text-opacity-70 w-5 h-5 z-10" />
                  <input
                    type="text"
                    placeholder="React, 디자인, 마케팅... 무엇을 배우고 싶나요?"
                    className="w-full pl-14 pr-32 py-4 bg-transparent text-white placeholder-white placeholder-opacity-70 focus:outline-none text-lg"
                  />
                  <button className="absolute right-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-300">
                    검색
                  </button>
                </div>
              </div>
              
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                <span className="text-white text-opacity-70 text-sm">인기 검색어:</span>
                {['React', 'Python', 'UI/UX', '마케팅', '엑셀'].map((keyword) => (
                  <button key={keyword} className="text-sm text-white bg-white bg-opacity-10 hover:bg-opacity-20 px-3 py-1 rounded-full transition-colors">
                    {keyword}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="group bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold hover:bg-gray-50 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center">
                <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                무료 강의 체험하기
              </button>
              <button className="group border-2 border-white text-white px-8 py-4 rounded-xl font-semibold hover:bg-white hover:text-blue-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105">
                강사로 시작하기
                <ChevronRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">믿을 수 있는 온라인 교육 플랫폼</h2>
            <p className="text-gray-600">수많은 학습자들이 LearnFlow와 함께 성장하고 있습니다</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center group">
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                    <stat.icon className="w-8 h-8 text-white" />
                  </div>
                </div>
                <div className="text-4xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">{stat.value}</div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">다양한 분야의 전문 강의</h2>
            <p className="text-xl text-gray-600">당신의 관심사에 맞는 카테고리를 선택해보세요</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {categories.map((category, index) => (
              <div key={index} className="group cursor-pointer">
                <div className="text-center p-6 rounded-2xl border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all duration-300 bg-white">
                  <div className={`w-16 h-16 ${category.color} rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-all duration-300`}>
                    <category.icon className="w-8 h-8" />
                  </div>
                  <h3 className="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">{category.name}</h3>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Courses */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">인기 강의</h2>
              <p className="text-xl text-gray-600">수강생들이 가장 많이 선택한 베스트 강의</p>
            </div>
            <button className="hidden md:flex items-center text-blue-600 hover:text-blue-700 font-semibold group">
              전체보기
              <ChevronRight className="w-5 h-5 ml-1 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredCourses.map((course) => (
              <div key={course.id} className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer border">
                <div className="relative overflow-hidden">
                  <img 
                    src={course.image} 
                    alt={course.title}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 left-3">
                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs px-2 py-1 rounded-full font-medium">
                      {course.level}
                    </span>
                  </div>
                  <div className="absolute top-3 right-3">
                    <div className="bg-white bg-opacity-90 backdrop-blur-sm rounded-full p-2">
                      <Heart className="w-4 h-4 text-gray-600 hover:text-red-500 transition-colors" />
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  <h3 className="font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors leading-tight">
                    {course.title}
                  </h3>
                  <p className="text-gray-600 mb-3">{course.instructor}</p>
                  
                  <div className="flex items-center mb-3 space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <Star className="w-4 h-4 text-yellow-400 mr-1" />
                      <span>{course.rating}</span>
                    </div>
                    <div className="flex items-center">
                      <Users className="w-4 h-4 mr-1" />
                      <span>{course.students}명</span>
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      <span>{course.duration}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-bold text-gray-900">{course.price}</span>
                      <span className="text-sm text-gray-500 line-through">{course.originalPrice}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">지금 바로 시작하세요</h2>
          <p className="text-xl mb-8 text-blue-100">
            수천 명의 학습자들이 LearnFlow와 함께 성장하고 있습니다.
            <br />
            당신도 오늘부터 새로운 기술을 배워보세요.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold hover:bg-gray-50 transition-colors">
              무료로 시작하기
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-xl font-semibold hover:bg-white hover:text-blue-600 transition-colors">
              강의 둘러보기
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">LF</span>
                </div>
                <span className="text-xl font-bold">LearnFlow</span>
              </div>
              <p className="text-gray-400 mb-4">자연스러운 학습의 흐름으로 모두가 성장할 수 있는 세상을 만들어갑니다.</p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">서비스</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">강의 목록</a></li>
                <li><a href="#" className="hover:text-white transition-colors">카테고리</a></li>
                <li><a href="#" className="hover:text-white transition-colors">무료 강의</a></li>
                <li><a href="#" className="hover:text-white transition-colors">강사 지원</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">고객지원</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">고객센터</a></li>
                <li><a href="#" className="hover:text-white transition-colors">자주 묻는 질문</a></li>
                <li><a href="#" className="hover:text-white transition-colors">공지사항</a></li>
                <li><a href="#" className="hover:text-white transition-colors">문의하기</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">회사</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">회사소개</a></li>
                <li><a href="#" className="hover:text-white transition-colors">이용약관</a></li>
                <li><a href="#" className="hover:text-white transition-colors">개인정보처리방침</a></li>
                <li><a href="#" className="hover:text-white transition-colors">채용정보</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 LearnFlow. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;