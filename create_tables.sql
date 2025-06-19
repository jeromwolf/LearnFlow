-- course_reviews 테이블 생성
CREATE TABLE IF NOT EXISTS public.course_reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES public.courses(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_course_review UNIQUE (user_id, course_id)
);

-- lesson_completions 테이블 생성
CREATE TABLE IF NOT EXISTS public.lesson_completions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    lesson_id BIGINT NOT NULL REFERENCES public.lessons(id) ON DELETE CASCADE,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_lesson_completion UNIQUE (user_id, lesson_id)
);

-- 테이블 생성 확인을 위한 주석
COMMENT ON TABLE public.course_reviews IS '강의 리뷰를 저장하는 테이블';
COMMENT ON TABLE public.lesson_completions IS '강의 완료 상태를 추적하는 테이블';

-- RLS(행 수준 보안) 활성화
ALTER TABLE public.course_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lesson_completions ENABLE ROW LEVEL SECURITY;
