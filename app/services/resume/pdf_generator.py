"""PDF resume generator using fpdf2 - no LaTeX required."""

import tempfile
from fpdf import FPDF


def _sanitize_text(text):
    """Remove or replace characters not supported by Helvetica font."""
    if not text:
        return ""
    text = str(text)
    return text.encode('ascii', 'ignore').decode('ascii')


def generate_resume_pdf(data: dict, template_id: str = "ats_standard") -> str:
    """Generate a PDF resume using a specific template style."""
    from app.services.resume.templates import TEMPLATES

    style = TEMPLATES.get(template_id, TEMPLATES["ats_standard"])
    ui = data.get("user_information", {}) or {}

    # ===== DYNAMIC CONTENT ANALYSIS =====
    # Calculate content volume to determine spacing
    experiences = ui.get("experiences", []) or []
    education = ui.get("education", []) or []
    projects = data.get("projects", []) or []
    certs = data.get("certificate", []) or []
    skills = ui.get("skills", {}) or {}
    hard_skills = skills.get("hard_skills", []) or []
    soft_skills = skills.get("soft_skills", []) or []
    
    # Count total content items
    total_bullets = sum(len(exp.get("four_tasks", []) or []) for exp in experiences)
    total_project_goals = sum(len(proj.get("two_goals_of_the_project", []) or []) for proj in projects)
    total_items = len(experiences) + len(education) + len(projects) + len(certs)
    total_text_items = total_bullets + total_project_goals + len(hard_skills) + len(soft_skills)
    
    # Determine spacing tier based on content
    if total_items <= 4 and total_text_items <= 10:
        # LOW content - generous spacing
        spacing_tier = "spacious"
        spacing_cfg = {"margin": 10, "ln_small": 2, "ln_large": 5, "bullet_ln": 1.5, "section_gap": 4}
    elif total_items <= 7 and total_text_items <= 18:
        # MEDIUM content - balanced spacing
        spacing_tier = "balanced"
        spacing_cfg = {"margin": 9, "ln_small": 2, "ln_large": 4, "bullet_ln": 1, "section_gap": 3}
    else:
        # HIGH content - tight spacing to fit one page
        spacing_tier = "compact"
        spacing_cfg = {"margin": 8, "ln_small": 1, "ln_large": 3, "bullet_ln": 0.5, "section_gap": 2}

    class ResumePDF(FPDF):
        def header(self):
            pass

        def footer(self):
            pass  # No footer text

    pdf = ResumePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=False)  # Force ONE page only
    pdf.set_margins(spacing_cfg["margin"], spacing_cfg["margin"], spacing_cfg["margin"])
    
    # Configure Colors based on template
    color_map = {
        "ats_standard": (0, 0, 0),
        "modern_pro": (37, 99, 235), # Blue
        "executive_dark": (40, 40, 40), # Dark Grey
        "creative_flow": (147, 51, 234), # Purple
        "bold_sidebar": (220, 38, 38) # Red
    }
    accent_color = color_map.get(template_id, (0, 0, 0))

    def reset_cursor():
        pdf.set_x(pdf.l_margin)

    def check_page_break(height_needed: float):
        if pdf.get_y() + height_needed > pdf.page_break_trigger:
            pdf.add_page()
            reset_cursor()

    def add_section_title(text):
        pdf.ln(spacing_cfg["ln_large"])
        reset_cursor()
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*accent_color)
        pdf.cell(0, 4.5, _sanitize_text(text).upper(), ln=1)
        reset_cursor()
        pdf.set_draw_color(*accent_color)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y() + 0.25, pdf.w - pdf.r_margin, pdf.get_y() + 0.25)
        pdf.ln(1.5)
        pdf.set_text_color(0, 0, 0)

    def add_body_text(text):
        reset_cursor()
        pdf.set_font('Helvetica', '', 7.5)
        pdf.set_text_color(60, 60, 60)
        line_height = 3.5 if spacing_tier == "compact" else 4
        pdf.multi_cell(0, line_height, _sanitize_text(text), align='J')
        pdf.ln(0.5)

    def add_bullet(items):
        for item in items:
            reset_cursor()
            pdf.set_font('Helvetica', '', 7.5)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 2.5)
            pdf.multi_cell(0, 3.5, f'- {_sanitize_text(item)}', align='J')
        pdf.ln(spacing_cfg["bullet_ln"])
    
    def add_label_value(label, value):
        reset_cursor()
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.cell(0, 5, _sanitize_text(label))
        pdf.ln(5)
        reset_cursor()
        pdf.set_font('Helvetica', '', 9.5)
        pdf.multi_cell(0, 5, _sanitize_text(value))
        pdf.ln(2)
    
    # ===== PAGE 1: HEADER =====
    pdf.add_page()

    # Name - Center aligned
    reset_cursor()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, _sanitize_text(ui.get('name', 'Resume')), align='C', ln=1)

    # Thin line under name
    pdf.set_draw_color(*accent_color)
    pdf.set_line_width(0.25)
    name_width = pdf.get_string_width(_sanitize_text(ui.get('name', 'Resume')))
    line_start = (pdf.w - name_width) / 2 - 3
    line_end = (pdf.w + name_width) / 2 + 3
    pdf.line(line_start, pdf.get_y() + 0.4, line_end, pdf.get_y() + 0.4)
    pdf.ln(1.5)

    # Job Title
    reset_cursor()
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 4.5, _sanitize_text(ui.get('main_job_title', '')), align='C', ln=1)

    # Contact Info
    pdf.set_font('Helvetica', '', 7.5)
    contact_y = pdf.get_y()
    contact_items = []
    
    # Phone
    if ui.get('phone') or ui.get('mobile'):
        phone = ui.get('phone') or ui.get('mobile')
        contact_items.append(('phone', _sanitize_text(phone)))
    
    # Email
    if ui.get('email'):
        contact_items.append(('email', _sanitize_text(ui['email'])))
    
    # LinkedIn
    if ui.get('linkedin'):
        linkedin_text = _sanitize_text(ui['linkedin'])
        if linkedin_text.lower().startswith('linkedin:'):
            linkedin_text = linkedin_text.split(':', 1)[1].strip()
        contact_items.append(('linkedin', linkedin_text))
    
    # GitHub
    if ui.get('github'):
        github_text = _sanitize_text(ui['github'])
        if github_text.lower().startswith('github:'):
            github_text = github_text.split(':', 1)[1].strip()
        contact_items.append(('github', github_text))
    
    # Portfolio
    if ui.get('portfolio'):
        portfolio_text = _sanitize_text(ui['portfolio'])
        if portfolio_text.lower().startswith('http'):
            portfolio_text = portfolio_text.split('//')[1].split('/')[0]
        contact_items.append(('portfolio', portfolio_text))
    
    # LeetCode
    if ui.get('leetcode'):
        leetcode_text = _sanitize_text(ui['leetcode'])
        if leetcode_text.lower().startswith('leetcode:'):
            leetcode_text = leetcode_text.split(':', 1)[1].strip()
        contact_items.append(('leetcode', leetcode_text))
    
    # GeeksforGeeks
    if ui.get('geeksforgeeks'):
        gfg_text = _sanitize_text(ui['geeksforgeeks'])
        if gfg_text.lower().startswith('geeksforgeeks:'):
            gfg_text = gfg_text.split(':', 1)[1].strip()
        contact_items.append(('geeksforgeeks', gfg_text))
    
    # Render contact info - compact with minimal spacing
    if contact_items:
        full_text = ' | '.join([text for _, text in contact_items])
        text_width = pdf.get_string_width(full_text)
        start_x = (pdf.w - text_width) / 2
        pdf.set_x(start_x)

        for i, (item_type, text) in enumerate(contact_items):
            x_start = pdf.get_x()
            text_width = pdf.get_string_width(text)

            if item_type == 'email':
                pdf.set_text_color(0, 102, 204)
                pdf.set_font('Helvetica', 'U', 7.5)
                pdf.cell(text_width, 4, text)
                pdf.link(x_start, contact_y, text_width, 4, f"mailto:{text}")
            elif item_type == 'linkedin':
                pdf.set_text_color(0, 119, 181)
                pdf.set_font('Helvetica', 'U', 7.5)
                pdf.cell(text_width, 4, text)
                pdf.link(x_start, contact_y, text_width, 4, f"https://linkedin.com/in/{text}")
            elif item_type == 'github':
                pdf.set_text_color(51, 51, 51)
                pdf.set_font('Helvetica', 'U', 7.5)
                pdf.cell(text_width, 4, text)
                pdf.link(x_start, contact_y, text_width, 4, f"https://github.com/{text}")
            elif item_type == 'portfolio':
                pdf.set_text_color(0, 128, 0)
                pdf.set_font('Helvetica', 'U', 7.5)
                pdf.cell(text_width, 4, text)
                pdf.link(x_start, contact_y, text_width, 4, f"https://{text}")
            elif item_type == 'leetcode':
                pdf.set_text_color(255, 165, 0)
                pdf.set_font('Helvetica', 'U', 7.5)
                pdf.cell(text_width, 4, text)
                pdf.link(x_start, contact_y, text_width, 4, f"https://leetcode.com/{text}")
            elif item_type == 'geeksforgeeks':
                pdf.set_text_color(51, 153, 51)
                pdf.set_font('Helvetica', 'U', 7.5)
                pdf.cell(text_width, 4, text)
                pdf.link(x_start, contact_y, text_width, 4, f"https://geeksforgeeks.org/user/{text}")
            elif item_type == 'phone':
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Helvetica', '', 7.5)
                pdf.cell(text_width, 4, text)

            # Add pipe separator between items
            if i < len(contact_items) - 1:
                sep_width = pdf.get_string_width(' | ')
                pdf.set_text_color(150, 150, 150)
                pdf.set_font('Helvetica', '', 7.5)
                pdf.cell(sep_width, 4, '|')

        pdf.ln(4.5)

    # Thin separator line
    reset_cursor()
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(pdf.l_margin, pdf.get_y() + 0.4, pdf.w - pdf.r_margin, pdf.get_y() + 0.4)
    pdf.ln(2.5)
    
    # ===== SUMMARY (COMPACT) =====
    if ui.get('profile_description'):
        add_section_title('Professional Summary')
        add_body_text(ui['profile_description'])

    # ===== SKILLS (CATEGORIZED, ATS-FRIENDLY) =====
    skills = ui.get('skills', {})
    hard_skills = skills.get('hard_skills', [])
    soft_skills = skills.get('soft_skills', [])
    
    if hard_skills or soft_skills:
        add_section_title('Technical Skills')
        
        # Smart categorization of hard skills
        programming_langs = []
        ml_ai_skills = []
        web_dev_skills = []
        cloud_database_skills = []
        tools_skills = []
        other_skills = []
        
        for skill in hard_skills:
            skill_lower = skill.lower()
            # Programming Languages
            if any(x in skill_lower for x in ['python', 'javascript', 'html', 'css', 'java', 'c++', 'c#', 'typescript']):
                programming_langs.append(skill)
            # ML/AI
            elif any(x in skill_lower for x in ['tensorflow', 'pytorch', 'open cv', 'machine learning', 'deep learning', 'computer vision', 'langchain', 'langgraph', 'rag', 'gemini', 'vertex ai', 'nlp', 'object detection', 'image processing']):
                ml_ai_skills.append(skill)
            # Web Development
            elif any(x in skill_lower for x in ['react', 'node.js', 'express', 'flask', 'fastapi', 'django', 'angular', 'vue']):
                web_dev_skills.append(skill)
            # Cloud & Database
            elif any(x in skill_lower for x in ['gcp', 'google cloud', 'aws', 'azure', 'firebase', 'mysql', 'mongodb', 'postgresql', 'redis', 'docker', 'kubernetes']):
                cloud_database_skills.append(skill)
            else:
                other_skills.append(skill)
        
        # Display categorized skills with proper wrapping
        if programming_langs:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(20, 4, 'Programming:')
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 20)
            pdf.multi_cell(0, 3.5, ', '.join([_sanitize_text(s) for s in programming_langs]))
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)

        if ml_ai_skills:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(20, 4, 'AI/ML & CV:')
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 20)
            pdf.multi_cell(0, 3.5, ', '.join([_sanitize_text(s) for s in ml_ai_skills]))
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)

        if web_dev_skills:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(20, 4, 'Web/Backend:')
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 20)
            pdf.multi_cell(0, 3.5, ', '.join([_sanitize_text(s) for s in web_dev_skills]))
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)

        if cloud_database_skills:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(20, 4, 'Cloud/DB:')
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 20)
            pdf.multi_cell(0, 3.5, ', '.join([_sanitize_text(s) for s in cloud_database_skills]))
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)

        if other_skills:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(20, 4, 'Other Tools:')
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 20)
            pdf.multi_cell(0, 3.5, ', '.join([_sanitize_text(s) for s in other_skills]))
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)

        # Soft Skills - with wrapping
        if soft_skills:
            pdf.ln(0.5)
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(18, 4, 'Soft Skills:')
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 18)
            pdf.multi_cell(0, 3.5, ', '.join([_sanitize_text(s) for s in soft_skills]))
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)
    
    # ===== EXPERIENCE =====
    experiences = ui.get('experiences', [])
    if experiences:
        add_section_title('Experience')
        for exp in experiences:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 4, f"{_sanitize_text(exp.get('job_title', ''))} at {_sanitize_text(exp.get('company', ''))}", ln=1)

            reset_cursor()
            pdf.set_font('Helvetica', 'I', 7)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 3.5, f"{_sanitize_text(exp.get('start_date', ''))} - {_sanitize_text(exp.get('end_date', ''))}", ln=1)
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)

            tasks = exp.get('four_tasks', [])
            if tasks:
                add_bullet(tasks)
            
            pdf.ln(spacing_cfg["section_gap"])
    
    # ===== EDUCATION =====
    education = ui.get('education', [])
    if education:
        add_section_title('Education')
        for edu in education:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 4, f"{_sanitize_text(edu.get('degree', ''))} - {_sanitize_text(edu.get('institution', ''))}", ln=1)

            reset_cursor()
            pdf.set_font('Helvetica', 'I', 7)
            pdf.set_text_color(100, 100, 100)
            date_gpa = []
            if edu.get('start_date'):
                date_gpa.append(f"{_sanitize_text(edu['start_date'])} - {_sanitize_text(edu['end_date'])}")
            if edu.get('description'):
                date_gpa.append(f"CGPA: {_sanitize_text(edu['description'])}")
            if date_gpa:
                pdf.cell(0, 3.5, ' | '.join(date_gpa), ln=1)
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)

    # ===== ACHIEVEMENTS =====
    achievements = data.get('achievements', []) or ui.get('achievements', [])
    if achievements:
        add_section_title('Achievements')
        for achievement in achievements:
            reset_cursor()
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(pdf.l_margin + 2.5)
            if isinstance(achievement, dict):
                text = achievement.get('title', achievement.get('name', ''))
                if achievement.get('description'):
                    text += f" - {achievement['description']}"
            else:
                text = str(achievement)
            pdf.multi_cell(0, 3.5, f'- {_sanitize_text(text)}', align='L')
        pdf.ln(spacing_cfg["section_gap"])
        pdf.set_text_color(0, 0, 0)

    # ===== EXTRACURRICULAR ACTIVITIES =====
    activities = data.get('extracurricular_activities', []) or data.get('extra_curricular_activities', []) or ui.get('extracurricular_activities', [])
    if activities:
        add_section_title('Extracurricular Activities')
        for activity in activities:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            if isinstance(activity, dict):
                name = activity.get('name', activity.get('activity', ''))
                pdf.cell(0, 4, _sanitize_text(name), ln=1)
                if activity.get('description'):
                    reset_cursor()
                    pdf.set_font('Helvetica', '', 7)
                    pdf.set_text_color(60, 60, 60)
                    pdf.set_x(pdf.l_margin + 2.5)
                    pdf.multi_cell(0, 3, f'- {_sanitize_text(activity["description"])}', align='L')
                    pdf.ln(0.5)
                    pdf.set_text_color(0, 0, 0)
                if activity.get('start_date') or activity.get('end_date'):
                    reset_cursor()
                    pdf.set_font('Helvetica', 'I', 6.5)
                    pdf.set_text_color(100, 100, 100)
                    dates = []
                    if activity.get('start_date'):
                        dates.append(_sanitize_text(activity['start_date']))
                    if activity.get('end_date'):
                        dates.append(_sanitize_text(activity['end_date']))
                    if dates:
                        pdf.cell(0, 3, ' | '.join(dates), ln=1)
                    pdf.ln(0.5)
                    pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_font('Helvetica', '', 7)
                pdf.set_text_color(60, 60, 60)
                pdf.set_x(pdf.l_margin + 2.5)
                pdf.multi_cell(0, 3, f'- {_sanitize_text(activity)}', align='L')
                pdf.ln(0.5)
                pdf.set_text_color(0, 0, 0)

        pdf.ln(spacing_cfg["section_gap"])

    # ===== PROJECTS =====
    projects = data.get('projects', [])
    if projects:
        add_section_title('Projects')
        for proj in projects:
            reset_cursor()
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 4, f"{_sanitize_text(proj.get('project_name', ''))}", ln=1)
            pdf.ln(0.5)

            goals = proj.get('two_goals_of_the_project', [])
            if goals:
                for goal in goals:
                    reset_cursor()
                    pdf.set_font('Helvetica', '', 7)
                    pdf.set_text_color(60, 60, 60)
                    pdf.set_x(pdf.l_margin + 2.5)
                    pdf.multi_cell(0, 3.5, f'- {_sanitize_text(goal)}', align='L')
                pdf.set_text_color(0, 0, 0)

            if proj.get('project_end_result') or proj.get('tech_stack'):
                pdf.ln(0.5)
                extras = []
                if proj.get('project_end_result'):
                    result_text = _sanitize_text(proj['project_end_result'])
                    if len(result_text) > 100:
                        result_text = result_text[:97] + "..."
                    extras.append(f"Result: {result_text}")
                if proj.get('tech_stack'):
                    tech_text = ', '.join([_sanitize_text(t) for t in proj['tech_stack']])
                    if len(tech_text) > 70:
                        tech_text = tech_text[:67] + "..."
                    extras.append(f"Tech: {tech_text}")

                if extras:
                    full_text = ' | '.join(extras)
                    reset_cursor()
                    pdf.set_font('Helvetica', 'I', 7)
                    pdf.set_text_color(100, 100, 100)
                    pdf.set_x(pdf.l_margin + 2.5)
                    pdf.multi_cell(0, 3, full_text, align='L')
                    pdf.set_text_color(0, 0, 0)

            pdf.ln(spacing_cfg["section_gap"])

    # ===== CERTIFICATES =====
    certs = data.get('certificate', [])
    if certs:
        add_section_title('Certificates')
        for cert in certs:
            pdf.set_font('Helvetica', 'B', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 4, f"{_sanitize_text(cert.get('name', ''))}", ln=1)
            reset_cursor()
            pdf.set_font('Helvetica', 'I', 7)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 3.5, f"{_sanitize_text(cert.get('institution', ''))} | {_sanitize_text(cert.get('date', ''))}", ln=1)
            pdf.ln(0.5)
            pdf.set_text_color(0, 0, 0)
            if cert.get('description'):
                pdf.ln(0.5)
                reset_cursor()
                pdf.set_font('Helvetica', '', 7)
                pdf.set_text_color(60, 60, 60)
                pdf.multi_cell(0, 3, _sanitize_text(cert['description']), align='J')
                pdf.set_text_color(0, 0, 0)
            pdf.ln(0.5)

    # ===== SAVE =====
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_pdf.close()
    pdf.output(temp_pdf.name)
    return temp_pdf.name
