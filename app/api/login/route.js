import { NextResponse } from "next/server";
import { expectedToken } from "../_supabase";

const validCodes = new Set(Array.from({ length: 10 }, (_, i) => `STU${String(i + 1).padStart(2, "0")}`));

export async function POST(request) {
  const body = await request.json();
  const studentName = String(body.student_name || "").trim();
  const studentCode = String(body.student_code || "").trim();
  const accessCode = String(body.access_code || "").trim();
  const expectedAccessCode = process.env.STUDENT_ACCESS_CODE || "qigong2026";

  if (!studentName) {
    return NextResponse.json({ error: "请填写姓名" }, { status: 400 });
  }
  if (!validCodes.has(studentCode)) {
    return NextResponse.json({ error: "学生编号应为 STU01-STU10" }, { status: 400 });
  }
  if (accessCode !== expectedAccessCode) {
    return NextResponse.json({ error: "访问口令不正确" }, { status: 401 });
  }

  return NextResponse.json({
    session: {
      student_name: studentName,
      student_code: studentCode,
      token: expectedToken(studentCode),
    },
  });
}
