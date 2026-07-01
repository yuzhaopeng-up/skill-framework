# 垂直行业蓝图：教育 (Education)

**Industry Code**: `education`
**版本**: v1.0
**状态**: 蓝图

---

## 1. 行业特征与约束

| 维度 | 特征 | 对Skill设计的影响 |
|------|------|-------------------|
| **学段差异大** | K12 / 高校 / 职业 / 企业培训 / 终身教育 | Skill按学段分组 |
| **未成年保护** | K12涉及未成年，受《未成年人保护法》《个人信息保护法》约束 | 严格隐私+家长知情同意 |
| **教学闭环** | 备课→授课→练习→批改→评估→反馈 | 流程可标准化 |
| **多角色** | 教师/学生/家长/教研/管理者 | 多端Skill |
| **强内容性** | 教材/题库/课件/视频/作业 | 需要内容生成与版权管理 |
| **效果评估** | 学习效果难量化、长周期 | 需多维度评估指标 |

---

## 2. 核心场景地图

| 场景 | 描述 | L2复用 | L3 SkillID |
|------|------|--------|-------------|
| AI备课助手 | 课标+教材→教案+课件+练习题 | document_pipeline + taskflow | `l3_lesson_planning` |
| 智能批改 | 作业（文本/图片）→批改+订正建议 | document_pipeline | `l3_homework_grading` |
| 个性化学习路径 | 学情数据→定制学习计划+资源推荐 | taskflow + alert_engine | `l3_personalized_path` |
| 学情分析报告 | 班级/学生数据→周/月报+预警 | document_pipeline + cross_channel | `l3_learning_analytics` |
| 智能答疑 | 学生提问→分步讲解+相似题 | cross_channel | `l3_qa_tutor` |
| 课堂AI助教 | 课堂实录→重点摘要+知识点+错题 | document_pipeline | `l3_classroom_assist` |
| 作文/写作辅导 | 作文→评分+修改建议+范文对照 | document_pipeline | `l3_writing_coach` |
| 家校沟通 | 学生表现→家长定期通报+建议 | cross_channel + taskflow | `l3_school_home_link` |
| 试题命制 | 知识点+难度→自动出题+解析 | document_pipeline | `l3_test_generation` |
| 教研协作 | 多教师备课→优质教案沉淀+复用 | taskflow + document_pipeline | `l3_teaching_research` |
| 培训闯关学习 | 学员→关卡式学习+技能确认+证书 | taskflow + cross_channel | `l3_training_quest` |

---

## 3. L0/L1 行业专用Skill需求

### L0 连接器
- `l0_lms_adapter` LMS（学习管理系统）适配（Moodle/钉钉家校本/智学网/学习通）
- `l0_textbook_db` 教材/课标数据库
- `l0_question_bank` 题库系统
- `l0_video_lecture` 录课/直播平台（腾讯课堂/钉钉直播/Zoom）
- `l0_grade_system` 成绩管理系统
- `l0_attendance_system` 考勤系统

### L1 基础能力
- `l1_homework_ocr` 作业图片OCR（手写体识别 / 公式识别 / LaTeX）
- `l1_subject_grader` 学科批改（语文/数学/英语/理化生）
- `l1_essay_score` 作文评分（多维度：审题/结构/语言/卷面）
- `l1_knowledge_graph` 学科知识图谱（K12/学科）
- `l1_difficulty_estimate` 题目难度估计（IRT模型）
- `l1_learning_state` 学情建模（掌握度/遗忘曲线/薄弱点）
- `l1_minor_protect_filter` 未成年保护过滤（不当内容/隐私/营销诱导）

---

## 4. 标杆场景：AI备课助手（详设）

### 4.1 业务价值
教师备课时间从平均 90 分钟/课时缩短到 30 分钟，且产出（教案+课件+练习）一站式齐全。

### 4.2 流程设计

```yaml
flow_id: lesson_planning_v1
input_schema:
  - {name: subject, type: string, required: true}        # 学科
  - {name: grade, type: string, required: true}          # 年级
  - {name: chapter, type: string, required: true}        # 章节
  - {name: lesson_minutes, type: int, default: 40}
  - {name: teaching_style, type: enum, values: [启发式, 讲授式, 探究式, 翻转课堂]}
  - {name: teacher_id, type: string, required: true}

steps:
  - id: load_curriculum
    type: skill_call
    skill: l0_textbook_db
    params:
      subject: "${input.subject}"
      grade: "${input.grade}"
      chapter: "${input.chapter}"
    output: curriculum

  - id: identify_knowledge_points
    type: skill_call
    skill: l1_knowledge_graph
    params:
      action: extract_points
      curriculum: "${curriculum}"
    output: points

  - id: parallel_generate
    type: parallel
    branches:
      - id: lesson_plan
        skill: l1_lesson_plan_generate
        params:
          knowledge_points: "${points}"
          minutes: "${input.lesson_minutes}"
          style: "${input.teaching_style}"
      - id: slides
        skill: l1_slides_generate                # 用 design-md / popular-web-designs
        params:
          points: "${points}"
          template: "education_minimal"
      - id: exercises
        skill: l1_exercises_generate
        params:
          points: "${points}"
          difficulty_distribution: { easy: 0.4, medium: 0.4, hard: 0.2 }
          types: [选择, 填空, 简答, 应用]
      - id: classroom_qa
        skill: l1_classroom_qa_generate
        params: { points: "${points}", count: 8 }
    aggregate: collect_all
    output: lesson_pack

  - id: minor_safety_check
    type: skill_call
    skill: l1_minor_protect_filter
    params: { content: "${lesson_pack}" }
    output: safety
    on_error: { strategy: stop, alert: true }

  - id: deliver_to_teacher
    type: skill_call
    skill: l2_cross_channel_router
    params:
      message_type: report
      title: "${input.subject} ${input.grade} ${input.chapter} 备课包已生成"
      attachments:
        - "${lesson_pack.lesson_plan.docx}"
        - "${lesson_pack.slides.pptx}"
        - "${lesson_pack.exercises.docx}"
      buttons:
        - {text: "一键修改", action: "open_editor"}
        - {text: "提交教研组", action: "submit_to_review"}
      recipients: { channels: [feishu, wecom], targets: ["${input.teacher_id}"] }

  - id: archive_to_research
    type: skill_call
    skill: l0_lms_adapter
    params:
      action: archive_lesson
      teacher_id: "${input.teacher_id}"
      content: "${lesson_pack}"
```

---

## 5. 多Agent协作场景（L4）

| 场景 | 参与Agent | 模式 |
|------|-----------|------|
| **个性化学伴** | 答疑Agent + 学情Agent + 规划Agent + 家长Agent | 长周期协同 |
| **教研组协同备课** | 主备Agent + 同学科Agent + 教研组长Agent | 并行+共识 |
| **多学科融合教学** | 各学科Agent + 主任Agent | 并行+主持 |
| **培训闯关教练** | 关卡Agent + 评估Agent + 反馈Agent | 状态机 |

---

## 6. 治理红线

1. **未成年保护**：K12场景默认严格内容过滤（暴力/不良/营销/诱导）
2. **隐私**：未成年学生数据严禁外发，家长知情同意
3. **教学辅助而非替代**：AI不做"上课"，做"助教"
4. **成绩客观性**：AI批改可作参考，关键考试由教师复核
5. **版权**：教材/题库使用必须授权或自有
6. **不诱导消费**：教培场景不得诱导付费/续课（《"双减"政策》）

---

## 7. 实施路线

| 阶段 | 周期 | 内容 |
|------|------|------|
| Phase 1 | 1-2月 | LMS连接器 + L1批改/OCR + L3备课助手 |
| Phase 2 | 3-4月 | 学情分析 + 答疑 + L3批改/学情 |
| Phase 3 | 5-6月 | 个性化路径 + L4学伴 + 教研协作 |
| Phase 4 | 持续 | 学段拓展（高校/职业/企培）+ 效果评估 |
