import { NextResponse } from "next/server";
import { assertStudentToken, getSupabase } from "../_supabase";

function assignmentNumber(studentCode) {
  const number = Number(String(studentCode || "").replace("STU", ""));
  return Number.isFinite(number) ? number : 0;
}

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const studentCode = searchParams.get("student_code") || "";
  if (!assertStudentToken(request, studentCode)) {
    return NextResponse.json({ error: "登录已失效，请重新登录" }, { status: 401 });
  }

  const assignee = assignmentNumber(studentCode);
  const supabase = getSupabase();
  const { data: videos, error } = await supabase
    .from("coding_videos")
    .select("*")
    .or(`primary_student.eq.${assignee},double_student.eq.${assignee}`)
    .order("priority", { ascending: true });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const videoIds = (videos || []).map((video) => video.video_id);
  let submissions = [];
  if (videoIds.length > 0) {
    const { data: existing, error: submissionError } = await supabase
      .from("coding_submissions")
      .select("*")
      .eq("student_code", studentCode)
      .in("video_id", videoIds);
    if (submissionError) {
      return NextResponse.json({ error: submissionError.message }, { status: 500 });
    }
    submissions = existing || [];
  }
  const byVideo = new Map(submissions.map((submission) => [submission.video_id, submission]));
  const tasks = (videos || []).map((video) => ({
    ...video,
    task_role: video.primary_student === assignee ? "primary" : "double_check",
    my_submission: byVideo.get(video.video_id) || null,
  }));

  return NextResponse.json({ tasks });
}
