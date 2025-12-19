import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
    // We'll allow it for now but log a warning, user needs to set .env
    console.warn("Supabase keys missing in .env")
}

export const supabase = createClient(supabaseUrl || "", supabaseAnonKey || "")
