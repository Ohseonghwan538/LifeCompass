import streamlit as st
import google.generativeai as genai
import json
import re
import plotly.graph_objects as go
import pandas as pd
import os

# ==========================================
# 1. 설정 및 초기화
# ==========================================
st.set_page_config(page_title="Life Compass AI", layout="wide")
MAX_DAYS = 3  # 1: 결정론, 2: 데이터 축적, 3: 정체성 전이

# API 키 설정 로직
api_key = os.environ.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("🔑 Google Gemini API")
    if not api_key:
        api_key = st.text_input("API Key를 입력하거나 환경 변수(GEMINI_API_KEY)를 설정하세요", type="password")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.success("API Key 설정 완료.")
        except Exception as e:
            st.error(f"API Key 설정 오류: {e}")
            api_key = None
    
    st.divider()

# 세션 상태 초기화
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.day = 1
    
    # 캐릭터 초기 페르소나 설정
    st.session_state.persona = "한국 거주, 20대 소프트웨어학과를 졸업 예정자"
    
    # 점수 초기화
    initial_scores = {
        "self": 50, "others": 50, "world": 50, "attitude": 50
    }
    st.session_state.initial_scores = initial_scores.copy()
    st.session_state.scores = initial_scores.copy()
    
    # 자원 초기화
    st.session_state.resources = {
        "energy": 100, "money": 100
    }
    
    st.session_state.last_choice_text = None 
    st.session_state.current_scenario = None
    st.session_state.analysis_result = None
    st.session_state.user_reflection = ""
    st.session_state.history = []
    st.session_state.game_over = False

# ==========================================
# 2. 유틸리티 함수
# ==========================================
def clean_json_text(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```', '', text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0).strip() if match else text.strip()

def draw_radar_chart(current_scores, initial_scores=None):
    categories = ['나 자신(성장)', '타인(사랑)', '세상(기여)', '태도(균형)']
    fig = go.Figure()

    if initial_scores:
        fig.add_trace(go.Scatterpolar(
            r=[initial_scores['self'], initial_scores['others'], initial_scores['world'], initial_scores['attitude'], initial_scores['self']],
            theta=categories + [categories[0]],
            fill='toself', name='여정 시작 전', line_color='gray', opacity=0.5, line_dash='dot'
        ))

    fig.add_trace(go.Scatterpolar(
        r=[current_scores['self'], current_scores['others'], current_scores['world'], current_scores['attitude'], current_scores['self']],
        theta=categories + [categories[0]],
        fill='toself', name='현재 상태', line_color='#4A90E2'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        font=dict(family="Malgun Gothic, Nanum Gothic, sans-serif"),
        margin=dict(t=20, b=20, l=10, r=10),
        height=300 
    )
    return fig

# ==========================================
# 3. AI 통신 (진화형 딜레마 생성 로직 적용)
# ==========================================
def get_gemini_response(prompt):
    if not api_key: return None
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash", # 최신 모델 권장
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        return json.loads(clean_json_text(response.text))
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# 4대 가치 정의
PHILOSOPHY_CONTEXT = """
인간의 삶을 지탱하는 4가지 핵심 가치:
1. [Self] 나 자신을 향한 추구: 성장, 자율성.
2. [Others] 타인을 향한 추구: 사랑, 유대.
3. [World] 세상을 향한 추구: 기여, 의미.
4. [Attitude] 태도에 대한 추구: 균형, 수용.
"""

def generate_scenario():
    day = st.session_state.day
    history_summary = "\n".join([f"Day {h['day']}: 선택한 가치 변화 분석 - {h['log']}" for h in st.session_state.history])
    last_reflection = st.session_state.user_reflection if st.session_state.user_reflection else "첫 시작"
    last_choice = st.session_state.last_choice_text if st.session_state.last_choice_text else "없음"

    # [MODIFIED] 3단계 진화 로직 정의
    if day == 1:
        phase_instruction = f"""
        **[Step 1: 결정론(Determinism) 단계]**
        사용자에 대한 정보가 부족합니다. 아래의 고정된 페르소나에 전적으로 의존하여 가장 개연성 있는 보편적인 첫 딜레마를 생성하세요.
        - 페르소나: {st.session_state.persona}
        """
    elif day == 2:
        phase_instruction = f"""
        **[Step 2: 데이터 축적(Data Accumulation) 단계]**
        이제 사용자의 선택 데이터가 쌓이기 시작했습니다. 기존 페르소나와 사용자의 직전 행동 사이의 인과관계를 반영하세요.
        - 직전 선택: {last_choice}
        - 직전 회고: {last_reflection}
        페르소나의 상황에 사용자의 실제 선택이 만들어낸 새로운 맥락(Context)을 더해 딜레마를 구성하세요.
        """
    else:
        phase_instruction = f"""
        **[Step 3: 정체성의 전이(Identity Shift) 단계]**
        이제 초기 페르소나보다 사용자가 쌓아온 '구체적인 삶의 궤적'이 더 중요합니다. 
        초기 페르소나의 틀을 벗어나, 현재 가치 점수와 여정 기록을 바탕으로 오직 이 사용자만을 위한 맞춤형 딜레마를 제공하세요.
        - 현재 가치 상태: {st.session_state.scores}
        - 여정의 궤적: {history_summary}
        사용자의 정체성이 어떻게 변화해왔는지 파악하고, 그 변화의 끝에서 마주할 법한 결정적인 딜레마를 생성하세요.
        """

    prompt = f"""
    당신은 인생의 철학적 멘토이자 시뮬레이터입니다.
    
    {phase_instruction}

    [공통 요구 사항]
    위 단계별 지침에 따라 오늘 사용자가 마주칠 '철학적 딜레마' 상황을 생성하세요.
    단순한 이익 계산이 아니라 가치관의 충돌을 다뤄야 합니다.

    Output JSON Schema:
    {{
        "title": "딜레마 제목", "description": "상황 설명",
        "options": {{
            "A": {{ "text": "선택지", "value_focus": "Self" }},
            "B": {{ "text": "선택지", "value_focus": "Others" }},
            "C": {{ "text": "선택지", "value_focus": "Attitude" }}
        }}
    }}
    """
    return get_gemini_response(prompt)

def evaluate_choice(choice_key, scenario):
    prompt = f"""
    상황: {scenario['title']}
    선택: {choice_key}. {scenario['options'][choice_key]['text']}
    {PHILOSOPHY_CONTEXT}

    이 선택이 4가지 가치와 자원에 미치는 영향을 분석하고, 사용자가 성찰할 수 있는 질문을 생성하세요.

    **[중요] feedback_question 생성 지침:**
    단순히 기분이나 가치관을 묻지 마세요. 회고(Reflection)의 본질적 목적을 달성할 수 있는 질문이어야 합니다.
    1. **결과 분석**: 이 선택이 가져온 긍정적/부정적 결과에 대한 통찰 제공.
    2. **개선점 파악**: 사용자가 무엇을 놓쳤거나 더 잘할 수 있었을지 유도.
    3. **실행 계획**: 향후 유사한 딜레마 상황에서 더 나은 결과를 만들기 위한 구체적인 선택 기준을 물어봄.

    Output JSON Schema:
    {{
        "changes": {{
            "self": int(-10~10), "others": int, "world": int, "attitude": int,
            "energy": int(자원소모), "money": int(자원소모)
        }},
        "analysis_text": "철학적 분석 (줄글)",
        "feedback_question": "실천적이고 목적 지향적인 회고 질문"
    }}
    """
    return get_gemini_response(prompt)

def generate_final_report():
    history_text = "\n".join([f"Day {h['day']}: {h['log']}" for h in st.session_state.history])
    prompt = f"""
    사용자가 {MAX_DAYS}일간의 시뮬레이션을 마쳤습니다.
    [초기] {st.session_state.initial_scores}
    [최종] {st.session_state.scores}
    [기록] {history_text}
    
    사용자가 초기 페르소나에서 어떤 자신만의 정체성으로 전이(Shift)되었는지 분석하여 최종 보고서를 작성하세요.
    Output JSON Schema:
    {{
        "persona_type": "최종 정체성 정의 (예: 타인의 가치를 지키는 학자)",
        "summary": "전체 여정의 궤적 요약 (3문장)",
        "strengths": "발견된 가치적 강점",
        "weaknesses": "보완이 필요한 가치",
        "advice": "미래를 위한 조언"
    }}
    """
    return get_gemini_response(prompt)

# ==========================================
# 4. UI 구성
# ==========================================

with st.sidebar:
    st.markdown("### 🧭 Life Compass")
    st.plotly_chart(draw_radar_chart(st.session_state.scores, st.session_state.initial_scores), width="stretch")
    
    st.markdown("---")
    st.markdown("**현실 자원**")
    energy_progress = min(st.session_state.resources['energy'] / 100, 1.0)
    st.progress(energy_progress, text=f"⚡ Energy: {st.session_state.resources['energy']}")
    money_progress = min(st.session_state.resources['money'] / 100, 1.0)
    st.progress(money_progress, text=f"💰 Money: {st.session_state.resources['money']}")
    st.caption(f"📅 Day: {st.session_state.day} / {MAX_DAYS}")

st.title("🌱 Value-Based Life Simulator")
# 진행 단계에 따른 상태 표시
if st.session_state.day == 1:
    st.info("📍 **1단계: 결정론** - 주어진 페르소나의 삶에서 시작합니다.")
elif st.session_state.day == 2:
    st.info("📍 **2단계: 데이터 축적** - 당신의 선택이 삶의 맥락을 만들기 시작합니다.")
else:
    st.info("📍 **3단계: 정체성 전이** - 이제 당신의 선택이 곧 당신의 정체성입니다.")

if not api_key:
    st.warning("👈 사이드바에 API Key를 입력하여 여정을 시작하세요.")
    st.stop()

# --- [종료 조건] ---
if st.session_state.day > MAX_DAYS:
    st.session_state.game_over = True

# --- [게임 오버] ---
if st.session_state.game_over:
    st.balloons()
    st.success("🎉 모든 여정을 마쳤습니다!")
    
    if "final_report" not in st.session_state:
        with st.spinner("📜 최종 보고서 작성 중..."):
            st.session_state.final_report = generate_final_report()
    
    report = st.session_state.final_report
    if report:
        st.header(f"📜 최종 보고서: {report['persona_type']}")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### 📊 변화 추이")
            st.plotly_chart(draw_radar_chart(st.session_state.scores, st.session_state.initial_scores), width="stretch")
            st.caption("회색 점선: 시작 전 / 파란색 영역: 최종 상태")
        with col2:
            st.markdown("### 📝 AI 분석")
            st.markdown(f"**요약:** {report['summary']}")
            st.markdown(f"**💪 강점:** {report['strengths']}")
            st.markdown(f"**⚠️ 보완점:** {report['weaknesses']}")
            st.info(f"**💡 조언:** {report['advice']}")
            
        if st.button("🔄 새로운 삶 시작하기"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
    st.stop()

# --- [게임 진행] ---

# 1. 시나리오 생성
if st.session_state.current_scenario is None:
    with st.spinner("💭 다음 상황을 생성하는 중..."):
        data = generate_scenario()
        if data:
            st.session_state.current_scenario = data
            st.rerun()

# 2. 딜레마 및 선택
if st.session_state.current_scenario and st.session_state.analysis_result is None:
    scn = st.session_state.current_scenario
    st.subheader(f"Day {st.session_state.day}: {scn['title']}")
    st.write(scn['description'])
    
    col1, col2, col3 = st.columns(3)
    
    def on_click(k):
        with st.spinner("⚖️ 분석 중..."):
            st.session_state.last_choice_text = scn['options'][k]['text']
            res = evaluate_choice(k, scn)
            if res:
                c = res['changes']
                for key in ['self', 'others', 'world', 'attitude']:
                    st.session_state.scores[key] = max(0, min(100, st.session_state.scores[key] + c.get(key, 0)))
                st.session_state.resources['energy'] = max(0, min(100, st.session_state.resources['energy'] + c.get('energy', 0)))
                st.session_state.resources['money'] = max(0, st.session_state.resources['money'] + c.get('money', 0))
                st.session_state.analysis_result = res
                st.rerun()

    options = scn['options']
    with col1:
        st.info(f"**A. {options['A']['text']}**\n\n🎯 Focus: {options['A']['value_focus']}")
        st.button("선택 A", key="btn_a", on_click=on_click, args=("A",), width="stretch")
    with col2:
        st.success(f"**B. {options['B']['text']}**\n\n🎯 Focus: {options['B']['value_focus']}")
        st.button("선택 B", key="btn_b", on_click=on_click, args=("B",), width="stretch")
    with col3:
        st.warning(f"**C. {options['C']['text']}**\n\n🎯 Focus: {options['C']['value_focus']}")
        st.button("선택 C", key="btn_c", on_click=on_click, args=("C",), width="stretch")

# 3. 결과 분석 및 회고
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    
    st.divider()
    st.subheader("💡 Insight & Reflection")
    st.markdown(f"> {res['analysis_text']}")
    
    st.markdown("---")
    st.markdown(f"**🧐 성장을 위한 회고 질문:**\n{res['feedback_question']}")
    
    reflection = st.text_input("위 질문에 대한 답과 구체적인 계획을 기록하세요:", key="reflection_input")
    
    if st.button("다음 날로 나아가기"):
        if reflection:
            st.session_state.user_reflection = reflection
            st.session_state.history.append({"day": st.session_state.day, "log": res['analysis_text']})
            st.session_state.day += 1
            st.session_state.current_scenario = None
            st.session_state.analysis_result = None
            st.rerun()
        else:
            st.toast("성장을 위해 회고를 작성해주세요.")