# -*- coding: utf-8 -*-
"""
다국어(i18n) 데이터 및 헬퍼
  지원 언어 : KR(한국어) · EN(English) · CH(中文/简体) · JP(日本語)
  - current       : 현재 언어 (기본 KR)
  - t(text)       : 스토리 텍스트 번역 (KR 은 원문 그대로)
  - nm(name)      : 화자 이름 번역
  - stat(key)     : 스탯 라벨(내부키→표시명)
  - ui(key, **kw) : UI 문자열 (템플릿 포맷 지원)

원문(한국어)을 키로 사용하며, 등록되지 않은 문자열은 원문으로 폴백한다.
"""

LANGS = ["KR", "EN", "CH", "JP"]          # 상단 국기 표시 순서
LANG_NATIVE = {"KR": "한국어", "EN": "English", "CH": "中文", "JP": "日本語"}
current = "KR"

# 플레이어가 만든 캐릭터 이름 — 설정되면 화자 "나" 대신 이 이름을 표시
player_name = ""


def set_lang(code):
    global current
    if code in LANGS:
        current = code


def set_player_name(name):
    global player_name
    player_name = (name or "").strip()


# ── 화자 이름 ────────────────────────────────────────
NAMES = {
    "나":     {"EN": "Me",        "CH": "我",     "JP": "私"},
    "헨리":   {"EN": "Henry",     "CH": "亨利",   "JP": "ヘンリー"},
    "병사A":  {"EN": "Soldier A", "CH": "士兵A",  "JP": "兵士A"},
    "병사B":  {"EN": "Soldier B", "CH": "士兵B",  "JP": "兵士B"},
    "대니얼": {"EN": "Daniel",    "CH": "丹尼尔", "JP": "ダニエル"},
    "마크":   {"EN": "Mark",      "CH": "马克",   "JP": "マーク"},
    "노병":   {"EN": "Veteran",   "CH": "老兵",   "JP": "老兵"},
    "지휘관": {"EN": "Commander", "CH": "指挥官", "JP": "指揮官"},
    "병사":   {"EN": "Soldier",   "CH": "士兵",   "JP": "兵士"},
    "짐":     {"EN": "Jim",       "CH": "吉姆",   "JP": "ジム"},
    "부상병": {"EN": "Wounded",   "CH": "伤兵",   "JP": "負傷兵"},
    "윌슨":   {"EN": "Wilson",    "CH": "威尔逊", "JP": "ウィルソン"},
    "의무병": {"EN": "Medic",     "CH": "医护兵", "JP": "衛生兵"},
    # HUD 그룹 헤더
    "Henry":    {"EN": "Henry",  "CH": "亨利",     "JP": "ヘンリー"},
    "플레이어": {"EN": "Player", "CH": "玩家",     "JP": "プレイヤー"},
}

# ── 스탯 라벨 (내부키 기준) ──────────────────────────
STAT = {
    "신뢰":       {"KR": "신뢰도",     "EN": "Trust",    "CH": "信任",     "JP": "信頼"},
    "공감":       {"KR": "공감",       "EN": "Empathy",  "CH": "共情",     "JP": "共感"},
    "인간본능":   {"KR": "인간 본능",  "EN": "Humanity", "CH": "人性本能", "JP": "人間の本能"},
    "사회적역할": {"KR": "사회적 역할","EN": "Duty",     "CH": "社会角色", "JP": "社会的役割"},
    "죄책감":     {"KR": "죄책감",     "EN": "Guilt",    "CH": "罪恶感",   "JP": "罪悪感"},
    "용기":       {"KR": "용기",       "EN": "Courage",  "CH": "勇气",     "JP": "勇気"},
}

# ── UI 문자열 ────────────────────────────────────────
UI = {
    "title_main":  {"KR": "붉은 무공훈장", "EN": "The Red Badge of Courage", "CH": "红色英勇勋章", "JP": "赤い武功章"},
    "menu_credit": {"KR": "원작 · Stephen Crane 『The Red Badge of Courage』",
                    "EN": "Based on Stephen Crane's 'The Red Badge of Courage'",
                    "CH": "原著 · 斯蒂芬·克莱恩《The Red Badge of Courage》",
                    "JP": "原作 · スティーヴン・クレイン『The Red Badge of Courage』"},
    "menu_start":  {"KR": "시작하기", "EN": "Start", "CH": "开始", "JP": "始める"},
    "menu_hint":   {"KR": "TAB 스탯 패널  ·  ↑↓ · Enter 선택  ·  ESC 메뉴",
                    "EN": "TAB Stats  ·  ↑↓ · Enter select  ·  ESC menu",
                    "CH": "TAB 状态面板  ·  ↑↓ · Enter 选择  ·  ESC 菜单",
                    "JP": "TAB ステータス  ·  ↑↓ · Enter 選択  ·  ESC メニュー"},
    # 시작 메뉴 / 이어하기
    "menu_continue": {"KR": "이어하기", "EN": "Continue", "CH": "继续游戏", "JP": "つづきから"},
    "menu_new":      {"KR": "새 이야기", "EN": "New Story", "CH": "新游戏", "JP": "はじめから"},
    "menu_back":     {"KR": "뒤로가기", "EN": "Back", "CH": "返回", "JP": "戻る"},
    # 일시정지 / 설정 메뉴
    "pause_title": {"KR": "일시정지", "EN": "Paused", "CH": "暂停", "JP": "一時停止"},
    "resume":      {"KR": "계속하기", "EN": "Resume", "CH": "继续", "JP": "再開"},
    "save":        {"KR": "저장하기", "EN": "Save", "CH": "保存", "JP": "セーブ"},
    "load":        {"KR": "불러오기", "EN": "Load", "CH": "读取", "JP": "ロード"},
    "to_title":    {"KR": "메인 화면으로", "EN": "Main Menu", "CH": "返回主菜单", "JP": "タイトルへ"},
    "quit":        {"KR": "게임 종료", "EN": "Quit Game", "CH": "退出游戏", "JP": "ゲーム終了"},
    "bgm_vol":     {"KR": "배경음악", "EN": "Music", "CH": "背景音乐", "JP": "BGM"},
    "sfx_vol":     {"KR": "효과음", "EN": "Sound FX", "CH": "音效", "JP": "効果音"},
    "pause_hint":  {"KR": "← → 볼륨 조절  ·  ↑↓ · Enter 선택  ·  ESC 닫기",
                    "EN": "← → Volume  ·  ↑↓ · Enter select  ·  ESC close",
                    "CH": "← → 音量  ·  ↑↓ · Enter 选择  ·  ESC 关闭",
                    "JP": "← → 音量  ·  ↑↓ · Enter 選択  ·  ESC 閉じる"},
    "saved_msg":   {"KR": "저장되었습니다", "EN": "Game saved", "CH": "已保存", "JP": "セーブしました"},
    "loaded_msg":  {"KR": "불러왔습니다", "EN": "Game loaded", "CH": "已读取", "JP": "ロードしました"},
    "no_save":     {"KR": "저장된 게임이 없습니다", "EN": "No saved game", "CH": "没有存档", "JP": "セーブデータがありません"},
    # 대사 로그(백로그)
    "backlog_title": {"KR": "대사 기록", "EN": "Dialogue Log", "CH": "对话记录", "JP": "セリフログ"},
    "backlog_hint":  {"KR": "휠로 스크롤  ·  ESC · 클릭으로 닫기",
                      "EN": "Scroll with wheel  ·  ESC · click to close",
                      "CH": "滚轮滚动  ·  ESC · 点击关闭",
                      "JP": "ホイールでスクロール  ·  ESC · クリックで閉じる"},
    "backlog_empty": {"KR": "아직 기록된 대사가 없습니다", "EN": "No dialogue recorded yet", "CH": "还没有对话记录", "JP": "まだログはありません"},
    "hint_advance":{"KR": "Click / Space bar", "EN": "Click / Space bar", "CH": "点击 / 空格键", "JP": "クリック / スペースキー"},
    "choice_q":    {"KR": "당신의 선택은?", "EN": "What is your choice?", "CH": "你的选择是？", "JP": "あなたの選択は？"},
    "explore_q":   {"KR": "어디를 조사할까?", "EN": "Where will you look?", "CH": "去调查哪里？", "JP": "どこを調べる？"},
    "explore_footer": {"KR": "모두 조사하면 밤이 온다  ·  조사 완료 {done} / {total}",
                       "EN": "Search everywhere for night to fall  ·  {done} / {total} done",
                       "CH": "调查完所有地点，夜晚便会到来  ·  已调查 {done} / {total}",
                       "JP": "すべて調べると夜が来る  ·  調査済み {done} / {total}"},
    "conflict_title":   {"KR": "갈등의 저울", "EN": "Scale of Conflict", "CH": "冲突的天平", "JP": "葛藤の天秤"},
    "conflict_human":   {"KR": "인간으로 살아남기", "EN": "Survive as a Human", "CH": "作为人活下去", "JP": "人間として生き残る"},
    "conflict_soldier": {"KR": "군인으로 살아가기", "EN": "Live as a Soldier", "CH": "作为军人活下去", "JP": "軍人として生きる"},
    "frag_hud":    {"KR": "기억 조각  {n} / {t}", "EN": "Fragments  {n} / {t}", "CH": "记忆碎片  {n} / {t}", "JP": "記憶の欠片  {n} / {t}"},
    # HUD 스탯 그룹 제목 (직관적 분류)
    "grp_relation": {"KR": "헨리와의 관계", "EN": "Bond with Henry", "CH": "与亨利的关系", "JP": "ヘンリーとの絆"},
    "grp_player":   {"KR": "플레이어 능력치", "EN": "Your Traits", "CH": "玩家能力", "JP": "プレイヤー能力"},
    "grp_henry":    {"KR": "헨리의 상태", "EN": "Henry's State", "CH": "亨利的状态", "JP": "ヘンリーの状態"},
    "stat_word":   {"KR": "스탯", "EN": "STATS", "CH": "状态", "JP": "ステータス"},
    "frag_result": {"KR": "기억 조각  {n}/{t}", "EN": "Fragments  {n}/{t}", "CH": "记忆碎片  {n}/{t}", "JP": "記憶の欠片  {n}/{t}"},
    "result_continue": {"KR": "»  클릭하여 계속", "EN": "»  Click to continue", "CH": "»  点击继续", "JP": "»  クリックして続ける"},
    "fq_title":    {"KR": "당신에게 용기란 무엇입니까?", "EN": "What is courage, to you?", "CH": "对你而言，勇气是什么？", "JP": "あなたにとって、勇気とは何ですか？"},
    "fq1":         {"KR": "두려움이 없는 것", "EN": "Having no fear", "CH": "没有恐惧", "JP": "恐怖がないこと"},
    "fq2":         {"KR": "두려움을 이겨내는 것", "EN": "Overcoming fear", "CH": "战胜恐惧", "JP": "恐怖に打ち勝つこと"},
    "fq3":         {"KR": "두려움을 인정하고도 행동하는 것", "EN": "Acting even while admitting fear", "CH": "承认恐惧却依然行动", "JP": "恐怖を認めてなお行動すること"},
    "fq4":         {"KR": "아직 모르겠다", "EN": "I still don't know", "CH": "还不知道", "JP": "まだわからない"},
    "fq_note_end": {"KR": "당신의 대답은 저장되지 않습니다  ·  클릭하면 종료",
                    "EN": "Your answer will not be saved  ·  Click to exit",
                    "CH": "你的回答不会被保存  ·  点击退出",
                    "JP": "あなたの答えは保存されません  ·  クリックで終了"},
    "fq_note":     {"KR": "(선택은 저장되지 않습니다)", "EN": "(Your choice will not be saved)", "CH": "（选择不会被保存）", "JP": "（選択は保存されません）"},
    "frag_toast":  {"KR": "기억 조각 획득 · {name}", "EN": "Fragment obtained · {name}", "CH": "获得记忆碎片 · {name}", "JP": "記憶の欠片を獲得 · {name}"},
    "frag_get":    {"KR": "기억 조각 획득", "EN": "MEMORY FRAGMENT OBTAINED", "CH": "获得记忆碎片", "JP": "記憶の欠片を獲得"},
    "frag_get_hint": {"KR": "클릭하여 계속", "EN": "Click to continue", "CH": "点击继续", "JP": "クリックして続ける"},
    "mono_label":  {"KR": "속마음", "EN": "Inner Voice", "CH": "心声", "JP": "心の声"},
    "placeholder": {"KR": "assets 폴더에 이미지를 넣어 주세요",
                    "EN": "Please place images in the assets folder",
                    "CH": "请将图片放入 assets 文件夹",
                    "JP": "assets フォルダに画像を入れてください"},
    # 엔딩 타이틀(결과 화면)
    "end_TRUE":   {"KR": "TRUE END 「진정한 용기」",       "EN": "TRUE END — True Courage",              "CH": "TRUE END 「真正的勇气」",   "JP": "TRUE END 「本当の勇気」"},
    "end_GOOD":   {"KR": "GOOD END 「앞으로 나아간 사람」", "EN": "GOOD END — The One Who Walked On",     "CH": "GOOD END 「向前迈进的人」", "JP": "GOOD END 「前へ進んだ人」"},
    "end_NORMAL": {"KR": "NORMAL END 「정답 없는 질문」",   "EN": "NORMAL END — A Question Without Answer","CH": "NORMAL END 「没有答案的问题」","JP": "NORMAL END 「答えのない問い」"},
    "end_BAD":    {"KR": "BAD END 「붉은 무공훈장」",       "EN": "BAD END — The Red Badge of Courage",   "CH": "BAD END 「红色英勇勋章」",  "JP": "BAD END 「赤い武功章」"},
    "end_HIDDEN": {"KR": "HIDDEN END 「인간이라는 이름」",  "EN": "HIDDEN END — The Name of Human",       "CH": "HIDDEN END 「名为人类」",  "JP": "HIDDEN END 「人間という名」"},

    # ── 캐릭터 만들기 ──
    "cc_title":   {"KR": "나의 캐릭터 만들기", "EN": "Create Your Character", "CH": "创建你的角色", "JP": "あなたのキャラクターを作る"},
    "cc_subtitle":{"KR": "이 이야기에 참여할 '나'를 설정합니다", "EN": "Set up the 'you' who will enter this story", "CH": "设定将进入这个故事的“你”", "JP": "この物語に入る「あなた」を設定します"},
    "cc_name":    {"KR": "이름", "EN": "Name", "CH": "名字", "JP": "名前"},
    "cc_name_ph": {"KR": "이름을 입력하세요 (최대 {n}자)", "EN": "Enter your name (max {n})", "CH": "请输入名字（最多 {n} 字）", "JP": "名前を入力（最大 {n} 文字）"},
    "cc_gender":  {"KR": "성별", "EN": "Gender", "CH": "性别", "JP": "性別"},
    "cc_age":     {"KR": "나이", "EN": "Age", "CH": "年龄", "JP": "年齢"},
    "cc_grade":   {"KR": "학년", "EN": "Year", "CH": "年级", "JP": "学年"},
    "cc_portrait":{"KR": "초상 선택", "EN": "Choose Portrait", "CH": "选择肖像", "JP": "肖像を選ぶ"},
    "grade_1":    {"KR": "1학년", "EN": "Year 1", "CH": "1年级", "JP": "1年生"},
    "grade_2":    {"KR": "2학년", "EN": "Year 2", "CH": "2年级", "JP": "2年生"},
    "grade_3":    {"KR": "3학년", "EN": "Year 3", "CH": "3年级", "JP": "3年生"},
    "cc_major":   {"KR": "전공", "EN": "Major", "CH": "专业", "JP": "専攻"},
    "cc_mbti":    {"KR": "MBTI", "EN": "MBTI", "CH": "MBTI", "JP": "MBTI"},
    "cc_look":    {"KR": "외형 꾸미기", "EN": "Appearance", "CH": "外形装扮", "JP": "外見の設定"},
    "cc_hair":    {"KR": "머리 스타일", "EN": "Hair", "CH": "发型", "JP": "髪型"},
    "cc_glasses": {"KR": "안경", "EN": "Glasses", "CH": "眼镜", "JP": "メガネ"},
    "cc_band":    {"KR": "헤어밴드", "EN": "Hairband", "CH": "发箍", "JP": "ヘアバンド"},
    "cc_face":    {"KR": "얼굴형", "EN": "Face", "CH": "脸型", "JP": "顔の形"},
    "cc_haircol": {"KR": "머리 색", "EN": "Hair Color", "CH": "发色", "JP": "髪の色"},
    "cc_random":  {"KR": "랜덤", "EN": "Random", "CH": "随机", "JP": "ランダム"},
    "cc_next":    {"KR": "다음  ›", "EN": "Next  ›", "CH": "下一步  ›", "JP": "次へ  ›"},
    "cc_prev":    {"KR": "‹  이전", "EN": "‹  Back", "CH": "‹  上一步", "JP": "‹  戻る"},
    "cc_start":   {"KR": "이 캐릭터로 시작", "EN": "Start with this character", "CH": "以此角色开始", "JP": "このキャラで始める"},
    "cc_need_name": {"KR": "이름을 입력해 주세요", "EN": "Please enter a name", "CH": "请输入名字", "JP": "名前を入力してください"},
    "cc_hint":    {"KR": "클릭하여 선택  ·  이름 칸을 눌러 입력  ·  Enter 다음",
                   "EN": "Click to choose  ·  click the name box to type  ·  Enter next",
                   "CH": "点击选择  ·  点名字框输入  ·  Enter 下一步",
                   "JP": "クリックで選択  ·  名前欄をクリックで入力  ·  Enter 次へ"},
    "opt_on":     {"KR": "있음", "EN": "On", "CH": "有", "JP": "あり"},
    "opt_off":    {"KR": "없음", "EN": "Off", "CH": "无", "JP": "なし"},
    "g_m":  {"KR": "남", "EN": "Male", "CH": "男", "JP": "男"},
    "g_f":  {"KR": "여", "EN": "Female", "CH": "女", "JP": "女"},
    "g_x":  {"KR": "선택 안 함", "EN": "Prefer not", "CH": "不选择", "JP": "回答しない"},
    "age_h1": {"KR": "고1", "EN": "10th gr.", "CH": "高一", "JP": "高1"},
    "age_h2": {"KR": "고2", "EN": "11th gr.", "CH": "高二", "JP": "高2"},
    "age_h3": {"KR": "고3", "EN": "12th gr.", "CH": "高三", "JP": "高3"},
    "age_20": {"KR": "20대", "EN": "20s", "CH": "20多岁", "JP": "20代"},
    "age_30": {"KR": "30대", "EN": "30s", "CH": "30多岁", "JP": "30代"},
    "age_40": {"KR": "40대", "EN": "40s", "CH": "40多岁", "JP": "40代"},
    "age_50": {"KR": "50대", "EN": "50s", "CH": "50多岁", "JP": "50代"},
    "age_60": {"KR": "60대", "EN": "60s", "CH": "60多岁", "JP": "60代"},
    "maj_ec": {"KR": "영중", "EN": "Eng-Chi", "CH": "英中", "JP": "英中"},
    "maj_ej": {"KR": "영일", "EN": "Eng-Jpn", "CH": "英日", "JP": "英日"},
    "maj_ch": {"KR": "중국어", "EN": "Chinese", "CH": "中文", "JP": "中国語"},
    "maj_jp": {"KR": "일본어", "EN": "Japanese", "CH": "日语", "JP": "日本語"},
    "face_round":  {"KR": "둥근형", "EN": "Round", "CH": "圆形", "JP": "丸型"},
    "face_square": {"KR": "각진형", "EN": "Square", "CH": "方形", "JP": "四角"},

    # ── 성향 설문 (사전) ──
    "sv_title":  {"KR": "나의 성향 테스트", "EN": "My Tendency Test", "CH": "我的倾向测试", "JP": "わたしの傾向テスト"},
    "sv_intro":  {"KR": "게임 전, 가벼운 질문 3가지. 정답은 없습니다.",
                  "EN": "Three light questions before we begin. There are no right answers.",
                  "CH": "开始前的三个小问题。没有标准答案。",
                  "JP": "始める前に、軽い3つの質問。正解はありません。"},
    "sv_pick":   {"KR": "A 와 B 중 하나를 고르세요", "EN": "Choose A or B", "CH": "请在 A 与 B 中选择", "JP": "A か B を選んでください"},
    "sv_progress": {"KR": "질문 {i} / {n}", "EN": "Question {i} / {n}", "CH": "问题 {i} / {n}", "JP": "質問 {i} / {n}"},
    "q1_t": {"KR": "당신은 학급 반장입니다. 평소 성실하지만 오늘따라 몸이 아파 지각한 친구가 있습니다. 원칙대로라면 예외 없이 벌점을 줘야 합니다. 당신의 선택은?",
             "EN": "You are the class monitor. A usually diligent friend is late today because they're ill. By the rules, you must give a penalty with no exception. Your choice?",
             "CH": "你是班长。一位平时认真的朋友今天因身体不适而迟到。按规定必须一视同仁地记过。你的选择是？",
             "JP": "あなたは学級委員長。普段は真面目な友人が、今日は体調が悪くて遅刻しました。原則では例外なく罰点を与えるべきです。あなたの選択は？"},
    "q1_a": {"KR": "원칙은 원칙이다. 규칙대로 벌점을 준다.", "EN": "Rules are rules. Give the penalty.", "CH": "原则就是原则，照规矩记过。", "JP": "原則は原則。規則どおり罰点を与える。"},
    "q1_b": {"KR": "친구의 사정을 이해하고 이번 한 번만 눈감아 준다.", "EN": "Understand their situation and let it slide just this once.", "CH": "体谅朋友的处境，这一次睁一只眼闭一只眼。", "JP": "友人の事情を汲んで、今回だけ見逃す。"},
    "q2_t": {"KR": "나의 치명적 실수를 아무도 모릅니다. 조용히 덮으면 모두가 나를 칭송하지만, 솔직히 고백하면 큰 질타를 받습니다. 당신의 선택은?",
             "EN": "No one knows your fatal mistake. Bury it quietly and everyone praises you; confess honestly and you face harsh blame. Your choice?",
             "CH": "没有人知道你的致命失误。悄悄掩盖，众人便会称赞你；如实坦白，则会遭到严厉指责。你的选择是？",
             "JP": "あなたの致命的なミスを誰も知りません。黙って隠せば皆に称賛され、正直に告白すれば激しく責められます。あなたの選択は？"},
    "q2_a": {"KR": "비난을 받더라도 솔직하게 진실을 밝힌다.", "EN": "Tell the truth honestly, even if blamed.", "CH": "即使被指责，也如实说出真相。", "JP": "非難されても正直に真実を明かす。"},
    "q2_b": {"KR": "조용히 묻어두고 칭찬과 평판을 유지한다.", "EN": "Bury it quietly and keep the praise and reputation.", "CH": "悄悄掩盖，维持赞誉与名声。", "JP": "静かに隠し、称賛と評判を保つ。"},
    "q3_t": {"KR": "가장 중요한 기말고사 전날 새벽, 친한 친구가 심각한 고민으로 울며 전화했습니다. 내일 시험이 입시를 좌우합니다. 당신의 선택은?",
             "EN": "The dawn before your most important final exam, a close friend calls in tears over a serious worry. Tomorrow's exam could decide your future. Your choice?",
             "CH": "最重要的期末考前一天凌晨，好友因严重烦恼哭着打来电话。明天的考试将左右你的升学。你的选择是？",
             "JP": "最も大切な期末試験の前夜、親友が深刻な悩みで泣きながら電話してきました。明日の試験は進路を左右します。あなたの選択は？"},
    "q3_a": {"KR": "내일 시험이 더 중요하므로, 미안하지만 내일 이야기하자고 한다.", "EN": "Tomorrow's exam matters more — apologize and say let's talk tomorrow.", "CH": "明天的考试更重要，抱歉地说明天再聊。", "JP": "明日の試験が大事だから、悪いけど明日話そうと言う。"},
    "q3_b": {"KR": "내 성적이 떨어질 각오를 하더라도, 친구의 이야기를 끝까지 들어준다.", "EN": "Even at the cost of my grades, listen to my friend to the end.", "CH": "哪怕成绩下滑，也把朋友的话听到最后。", "JP": "成績が下がる覚悟でも、友人の話を最後まで聞く。"},

    # ── 교차 분석 ──
    "an_title":  {"KR": "성향 × 선택 교차 분석", "EN": "Tendency × Choices — Cross Analysis", "CH": "倾向 × 选择 交叉分析", "JP": "傾向 × 選択 クロス分析"},
    "an_profile":{"KR": "{name}  ·  {gender} · {age} · {major} · {mbti}",
                  "EN": "{name}  ·  {gender} · {age} · {major} · {mbti}",
                  "CH": "{name}  ·  {gender} · {age} · {major} · {mbti}",
                  "JP": "{name}  ·  {gender} · {age} · {major} · {mbti}"},
    "an_profile_rest": {"KR": "· {gender} · {age} · {major} · {mbti}",
                        "EN": "· {gender} · {age} · {major} · {mbti}",
                        "CH": "· {gender} · {age} · {major} · {mbti}",
                        "JP": "· {gender} · {age} · {major} · {mbti}"},
    "an_ending": {"KR": "도달한 엔딩", "EN": "Ending reached", "CH": "抵达的结局", "JP": "到達したエンディング"},
    "an_scale":  {"KR": "갈등의 저울", "EN": "Scale of Conflict", "CH": "冲突的天平", "JP": "葛藤の天秤"},
    "an_pre":    {"KR": "사전 성향", "EN": "Pre-survey", "CH": "事前倾向", "JP": "事前の傾向"},
    "an_ingame": {"KR": "게임 속 결과", "EN": "In-game result", "CH": "游戏中的结果", "JP": "ゲーム内の結果"},
    "an_match":  {"KR": "예측과 일치", "EN": "Matches prediction", "CH": "与预测一致", "JP": "予測と一致"},
    "an_diff":   {"KR": "예측과 다른 반전", "EN": "A reversal", "CH": "出现反转", "JP": "予測と異なる反転"},
    "an_q1dim":  {"KR": "원칙 vs 공감", "EN": "Principle vs Empathy", "CH": "原则 vs 共情", "JP": "原則 vs 共感"},
    "an_q2dim":  {"KR": "가짜 명예 vs 진정한 용기", "EN": "False Honor vs True Courage", "CH": "虚假荣誉 vs 真正勇气", "JP": "偽りの名誉 vs 本当の勇気"},
    "an_q3dim":  {"KR": "개인의 안위 vs 이타심", "EN": "Self vs Altruism", "CH": "个人安危 vs 利他", "JP": "自己の安寧 vs 利他"},
    "an_q1A":    {"KR": "원칙(군인)을 택함", "EN": "chose principle (soldier)", "CH": "选择原则（军人）", "JP": "原則（軍人）を選択"},
    "an_q1B":    {"KR": "공감(인간)을 택함", "EN": "chose empathy (human)", "CH": "选择共情（人）", "JP": "共感（人間）を選択"},
    "an_q2A":    {"KR": "진실·용기를 택함", "EN": "chose truth & courage", "CH": "选择真相与勇气", "JP": "真実・勇気を選択"},
    "an_q2B":    {"KR": "명예 유지를 택함", "EN": "chose to keep honor", "CH": "选择维持名誉", "JP": "名誉維持を選択"},
    "an_q3A":    {"KR": "개인의 안위를 택함", "EN": "chose self-interest", "CH": "选择个人安危", "JP": "自己の安寧を選択"},
    "an_q3B":    {"KR": "이타·희생을 택함", "EN": "chose altruism", "CH": "选择利他与牺牲", "JP": "利他・犠牲を選択"},
    "an_q1meas": {"KR": "게임에서 '군인' {s} · '인간' {h} » {lean} 쪽이 더 무거움",
                  "EN": "In game: soldier {s} · human {h} » leaned toward {lean}",
                  "CH": "游戏中：军人 {s} · 人 {h} » 更偏向 {lean}",
                  "JP": "ゲーム内：軍人 {s} · 人間 {h} » {lean} 側が重い"},
    "an_q2meas": {"KR": "용기 {c} · 죄책감 {g} · 엔딩 {end}",
                  "EN": "Courage {c} · Guilt {g} · Ending {end}",
                  "CH": "勇气 {c} · 罪恶感 {g} · 结局 {end}",
                  "JP": "勇気 {c} · 罪悪感 {g} · エンディング {end}"},
    "an_q3meas": {"KR": "인간 본능 {i} · 공감 {e} » {lean} 쪽이 강함",
                  "EN": "Instinct {i} · Empathy {e} » stronger in {lean}",
                  "CH": "人性本能 {i} · 共情 {e} » {lean} 更强",
                  "JP": "本能 {i} · 共感 {e} » {lean} が強い"},
    "an_lean_s": {"KR": "군인", "EN": "soldier", "CH": "军人", "JP": "軍人"},
    "an_lean_h": {"KR": "인간", "EN": "human", "CH": "人", "JP": "人間"},
    "an_lean_i": {"KR": "본능", "EN": "instinct", "CH": "本能", "JP": "本能"},
    "an_lean_e": {"KR": "공감", "EN": "empathy", "CH": "共情", "JP": "共感"},
    "an_summary_title": {"KR": "종합 리포트", "EN": "Overall Report", "CH": "综合报告", "JP": "総合レポート"},
    "an_sum_consistent": {"KR": "당신은 사전 성향과 게임 속 선택이 대체로 '일관'되었습니다. 신념이 위기 상황에서도 흔들리지 않는 유형입니다.",
                          "EN": "Your pre-survey tendencies and in-game choices were largely 'consistent'. Your convictions held steady even under pressure.",
                          "CH": "你的事前倾向与游戏中的选择大体'一致'。属于在危机中信念也不动摇的类型。",
                          "JP": "あなたの事前傾向とゲーム内の選択はおおむね「一貫」していました。危機でも信念が揺らがないタイプです。"},
    "an_sum_mixed":      {"KR": "당신은 사전 성향과 게임 속 선택 사이에 '반전'이 있었습니다. 극한 상황이 평소의 신념과 다른 선택을 이끌어냈습니다.",
                          "EN": "There were 'reversals' between your survey tendencies and in-game choices. Extreme situations drew out choices different from your usual beliefs.",
                          "CH": "你的事前倾向与游戏选择之间出现了'反转'。极端处境引出了与平日信念不同的选择。",
                          "JP": "事前傾向とゲーム内の選択に「反転」がありました。極限状況が普段の信念と異なる選択を引き出したのです。"},
    "an_footer": {"KR": "이 결과는 results.csv 에 기록되었습니다  ·  클릭하여 종료",
                  "EN": "This result was logged to results.csv  ·  Click to exit",
                  "CH": "该结果已记录到 results.csv  ·  点击退出",
                  "JP": "この結果は results.csv に記録されました  ·  クリックで終了"},
}

# ── 스토리 텍스트 번역 (원문 KR → EN/CH/JP) ───────────
TR = {
    # 공통
    "……": {"EN": "......", "CH": "……", "JP": "……"},

    # ── CHAPTER 0 : 프롤로그 ──
    "1863년": {"EN": "1863", "CH": "1863年", "JP": "1863年"},
    "미국 남북전쟁": {"EN": "The American Civil War", "CH": "美国南北战争", "JP": "アメリカ南北戦争"},
    "수많은 청년들이 '영웅'이 되기 위해 전쟁터로 향했다.":
        {"EN": "Countless young men marched to the battlefield to become 'heroes'.",
         "CH": "无数青年为了成为'英雄'奔赴战场。",
         "JP": "数多くの若者が「英雄」になるため戦場へ向かった。"},
    "그러나 그들은 정말, 두려움을 느끼지 않았을까?":
        {"EN": "But did they truly feel no fear at all?",
         "CH": "但他们真的，一点都不感到恐惧吗？",
         "JP": "しかし彼らは本当に、恐怖を感じなかったのだろうか？"},
    "『붉은 무공훈장』": {"EN": "The Red Badge of Courage", "CH": "《红色英勇勋章》", "JP": "『赤い武功章』"},
    "하아… 과제가 왜 이렇게 많지. 영어영문학 발표에 심포지엄 발제까지…":
        {"EN": "Ugh... why do I have so much work. An English lit presentation, plus a symposium paper...",
         "CH": "唉…作业怎么这么多。英语文学发表，还有研讨会的课题…",
         "JP": "はぁ…課題が多すぎる。英文学の発表に、シンポジウムの報告まで…"},
    "오늘 안에 『붉은 무공훈장』도 다 읽어야 하는데…":
        {"EN": "And I still have to finish 'The Red Badge of Courage' today...",
         "CH": "今天还得把《红色英勇勋章》全部读完…",
         "JP": "今日中に『赤い武功章』も読み終えなきゃいけないのに…"},
    "솔직히 전쟁 소설은 별로다. 다 비슷하지 않을까? 영웅이 나오고, 이기고, 훈장을 받고…":
        {"EN": "Honestly, war novels aren't my thing. Aren't they all alike? A hero shows up, wins, gets a medal...",
         "CH": "老实说我不太喜欢战争小说。不都差不多吗？出现英雄，获胜，得勋章…",
         "JP": "正直、戦争小説は苦手だ。どれも似たようなものじゃない？英雄が出て、勝って、勲章をもらって…"},
    "어디 보자…": {"EN": "Let's see...", "CH": "我看看…", "JP": "どれどれ…"},
    "(책을 펼친다. 책장 넘기는 소리.)":
        {"EN": "(Opens the book. The sound of pages turning.)",
         "CH": "（翻开书。翻页的声音。）",
         "JP": "（本を開く。ページをめくる音。）"},
    "시간 경과": {"EN": "TIME PASSES", "CH": "时间流逝", "JP": "時間経過"},
    "2시간 후": {"EN": "2 hours later", "CH": "2小时后", "JP": "2時間後"},
    "드디어… 마지막 장이다.": {"EN": "Finally... the last chapter.", "CH": "终于…最后一章了。", "JP": "ついに…最後の章だ。"},
    "헨리는 결국 용감한 사람이 된 걸까. 아니면 끝까지 두려웠던 걸까.":
        {"EN": "Did Henry become a brave man in the end? Or was he afraid to the very last?",
         "CH": "亨利最终成了勇敢的人吗。还是到最后都在恐惧？",
         "JP": "ヘンリーは結局、勇敢な人になれたのだろうか。それとも最後まで怖かったのか。"},
    "(어디선가 바람 소리. 책장이 혼자 넘어가기 시작한다.)":
        {"EN": "(Wind from somewhere. The pages begin to turn on their own.)",
         "CH": "（不知何处传来风声。书页开始自己翻动。）",
         "JP": "（どこからか風の音。ページがひとりでにめくれ始める。）"},
    "…? 창문도 안 열렸는데?": {"EN": "...? But the window isn't even open?", "CH": "…？窗户明明没开啊？", "JP": "…？窓も開いていないのに？"},
    "마지막 페이지의 글자가 흐려지더니, 한 문장이 떠오른다.":
        {"EN": "The words on the last page blur, and a single sentence rises up.",
         "CH": "最后一页的字迹变得模糊，一句话浮现出来。",
         "JP": "最後のページの文字がぼやけ、一つの文章が浮かび上がる。"},
    "\"당신이라면": {"EN": "\"If it were you,", "CH": "「如果是你，", "JP": "「あなたなら、"},
    "어떤 선택을 하겠습니까?\"": {"EN": "what choice would you make?\"", "CH": "你会做出怎样的选择？」", "JP": "どんな選択をしますか？」"},
    "…이런 문장이 있었나?": {"EN": "...Was there a sentence like this?", "CH": "…有过这样一句话吗？", "JP": "…こんな文章、あっただろうか？"},
    "(손을 책 위에 올린다. 책이 붉은 빛을 내기 시작한다.)":
        {"EN": "(Places a hand on the book. It begins to glow red.)",
         "CH": "（把手放在书上。书开始发出红光。）",
         "JP": "（本の上に手を置く。本が赤い光を放ち始める。）"},
    "잠깐, 뭐야?!": {"EN": "Wait, what?!", "CH": "等等，怎么回事？！", "JP": "ちょっと、何これ？！"},
    "(총소리, 포성, 병사들의 비명. 콜록… 눈을 뜬다.)":
        {"EN": "(Gunfire, cannon blasts, soldiers screaming. Cough... eyes open.)",
         "CH": "（枪声，炮声，士兵的惨叫。咳…睁开眼。）",
         "JP": "（銃声、砲声、兵士たちの悲鳴。ゴホッ…目を開ける。）"},
    "…… 뭐야. 여긴…": {"EN": "...What. Where is this...", "CH": "……什么。这里是…", "JP": "……何だ。ここは…"},
    "화약 냄새, 피 냄새, 사람들 비명. 이건 꿈이 아니다.":
        {"EN": "The smell of gunpowder, of blood, people screaming. This is no dream.",
         "CH": "火药味，血腥味，人们的惨叫。这不是梦。",
         "JP": "火薬の匂い、血の匂い、人々の悲鳴。これは夢じゃない。"},
    "이 풍경… 설마. 붉은 무공훈장…?": {"EN": "This scene... don't tell me. The Red Badge of Courage...?", "CH": "这景象…难道。红色英勇勋章…？", "JP": "この光景…まさか。赤い武功章…？"},
    "1863년 미국 남북전쟁": {"EN": "1863, American Civil War", "CH": "1863年 美国南北战争", "JP": "1863年 アメリカ南北戦争"},
    "북군 진영 근처": {"EN": "Near the Union camp", "CH": "北军营地附近", "JP": "北軍陣営の近く"},
    "(부스럭 — 숲속에서 누군가 나온다.)":
        {"EN": "(Rustling — someone emerges from the forest.)",
         "CH": "（沙沙声——有人从林中走出。）",
         "JP": "（ガサッ——森の中から誰かが現れる。）"},
    "야. 너 누구야? 여긴 민간인이 있을 곳이 아니야.":
        {"EN": "Hey. Who are you? This is no place for a civilian.",
         "CH": "喂。你是谁？这里不是平民该待的地方。",
         "JP": "おい。お前、誰だ？ここは民間人がいる場所じゃない。"},
    "…헨리? 말투도 책에서 읽은 그대로다. 진짜 책 안으로 들어온 거야.":
        {"EN": "...Henry? Even his way of speaking is just like in the book. I really have entered the story.",
         "CH": "…亨利？连语气都和书里读到的一模一样。我真的进到书里来了。",
         "JP": "…ヘンリー？口調も本で読んだそのままだ。本当に本の中に入ってしまったんだ。"},
    "…… 잠깐. 괜찮아? 얼굴이 창백한데.":
        {"EN": "...Hey. Are you all right? You look pale.",
         "CH": "……等等。你没事吧？脸色很苍白。",
         "JP": "……おい。大丈夫か？顔が青いぞ。"},
    "① 피난민이라고 둘러댄다.": {"EN": "Pretend to be a refugee.", "CH": "谎称自己是难民。", "JP": "避難民だとごまかす。"},
    "난… 피난민이야. 길을 잃었어.": {"EN": "I'm... a refugee. I lost my way.", "CH": "我…是难民。迷路了。", "JP": "私は…避難民だ。道に迷ったんだ。"},
    "그렇구나. 운이 없었네.": {"EN": "I see. Bad luck.", "CH": "这样啊。运气不好。", "JP": "そうか。運がなかったな。"},
    "② 기억이 안 난다고 말한다.": {"EN": "Say you can't remember.", "CH": "说自己失忆了。", "JP": "記憶がないと言う。"},
    "기억이 잘 안 나…": {"EN": "I can't really remember...", "CH": "我记不太清了…", "JP": "よく思い出せなくて…"},
    "충격 때문인가.": {"EN": "Must be the shock.", "CH": "是受了惊吓吧。", "JP": "衝撃のせいか。"},
    "③ 사실을 말한다.": {"EN": "Tell the truth.", "CH": "说出实情。", "JP": "本当のことを話す。"},
    "사실… 난 미래에서 왔어.": {"EN": "Actually... I came from the future.", "CH": "其实…我来自未来。", "JP": "実は…私は未来から来たんだ。"},
    "…… 하하. 긴장해서 헛소리하는 거지?":
        {"EN": "...Haha. You're just talking nonsense from the stress, right?",
         "CH": "……哈哈。太紧张说胡话了吧？",
         "JP": "……はは。緊張して変なこと言ってるんだろ？"},
    "난 헨리 플레밍. 지원병이야.": {"EN": "I'm Henry Fleming. A volunteer.", "CH": "我是亨利·弗莱明。志愿兵。", "JP": "俺はヘンリー・フレミング。志願兵だ。"},
    "악수를 건네는 헨리의 손은, 미세하게 떨리고 있었다.":
        {"EN": "The hand Henry offered for a handshake was trembling, ever so slightly.",
         "CH": "亨利伸出握手的手，在微微颤抖。",
         "JP": "握手を差し出すヘンリーの手は、かすかに震えていた。"},
    "…떨고 있어.": {"EN": "...He's trembling.", "CH": "…在发抖。", "JP": "…震えてる。"},
    "NEW SYSTEM : 공감 (Empathy)": {"EN": "NEW SYSTEM : Empathy", "CH": "新系统 : 共情 (Empathy)", "JP": "新システム : 共感 (Empathy)"},
    "상대의 '행동'보다 '감정'을 이해하려 할수록 상승합니다.":
        {"EN": "It rises the more you try to understand others' 'feelings' rather than their 'actions'.",
         "CH": "越是去理解对方的'情感'而非'行为'，它就越会上升。",
         "JP": "相手の「行動」より「感情」を理解しようとするほど上昇します。"},
    "이 이야기의 핵심은 '설득'이 아니라 '이해'입니다.":
        {"EN": "The heart of this story is not 'persuasion' but 'understanding'.",
         "CH": "这个故事的核心不是'说服'，而是'理解'。",
         "JP": "この物語の核心は「説得」ではなく「理解」です。"},

    # ── CHAPTER 1 ──
    "CHAPTER 1": {"EN": "CHAPTER 1", "CH": "第一章", "JP": "第一章"},
    "전투 전날 밤": {"EN": "The Night Before Battle", "CH": "战斗前夜", "JP": "戦いの前夜"},
    "두려움을 느끼는 것은 비겁함인가?": {"EN": "Is feeling fear cowardice?", "CH": "感到恐惧就是懦弱吗？", "JP": "恐怖を感じることは、臆病なのか？"},
    "이곳은 이상했다. 전쟁터인데도 웃는 사람이 있었다. 편지를 쓰는 사람도, 농담을 하는 사람도 있었다.":
        {"EN": "This place was strange. Even on a battlefield, some laughed. Some wrote letters, some cracked jokes.",
         "CH": "这地方很奇怪。明明是战场，却有人在笑。有人写信，也有人开玩笑。",
         "JP": "ここは奇妙だった。戦場なのに笑っている者がいた。手紙を書く者も、冗談を言う者もいた。"},
    "내일이면 누군가는 죽을 텐데.": {"EN": "Even though someone will die tomorrow.", "CH": "明天就会有人死去啊。", "JP": "明日には、誰かが死ぬというのに。"},
    "야. 내일 끝나면 술이나 실컷 마시자.": {"EN": "Hey. When this ends tomorrow, let's drink our fill.", "CH": "喂。明天结束了，就痛快喝一场吧。", "JP": "なあ。明日が終わったら、酒でも浴びるほど飲もうぜ。"},
    "끝나면? 살아서 말이지?": {"EN": "When it ends? If we live, you mean?", "CH": "结束了？前提是活着吧？", "JP": "終わったら？生きていればの話だろ？"},
    "(병사들이 웃는다. 그러나 그 웃음은 오래가지 않는다.)":
        {"EN": "(The soldiers laugh. But the laughter does not last long.)",
         "CH": "（士兵们笑了。但那笑声没能持续多久。）",
         "JP": "（兵士たちが笑う。だがその笑いは長くは続かない。）"},
    "웃고 있었지만, 아무도 웃고 있지 않았다.": {"EN": "They were laughing, yet no one was laughing at all.", "CH": "虽然在笑，却没有一个人真的在笑。", "JP": "笑っていたが、誰も笑ってなどいなかった。"},
    "자유 탐색": {"EN": "FREE EXPLORATION", "CH": "自由探索", "JP": "自由探索"},
    "모닥불 · 보급마차 · 강가(헨리)": {"EN": "Campfire · Supply Wagon · Riverside (Henry)", "CH": "篝火 · 补给马车 · 河边（亨利）", "JP": "焚き火 · 補給馬車 · 川辺（ヘンリー）"},
    "모든 장소를 조사해야 밤이 온다.": {"EN": "Investigate every place for night to fall.", "CH": "调查完所有地点，夜晚才会到来。", "JP": "すべての場所を調べると夜が訪れる。"},
    "모닥불": {"EN": "Campfire", "CH": "篝火", "JP": "焚き火"},
    "보급마차": {"EN": "Supply Wagon", "CH": "补给马车", "JP": "補給馬車"},
    "강가 (헨리)": {"EN": "Riverside (Henry)", "CH": "河边（亨利）", "JP": "川辺（ヘンリー）"},
    "(병사들이 카드놀이를 하고 있다.)": {"EN": "(Soldiers are playing cards.)", "CH": "（士兵们在打牌。）", "JP": "（兵士たちがトランプをしている。）"},
    "안녕하세요.": {"EN": "Hello.", "CH": "你好。", "JP": "こんにちは。"},
    "…… 앉아.": {"EN": "...Sit.", "CH": "……坐吧。", "JP": "……座れよ。"},
    "안 무서우세요?": {"EN": "Aren't you scared?", "CH": "您不害怕吗？", "JP": "怖くないんですか？"},
    "무섭지. 무섭지 않은 사람은 거짓말쟁이거나, 미친 사람이야.":
        {"EN": "Of course I am. Anyone who isn't scared is either a liar or a madman.",
         "CH": "怕啊。不怕的人不是骗子，就是疯子。",
         "JP": "怖いさ。怖くない奴は嘘つきか、いかれてるかのどっちかだ。"},
    "그럼 왜 이렇게 웃으세요?": {"EN": "Then why do you laugh like this?", "CH": "那您为什么还笑成这样？", "JP": "じゃあ、どうしてそんなに笑ってるんですか？"},
    "…… 겁이 나니까. 웃지 않으면, 울 것 같거든.":
        {"EN": "...Because I'm scared. If I don't laugh, I think I'll cry.",
         "CH": "……因为害怕啊。不笑的话，感觉就要哭了。",
         "JP": "……怖いからさ。笑わなきゃ、泣いちまいそうだからな。"},
    "① \"…이해돼요.\"": {"EN": "\"...I understand.\"", "CH": "\"…我能理解。\"", "JP": "\"…わかります。\""},
    "② \"군인이니까 참아야죠.\"": {"EN": "\"You're a soldier, you have to endure it.\"", "CH": "\"当兵的就得忍着吧。\"", "JP": "\"軍人なんだから、我慢しないと。\""},
    "③ \"저라면 못 웃었을 것 같아요.\"": {"EN": "\"I don't think I could laugh, if it were me.\"", "CH": "\"要是我，大概笑不出来。\"", "JP": "\"私なら、笑えなかったと思います。\""},
    "전쟁은 총보다 먼저, 사람의 표정을 바꾼다.": {"EN": "War changes a person's face before it fires a single shot.", "CH": "战争在开枪之前，先改变了人的表情。", "JP": "戦争は銃よりも先に、人の表情を変える。"},
    "안녕하세요!!": {"EN": "Hello!!", "CH": "你好！！", "JP": "こんにちは！！"},
    "안 무서워?": {"EN": "Aren't you scared?", "CH": "你不怕吗？", "JP": "怖くないの？"},
    "전혀요! 내일 영웅이 될 거예요.": {"EN": "Not at all! Tomorrow I'll be a hero.", "CH": "完全不怕！明天我就要成为英雄了。", "JP": "全然！明日、俺は英雄になるんだ。"},
    "…… 나도 처음엔 그랬지.": {"EN": "...I was like that too, at first.", "CH": "……我一开始也是这么想的。", "JP": "……俺も最初はそうだったよ。"},
    "(마크는 웃지만, 총을 닦는 손은 떨리고 있다.)": {"EN": "(Mark is smiling, but the hand cleaning his rifle is shaking.)", "CH": "（马克在笑，可擦枪的手却在发抖。）", "JP": "（マークは笑っているが、銃を拭く手は震えている。）"},
    "희망도, 허세도, 공포를 숨기는 방법이었다.": {"EN": "Hope and bravado alike were just ways of hiding fear.", "CH": "希望也好，逞强也好，都是掩饰恐惧的方式。", "JP": "希望も、虚勢も、恐怖を隠すための手段だった。"},
    "(헨리가 혼자 앉아 돌을 물에 던지고 있다.)": {"EN": "(Henry sits alone, tossing stones into the water.)", "CH": "（亨利独自坐着，往水里扔石子。）", "JP": "（ヘンリーが一人で座り、石を水に投げている。）"},
    "혼자 있었네.": {"EN": "You're alone.", "CH": "你一个人啊。", "JP": "一人だったんだね。"},
    "말 안 해도 돼.": {"EN": "You don't have to talk.", "CH": "不说也没关系。", "JP": "話さなくてもいいよ。"},
    "(한참 뒤, 헨리가 입을 연다.)": {"EN": "(After a long while, Henry speaks.)", "CH": "（过了许久，亨利开口了。）", "JP": "（しばらくして、ヘンリーが口を開く。）"},
    "넌. 무섭지 않아?": {"EN": "You. Aren't you afraid?", "CH": "你。不害怕吗？", "JP": "君は。怖くないのか？"},
    "① \"무서워.\"": {"EN": "\"I'm scared.\"", "CH": "\"我怕。\"", "JP": "\"怖いよ。\""},
    "…… 다행이다.": {"EN": "...Thank goodness.", "CH": "……太好了。", "JP": "……よかった。"},
    "왜?": {"EN": "Why?", "CH": "为什么？", "JP": "どうして？"},
    "나만 그런 줄 알았거든.": {"EN": "I thought I was the only one.", "CH": "我还以为只有我这样。", "JP": "俺だけかと思ってたから。"},
    "② \"괜찮아.\"": {"EN": "\"I'm fine.\"", "CH": "\"没事。\"", "JP": "\"平気だよ。\""},
    "…… 그렇구나. 넌 강하네.": {"EN": "...I see. You're strong.", "CH": "……这样啊。你很坚强。", "JP": "……そうか。君は強いな。"},
    "③ \"잘 모르겠어.\"": {"EN": "\"I'm not sure.\"", "CH": "\"我也说不清。\"", "JP": "\"よくわからない。\""},
    "…… 나도 그래.": {"EN": "...Me neither.", "CH": "……我也是。", "JP": "……俺もだよ。"},
    "밤. 모닥불은 거의 꺼져간다.": {"EN": "Night. The campfire is almost out.", "CH": "夜晚。篝火几乎快熄灭了。", "JP": "夜。焚き火はほとんど消えかけている。"},
    "이거. 여분 군복이야. 입고 다녀. 여기선 남들과 같아 보여야 살아남으니까.":
        {"EN": "Here. A spare uniform. Wear it. Around here, you survive by looking like everyone else.",
         "CH": "给。备用的军服。穿上吧。在这儿，看起来和别人一样才能活下来。",
         "JP": "これ。予備の軍服だ。着ておけ。ここじゃ、他の連中と同じに見えなきゃ生き残れないからな。"},
    "기억 조각 : 군복": {"EN": "Memory Fragment : Uniform", "CH": "记忆碎片 : 军服", "JP": "記憶の欠片 : 軍服"},
    "전쟁은 '개성'보다 '소속'이 생존을 좌우한다.":
        {"EN": "In war, 'belonging' decides survival more than 'individuality'.",
         "CH": "在战争中，'归属'比'个性'更决定生死。",
         "JP": "戦争では「個性」より「所属」が生存を左右する。"},
    "군복": {"EN": "Uniform", "CH": "军服", "JP": "軍服"},
    "CHAPTER 1 RESULT 「전투 전날 밤」": {"EN": "CHAPTER 1 RESULT — The Night Before Battle", "CH": "第一章 结算 「战斗前夜」", "JP": "第一章 リザルト 「戦いの前夜」"},

    # ── CHAPTER 2 ──
    "CHAPTER 2": {"EN": "CHAPTER 2", "CH": "第二章", "JP": "第二章"},
    "도망친 병사": {"EN": "The Soldier Who Fled", "CH": "逃跑的士兵", "JP": "逃げた兵士"},
    "살고 싶은 인간의 본능은 비겁함인가.": {"EN": "Is the human instinct to survive cowardice?", "CH": "人想活下去的本能，就是懦弱吗。", "JP": "生きたいという人間の本能は、臆病なのか。"},
    "(나팔 소리. 병사들이 급하게 일어난다.)": {"EN": "(A bugle call. The soldiers scramble to their feet.)", "CH": "（号角声。士兵们慌忙起身。）", "JP": "（ラッパの音。兵士たちが慌てて起き上がる。）"},
    "전원 집합!! 적군이 움직인다!!": {"EN": "All hands, assemble!! The enemy is on the move!!", "CH": "全体集合！！敌军动了！！", "JP": "総員集合！！敵が動いたぞ！！"},
    "드디어… 시작되는구나.": {"EN": "So it begins... at last.", "CH": "终于…要开始了。", "JP": "ついに…始まるのか。"},
    "(헨리가 총을 집어 든다. 손이 떨리고 있다.)": {"EN": "(Henry picks up his rifle. His hands are shaking.)", "CH": "（亨利拿起枪。手在发抖。）", "JP": "（ヘンリーが銃を手に取る。手が震えている。）"},
    "헨리. 괜찮아?": {"EN": "Henry. Are you okay?", "CH": "亨利。你还好吗？", "JP": "ヘンリー。大丈夫？"},
    "① \"무서우면 말해도 돼.\"": {"EN": "\"It's okay to say if you're scared.\"", "CH": "\"害怕的话，说出来也没关系。\"", "JP": "\"怖いなら、言ってもいいんだよ。\""},
    "…… 사실. 무섭다. 정말, 도망가고 싶을 정도로.":
        {"EN": "...The truth is, I'm scared. Enough that I really want to run.",
         "CH": "……其实。我很怕。怕到真想逃跑。",
         "JP": "……本当は。怖いんだ。逃げ出したいくらい、本当に。"},
    "근데 그렇게 말하면 다들 날 비웃겠지.": {"EN": "But if I say that, everyone will laugh at me.", "CH": "可要是那么说，大家都会笑话我吧。", "JP": "でも、そんなこと言ったら、みんな俺を笑うだろうな。"},
    "② \"군인이잖아.\"": {"EN": "\"You're a soldier.\"", "CH": "\"你可是军人啊。\"", "JP": "\"軍人だろ。\""},
    "…… 그래. 군인이지.": {"EN": "...Right. A soldier.", "CH": "……对。是军人。", "JP": "……ああ。軍人だな。"},
    "③ 말없이 옆에 선다.": {"EN": "Stand beside him in silence.", "CH": "默默地站到他身边。", "JP": "何も言わず、そばに立つ。"},
    "(아무 말 없이, 헨리 옆에 선다.)": {"EN": "(Without a word, you stand beside Henry.)", "CH": "（一言不发，站到亨利身边。）", "JP": "（何も言わず、ヘンリーの隣に立つ。）"},
    "(총성. 탕! 탕! 포성. 병사들의 함성.)": {"EN": "(Gunshots. Bang! Bang! Cannon fire. The soldiers' war cries.)", "CH": "（枪声。砰！砰！炮声。士兵们的呐喊。）", "JP": "（銃声。パン！パン！砲声。兵士たちの雄叫び。）"},
    "사격!!": {"EN": "Fire!!", "CH": "射击！！", "JP": "撃て！！"},
    "헨리!! 엎드려!!": {"EN": "Henry!! Get down!!", "CH": "亨利！！趴下！！", "JP": "ヘンリー！！伏せろ！！"},
    "(총알이 머리 위를 스친다.)": {"EN": "(A bullet grazes past overhead.)", "CH": "（子弹从头顶擦过。）", "JP": "（銃弾が頭上をかすめる。）"},
    "책에서 읽었던 것과 전혀 달랐다. 연기. 비명. 흙. 피.": {"EN": "It was nothing like what I'd read in the book. Smoke. Screams. Dirt. Blood.", "CH": "和书里读到的完全不同。硝烟。惨叫。泥土。鲜血。", "JP": "本で読んだのとはまるで違った。煙。悲鳴。土。血。"},
    "전진!!": {"EN": "Advance!!", "CH": "前进！！", "JP": "前進！！"},
    "병사들이 함께 달려간다. 헨리도 이를 악물고 따라간다.": {"EN": "The soldiers charge together. Henry grits his teeth and follows.", "CH": "士兵们一齐冲了出去。亨利也咬牙跟上。", "JP": "兵士たちが一斉に駆け出す。ヘンリーも歯を食いしばってついていく。"},
    "(잠시 후, 적군이 후퇴한다.)": {"EN": "(After a while, the enemy retreats.)", "CH": "（片刻后，敌军撤退了。）", "JP": "（しばらくして、敵が後退する。）"},
    "우리가 막았다!!": {"EN": "We held them off!!", "CH": "我们挡住了！！", "JP": "俺たちが防いだぞ！！"},
    "…… 살았다.": {"EN": "...We made it.", "CH": "……活下来了。", "JP": "……助かった。"},
    "잘했어.": {"EN": "Well done.", "CH": "干得好。", "JP": "よくやった。"},
    "아직… 끝난 게 아니야.": {"EN": "It's not... over yet.", "CH": "还…没结束。", "JP": "まだ…終わってない。"},
    "(멀리서 북소리.)": {"EN": "(Drums, far in the distance.)", "CH": "（远处传来鼓声。）", "JP": "（遠くで太鼓の音。）"},
    "또 온다!!": {"EN": "Here they come again!!", "CH": "又来了！！", "JP": "また来るぞ！！"},
    "이번에는 더 많은 적군. 병사들의 표정이 굳는다.": {"EN": "Even more enemies this time. The soldiers' faces harden.", "CH": "这次敌军更多了。士兵们的表情凝固。", "JP": "今度はさらに多くの敵。兵士たちの表情がこわばる。"},
    "(헨리의 시선 끝에, 도망가는 병사 한 명.)": {"EN": "(At the end of Henry's gaze, a single soldier running away.)", "CH": "（亨利视线的尽头，有一名士兵在逃跑。）", "JP": "（ヘンリーの視線の先に、逃げていく一人の兵士。）"},
    "(헨리 독백) 왜… 저 사람은 도망치는데, 난 여기 있어야 하지?":
        {"EN": "(Henry's thoughts) Why... does he get to run, while I have to stay here?",
         "CH": "（亨利独白）为什么…那个人能逃，我却得留在这儿？",
         "JP": "（ヘンリーの独白）どうして…あいつは逃げるのに、俺はここにいなきゃならないんだ？"},
    "헨리?": {"EN": "Henry?", "CH": "亨利？", "JP": "ヘンリー？"},
    "① \"같이 버티자.\"": {"EN": "\"Let's hold on together.\"", "CH": "\"一起撑下去吧。\"", "JP": "\"一緒に踏ん張ろう。\""},
    "…… 그래. 버텨 볼게.": {"EN": "...Okay. I'll try to hold on.", "CH": "……好。我试着撑住。", "JP": "……ああ。踏ん張ってみる。"},
    "② \"도망쳐도 된다고는 말 못 해.\"": {"EN": "\"I can't tell you it's okay to run.\"", "CH": "\"我没法说逃跑也没关系。\"", "JP": "\"逃げてもいいとは、言えない。\""},
    "…… 알아. 나도.": {"EN": "...I know. Me too.", "CH": "……我知道。我也是。", "JP": "……わかってる。俺もだ。"},
    "③ \"무슨 생각해?\"": {"EN": "\"What are you thinking?\"", "CH": "\"你在想什么？\"", "JP": "\"何を考えてる？\""},
    "…… 나도. 도망가고 싶어.": {"EN": "...Me too. I want to run.", "CH": "……我也。想逃。", "JP": "……俺も。逃げたいよ。"},
    "(갑자기 포탄이 떨어진다. — 콰아앙!!)": {"EN": "(Suddenly a shell falls. — BOOM!!)", "CH": "（突然炮弹落下。——轰隆！！）", "JP": "（突然、砲弾が落ちる。——ドオォン！！）"},
    "연기 속. 헨리가 사라진다.": {"EN": "In the smoke, Henry vanishes.", "CH": "硝烟中。亨利消失了。", "JP": "煙の中。ヘンリーが消える。"},
    "(연기가 걷힌다.)": {"EN": "(The smoke clears.)", "CH": "（硝烟散去。）", "JP": "（煙が晴れる。）"},
    "헨리!!": {"EN": "Henry!!", "CH": "亨利！！", "JP": "ヘンリー！！"},
    "헨리가 숲을 향해 뛰고 있다.": {"EN": "Henry is running toward the forest.", "CH": "亨利正朝着树林奔跑。", "JP": "ヘンリーが森へ向かって走っている。"},
    "① 따라간다.": {"EN": "Follow him.", "CH": "追上去。", "JP": "追いかける。"},
    "플레이어도 헨리를 뒤쫓는다.": {"EN": "You chase after Henry.", "CH": "你也追着亨利跑去。", "JP": "あなたもヘンリーを追う。"},
    "② 전장에 남는다.": {"EN": "Stay on the battlefield.", "CH": "留在战场。", "JP": "戦場に残る。"},
    "잠시 남으려 하지만, 헨리를 이대로 둘 수는 없어 결국 뒤쫓는다.":
        {"EN": "You try to stay, but you can't leave Henry like this, and end up chasing him.",
         "CH": "本想留下，但无法就这样丢下亨利，最终还是追了上去。",
         "JP": "残ろうとするが、ヘンリーをこのままにはできず、結局追いかける。"},
    "③ 잠시 망설인다.": {"EN": "Hesitate for a moment.", "CH": "犹豫了一下。", "JP": "少しためらう。"},
    "잠시 망설이다, 결국 헨리를 따라간다.": {"EN": "After a moment's hesitation, you follow Henry after all.", "CH": "犹豫片刻，最终还是跟上了亨利。", "JP": "少しためらったが、結局ヘンリーを追う。"},
    "(헨리는 거친 숨을 몰아쉰다. 하… 하…)": {"EN": "(Henry is gasping for breath. Ha... ha...)", "CH": "（亨利大口喘着气。哈…哈…）", "JP": "（ヘンリーは荒い息をつく。はぁ…はぁ…）"},
    "난… 도망쳤어.": {"EN": "I... ran away.", "CH": "我…逃跑了。", "JP": "俺は…逃げた。"},
    "(긴 침묵.)": {"EN": "(A long silence.)", "CH": "（长久的沉默。）", "JP": "（長い沈黙。）"},
    "이제 난, 겁쟁이인 거지?": {"EN": "So now I'm a coward, right?", "CH": "现在我，就是个懦夫了吧？", "JP": "もう俺は、臆病者ってことだよな？"},
    "① \"아니.\"": {"EN": "\"No.\"", "CH": "\"不是。\"", "JP": "\"違う。\""},
    "살고 싶었던 거잖아. 그건 인간이라면 당연한 감정이야.":
        {"EN": "You wanted to live. That's a natural feeling for any human.",
         "CH": "你只是想活下去。那是人之常情。",
         "JP": "生きたかっただけだろ。それは人間なら当たり前の感情だよ。"},
    "(헨리의 눈에 눈물이 맺힌다.)": {"EN": "(Tears well up in Henry's eyes.)", "CH": "（亨利的眼里泛起泪水。）", "JP": "（ヘンリーの目に涙がにじむ。）"},
    "② \"잘못한 건 맞아.\"": {"EN": "\"You did do wrong, though.\"", "CH": "\"你确实做错了。\"", "JP": "\"間違ったのは確かだよ。\""},
    "잘못한 건, 맞아.": {"EN": "You did do wrong, that's true.", "CH": "做错了，这是事实。", "JP": "間違ったのは、確かだ。"},
    "…… 그래. 알아.": {"EN": "...Yeah. I know.", "CH": "……嗯。我知道。", "JP": "……ああ。わかってる。"},
    "③ \"나도 모르겠어.\"": {"EN": "\"I don't know either.\"", "CH": "\"我也不知道。\"", "JP": "\"俺にもわからない。\""},
    "나도… 모르겠어.": {"EN": "I... don't know either.", "CH": "我也…不知道。", "JP": "俺も…わからないよ。"},
    "둘은 숲속을 걷는다. 갑자기 다람쥐 한 마리가 발소리를 듣고 재빨리 달아난다.":
        {"EN": "The two walk through the forest. Suddenly a squirrel, hearing their footsteps, darts away.",
         "CH": "两人走在林中。突然一只松鼠听到脚步声，飞快地逃开了。",
         "JP": "二人は森の中を歩く。突然、一匹のリスが足音を聞いて素早く逃げ去る。"},
    "봤어?": {"EN": "Did you see that?", "CH": "看见了吗？", "JP": "見たか？"},
    "응.": {"EN": "Yeah.", "CH": "嗯。", "JP": "うん。"},
    "저 다람쥐도 살려고 도망쳤잖아. 아무도 저걸 겁쟁이라곤 안 하잖아.":
        {"EN": "That squirrel ran to live, too. No one calls it a coward.",
         "CH": "那只松鼠也是为了活命才逃的。没人会说它是懦夫。",
         "JP": "あのリスも生きるために逃げただろ。誰もあれを臆病者とは言わない。"},
    "그런데 왜 사람은… 도망치면 겁쟁이가 되는 걸까.":
        {"EN": "So why is it that when a person runs... they become a coward?",
         "CH": "可为什么人一逃跑…就成了懦夫呢。",
         "JP": "なのにどうして人間は…逃げると臆病者になるんだろう。"},
    "멀리서 비틀거리며 걸어오는 병사.": {"EN": "A soldier staggers toward them from afar.", "CH": "远处一名士兵踉跄着走来。", "JP": "遠くから、よろめきながら歩いてくる兵士。"},
    "저 사람은…": {"EN": "That man is...", "CH": "那个人是…", "JP": "あの人は…"},
    "짐.": {"EN": "Jim.", "CH": "吉姆。", "JP": "ジムだ。"},
    "(짐 콘클린은 배를 움켜쥔 채 말없이 걷는다.)": {"EN": "(Jim Conklin walks in silence, clutching his stomach.)", "CH": "（吉姆·康克林捂着肚子，默默地走着。）", "JP": "（ジム・コンクリンは腹を押さえたまま、黙って歩く。）"},
    "도와야 해!": {"EN": "We have to help him!", "CH": "得救他！", "JP": "助けなきゃ！"},
    "① 끝까지 함께 간다.": {"EN": "Stay with him to the very end.", "CH": "陪他走到最后。", "JP": "最後まで付き添う。"},
    "(플레이어는 짐의 어깨를 붙잡는다.)": {"EN": "(You take hold of Jim's shoulder.)", "CH": "（你抓住吉姆的肩膀。）", "JP": "（あなたはジムの肩を支える。）"},
    "…… 괜찮아.": {"EN": "...I'm fine.", "CH": "……没事的。", "JP": "……大丈夫だ。"},
    "짐은 숲속 깊은 곳, 아무도 없는 들판으로 천천히 걸어간다. 그리고 무릎을 꿇는다.":
        {"EN": "Jim walks slowly into a deserted field deep in the forest. Then he sinks to his knees.",
         "CH": "吉姆缓缓走向林深处一片无人的旷野。然后跪了下去。",
         "JP": "ジムは森の奥深く、誰もいない野原へゆっくりと歩いていく。そして膝をつく。"},
    "(잠시 후. 그는 조용히 쓰러진다. …… 침묵.)": {"EN": "(After a moment, he quietly collapses. ...Silence.)", "CH": "（片刻后。他静静地倒下。……沉默。）", "JP": "（しばらくして。彼は静かに倒れる。……沈黙。）"},
    "플레이어는 천천히, 짐의 눈을 감겨 준다.": {"EN": "You slowly close Jim's eyes.", "CH": "你缓缓地，为吉姆合上双眼。", "JP": "あなたはゆっくりと、ジムの目を閉じてやる。"},
    "기억 조각 : 짐의 군번줄": {"EN": "Memory Fragment : Jim's Dog Tags", "CH": "记忆碎片 : 吉姆的军牌", "JP": "記憶の欠片 : ジムの認識票"},
    "죽음은 책 속 문장이 아니라, 누군가의 마지막이었다.":
        {"EN": "Death was not a sentence in a book, but someone's final moment.",
         "CH": "死亡不是书里的一句话，而是某个人的最后一刻。",
         "JP": "死は本の中の一文ではなく、誰かの最期だった。"},
    "짐의 군번줄": {"EN": "Jim's Dog Tags", "CH": "吉姆的军牌", "JP": "ジムの認識票"},
    "② 의무병을 부르러 간다.": {"EN": "Go call for a medic.", "CH": "去叫医护兵。", "JP": "衛生兵を呼びに行く。"},
    "의무병을 찾아 달려가지만, 돌아왔을 때 짐은 이미 들판에 쓰러져 있었다.":
        {"EN": "You run to find a medic, but by the time you return, Jim has already fallen in the field.",
         "CH": "你跑去找医护兵，但回来时，吉姆已经倒在旷野中了。",
         "JP": "衛生兵を探して駆け出すが、戻った時にはジムはすでに野原に倒れていた。"},
    "③ 헨리만 따라간다.": {"EN": "Just follow Henry.", "CH": "只跟着亨利走。", "JP": "ヘンリーだけについていく。"},
    "차마 다가가지 못한다. 짐은 홀로 숲 안으로 사라진다.":
        {"EN": "You can't bring yourself to approach. Jim vanishes alone into the forest.",
         "CH": "你终究没能上前。吉姆独自消失在林中。",
         "JP": "どうしても近づけない。ジムは一人、森の中へ消えていく。"},
    "(헨리 독백) 나는 살려고 도망쳤다. 짐은 끝까지 싸우다 죽었다.":
        {"EN": "(Henry's thoughts) I ran to survive. Jim fought to the end and died.",
         "CH": "（亨利独白）我为了活命而逃。吉姆战斗到最后而死。",
         "JP": "（ヘンリーの独白）俺は生きるために逃げた。ジムは最後まで戦って死んだ。"},
    "나는… 정말… 비겁한 걸까.": {"EN": "Am I... really... a coward?", "CH": "我…真的…是懦夫吗。", "JP": "俺は…本当に…臆病者なのか。"},
    "「도망친 병사」": {"EN": "The Soldier Who Fled", "CH": "「逃跑的士兵」", "JP": "「逃げた兵士」"},
    "CHAPTER 2 RESULT 「도망친 병사」": {"EN": "CHAPTER 2 RESULT — The Soldier Who Fled", "CH": "第二章 结算 「逃跑的士兵」", "JP": "第二章 リザルト 「逃げた兵士」"},

    # ── CHAPTER 3 ──
    "CHAPTER 3": {"EN": "CHAPTER 3", "CH": "第三章", "JP": "第三章"},
    "붉은 무공훈장": {"EN": "The Red Badge of Courage", "CH": "红色英勇勋章", "JP": "赤い武功章"},
    "영웅은 어떻게 만들어지는가?": {"EN": "How is a hero made?", "CH": "英雄是如何被造就的？", "JP": "英雄はどうやって作られるのか？"},
    "해가 기울고 있다. 헨리와 플레이어는 말없이 걷는다.": {"EN": "The sun is setting. Henry and you walk in silence.", "CH": "夕阳西斜。亨利与你默默地走着。", "JP": "陽が傾いていく。ヘンリーとあなたは黙って歩く。"},
    "짐이 계속 생각나. 끝까지 싸우다 죽었잖아. 나는… 도망쳤는데.":
        {"EN": "I keep thinking about Jim. He fought to the end and died. But I... ran.",
         "CH": "我一直想起吉姆。他战斗到最后而死。而我…却逃了。",
         "JP": "ジムのことがずっと頭から離れない。最後まで戦って死んだのに。俺は…逃げたのに。"},
    "① \"너도 살아남으려고 한 거야.\"": {"EN": "\"You were just trying to survive, too.\"", "CH": "\"你也只是想活下去而已。\"", "JP": "\"君も生き延びようとしただけだよ。\""},
    "살고 싶은 마음은 죄가 아니야.": {"EN": "Wanting to live is not a sin.", "CH": "想活下去，不是罪。", "JP": "生きたいと願うことは、罪じゃない。"},
    "…… 그러면 왜, 나는 계속 죄인 같지?": {"EN": "...Then why do I keep feeling like a sinner?", "CH": "……那为什么，我总觉得自己像个罪人？", "JP": "……なら、どうして俺はずっと罪人みたいに感じるんだ？"},
    "② \"짐은 짐이고, 넌 너야.\"": {"EN": "\"Jim is Jim, and you are you.\"", "CH": "\"吉姆是吉姆，你是你。\"", "JP": "\"ジムはジム、君は君だよ。\""},
    "…… 그렇게 나눌 수 있으면 좋겠다.": {"EN": "...I wish I could separate it like that.", "CH": "……要是能这样分开就好了。", "JP": "……そんなふうに割り切れたらいいのにな。"},
    "③ \"도망친 건 사실이잖아.\"": {"EN": "\"You did run, though. That's a fact.\"", "CH": "\"你逃跑了，这是事实。\"", "JP": "\"逃げたのは事実だろ。\""},
    "…… 그래. 사실이지.": {"EN": "...Yeah. It's a fact.", "CH": "……嗯。是事实。", "JP": "……ああ。事実だ。"},
    "숲길. 도망친 병사들과 부상병들이 뒤섞여 있다. 누군가는 다리를 절고, 누군가는 친구를 업고 간다.":
        {"EN": "A forest path. Deserters and wounded soldiers are mixed together. Some limp, some carry a friend on their back.",
         "CH": "林间小路。逃兵和伤兵混杂在一起。有人瘸着腿，有人背着战友。",
         "JP": "森の道。逃げた兵士と負傷兵が入り混じっている。足を引きずる者、友を背負って歩く者。"},
    "이들은 패배한 병사였다. 하지만 겁쟁이라고 단정할 수는 없었다.":
        {"EN": "These were defeated soldiers. But I couldn't call them cowards.",
         "CH": "他们是战败的士兵。但不能就此断定他们是懦夫。",
         "JP": "彼らは敗れた兵士だった。だが、臆病者と決めつけることはできなかった。"},
    "물… 제발…": {"EN": "Water... please...", "CH": "水…求你了…", "JP": "水を…頼む…"},
    "① 물을 건넨다.": {"EN": "Offer him water.", "CH": "递上水。", "JP": "水を差し出す。"},
    "고맙네…": {"EN": "Thank you...", "CH": "谢谢你…", "JP": "ありがとう…"},
    "기억 조각 : 붉은 손수건": {"EN": "Memory Fragment : Red Handkerchief", "CH": "记忆碎片 : 红手帕", "JP": "記憶の欠片 : 赤いハンカチ"},
    "부상병이 감사의 의미로 건네준다.": {"EN": "The wounded soldier hands it over in thanks.", "CH": "伤兵为表感谢而递给你的。", "JP": "負傷兵が感謝のしるしに手渡してくれる。"},
    "붉은 손수건": {"EN": "Red Handkerchief", "CH": "红手帕", "JP": "赤いハンカチ"},
    "② 의무병을 찾는다.": {"EN": "Look for a medic.", "CH": "去找医护兵。", "JP": "衛生兵を探す。"},
    "의무병을 찾아 나서지만, 인파 속에서 부상병을 놓치고 만다.":
        {"EN": "You set off to find a medic, but lose the wounded soldier in the crowd.",
         "CH": "你去找医护兵，却在人群中弄丢了那名伤兵。",
         "JP": "衛生兵を探しに行くが、人混みの中で負傷兵を見失ってしまう。"},
    "③ 지나친다.": {"EN": "Walk past.", "CH": "走过去。", "JP": "通り過ぎる。"},
    "차마 감당할 수 없어, 고개를 돌리고 지나친다.":
        {"EN": "Unable to bear it, you turn your head away and walk past.",
         "CH": "实在无法承受，你别过头走了过去。",
         "JP": "とても耐えられず、目をそらして通り過ぎる。"},
    "비켜!! 길 비켜!!": {"EN": "Move!! Out of the way!!", "CH": "让开！！让路！！", "JP": "どけ！！道を空けろ！！"},
    "패닉 상태. 사람들이 서로 밀친다. 갑자기 뒤에서 누군가 달려온다.":
        {"EN": "Panic. People shove one another. Suddenly, someone comes running from behind.",
         "CH": "一片恐慌。人们互相推搡。突然，有人从后面冲了过来。",
         "JP": "パニック状態。人々が押し合う。突然、後ろから誰かが駆けてくる。"},
    "(쿵!! — 뒤에서 달려온 병사의 총 개머리판이 헨리의 이마를 강하게 가격한다.)":
        {"EN": "(THUD!! — The rifle butt of a soldier running from behind strikes Henry hard on the forehead.)",
         "CH": "（砰！！——从后方冲来的士兵，用枪托狠狠砸中亨利的额头。）",
         "JP": "（ゴッ！！——後ろから走ってきた兵士の銃床が、ヘンリーの額を強く殴りつける。）"},
    "윽!": {"EN": "Ugh!", "CH": "唔！", "JP": "うぐっ！"},
    "헨리!! 괜찮아?!": {"EN": "Henry!! Are you okay?!", "CH": "亨利！！你没事吧？！", "JP": "ヘンリー！！大丈夫か？！"},
    "(헨리가 피를 손으로 만져 본다. 붉은 피.)": {"EN": "(Henry touches the blood with his hand. Red blood.)", "CH": "（亨利用手摸了摸血。鲜红的血。）", "JP": "（ヘンリーが手で血に触れる。赤い血。）"},
    "이 상처는 적이 아니라, 아군이 만든 상처였다.": {"EN": "This wound was made not by the enemy, but by his own side.", "CH": "这道伤，不是敌人造成的，而是自己人。", "JP": "この傷は敵ではなく、味方がつけた傷だった。"},
    "헨리!! 살아 있었구나!!": {"EN": "Henry!! You're alive!!", "CH": "亨利！！你还活着！！", "JP": "ヘンリー！！生きてたのか！！"},
    "머리 좀 봐! 치열하게 싸웠나 보다! 대단하다, 영웅이네!":
        {"EN": "Look at his head! He must've fought fiercely! Amazing — a real hero!",
         "CH": "看看他的头！肯定是激战过一场！了不起，真是英雄！",
         "JP": "頭を見ろよ！激しく戦ったんだな！すげえ、英雄じゃないか！"},
    "(헨리는 아무 말도 하지 못한다.)": {"EN": "(Henry can't say a word.)", "CH": "（亨利一句话也说不出来。）", "JP": "（ヘンリーは何も言えない。）"},
    "아무도 진실을 몰랐다.": {"EN": "No one knew the truth.", "CH": "没有人知道真相。", "JP": "誰も真実を知らなかった。"},
    "꽤 깊게 베였군.": {"EN": "That's a pretty deep cut.", "CH": "伤得挺深啊。", "JP": "かなり深く切れているな。"},
    "훈장이네. 멋지다.": {"EN": "A badge of honor. Impressive.", "CH": "这是枚勋章啊。真帅。", "JP": "勲章だな。かっこいいぜ。"},
    "(헨리는 억지로 미소를 짓는다.)": {"EN": "(Henry forces a smile.)", "CH": "（亨利勉强挤出一丝微笑。）", "JP": "（ヘンリーは無理に笑みを浮かべる。）"},
    "① \"사실을 말하는 게 어때?\"": {"EN": "\"Why not tell the truth?\"", "CH": "\"要不说出实情吧？\"", "JP": "\"本当のことを話したらどうだ？\""},
    "거짓으로 얻은 존경은 언젠가 널 더 힘들게 할 거야.":
        {"EN": "Respect won through a lie will only make things harder for you someday.",
         "CH": "靠谎言换来的尊敬，总有一天会让你更难受。",
         "JP": "嘘で得た尊敬は、いつか君をもっと苦しめるよ。"},
    "잠시 후. 헨리는 소대장에게 사실을 털어놓는다.": {"EN": "A while later, Henry confesses the truth to the platoon leader.", "CH": "片刻后。亨利向排长坦白了实情。", "JP": "しばらくして。ヘンリーは小隊長に真実を打ち明ける。"},
    "뭐라고?": {"EN": "What?", "CH": "什么？", "JP": "何だと？"},
    "(잠시 웃음이 터진다. 그러나 윌슨이 먼저 입을 연다.)": {"EN": "(Laughter breaks out for a moment. But Wilson speaks first.)", "CH": "（一阵哄笑。但威尔逊先开了口。）", "JP": "（一瞬、笑いが起こる。だが、先に口を開いたのはウィルソンだった。）"},
    "도망친 적 없는 사람이 어디 있다고. 적어도 거짓을 인정할 용기는 있었네.":
        {"EN": "Who here has never run? At least you had the courage to admit the lie.",
         "CH": "谁没逃过啊。起码你有承认谎言的勇气。",
         "JP": "逃げたことのない奴なんているもんか。少なくとも、嘘を認める勇気はあったな。"},
    "② \"굳이 말하지 않아도 돼.\"": {"EN": "\"You don't have to say anything.\"", "CH": "\"没必要非说出来。\"", "JP": "\"無理に言わなくてもいいよ。\""},
    "살아남는 게 먼저였잖아.": {"EN": "Surviving came first.", "CH": "活下来才是最重要的。", "JP": "生き延びるのが先だっただろ。"},
    "…… 고마워.": {"EN": "...Thank you.", "CH": "……谢谢。", "JP": "……ありがとう。"},
    "(병사들이 계속 헨리를 칭찬한다. 헨리는 웃지만 표정은 굳어 있다.)":
        {"EN": "(The soldiers keep praising Henry. He smiles, but his face is stiff.)",
         "CH": "（士兵们不停地夸赞亨利。亨利笑着，表情却僵硬。）",
         "JP": "（兵士たちはヘンリーを称え続ける。ヘンリーは笑うが、表情はこわばっている。）"},
    "(헨리 속마음) 나는… 영웅이 아니다.": {"EN": "(Henry's thoughts) I'm... not a hero.", "CH": "（亨利心声）我…不是英雄。", "JP": "（ヘンリーの心の声）俺は…英雄なんかじゃない。"},
    "③ \"네가 결정해.\"": {"EN": "\"It's your call.\"", "CH": "\"由你来决定。\"", "JP": "\"君が決めればいい。\""},
    "거짓을 안고 살지, 진실을 말할지는 네 선택이야.":
        {"EN": "Whether you live with the lie or tell the truth is your choice.",
         "CH": "是背着谎言活下去，还是说出真相，由你选择。",
         "JP": "嘘を抱えて生きるか、真実を話すかは、君の選択だ。"},
    "헨리는 결국 아무 말도 하지 않는다.": {"EN": "In the end, Henry says nothing.", "CH": "亨利最终什么也没说。", "JP": "ヘンリーは結局、何も言わなかった。"},
    "밤. 병사들이 잠들었다. 헨리 혼자 깨어 있다.": {"EN": "Night. The soldiers are asleep. Only Henry is awake.", "CH": "夜晚。士兵们都睡了。只有亨利醒着。", "JP": "夜。兵士たちは眠りについた。ヘンリーだけが起きている。"},
    "플레이어. 나, 사실 아직도 무섭다. 다음 전투에서도 도망칠까 봐.":
        {"EN": "You know, I'm... honestly still scared. Afraid I'll run again in the next battle.",
         "CH": "你啊。其实我…到现在还是害怕。怕下一场仗又会逃跑。",
         "JP": "なあ。俺、実はまだ怖いんだ。次の戦いでも逃げちまうんじゃないかって。"},
    "① \"도망칠 수도 있어.\"": {"EN": "\"You might run. And that's okay.\"", "CH": "\"逃跑也是有可能的。\"", "JP": "\"逃げるかもしれない。それでもいい。\""},
    "…… 그렇게 말해 주니까, 오히려 버틸 수 있을 것 같아.":
        {"EN": "...Strangely, hearing you say that makes me feel I can hold on.",
         "CH": "……你这么说，我反倒觉得能撑下去了。",
         "JP": "……そう言ってくれると、かえって踏ん張れそうな気がするよ。"},
    "② \"이번엔 다를 거야.\"": {"EN": "\"It'll be different this time.\"", "CH": "\"这次会不一样的。\"", "JP": "\"今度は違うさ。\""},
    "…… 그럴까. 그러길 바라.": {"EN": "...You think so? I hope so.", "CH": "……是吗。但愿如此。", "JP": "……そうかな。そうだといいけど。"},
    "③ \"모르겠어.\"": {"EN": "\"I don't know.\"", "CH": "\"我不知道。\"", "JP": "\"わからない。\""},
    "헨리는 아무 말 없이 하늘만 바라본다.": {"EN": "Henry gazes at the sky without a word.", "CH": "亨利一言不发，只望着天空。", "JP": "ヘンリーは何も言わず、ただ空を見上げている。"},
    "「붉은 무공훈장」": {"EN": "The Red Badge of Courage", "CH": "「红色英勇勋章」", "JP": "「赤い武功章」"},
    "CHAPTER 3 RESULT 「붉은 무공훈장」": {"EN": "CHAPTER 3 RESULT — The Red Badge of Courage", "CH": "第三章 结算 「红色英勇勋章」", "JP": "第三章 リザルト 「赤い武功章」"},

    # ── CHAPTER 4 ──
    "CHAPTER 4": {"EN": "CHAPTER 4", "CH": "第四章", "JP": "第四章"},
    "용기의 의미": {"EN": "The Meaning of Courage", "CH": "勇气的意义", "JP": "勇気の意味"},
    "용기는 두려움이 없는 것이 아니라, 두려움을 인정하고도 행동하는 것이다.":
        {"EN": "Courage is not the absence of fear, but acting even while admitting it.",
         "CH": "勇气不是没有恐惧，而是承认恐惧却依然行动。",
         "JP": "勇気とは恐怖がないことではなく、恐怖を認めてなお行動することだ。"},
    "새벽. 안개가 자욱하다. 병사들은 말없이 장비를 챙긴다. 누구도 농담하지 않는다.":
        {"EN": "Dawn. Thick fog. The soldiers gather their gear in silence. No one jokes.",
         "CH": "黎明。浓雾弥漫。士兵们默默地整理装备。没有人开玩笑。",
         "JP": "夜明け。霧が立ち込めている。兵士たちは黙って装備を整える。誰も冗談を言わない。"},
    "오늘은 모두가 조용했다.": {"EN": "Today, everyone was quiet.", "CH": "今天，所有人都很安静。", "JP": "今日は、みんな静かだった。"},
    "잠 못 잤어?": {"EN": "Couldn't sleep?", "CH": "没睡好吗？", "JP": "眠れなかった？"},
    "…… 어젯밤 계속 생각했어. 다음에도 도망칠까 봐.":
        {"EN": "...I kept thinking all last night. Afraid I'd run again.",
         "CH": "……昨晚一直在想。怕下次又会逃。",
         "JP": "……昨夜、ずっと考えてた。次も逃げちまうんじゃないかって。"},
    "① \"무서운 건 당연해.\"": {"EN": "\"It's natural to be afraid.\"", "CH": "\"害怕是理所当然的。\"", "JP": "\"怖いのは当たり前だよ。\""},
    "…… 그래도 이번엔, 도망치고 싶지 않아.": {"EN": "...Still, this time, I don't want to run.", "CH": "……可这次，我不想逃了。", "JP": "……それでも今度は、逃げたくないんだ。"},
    "② \"이번엔 달라질 거야.\"": {"EN": "\"You'll be different this time.\"", "CH": "\"这次你会不一样的。\"", "JP": "\"今度は変われるさ。\""},
    "…… 그 말, 믿어 볼게.": {"EN": "...I'll try to believe that.", "CH": "……这话，我信了。", "JP": "……その言葉、信じてみるよ。"},
    "③ \"군인은 싸워야 해.\"": {"EN": "\"A soldier has to fight.\"", "CH": "\"军人就该战斗。\"", "JP": "\"軍人は戦わなきゃならない。\""},
    "…… 그래. 군인이니까.": {"EN": "...Right. Because I'm a soldier.", "CH": "……对。因为是军人。", "JP": "……ああ。軍人だからな。"},
    "(나팔. 포성.)": {"EN": "(A bugle. Cannon fire.)", "CH": "（号角。炮声。）", "JP": "（ラッパ。砲声。）"},
    "북군이 달린다. 헨리도 달린다. 플레이어도 함께 뛰기 시작한다.": {"EN": "The Union soldiers charge. Henry runs. You start running with them.", "CH": "北军冲锋。亨利也在跑。你也开始一起奔跑。", "JP": "北軍が駆ける。ヘンリーも駆ける。あなたも一緒に走り出す。"},
    "(포탄이 터진다. 한 병사가 다리를 붙잡고 쓰러진다.)": {"EN": "(A shell explodes. A soldier falls, clutching his leg.)", "CH": "（炮弹爆炸。一名士兵抱着腿倒下。）", "JP": "（砲弾が炸裂する。一人の兵士が足を押さえて倒れる。）"},
    "살려줘…": {"EN": "Help me...", "CH": "救救我…", "JP": "助けてくれ…"},
    "멈추지 마!!": {"EN": "Don't stop!!", "CH": "别停下！！", "JP": "止まるな！！"},
    "① 병사를 구한다.": {"EN": "Save the soldier.", "CH": "救那名士兵。", "JP": "兵士を助ける。"},
    "헨리! 같이 들자!": {"EN": "Henry! Help me lift him!", "CH": "亨利！一起抬！", "JP": "ヘンリー！一緒に運ぼう！"},
    "알겠어!": {"EN": "Got it!", "CH": "好！", "JP": "わかった！"},
    "(둘이 병사를 부축한다.)": {"EN": "(The two of you support the soldier.)", "CH": "（两人搀扶起那名士兵。）", "JP": "（二人で兵士を支える。）"},
    "고맙다…": {"EN": "Thank you...", "CH": "谢谢…", "JP": "ありがとう…"},
    "기억 조각 : 탄피": {"EN": "Memory Fragment : Cartridge Case", "CH": "记忆碎片 : 弹壳", "JP": "記憶の欠片 : 薬莢"},
    "누군가를 구한 순간, 주머니에 남은 한 발.": {"EN": "A single round left in your pocket from the moment you saved someone.", "CH": "救下某人的那一刻，留在口袋里的一发子弹。", "JP": "誰かを救ったその瞬間、ポケットに残った一発。"},
    "탄피": {"EN": "Cartridge Case", "CH": "弹壳", "JP": "薬莢"},
    "② 명령을 따른다.": {"EN": "Follow orders.", "CH": "服从命令。", "JP": "命令に従う。"},
    "이를 악물고 명령을 따라 앞으로 달린다. 뒤를 돌아보지 않는다.":
        {"EN": "Gritting your teeth, you obey the order and run forward. You don't look back.",
         "CH": "咬紧牙关，遵从命令向前奔跑。你没有回头。",
         "JP": "歯を食いしばり、命令に従って前へ走る。振り返らない。"},
    "③ 헨리의 판단을 따른다.": {"EN": "Follow Henry's judgment.", "CH": "听从亨利的判断。", "JP": "ヘンリーの判断に従う。"},
    "…… 구하자. 그냥 둘 순 없어.": {"EN": "...Let's save him. We can't just leave him.", "CH": "……救他吧。不能就这么丢下。", "JP": "……助けよう。放ってはおけない。"},
    "적군의 공격. 북군의 연대기(깃발)가 땅에 떨어진다.": {"EN": "The enemy attacks. The Union regimental colors fall to the ground.", "CH": "敌军进攻。北军的团旗（军旗）落到了地上。", "JP": "敵の攻撃。北軍の連隊旗（軍旗）が地に落ちる。"},
    "깃발이!!": {"EN": "The flag!!", "CH": "军旗！！", "JP": "旗が！！"},
    "순간 모두가 멈춘다. 헨리는 깃발을 바라본다.": {"EN": "For a moment everyone freezes. Henry stares at the flag.", "CH": "刹那间所有人都停住了。亨利凝视着那面旗。", "JP": "一瞬、全員が動きを止める。ヘンリーは旗を見つめる。"},
    "헨리!": {"EN": "Henry!", "CH": "亨利！", "JP": "ヘンリー！"},
    "(헨리 독백) 난 도망쳤던 병사다.": {"EN": "(Henry's thoughts) I'm the soldier who ran.", "CH": "（亨利独白）我是逃跑过的士兵。", "JP": "（ヘンリーの独白）俺は逃げた兵士だ。"},
    "…… 하지만 이번에는.": {"EN": "...But this time.", "CH": "……但这一次。", "JP": "……でも、今度は。"},
    "이번엔, 내가 가.": {"EN": "This time, I'll go.", "CH": "这次，我上。", "JP": "今度は、俺が行く。"},
    "헨리가 깃발을 집어 든다. 바람에 연대기가 휘날린다.": {"EN": "Henry picks up the flag. The colors stream in the wind.", "CH": "亨利拾起军旗。团旗在风中猎猎飘扬。", "JP": "ヘンリーが旗を拾い上げる。連隊旗が風にはためく。"},
    "깃발이다!! 따라가!!": {"EN": "The flag!! Follow it!!", "CH": "军旗！！跟上去！！", "JP": "旗だ！！続け！！"},
    "각성": {"EN": "AWAKENING", "CH": "觉醒", "JP": "覚醒"},
    "용기 ▲ +20": {"EN": "Courage ▲ +20", "CH": "勇气 ▲ +20", "JP": "勇気 ▲ +20"},
    "사회적역할 ▲ +10": {"EN": "Duty ▲ +10", "CH": "社会角色 ▲ +10", "JP": "社会的役割 ▲ +10"},
    "죄책감 ▼ -10": {"EN": "Guilt ▼ -10", "CH": "罪恶感 ▼ -10", "JP": "罪悪感 ▼ -10"},
    "기억 조각 : 마지막 깃발": {"EN": "Memory Fragment : The Last Flag", "CH": "记忆碎片 : 最后的军旗", "JP": "記憶の欠片 : 最後の旗"},
    "두려움을 안고 든 깃발.": {"EN": "A flag raised while holding onto fear.", "CH": "怀着恐惧举起的旗帜。", "JP": "恐怖を抱えたまま掲げた旗。"},
    "마지막 깃발": {"EN": "The Last Flag", "CH": "最后的军旗", "JP": "最後の旗"},
    "병사들이 헨리를 따라 돌진한다. 총성. 포성. 함성.": {"EN": "The soldiers charge after Henry. Gunfire. Cannon. War cries.", "CH": "士兵们跟着亨利冲锋。枪声。炮声。呐喊。", "JP": "兵士たちがヘンリーに続いて突進する。銃声。砲声。雄叫び。"},
    "무섭다. 아직도. 정말 무섭다.": {"EN": "I'm scared. Still. I'm truly scared.", "CH": "害怕。依然。真的很害怕。", "JP": "怖い。今でも。本当に怖い。"},
    "(잠시 침묵.)": {"EN": "(A brief silence.)", "CH": "（短暂的沉默。）", "JP": "（しばしの沈黙。）"},
    "하지만. 두려운 채로 앞으로 가는 것도, 용기일 수 있잖아.":
        {"EN": "But... going forward while still afraid — that can be courage too, right?",
         "CH": "但是。带着恐惧仍向前走，这也可以是勇气吧。",
         "JP": "でも。怖いまま前へ進むことも、勇気って言えるだろ。"},
    "① \"같이 가자.\"": {"EN": "\"Let's go together.\"", "CH": "\"一起走吧。\"", "JP": "\"一緒に行こう。\""},
    "같이 가자. 혼자가 아니야.": {"EN": "Let's go together. You're not alone.", "CH": "一起走。你不是一个人。", "JP": "一緒に行こう。君は一人じゃない。"},
    "(헨리가 미소 짓는다. 둘은 함께 전진한다.)": {"EN": "(Henry smiles. The two advance together.)", "CH": "（亨利微笑。两人一同前进。）", "JP": "（ヘンリーが微笑む。二人は共に前進する。）"},
    "② \"앞으로!\"": {"EN": "\"Forward!\"", "CH": "\"前进！\"", "JP": "\"前へ！\""},
    "앞으로!": {"EN": "Forward!", "CH": "前进！", "JP": "前へ！"},
    "③ \"뒤로 빠져!\"": {"EN": "\"Fall back!\"", "CH": "\"退后！\"", "JP": "\"下がれ！\""},
    "뒤로 빠져! 무리하지 마!": {"EN": "Fall back! Don't push yourself!", "CH": "退后！别硬撑！", "JP": "下がれ！無理するな！"},
    "(총성이 멈춘다. 해가 지고 있다.)": {"EN": "(The gunfire stops. The sun is setting.)", "CH": "（枪声停止。夕阳西下。）", "JP": "（銃声が止む。陽が沈んでいく。）"},
    "이겼다!": {"EN": "We won!", "CH": "我们赢了！", "JP": "勝ったぞ！"},
    "(환호. 그러나 헨리는 웃지 않는다.)": {"EN": "(Cheers. But Henry does not smile.)", "CH": "（欢呼。但亨利没有笑。）", "JP": "（歓声。だがヘンリーは笑わない。）"},
    "왜 그래?": {"EN": "What's wrong?", "CH": "怎么了？", "JP": "どうしたの？"},
    "짐이 생각났어. 이긴 사람보다, 돌아오지 못한 사람이 먼저 떠올랐어.":
        {"EN": "I thought of Jim. Before the winners, it was those who never came back that came to mind.",
         "CH": "我想起了吉姆。比起获胜的人，先浮现的是那些回不来的人。",
         "JP": "ジムを思い出した。勝った者より、帰れなかった者が先に浮かんだんだ。"},
    "플레이어. 고마워. 넌 내가 어떤 사람이 되어야 한다고 강요하지 않았어. 그냥 내 이야기를 들어줬잖아.":
        {"EN": "Thank you. You never forced me to become someone. You just listened to my story.",
         "CH": "谢谢你。你从没强迫我该成为什么样的人。你只是倾听了我的故事。",
         "JP": "ありがとう。君は、俺がどんな人間になるべきかを押し付けなかった。ただ、俺の話を聞いてくれた。"},
    "헨리와 플레이어가 노을을 바라본다.": {"EN": "Henry and you gaze at the sunset.", "CH": "亨利与你眺望着晚霞。", "JP": "ヘンリーとあなたは夕焼けを見つめる。"},
    "덕분에 난 나 자신을, 조금은 용서할 수 있을 것 같아.":
        {"EN": "Thanks to you, I think I can forgive myself, at least a little.",
         "CH": "多亏了你，我觉得自己能稍微原谅自己了。",
         "JP": "君のおかげで、俺は自分を、少しは許せそうな気がするよ。"},
    "(헨리 속마음) 하지만 나는 아직, 나를 완전히 용서하지 못했다.":
        {"EN": "(Henry's thoughts) But I still haven't fully forgiven myself.",
         "CH": "（亨利心声）但我还是，没能完全原谅自己。",
         "JP": "（ヘンリーの心の声）だが俺はまだ、自分を完全には許せていない。"},
    "『용기의 의미』": {"EN": "The Meaning of Courage", "CH": "《勇气的意义》", "JP": "『勇気の意味』"},
    "CHAPTER 4 RESULT 「용기의 의미」": {"EN": "CHAPTER 4 RESULT — The Meaning of Courage", "CH": "第四章 结算 「勇气的意义」", "JP": "第四章 リザルト 「勇気の意味」"},

    # ── CHAPTER 5 ──
    "CHAPTER 5": {"EN": "CHAPTER 5", "CH": "第五章", "JP": "第五章"},
    "당신이라면 어떤 선택을 하겠습니까": {"EN": "What Choice Would You Make?", "CH": "如果是你，会做出怎样的选择", "JP": "あなたなら、どんな選択をしますか"},
    "전쟁은 영웅을 만드는가, 아니면 인간을 시험하는가.": {"EN": "Does war make heroes, or does it test humanity?", "CH": "战争是造就英雄，还是考验人性。", "JP": "戦争は英雄を作るのか、それとも人間を試すのか。"},
    "(전투가 끝난다. 총성이 멎는다. 주변은 조용하다.)": {"EN": "(The battle ends. The gunfire dies. All around is quiet.)", "CH": "（战斗结束。枪声平息。四周一片寂静。）", "JP": "（戦いが終わる。銃声が止む。あたりは静かだ。）"},
    "갑자기, 플레이어가 가지고 있던 『붉은 무공훈장』이 빛나기 시작한다.":
        {"EN": "Suddenly, the copy of 'The Red Badge of Courage' you were holding begins to glow.",
         "CH": "突然，你手中的《红色英勇勋章》开始发光。",
         "JP": "突然、あなたが持っていた『赤い武功章』が輝き始める。"},
    "…… 이 빛은…": {"EN": "...This light...", "CH": "……这光…", "JP": "……この光は…"},
    "돌아갈 시간이네.": {"EN": "Time for you to go back.", "CH": "该回去了。", "JP": "帰る時間だな。"},
    "뭐?": {"EN": "What?", "CH": "什么？", "JP": "え？"},
    "넌 원래 여기 사람이 아니잖아.": {"EN": "You don't belong here, after all.", "CH": "你本来就不属于这里。", "JP": "君は元々、ここの人間じゃないだろ。"},
    "처음부터 알고 있었어.": {"EN": "I knew from the start.", "CH": "我从一开始就知道。", "JP": "最初から知ってたよ。"},
    "알고 있었는데 왜 말 안 했어?": {"EN": "You knew, so why didn't you say anything?", "CH": "既然知道，为什么不说？", "JP": "知ってたのに、どうして言わなかったの？"},
    "누군가에게 내 이야기를, 들려주고 싶었거든.": {"EN": "Because I wanted to tell someone my story.", "CH": "因为我想把我的故事，讲给某个人听。", "JP": "誰かに、俺の話を聞いてほしかったんだ。"},
    "헨리와 플레이어가 천천히 걸어간다. 멀리 노을이 진다.": {"EN": "Henry and you walk slowly. Far away, the sun sets.", "CH": "亨利与你缓缓走着。远处，夕阳西沉。", "JP": "ヘンリーとあなたはゆっくりと歩く。遠くで夕日が沈む。"},
    "① \"넌 영웅이야.\"": {"EN": "\"You're a hero.\"", "CH": "\"你是英雄。\"", "JP": "\"君は英雄だ。\""},
    "…… 정말?": {"EN": "...Really?", "CH": "……真的？", "JP": "……本当に？"},
    "두려웠지만 끝내 앞으로 나아갔잖아.": {"EN": "You were afraid, but in the end you moved forward.", "CH": "你虽然害怕，最终还是向前迈进了。", "JP": "怖かったけど、最後には前へ進んだじゃないか。"},
    "② \"넌 인간이야.\"": {"EN": "\"You're human.\"", "CH": "\"你是个人。\"", "JP": "\"君は人間だ。\""},
    "넌 영웅 이전에 인간이야. 살고 싶었던 것도, 무서웠던 것도, 모두 인간다운 감정이야.":
        {"EN": "Before being a hero, you're human. Wanting to live, being afraid — those are all human feelings.",
         "CH": "在成为英雄之前，你是个人。想活下去，会害怕，都是人之常情。",
         "JP": "君は英雄である前に、人間だ。生きたかったことも、怖かったことも、全部、人間らしい感情だよ。"},
    "…… 그 말을, 누군가에게 듣고 싶었어.": {"EN": "...I wanted to hear those words from someone.", "CH": "……这句话，我一直想从某个人那里听到。", "JP": "……その言葉を、誰かに言ってほしかったんだ。"},
    "③ \"아직 잘 모르겠어.\"": {"EN": "\"I'm still not sure.\"", "CH": "\"我还不太确定。\"", "JP": "\"まだよくわからない。\""},
    "나도, 아직 답을 모르겠어.": {"EN": "I don't know the answer yet, either.", "CH": "我也，还不知道答案。", "JP": "俺も、まだ答えはわからないよ。"},
    "빛이 점점 강해진다.": {"EN": "The light grows stronger and stronger.", "CH": "光越来越强。", "JP": "光がだんだん強くなっていく。"},

    # ── ENDINGS ──
    "나는 전쟁이 영웅을 만든다고 생각했다. 하지만 전쟁은 사람에게 끝없이 선택을 강요했다.":
        {"EN": "I thought war made heroes. But war endlessly forced people to choose.",
         "CH": "我曾以为战争造就英雄。但战争，只是无止境地逼迫人做出选择。",
         "JP": "私は戦争が英雄を作ると思っていた。だが戦争は、人に果てしなく選択を強いた。"},
    "살 것인가. 남을 것인가. 진실을 말할 것인가. 숨길 것인가.":
        {"EN": "To live, or to stay. To speak the truth, or to hide it.",
         "CH": "是活下去，还是留下。是说出真相，还是隐瞒。",
         "JP": "生きるのか。留まるのか。真実を語るのか。隠すのか。"},
    "(회상) …… 나, 무섭다.": {"EN": "(Flashback) ...I'm scared.", "CH": "（回想）……我，害怕。", "JP": "（回想）……俺、怖いんだ。"},
    "그 말을 할 수 있었던 순간부터. 넌 이미 용기 있는 사람이었어.":
        {"EN": "From the moment you could say those words, you were already a person of courage.",
         "CH": "从你能说出那句话的那一刻起，你就已经是个勇敢的人了。",
         "JP": "その言葉を言えた瞬間から。君はもう、勇気ある人間だったんだ。"},
    "(헨리가 플레이어를 향해 웃는다.)": {"EN": "(Henry smiles at you.)", "CH": "（亨利朝你微笑。）", "JP": "（ヘンリーがあなたに向かって微笑む。）"},
    "고마워. 이제 나는… 나를 미워하지 않아.": {"EN": "Thank you. Now I... don't hate myself anymore.", "CH": "谢谢你。现在我…不再讨厌自己了。", "JP": "ありがとう。今の俺は…自分を嫌いじゃない。"},
    "책이 천천히 닫힌다.": {"EN": "The book slowly closes.", "CH": "书缓缓合上。", "JP": "本がゆっくりと閉じる。"},
    "「진정한 용기」": {"EN": "True Courage", "CH": "「真正的勇气」", "JP": "「本当の勇気」"},
    "용기는 두려움이 없는 것이 아니라, 두려움을 인정하는 것이었다.":
        {"EN": "Courage was not the absence of fear, but the admission of it.",
         "CH": "勇气不是没有恐惧，而是承认恐惧。",
         "JP": "勇気とは恐怖がないことではなく、恐怖を認めることだった。"},
    "헨리는 살아남았다. 하지만 끝까지 말이 적었다.": {"EN": "Henry survived. But he stayed quiet to the end.", "CH": "亨利活了下来。但直到最后都寡言少语。", "JP": "ヘンリーは生き延びた。だが最後まで、口数は少なかった。"},
    "헨리는 완벽한 영웅이 아니었다. 하지만 도망쳤던 기억을 안고도, 앞으로 걸어갔다.":
        {"EN": "Henry was not a perfect hero. But even carrying the memory of running, he walked forward.",
         "CH": "亨利并非完美的英雄。但即便背负着逃跑的记忆，他仍向前走去。",
         "JP": "ヘンリーは完璧な英雄ではなかった。だが逃げた記憶を抱えたまま、前へ歩いていった。"},
    "그래도… 그는 앞으로 걸어갈 것이다. 그것만으로도 충분했다.":
        {"EN": "Still... he will keep walking forward. And that alone was enough.",
         "CH": "但…他会继续向前走。仅此就已足够。",
         "JP": "それでも…彼は前へ歩いていくだろう。それだけで、十分だった。"},
    "「앞으로 나아간 사람」": {"EN": "The One Who Walked On", "CH": "「向前迈进的人」", "JP": "「前へ進んだ人」"},
    "진엔딩보다 여운이 남는, 한 사람의 뒷모습.":
        {"EN": "A lingering image — one man's back, more haunting than the true ending.",
         "CH": "比真结局更令人回味的，一个人的背影。",
         "JP": "トゥルーエンドよりも余韻の残る、一人の後ろ姿。"},
    "현실로 돌아왔다. 책은 원래 자리에 그대로 있다.": {"EN": "I'm back in reality. The book sits right where it was.", "CH": "回到了现实。书还在原来的地方。", "JP": "現実に戻ってきた。本は元の場所にそのままある。"},
    "전쟁은 정답을 주지 않았다. 나는 아직도 모르겠다. 용기란 무엇인지.":
        {"EN": "War gave no answer. I still don't know what courage is.",
         "CH": "战争没有给出答案。我至今仍不明白，勇气究竟是什么。",
         "JP": "戦争は答えをくれなかった。私は今でもわからない。勇気とは何なのか。"},
    "「정답 없는 질문」": {"EN": "A Question Without an Answer", "CH": "「没有答案的问题」", "JP": "「答えのない問い」"},
    "원작의 분위기와 가장 닮은 결말.": {"EN": "The ending closest in spirit to the original novel.", "CH": "与原著气质最为相似的结局。", "JP": "原作の雰囲気に最も近い結末。"},
    "헨리는 끝까지 아무 말도 하지 않았다. 병사들은 그를 영웅이라 불렀다.":
        {"EN": "Henry said nothing to the very end. The soldiers called him a hero.",
         "CH": "亨利到最后什么也没说。士兵们称他为英雄。",
         "JP": "ヘンリーは最後まで何も言わなかった。兵士たちは彼を英雄と呼んだ。"},
    "그러나 그는, 자신을 끝내 용서하지 못했다.": {"EN": "But he never forgave himself in the end.", "CH": "然而他，终究没能原谅自己。", "JP": "だが彼は、最後まで自分を許せなかった。"},
    "넌… 결국 다른 사람들처럼, 날 겁쟁이로만 봤어.":
        {"EN": "You... in the end, like everyone else, only saw me as a coward.",
         "CH": "你…最终还是和其他人一样，只把我当成懦夫。",
         "JP": "君も…結局、他の連中と同じように、俺を臆病者としか見なかったんだ。"},
    "(헨리가 등을 돌린다.)": {"EN": "(Henry turns his back.)", "CH": "（亨利转过身去。）", "JP": "（ヘンリーが背を向ける。）"},
    "나는 끝내 그를 이해하지 못했다.": {"EN": "In the end, I never understood him.", "CH": "我终究没能理解他。", "JP": "私は最後まで、彼を理解できなかった。"},
    "빛. 도서관. 책을 덮는다.": {"EN": "Light. The library. The book closes.", "CH": "光。图书馆。合上书。", "JP": "光。図書館。本を閉じる。"},
    "표지의 제목이, 피처럼 붉게 물든다.": {"EN": "The title on the cover stains red, like blood.", "CH": "封面上的书名，染上了血一般的红。", "JP": "表紙の題名が、血のように赤く染まる。"},
    "이번에는, 그 제목이 전혀 다르게 보인다.": {"EN": "This time, that title looks completely different.", "CH": "这一次，那个书名看起来截然不同。", "JP": "今度は、その題名がまるで違って見える。"},
    "도서관. 플레이어는 책 마지막 장을 펼친다. 원래는 없던 한 줄이 나타난다.":
        {"EN": "The library. You open to the last page. A line that wasn't there before appears.",
         "CH": "图书馆。你翻开书的最后一页。一行原本没有的字浮现出来。",
         "JP": "図書館。あなたは本の最後のページを開く。元はなかった一行が現れる。"},
    "\"전쟁은 인간을 영웅으로 만들지 않는다.": {"EN": "\"War does not make people into heroes.", "CH": "「战争不会把人变成英雄。", "JP": "「戦争は人間を英雄にはしない。"},
    "인간을 인간으로 드러낼 뿐이다.\"": {"EN": "It only reveals people as human.\"", "CH": "它只是让人显露出人的本相。」", "JP": "ただ、人間を人間として露わにするだけだ。」"},
    "(목소리) …… 고마워.": {"EN": "(A voice) ...Thank you.", "CH": "（声音）……谢谢。", "JP": "（声）……ありがとう。"},
    "나는 전쟁을 이해한 것이 아니다. 나는 전쟁 속에서도 끝까지 인간으로 남으려 했던 사람을, 이해하게 되었다.":
        {"EN": "I didn't come to understand war. I came to understand a person who, even in war, tried to remain human to the end.",
         "CH": "我理解的不是战争。我理解的，是一个在战争中仍努力做人到最后的人。",
         "JP": "私は戦争を理解したのではない。戦争の中でも最後まで人間であろうとした一人の人を、理解したのだ。"},
    "획득한 기억 조각들이 책갈피가 되어 남는다.": {"EN": "The memory fragments you gathered remain as bookmarks.", "CH": "收集到的记忆碎片，化作书签留存下来。", "JP": "集めた記憶の欠片が、しおりとなって残る。"},
    "책갈피가 된 기억 조각": {"EN": "Memory Fragments Turned to Bookmarks", "CH": "化作书签的记忆碎片", "JP": "しおりになった記憶の欠片"},
    "군복 · 짐의 군번줄 · 붉은 손수건 · 탄피 · 마지막 깃발":
        {"EN": "Uniform · Jim's Dog Tags · Red Handkerchief · Cartridge Case · The Last Flag",
         "CH": "军服 · 吉姆的军牌 · 红手帕 · 弹壳 · 最后的军旗",
         "JP": "軍服 · ジムの認識票 · 赤いハンカチ · 薬莢 · 最後の旗"},
    "「인간이라는 이름」": {"EN": "The Name of Human", "CH": "「名为人类」", "JP": "「人間という名」"},
    "모든 것을 본 사람만이 도달하는 결말.": {"EN": "An ending reached only by those who have seen everything.", "CH": "只有看遍一切的人才能抵达的结局。", "JP": "すべてを見た者だけがたどり着く結末。"},
}


# ── 헬퍼 ─────────────────────────────────────────────
def t(text):
    """스토리 텍스트 번역. KR 또는 미등록 문자열은 원문 그대로."""
    if text is None or current == "KR":
        return text
    e = TR.get(text)
    if e:
        return e.get(current, text)
    return text


def nm(name):
    """화자 이름 번역. 화자가 '나'이고 플레이어 이름이 설정돼 있으면 그 이름을 쓴다."""
    if name == "나" and player_name:
        return player_name
    if name is None or current == "KR":
        return name
    e = NAMES.get(name)
    return e.get(current, name) if e else name


def stat(key):
    """스탯 내부키 → 현재 언어 라벨."""
    d = STAT.get(key)
    if not d:
        return key
    return d.get(current, d.get("KR", key))


def ui(key, **kw):
    """UI 문자열 (템플릿 포맷 지원)."""
    d = UI.get(key, {})
    s = d.get(current) or d.get("KR") or key
    return s.format(**kw) if kw else s
