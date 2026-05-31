import { NextResponse } from "next/server";
import { assertStudentToken, getSupabase } from "../_supabase";

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const studentCode = searchParams.get("student_code") || "";
  const token = request.headers.get("x-student-token") || "";
  if (!assertStudentToken(request, studentCode)) {
    return NextResponse.json({ error: "登录已失效，请重新登录" }, { status: 401 });
  }

  const supabase = getSupabase();
  const { data: tasks, error } = await supabase.rpc("get_qigong_coding_tasks", {
    p_student_code: studentCode,
    p_token: token,
    p_access_code: process.env.STUDENT_ACCESS_CODE || "qigong2026",
  });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ tasks: tasks || [] });
}
