import React, { useState, useEffect } from 'react';
import { Search, Filter, Star, Users, Clock, Heart, Play, ChevronDown, X, Grid, List, ArrowUpDown, BookOpen, Code, Palette, TrendingUp, Award } from 'lucide-react';

const CourseListPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('전체');
  const [selectedLevel, setSelectedLevel] = useState('전체');
  const [selectedPrice, setSelectedPrice] = useState('전체');
  const [sortBy, setSortBy] = useState('인기순');
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [showFilters, setShowFilters] = useState(false);
  const [likedCourses, setLikedCourses] = useState(new Set());

  // 강의 데이터
  const allCourses = [
    {
      id: 1,
      title: "React 완벽 마스터: 초급부터 고급까지",
      instructor: "김개발",
      image: "/api/placeholder/300/200",
      price: 89000,
      originalPrice: 129000,
      rating: 4.8,
      reviewCount: 324,
      students: 1245,
      duration: "12시간",
      level: "초급",
      category: "프로그래밍",
      description: "React의 기초부터 고급 개념까지, 실무에서 바로 사용할 수 있는 React 개발 능력을 키워보세요.",
      skills: ["React", "JavaScript", "JSX", "Hooks"],
      isBestseller: true,
      isNew: false,
      lastUpdated: "2024-12-01"
    },
    {
      id: 2,
      title: "디지털 마케팅 실무: SNS부터 퍼포먼스까지",
      instructor: "박마케터",
      image: "/api/placeholder/300/200",
      price: 75000,
      originalPrice: 99000,
      rating: 4.9,
      reviewCount: 256,
      students: 892,
      duration: "8시간",
      level: "중급",
      category: "마케팅",
      description: "SNS 마케팅부터 퍼포먼스 마케팅까지, 디지털 마케팅의 모든 것을 배워보세요.",
      skills: ["Facebook 광고", "Google 애즈", "SNS 마케팅", "데이터 분석"],
      isBestseller: false,
      isNew: true,
      lastUpdated: "2024-11-28"
    },
    {
      id: 3,
      title: "UI/UX 디자인 실무: 피그마로 완성하는 앱 디자인",
      instructor: "이디자이너",
      image: "/api/placeholder/300/200",
      price: 65000,
      originalPrice: 89000,
      rating: 4.7,
      reviewCount: 189,
      students: 756,
      duration: "10시간",
      level: "초급",
      category: "디자인",
      description: "피그마를 활용한 실무 UI/UX 디자인 프로세스를 경험해보세요.",
      skills: ["Figma", "UI 디자인", "UX 리서치", "프로토타이핑"],
      isBestseller: true,
      isNew: false,
      lastUpdated: "2024-11-15"
    },
    {
      id: 4,
      title: "데이터 분석 입문: 파이썬으로 시작하는 데이터 사이언스",
      instructor: "최데이터",
      image: "/api/placeholder/300/200",
      price: 95000,
      originalPrice: 139000,
      rating: 4.6,
      reviewCount: 412,
      students: 623,
      duration: "15시간",
      level: "초급",
      category: "프로그래밍",
      description: "파이썬을 활용한 데이터 분석의 기초부터 고급 기법까지 학습합니다.",
      skills: ["Python", "Pandas", "NumPy", "데이터 시각화"],
      isBestseller: false,
      isNew: false,
      lastUpdated: "2024-10-20"
    },
    {
      id: 5,
      title: "포토샵 마스터클래스: 전문가가 되는 완벽 가이드",
      instructor: "정그래픽",
      image: "/api/placeholder/300/200",
      price: 55000,
      originalPrice: 79000,
      rating: 4.5,
      reviewCount: 167,
      students: 445,
      duration: "9시간",
      level: "초급",
      category: "디자인",
      description: "포토샵의 모든 기능을 마스터하고 전문가 수준의 이미지 편집 능력을 키워보세요.",
      skills: ["Photoshop", "이미지 편집", "합성", "레이어"],
      isBestseller: false,
      isNew: true,
      lastUpdated: "2024-12-05"
    },
    {
      id: 6,
      title: "Node.js 백엔드 개발: Express부터 배포까지",
      instructor: "서백엔드",
      image: "/api/placeholder/300/200",
      price: 99000,
      originalPrice: 149000,
      rating: 4.8,
      reviewCount: 278,
      students: 534,
      duration: "18시간",
      level: "중급",
      category: "프로그래밍",
      description: "Node.js와 Express를 활용한 실무 백엔드 개발을 배우고 실제 서비스를 배포해보세요.",
      skills: ["Node.js", "Express", "MongoDB", "API 개발"],
      isBestseller: true,
      isNew: false,
      lastUpdated: "2024-11-10"
    },
    {
      id: 7,
      title: "엑셀 실무 완전정복: 기초부터 매크로까지",
      instructor: "김오피스",
      image: "/api/placeholder/300/200",
      price: 45000,
      originalPrice: 65000,
      rating: 4.4,
      reviewCount: 523,
      students: 1823,
      duration: "7시간",
      level: "초급",
      category: "비즈니스",
      description: "업무에 바로 적용할 수 있는 엑셀 실무 스킬을 모두 배워보세요.",
      skills: ["Excel", "VBA", "매크로", "데이터 분석"],
      isBestseller: true,
      isNew: false,
      lastUpdated: "2024-09-25"
    },
    {
      id: 8,
      title: "스피치 스킬업: 프레젠테이션의 달인 되기",
      instructor: "문스피치",
      image: "/api/placeholder/300/200",
      price: 39000,
      originalPrice: 59000,
      rating: 4.3,
      reviewCount: 145,
      students: 298,
      duration: "5시간",
      level: "초급",
      category: "자기계발",
      description: "효과적인 스피치와 프레젠테이션 스킬을 배우고 자신감을 기르세요.",
      skills: ["스피치", "프레젠테이션", "퍼블릭 스피킹", "커뮤니케이션"],
      isBestseller: false,
      isNew: true,
      lastUpdated: "2024-11-30"
    }
  ];

  const categories = [
    { name: "전체", count: allCourses.length },
    { name: "프로그래밍", count: allCourses.filter(c => c.category === "프로그래밍").length },
    { name: "디자인", count: allCourses.filter(c => c.category === "디자인").length },
    { name: "마케팅", count: allCourses.filter(c => c.category === "마케팅").length },
    { name: "비즈니스", count: allCourses.filter(c => c.category === "비즈니스").length },
    { name: "자기계발", count: allCourses.filter(c => c.category === "자기계발").length }
  ];

  // 필터링된 강의 목록
  const [filteredCourses, setFilteredCourses] = useState(allCourses);

  // 필터링 및 정렬 로직
  useEffect(() => {
    let filtered = allCourses.filter(course => {
      const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          course.instructor.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          course.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesCategory = selectedCategory === '전체' || course.category === selectedCategory;
      const matchesLevel = selectedLevel === '전체' || course.level === selectedLevel;
      
      let matchesPrice = true;
      if (selectedPrice === '무료') {
        matchesPrice = course.price === 0;
      } else if (selectedPrice === '50000원 이하') {
        matchesPrice = course.price <= 50000;
      } else if (selectedPrice === '50000-100000원') {
        matchesPrice = course.price > 50000 && course.price <= 100000;
      } else if (selectedPrice === '100000원 이상') {
        matchesPrice = course.price > 100000;
      }

      return matchesSearch && matchesCategory && matchesLevel && matchesPrice;
    });

    // 정렬
    switch (sortBy) {
      case '인기순':
        filtered.sort((a, b) => b.students - a.students);
        break;
      case '평점순':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case '최신순':
        filtered.sort((a, b) => new Date(b.lastUpdated) - new Date(a.lastUpdated));
        break;
      case '가격 낮은순':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case '가격 높은순':
        filtered.sort((a, b) => b.price - a.price);
        break;
      default:
        break;
    }

    setFilteredCourses(filtered);
  }, [searchTerm, selectedCategory, selectedLevel, selectedPrice, sortBy]);

  // 찜하기 토글
  const toggleLike = (courseId) => {
    const newLikedCourses = new Set(likedCourses);
    if (newLikedCourses.has(courseId)) {
      newLikedCourses.delete(courseId);
    } else {
      newLikedCourses.add(courseId);
    }
    setLikedCourses(newLikedCourses);
  };

  // 필터 초기화
  const resetFilters = () => {
    setSearchTerm('');
    setSelectedCategory('전체');
    setSelectedLevel('전체');
    setSelectedPrice('전체');
    setSortBy('인기순');
  };

  // 강의 카드 컴포넌트 (그리드 모드)
  const CourseCard = ({ course }) => (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer border border-gray-100 hover:border-blue-200">
      <div className="relative overflow-hidden">
        <img 
          src={course.image} 
          alt={course.title}
          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
        />
        
        {/* 뱃지들 */}
        <div className="absolute top-3 left-3 flex flex-col gap-2">
          {course.isBestseller && (
            <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium">
              베스트셀러
            </span>
          )}
          {course.isNew && (
            <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">
              NEW
            </span>
          )}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs px-2 py-1 rounded-full font-medium">
            {course.level}
          </span>
        </div>
        
        {/* 찜하기 버튼 */}
        <div className="absolute top-3 right-3">
          <button
            onClick={(e) => {
              e.stopPropagation();
              toggleLike(course.id);
            }}
            className="bg-white bg-opacity-90 backdrop-blur-sm rounded-full p-2 hover:bg-opacity-100 transition-all"
          >
            <Heart 
              className={`w-5 h-5 transition-colors ${
                likedCourses.has(course.id) ? 'text-red-500 fill-current' : 'text-gray-600 hover:text-red-500'
              }`} 
            />
          </button>
        </div>
        
        {/* 플레이 버튼 */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="bg-white bg-opacity-90 backdrop-blur-sm rounded-full p-4 transform scale-75 group-hover:scale-100 transition-transform duration-300">
            <Play className="w-8 h-8 text-blue-600" />
          </div>
        </div>
      </div>
      
      <div className="p-6">
        <h3 className="font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors text-lg leading-tight line-clamp-2">
          {course.title}
        </h3>
        <p className="text-gray-600 font-medium mb-3">{course.instructor}</p>
        
        <div className="flex items-center mb-3 space-x-4 text-sm text-gray-500">
          <div className="flex items-center bg-yellow-50 px-2 py-1 rounded-full">
            <Star className="w-4 h-4 text-yellow-400 mr-1" />
            <span className="font-medium text-yellow-600">{course.rating}</span>
            <span className="ml-1">({course.reviewCount})</span>
          </div>
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-1" />
            <span>{course.students.toLocaleString()}명</span>
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            <span>{course.duration}</span>
          </div>
        </div>

        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {course.skills.slice(0, 3).map((skill, index) => (
              <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                {skill}
              </span>
            ))}
            {course.skills.length > 3 && (
              <span className="text-xs text-gray-500">+{course.skills.length - 3}</span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-gray-900">{course.price.toLocaleString()}원</span>
            {course.originalPrice > course.price && (
              <span className="text-sm text-gray-400 line-through">{course.originalPrice.toLocaleString()}원</span>
            )}
          </div>
          {course.originalPrice > course.price && (
            <div className="text-sm text-green-600 font-semibold bg-green-50 px-2 py-1 rounded-full">
              {Math.round(((course.originalPrice - course.price) / course.originalPrice) * 100)}% 할인
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // 리스트 모드 컴포넌트
  const CourseListItem = ({ course }) => (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group cursor-pointer border border-gray-100 hover:border-blue-200 p-6">
      <div className="flex gap-6">
        <div className="relative w-48 h-32 flex-shrink-0 overflow-hidden rounded-lg">
          <img 
            src={course.image} 
            alt={course.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          
          {/* 뱃지들 */}
          <div className="absolute top-2 left-2 flex flex-col gap-1">
            {course.isBestseller && (
              <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                베스트셀러
              </span>
            )}
            {course.isNew && (
              <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                NEW
              </span>
            )}
          </div>
        </div>
        
        <div className="flex-1">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-gray-900 group-hover:text-blue-600 transition-colors text-xl leading-tight">
              {course.title}
            </h3>
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleLike(course.id);
              }}
              className="ml-4"
            >
              <Heart 
                className={`w-5 h-5 transition-colors ${
                  likedCourses.has(course.id) ? 'text-red-500 fill-current' : 'text-gray-400 hover:text-red-500'
                }`} 
              />
            </button>
          </div>
          
          <p className="text-gray-600 font-medium mb-2">{course.instructor}</p>
          <p className="text-gray-600 mb-3 line-clamp-2">{course.description}</p>
          
          <div className="flex items-center mb-3 space-x-6 text-sm text-gray-500">
            <div className="flex items-center bg-yellow-50 px-2 py-1 rounded-full">
              <Star className="w-4 h-4 text-yellow-400 mr-1" />
              <span className="font-medium text-yellow-600">{course.rating}</span>
              <span className="ml-1">({course.reviewCount})</span>
            </div>
            <div className="flex items-center">
              <Users className="w-4 h-4 mr-1" />
              <span>{course.students.toLocaleString()}명</span>
            </div>
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              <span>{course.duration}</span>
            </div>
            <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
              {course.level}
            </span>
          </div>
          
          <div className="mb-3">
            <div className="flex flex-wrap gap-1">
              {course.skills.map((skill, index) => (
                <span key={index} className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-full">
                  {skill}
                </span>
              ))}
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-gray-900">{course.price.toLocaleString()}원</span>
              {course.originalPrice > course.price && (
                <span className="text-lg text-gray-400 line-through">{course.originalPrice.toLocaleString()}원</span>
              )}
            </div>
            {course.originalPrice > course.price && (
              <div className="text-sm text-green-600 font-semibold bg-green-50 px-3 py-1 rounded-full">
                {Math.round(((course.originalPrice - course.price) / course.originalPrice) * 100)}% 할인
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">LF</span>
              </div>
              <span className="text-xl font-bold text-gray-900">LearnFlow</span>
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-2xl mx-8">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="강의, 강사, 기술을 검색해보세요"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Auth Buttons */}
            <div className="flex items-center space-x-4">
              <button className="text-gray-700 hover:text-blue-600 font-medium transition-colors">로그인</button>
              <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-medium">
                회원가입
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* 사이드바 필터 */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sticky top-24">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900">필터</h3>
                <button 
                  onClick={resetFilters}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  초기화
                </button>
              </div>

              {/* 카테고리 */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">카테고리</h4>
                <div className="space-y-2">
                  {categories.map((category) => (
                    <button
                      key={category.name}
                      onClick={() => setSelectedCategory(category.name)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center justify-between ${
                        selectedCategory === category.name
                          ? 'bg-blue-50 text-blue-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <span>{category.name}</span>
                      <span className={`text-sm ${selectedCategory === category.name ? 'text-blue-500' : 'text-gray-400'}`}>
                        {category.count}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* 난이도 */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">난이도</h4>
                <div className="space-y-2">
                  {['전체', '초급', '중급', '고급'].map((level) => (
                    <button
                      key={level}
                      onClick={() => setSelectedLevel(level)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        selectedLevel === level
                          ? 'bg-blue-50 text-blue-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              {/* 가격 */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">가격</h4>
                <div className="space-y-2">
                  {['전체', '무료', '50000원 이하', '50000-100000원', '100000원 이상'].map((price) => (
                    <button
                      key={price}
                      onClick={() => setSelectedPrice(price)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        selectedPrice === price
                          ? 'bg-blue-50 text-blue-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {price}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 메인 콘텐츠 */}
          <div className="flex-1">
            {/* 상단 컨트롤 */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  {selectedCategory === '전체' ? '모든 강의' : `${selectedCategory} 강의`}
                </h1>
                <p className="text-gray-600">
                  총 <span className="font-semibold text-blue-600">{filteredCourses.length}개</span>의 강의를 찾았습니다
                </p>
              </div>

              <div className="flex items-center space-x-4">
                {/* 정렬 */}
                <div className="relative">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="appearance-none bg-white border border-gray-200 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="인기순">인기순</option>
                    <option value="평점순">평점순</option>
                    <option value="최신순">최신순</option>
                    <option value="가격 낮은순">가격 낮은순</option>
                    <option value="가격 높은순">가격 높은순</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>

                {/* 뷰 모드 */}
                <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                  >
                    <Grid className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                  >
                    <List className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* 필터 태그 */}
            {(selectedCategory !== '전체' || selectedLevel !== '전체' || selectedPrice !== '전체' || searchTerm) && (
              <div className="flex items-center gap-2 mb-6 flex-wrap">
                <span className="text-sm text-gray-600">적용된 필터:</span>
                
                {searchTerm && (
                  <div className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                    <span>검색: "{searchTerm}"</span>
                    <button 
                      onClick={() => setSearchTerm('')}
                      className="ml-2 hover:bg-blue-200 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}
                
                {selectedCategory !== '전체' && (
                  <div className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                    <span>{selectedCategory}</span>
                    <button 
                      onClick={() => setSelectedCategory('전체')}
                      className="ml-2 hover:bg-blue-200 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}
                
                {selectedLevel !== '전체' && (
                  <div className="flex items-center bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                    <span>{selectedLevel}</span>
                    <button 
                      onClick={() => setSelectedLevel('전체')}
                      className="ml-2 hover:bg-green-200 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}
                
                {selectedPrice !== '전체' && (
                  <div className="flex items-center bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                    <span>{selectedPrice}</span>
                    <button 
                      onClick={() => setSelectedPrice('전체')}
                      className="ml-2 hover:bg-purple-200 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* 강의 목록 */}
            {filteredCourses.length === 0 ? (
              <div className="text-center py-16">
                <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">검색 결과가 없습니다</h3>
                <p className="text-gray-600 mb-6">다른 검색어나 필터를 시도해보세요</p>
                <button
                  onClick={resetFilters}
                  className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors font-medium"
                >
                  모든 강의 보기
                </button>
              </div>
            ) : (
              <div className={`${
                viewMode === 'grid' 
                  ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
                  : 'space-y-6'
              }`}>
                {filteredCourses.map((course) => 
                  viewMode === 'grid' ? (
                    <CourseCard key={course.id} course={course} />
                  ) : (
                    <CourseListItem key={course.id} course={course} />
                  )
                )}
              </div>
            )}

            {/* 더 보기 버튼 */}
            {filteredCourses.length > 0 && (
              <div className="text-center mt-12">
                <button className="bg-white border border-gray-200 text-gray-700 px-8 py-4 rounded-xl hover:bg-gray-50 transition-colors font-medium">
                  더 많은 강의 보기
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 모바일 필터 버튼 */}
      <div className="fixed bottom-6 right-6 lg:hidden">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
        >
          <Filter className="w-6 h-6" />
        </button>
      </div>

      {/* 모바일 필터 모달 */}
      {showFilters && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 lg:hidden">
          <div className="absolute right-0 top-0 h-full w-80 bg-white p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-gray-900">필터</h3>
              <button 
                onClick={() => setShowFilters(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 모바일 필터 내용 (사이드바와 동일) */}
            <div className="space-y-6">
              {/* 카테고리 */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">카테고리</h4>
                <div className="space-y-2">
                  {categories.map((category) => (
                    <button
                      key={category.name}
                      onClick={() => setSelectedCategory(category.name)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center justify-between ${
                        selectedCategory === category.name
                          ? 'bg-blue-50 text-blue-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <span>{category.name}</span>
                      <span className={`text-sm ${selectedCategory === category.name ? 'text-blue-500' : 'text-gray-400'}`}>
                        {category.count}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* 난이도 */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">난이도</h4>
                <div className="space-y-2">
                  {['전체', '초급', '중급', '고급'].map((level) => (
                    <button
                      key={level}
                      onClick={() => setSelectedLevel(level)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        selectedLevel === level
                          ? 'bg-blue-50 text-blue-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              {/* 가격 */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">가격</h4>
                <div className="space-y-2">
                  {['전체', '무료', '50000원 이하', '50000-100000원', '100000원 이상'].map((price) => (
                    <button
                      key={price}
                      onClick={() => setSelectedPrice(price)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        selectedPrice === price
                          ? 'bg-blue-50 text-blue-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {price}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* 모바일 필터 하단 버튼 */}
            <div className="mt-8 space-y-3">
              <button
                onClick={resetFilters}
                className="w-full bg-gray-100 text-gray-700 py-3 rounded-xl font-medium hover:bg-gray-200 transition-colors"
              >
                필터 초기화
              </button>
              <button
                onClick={() => setShowFilters(false)}
                className="w-full bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 transition-colors"
              >
                강의 보기 ({filteredCourses.length}개)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseListPage;