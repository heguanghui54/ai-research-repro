import { NextResponse } from "next/server";
import { assertStudentToken, getSupabase } from "../_supabase";

const codingFields = [
  "dominant_frame",
  "body_visibility",
  "body_count",
  "movement_tempo",
  "camera_relation",
  "text_occlusion",
  "breath_cue",
  "mind_cue",
  "qi_meridian_cue",
  "risk_cue",
  "call_to_action",
  "platform_trace",
  "origin_reference",
  "supplement_mode",
  "binary_reversal",
  "recontextualization_scene",
  "visibility_centrality",
  "tempo_discipline",
  "efficacy_tagging",
  "image_trace_strength",
  "media_temporality",
  "cyber_wellness_symbol",
  "meme_density",
  "embodied_dissolution",
];

export async function POST(request) {
  const body = await request.json();
  const studentCode = String(body.student_code || "").trim();
  if (!assertStudentToken(request, studentCode)) {
    return NextResponse.json({ error: "登录已失效，请重新登录" }, { status: 401 });
  }
  const missing = codingFields.filter((field) => !String(body[field] || "").trim());
  if (missing.length > 0) {
    return NextResponse.json({ error: `还有字段未填写：${missing.join(", ")}` }, { status: 400 });
  }
  if (!body.watched) {
    return NextResponse.json({ error: "请先确认已经打开并观看/核验视频" }, { status: 400 });
  }

  const payload = {
    video_id: String(body.video_id || "").trim(),
    student_code: studentCode,
    student_name: String(body.student_name || "").trim(),
    task_role: String(body.task_role || "primary").trim(),
    watched: Boolean(body.watched),
    video_access_status: String(body.video_access_status || "opened").trim(),
    secondary_frames: String(body.secondary_frames || "").trim(),
    trace_markers: String(body.trace_markers || "").trim(),
    notes: String(body.notes || "").trim(),
    updated_at: new Date().toISOString(),
  };
  for (const field of codingFields) payload[field] = String(body[field] || "").trim();

  const supabase = getSupabase();
  const { data, error } = await supabase.rpc("upsert_qigong_coding_submission", {
    p_student_code: studentCode,
    p_token: request.headers.get("x-student-token") || "",
    p_access_code: process.env.STUDENT_ACCESS_CODE || "qigong2026",
    p_payload: payload,
  });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ submission: data });
}
