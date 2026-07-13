export interface Profile {
  name: string;
  gender: string;
  grade: string;
  major: string;
  mbti: string;
  portrait: number;
  survey: { q1: string | null; q2: string | null; q3: string | null };
}

export function defaultProfile(): Profile {
  return {
    name: "",
    gender: "g_x",
    grade: "grade_1",
    major: "maj_ec",
    mbti: "ENFP",
    portrait: 1,
    survey: { q1: null, q2: null, q3: null },
  };
}
