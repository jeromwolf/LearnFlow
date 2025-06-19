import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, SkipBack, SkipForward, Settings, BookOpen, MessageCircle, FileText, User, Star, ThumbsUp, ThumbsDown, Download, Share2, ChevronRight, ChevronLeft, Check, Lock, Clock, Users } from 'lucide-react';

const CourseLearningPage = () => {
  // 비디오 관련 상태
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // UI 상태
  const [activeTab, setActiveTab] = useState('curriculum'); // curriculum, qa, notes, materials
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [selectedVideo, setSelectedVideo] = useState(0);
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);
  const [note, setNote] = useState('');
  const [showNoteForm, setShowNoteForm] = useState(false);
  
  const videoRef = useRef(null);
  const progressRef = useRef(null);

  // 강의 데이터
  const courseData = {
    title: "React 완벽 마스터: 초급부터 고급까지",
    instructor: {
      name: "김개발",
      title: "Senior Frontend Developer",
      avatar: "/api/placeholder/50/50",
      rating: 4.9,
      students: 15432
    },
    totalDuration: "12시간 30분",
    totalLessons: 45,
    completedLessons: 12,
    progress: 27,
    sections: [
      {
        id: 1,
        title: "React 기초 개념",
        duration: "2시간 45분",
        lessons: [
          { id: 1, title: "React 소개 및 환경 설정", duration: "15:30", completed: true, current: false },
          { id: 2, title: "JSX 문법과 컴포넌트", duration: "22:15", completed: true, current: false },
          { id: 3, title: "Props와 State 이해하기", duration: "28:45", completed: true, current: true },
          { id: 4, title: "이벤트 핸들링", duration: "18:20", completed: false, current: false },
          { id: 5, title: "조건부 렌더링", duration: "20:30", completed: false, current: false }
        ]
      },
      {
        id: 2,
        title: "컴포넌트 심화",
        duration: "3시간 20분",
        lessons: [
          { id: 6, title: "함수형 컴포넌트와 클래스형 컴포넌트", duration: "25:45", completed: false, current: false },
          { id: 7, title: "생명주기 메서드", duration: "30:20", completed: false, current: false },
          { id: 8, title: "컴포넌트 스타일링", duration: "22:15", completed: false, current: false, locked: true },
          { id: 9, title: "컴포넌트 최적화", duration: "35:40", completed: false, current: false, locked: true }
        ]
      },
      {
        id: 3,
        title: "React Hooks",
        duration: "4시간 15분",
        lessons: [
          { id: 10, title: "useState Hook", duration: "28:30", completed: false, current: false, locked: true },
          { id: 11, title: "useEffect Hook", duration: "35:20", completed: false, current: false, locked: true },
          { id: 12, title: "useContext Hook", duration: "25:45", completed: false, current: false, locked: true },
          { id: 13, title: "Custom Hooks 만들기", duration: "40:15", completed: false, current: false, locked: true }
        ]
      }
    ]
  };

  const qnaData = [
    {
      id: 1,
      user: "학습자A",
      avatar: "/api/placeholder/40/40",
      question: "Props와 State의 차이점이 정확히 뭔가요?",
      answer: "Props는 부모 컴포넌트에서 자식 컴포넌트로 전달되는 읽기 전용 데이터이고, State는 컴포넌트 내부에서 관리되는 변경 가능한 데이터입니다.",
      timestamp: "2시간 전",
      likes: 12,
      isAnswered: true,
      instructor: true
    },
    {
      id: 2,
      user: "학습자B",
      avatar: "/api/placeholder/40/40",
      question: "이벤트 핸들링에서 this 바인딩은 언제 필요한가요?",
      answer: "",
      timestamp: "30분 전",
      likes: 3,
      isAnswered: false,
      instructor: false
    }
  ];

  const notes = [
    {
      id: 1,
      time: "05:23",
      content: "JSX는 JavaScript XML의 약자로, React에서 UI를 작성하는 문법",
      timestamp: "2024-12-10 14:30"
    },
    {
      id: 2,
      time: "12:45",
      content: "컴포넌트는 재사용 가능한 UI 조각. function 또는 class로 정의",
      timestamp: "2024-12-10 14:35"
    }
  ];

  // 비디오 제어 함수들
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleProgressClick = (e) => {
    if (progressRef.current && videoRef.current) {
      const rect = progressRef.current.getBoundingClientRect();
      const pos = (e.clientX - rect.left) / rect.width;
      const newTime = pos * duration;
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  const changePlaybackRate = (rate) => {
    setPlaybackRate(rate);
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
    }
    setShowSpeedMenu(false);
  };

  const skipTime = (seconds) => {
    if (videoRef.current) {
      videoRef.current.currentTime += seconds;
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // 노트 추가
  const addNote = () => {
    if (note.trim()) {
      // 실제로는 서버에 저장
      console.log('Adding note:', {
        time: formatTime(currentTime),
        content: note,
        timestamp: new Date().toISOString()
      });
      setNote('');
      setShowNoteForm(false);
    }
  };

  useEffect(() => {
    let timeout;
    const handleMouseMove = () => {
      setShowControls(true);
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        if (isPlaying) {
          setShowControls(false);
        }
      }, 3000);
    };

    const videoElement = videoRef.current;
    if (videoElement) {
      videoElement.addEventListener('mousemove', handleMouseMove);
      return () => {
        videoElement.removeEventListener('mousemove', handleMouseMove);
        clearTimeout(timeout);
      };
    }
  }, [isPlaying]);

  return (
    <div className="min-h-screen bg-gray-900 flex">
      {/* 사이드바 */}
      <div className={`bg-white transition-all duration-300 ${isSidebarOpen ? 'w-96' : 'w-0'} overflow-hidden flex-shrink-0`}>
        <div className="h-full flex flex-col">
          {/* 사이드바 헤더 */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">강의 콘텐츠</h2>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="p-2 hover:bg-gray-100 rounded-lg lg:hidden"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            </div>
            
            {/* 진도율 */}
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>진도율</span>
                <span>{courseData.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${courseData.progress}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>{courseData.completedLessons}/{courseData.totalLessons} 완료</span>
                <span>{courseData.totalDuration}</span>
              </div>
            </div>

            {/* 탭 버튼 */}
            <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('curriculum')}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'curriculum' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                커리큘럼
              </button>
              <button
                onClick={() => setActiveTab('qa')}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'qa' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Q&A
              </button>
              <button
                onClick={() => setActiveTab('notes')}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'notes' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                노트
              </button>
            </div>
          </div>

          {/* 사이드바 콘텐츠 */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'curriculum' && (
              <div className="p-4">
                {courseData.sections.map((section, sectionIndex) => (
                  <div key={section.id} className="mb-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">{section.title}</h3>
                      <span className="text-xs text-gray-500">{section.duration}</span>
                    </div>
                    
                    <div className="space-y-2">
                      {section.lessons.map((lesson, lessonIndex) => (
                        <div
                          key={lesson.id}
                          onClick={() => !lesson.locked && setSelectedVideo(lesson.id)}
                          className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${
                            lesson.current
                              ? 'bg-blue-50 border border-blue-200'
                              : lesson.locked
                              ? 'bg-gray-50 cursor-not-allowed'
                              : 'hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex-shrink-0 mr-3">
                            {lesson.locked ? (
                              <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
                                <Lock className="w-3 h-3 text-gray-500" />
                              </div>
                            ) : lesson.completed ? (
                              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                                <Check className="w-3 h-3 text-white" />
                              </div>
                            ) : lesson.current ? (
                              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                                <Play className="w-3 h-3 text-white" />
                              </div>
                            ) : (
                              <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center">
                                <span className="text-xs font-medium text-gray-600">{lessonIndex + 1}</span>
                              </div>
                            )}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium truncate ${
                              lesson.locked ? 'text-gray-400' : lesson.current ? 'text-blue-600' : 'text-gray-900'
                            }`}>
                              {lesson.title}
                            </p>
                            <p className="text-xs text-gray-500">{lesson.duration}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'qa' && (
              <div className="p-4">
                <div className="mb-4">
                  <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                    질문하기
                  </button>
                </div>
                
                <div className="space-y-4">
                  {qnaData.map((qa) => (
                    <div key={qa.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start space-x-3 mb-3">
                        <img src={qa.avatar} alt={qa.user} className="w-8 h-8 rounded-full" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-sm font-medium text-gray-900">{qa.user}</span>
                            <span className="text-xs text-gray-500">{qa.timestamp}</span>
                          </div>
                          <p className="text-sm text-gray-700">{qa.question}</p>
                        </div>
                      </div>
                      
                      {qa.isAnswered && (
                        <div className="mt-3 pl-11 border-l-2 border-blue-200">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-sm font-medium text-blue-600">강사 답변</span>
                          </div>
                          <p className="text-sm text-gray-700">{qa.answer}</p>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                        <div className="flex items-center space-x-4">
                          <button className="flex items-center space-x-1 text-gray-500 hover:text-blue-600 transition-colors">
                            <ThumbsUp className="w-4 h-4" />
                            <span className="text-xs">{qa.likes}</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'notes' && (
              <div className="p-4">
                <div className="mb-4">
                  <button
                    onClick={() => setShowNoteForm(!showNoteForm)}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                  >
                    노트 추가 ({formatTime(currentTime)})
                  </button>
                </div>

                {showNoteForm && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <textarea
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                      placeholder="이 시점에서 중요한 내용을 메모하세요..."
                      className="w-full p-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-green-500"
                      rows="3"
                    />
                    <div className="flex space-x-2 mt-3">
                      <button
                        onClick={addNote}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                      >
                        저장
                      </button>
                      <button
                        onClick={() => setShowNoteForm(false)}
                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors text-sm"
                      >
                        취소
                      </button>
                    </div>
                  </div>
                )}
                
                <div className="space-y-3">
                  {notes.map((note) => (
                    <div key={note.id} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-blue-600">{note.time}</span>
                        <span className="text-xs text-gray-500">{note.timestamp}</span>
                      </div>
                      <p className="text-sm text-gray-700">{note.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 메인 비디오 영역 */}
      <div className="flex-1 flex flex-col">
        {/* 비디오 플레이어 */}
        <div className="relative bg-black flex-1 group">
          <video
            ref={videoRef}
            className="w-full h-full object-contain"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            poster="/api/placeholder/800/450"
          >
            <source src="/api/placeholder/video" type="video/mp4" />
          </video>

          {/* 비디오 컨트롤 */}
          <div className={`absolute inset-0 bg-black bg-opacity-30 transition-opacity duration-300 ${
            showControls || !isPlaying ? 'opacity-100' : 'opacity-0'
          }`}>
            {/* 중앙 재생 버튼 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <button
                onClick={togglePlay}
                className={`bg-black bg-opacity-50 text-white p-4 rounded-full hover:bg-opacity-70 transition-all transform ${
                  isPlaying ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
                }`}
              >
                <Play className="w-8 h-8" />
              </button>
            </div>

            {/* 상단 컨트롤 */}
            <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black to-transparent">
              <div className="flex items-center justify-between text-white">
                <div className="flex items-center space-x-4">
                  {!isSidebarOpen && (
                    <button
                      onClick={() => setIsSidebarOpen(true)}
                      className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  )}
                  <h3 className="font-medium">Props와 State 이해하기</h3>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors">
                    <Share2 className="w-5 h-5" />
                  </button>
                  <button className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors">
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* 하단 컨트롤 */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black to-transparent">
              {/* 진행바 */}
              <div className="mb-4">
                <div 
                  ref={progressRef}
                  onClick={handleProgressClick}
                  className="w-full h-1 bg-white bg-opacity-30 rounded-full cursor-pointer group"
                >
                  <div 
                    className="h-full bg-blue-600 rounded-full relative transition-all duration-200 group-hover:h-2"
                    style={{ width: `${(currentTime / duration) * 100}%` }}
                  >
                    <div className="absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-blue-600 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-white">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={togglePlay}
                    className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  >
                    {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                  </button>
                  
                  <button
                    onClick={() => skipTime(-10)}
                    className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  >
                    <SkipBack className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={() => skipTime(10)}
                    className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  >
                    <SkipForward className="w-5 h-5" />
                  </button>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={toggleMute}
                      className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                    >
                      {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                    </button>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={volume}
                      onChange={handleVolumeChange}
                      className="w-20 accent-blue-600"
                    />
                  </div>

                  <span className="text-sm">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </span>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <button
                      onClick={() => setShowSpeedMenu(!showSpeedMenu)}
                      className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors flex items-center space-x-1"
                    >
                      <span className="text-sm">{playbackRate}x</span>
                    </button>
                    
                    {showSpeedMenu && (
                      <div className="absolute bottom-full right-0 mb-2 bg-black bg-opacity-80 rounded-lg p-2 space-y-1">
                        {[0.5, 0.75, 1, 1.25, 1.5, 2].map((rate) => (
                          <button
                            key={rate}
                            onClick={() => changePlaybackRate(rate)}
                            className={`block w-full text-left px-3 py-1 text-sm hover:bg-white hover:bg-opacity-20 rounded ${
                              playbackRate === rate ? 'text-blue-400' : 'text-white'
                            }`}
                          >
                            {rate}x
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  <button
                    onClick={toggleFullscreen}
                    className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  >
                    <Maximize className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 강의 정보 바 */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img src={courseData.instructor.avatar} alt={courseData.instructor.name} className="w-10 h-10 rounded-full" />
              <div>
                <h4 className="font-semibold text-gray-900">{courseData.instructor.name}</h4>
                <p className="text-sm text-gray-600">{courseData.instructor.title}</p>
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-400" />
                  <span>{courseData.instructor.rating}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="w-4 h-4" />
                  <span>{courseData.instructor.students.toLocaleString()}명</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                <ThumbsUp className="w-4 h-4" />
                <span>도움됨</span>
              </button>
              <button className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseLearningPage;