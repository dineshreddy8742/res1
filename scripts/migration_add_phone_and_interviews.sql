-- migration_add_phone_and_interviews.sql
-- Run this script in the Supabase SQL Editor

-- 1. Add phone_number to users table if not exists
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS phone_number TEXT;

-- 2. Create ai_interviews table
CREATE TABLE IF NOT EXISTS public.ai_interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    user_name TEXT,
    phone_number TEXT,
    resume_id TEXT,
    interview_date TEXT,
    interview_time TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create system_settings table
CREATE TABLE IF NOT EXISTS public.system_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Seed system settings default value
INSERT INTO public.system_settings (key, value) 
VALUES ('ai_interview_service', 'active') 
ON CONFLICT (key) DO NOTHING;
