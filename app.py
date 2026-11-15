import streamlit as st
import pysrt
from google import genai
import tempfile
import os

# Page Configuration
st.set_page_config(
    page_title="SRT Clipper & MM Translator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8F00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #888888;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF7600 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Settings & API Key
with st.sidebar:
    st.markdown("### ⚙️ Settings & API")
    
    # Environment သို့မဟုတ် Streamlit Secrets မှ Key ကို အရင်ရှာမည်
    env_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    
    if env_key:
        st.success("✅ API Key ချိတ်ဆက်ပြီးပါပြီ (Secrets)")
        api_key = env_key
    else:
        api_key = st.text_input("🔑 Gemini API Key ထည့်ပါ", type="password", help="Google AI Studio မှ ရသော Key ကို ထည့်ပါ")
        st.caption("[👉 အခမဲ့ API Key ယူရန် နှိပ်ပါ](https://aistudio.google.com/)")

    st.divider()
    st.markdown("### 🎭 ဘာသာပြန် လေသံ (Tone)")
    tone = st.selectbox(
        "ဗီဒီယို အမျိုးအစား ရွေးပါ",
        [
            "Storytelling / Movie Recap (ဇာတ်လမ်းပြောပုံစံ)",
            "Natural Spoken (သဘာဝ စကားပြောပုံစံ)",
            "Educational / Explainer (ဗဟုသုတ ရှင်းပြပုံစံ)"
        ]
    )
    
    batch_size = st.slider("Batch Size (တစ်ခါပြန်မည့် စာကြောင်းရေ)", 15, 50, 30)
    st.divider()
    st.info("💡 **CapCut Ready:** ဖြတ်လိုက်သော အပိုင်းကို CapCut ထဲ တန်းထည့်နိုင်ရန် အချိန်ကို `00:00:00,000` မှ အလိုအလျောက် ပြန်စပေးပါသည်။")

# Main Content
st.markdown('<div class="main-header">🎬 AI SRT Clipper & Myanmar Translator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">SRT စာတန်းထိုးများကို လိုသလောက်ဖြတ်ထုတ်ပြီး သဘာဝကျသော မြန်မာစကားပြောပုံစံသို့ ပြောင်းလဲပါ</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 SRT File ကို ဒီနေရာမှာ တင်ပါ (.srt)", type=["srt"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    subs = pysrt.open(tmp_path, encoding='utf-8')

    if len(subs) > 0:
        min_time = str(subs[0].start).split(',')[0]
        max_time = str(subs[-1].end).split(',')[0]

        # File Info Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("📄 စုစုပေါင်း စာကြောင်းရေ", f"{len(subs)} ကြောင်း")
        m2.metric("⏱️ စတင်ချိန် (Start)", min_time)
        m3.metric("🏁 ပြီးဆုံးချိန် (End)", max_time)

        st.markdown("---")
        st.subheader("✂️ ဖြတ်ထုတ်လိုသော အချိန်အပိုင်းအခြား ရွေးပါ")
        
        col1, col2 = st.columns(2)
        with col1:
            start_str = st.text_input("🟢 စတင်မည့်အချိန် (HH:MM:SS)", value=min_time)
        with col2:
            end_str = st.text_input("🔴 ပြီးဆုံးမည့်အချိန် (HH:MM:SS)", value=max_time)

        def parse_time(t_str):
            parts = list(map(int, t_str.strip().split(':')))
            return pysrt.SubRipTime(hours=parts[0], minutes=parts[1], seconds=parts[2])

        if st.button("🚀 ဖြတ်မယ် + မြန်မာဘာသာပြန်မယ်"):
            if not api_key:
                st.error("⚠️ ဘယ်ဘက်ခြမ်း Menu တွင် Gemini API Key အရင်ထည့်ပေးပါ (သို့မဟုတ်) Streamlit Secrets တွင် ထည့်သွင်းပါ။")
            else:
                try:
                    start_time = parse_time(start_str)
                    end_time = parse_time(end_str)

                    # Filter subtitles within time range
                    clipped_subs = pysrt.SubRipFile([
                        sub for sub in subs
                        if sub.start >= start_time and sub.end <= end_time
                    ])

                    if len(clipped_subs) == 0:
                        st.warning("⚠️ ရွေးချယ်ထားသော အချိန်အတွင်း စာတန်းထိုး မရှိပါ။ အချိန်ပြန်စစ်ပေးပါ။")
                    else:
                        # Reset timecode to 00:00:00,000 based on start_time
                        clipped_subs.shift(
                            hours=-start_time.hours,
                            minutes=-start_time.minutes,
                            seconds=-start_time.seconds,
                            milliseconds=-start_time.milliseconds
                        )

                        # Keep original text for comparison
                        original_preview = "\n\n".join([f"{i+1}\n{s.start} --> {s.end}\n{s.text}" for i, s in enumerate(clipped_subs)])

                        client = genai.Client(api_key=api_key)
                        progress_bar = st.progress(0)
                        status_box = st.empty()

                        total_subs = len(clipped_subs)

                        for i in range(0, total_subs, batch_size):
                            batch = clipped_subs[i:i+batch_size]
                            status_box.info(f"⏳ Gemini AI ဖြင့် ဘာသာပြန်နေပါသည်... ({min(i+batch_size, total_subs)} / {total_subs} ကြောင်း)")

                            prompt_lines = [f"{idx}|||{sub.text.replace(chr(10), ' ')}" for idx, sub in enumerate(batch)]
                            joined_text = "\n".join(prompt_lines)

                            prompt = (
                                f"Translate these subtitle lines into natural, engaging spoken Burmese suitable for short-form video narration (Style: {tone}). "
                                "Ensure smooth Burmese phrasing. Keep the exact same 'index|||translated_text' format for every single line. "
                                "Do not merge, skip, or add extra commentary.\n\n"
                                f"{joined_text}"
                            )

                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=prompt
                            )

                            translated_lines = response.text.strip().split("\n")
                            trans_dict = {}
                            for line in translated_lines:
                                if "|||" in line:
                                    k, v = line.split("|||", 1)
                                    if k.strip().isdigit():
                                        trans_dict[int(k.strip())] = v.strip()

                            for idx, sub in enumerate(batch):
                                sub.index = i + idx + 1
                                if idx in trans_dict:
                                    sub.text = trans_dict[idx]

                            progress_bar.progress(min((i + batch_size) / total_subs, 1.0))

                        status_box.empty()
                        out_path = tmp_path.replace(".srt", "_mm.srt")
                        clipped_subs.save(out_path, encoding='utf-8')

                        with open(out_path, "r", encoding="utf-8") as f:
                            result_srt = f.read()

                        st.success("🎉 ဖြတ်တောက်ပြီး မြန်မာဘာသာပြန်ဆိုမှု အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")

                        # Download Button
                        st.download_button(
                            label="📥 CapCut အသင့်သုံး မြန်မာ SRT ဒေါင်းလုဒ်ဆွဲရန်",
                            data=result_srt,
                            file_name=f"MM_{start_str.replace(':','')}_to_{end_str.replace(':','')}.srt",
                            mime="text/plain"
                        )

                        # Side-by-Side Preview
                        st.markdown("### 👀 နမူနာ နှိုင်းယှဉ်ကြည့်ရန် (Preview)")
                        p_col1, p_col2 = st.columns(2)
                        with p_col1:
                            st.text_area("မူရင်း SRT (အချိန် Reset လုပ်ပြီး)", original_preview, height=320)
                        with p_col2:
                            st.text_area("မြန်မာဘာသာပြန် SRT (00:00:00 မှ စသည်)", result_srt, height=320)

                except Exception as e:
                    st.error(f"❌ အမှားတစ်ခု ဖြစ်ပွားနေပါသည်: {e}")

    os.remove(tmp_path)
