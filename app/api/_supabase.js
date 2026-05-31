import { createClient } from "@supabase/supabase-js";

export function getSupabase() {
  const url = process.env.SUPABASE_URL || "https://onhfzpxxehumxmnvkxud.supabase.co";
  const key = process.env.SUPABASE_ANON_KEY || "sb_publishable_eqOx34s8pYSS31I7aB55Yg_9JaZdfcS";
  if (!url || !key) {
    throw new Error("Missing SUPABASE_URL or SUPABASE_ANON_KEY");
  }
  return createClient(url, key, {
    auth: { persistSession: false },
  });
}

export function expectedToken(studentCode) {
  const accessCode = process.env.STUDENT_ACCESS_CODE || "qigong2026";
  return Buffer.from(`${studentCode}:${accessCode}`).toString("base64url");
}

export function assertStudentToken(request, studentCode) {
  const token = request.headers.get("x-student-token") || "";
  if (!studentCode || token !== expectedToken(studentCode)) {
    return false;
  }
  return true;
}
