import streamlit as st
import google.generativeai as genai
import os

# Sahifa sozlamalari
st.set_page_config(page_title="Mening Ma'lumotlarim Chati", page_icon="🤖", layout="centered")

st.title("🤖 Onlayn AI Chatbot (Gemini)")
st.caption("Ushbu chat dasturi faqat siz kiritgan ma'lumotlar (data.txt) asosida javob beradi.")

# API Kalitni o'qish (Streamlit secrets yoki fayldan)
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key or api_key == "BU_YERGA_GEMINI_API_KALITINI_YOZING":
    st.error("Iltimos, `.streamlit/secrets.toml` fayliga haqiqiy Gemini API kalitini yozing!")
    st.stop()

# Gemini sozlamalari
genai.configure(api_key=api_key)

# Ma'lumotlarni o'qish
context_text = ""
try:
    with open("data.txt", "r", encoding="utf-8") as f:
        context_text = f.read()
except FileNotFoundError:
    st.warning("'data.txt' fayli topilmadi. Iltimos yarating va ma'lumotlaringizni yozing.")

# Tizim (System) uchun qat'iy ko'rsatma
SYSTEM_PROMPT = f"""Sen yordamchi sun'iy intellektsan. Sening birdan-bir vazifang foydalanuvchi savollariga faqat quyidagi ma'lumotlarga (CONTEXT) asoslanib javob berishdir.
Agar foydalanuvchi so'ragan savolning javobi quyidagi ma'lumotlar ichida bo'lmasa, SEN O'ZINGDAN QO'SHIB JAVOB BERISHING QAT'IYAN MAN ETILADI. 
Bunday holatda shunday deb javob ber: "Kechirasiz, menda bu haqida ma'lumot yo'q. Men faqat menga berilgan ma'lumotlar doirasida ishlayman."

CONTEXT:
{context_text}
"""

# Gemini modelini sozlash (gemini-1.5-flash tez va arzon)
generation_config = {
  "temperature": 0.1, # Javoblar aniq va faktga asoslangan bo'lishi uchun past harorat
}
model = genai.GenerativeModel(model_name="gemini-2.5-flash", 
                              system_instruction=SYSTEM_PROMPT,
                              generation_config=generation_config)

# Chat tarixi
if "chat_session" not in st.session_state:
    st.session_state["chat_session"] = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "model", "content": "Salom! Men sizning maxsus yordamchingizman. Nimani bilmoqchisiz?"}]

# Tarixni ekranga chiqarish
for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    avatar = "🤖" if msg["role"] == "model" else "👤"
    st.chat_message(role, avatar=avatar).write(msg["content"])

# Foydalanuvchi kiritishi
if prompt := st.chat_input("Savolingizni yozing..."):
    # Xabarni ko'rsatish
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)

    # Gemini'ga so'rov yuborish
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Modelga xabar jo'natish (stream orqali)
            response = st.session_state["chat_session"].send_message(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Xatolik yuz berdi: {e}")
            full_response = "Kechirasiz, texnik xatolik yuz berdi."

    # Model javobini tarixga saqlash
    st.session_state.messages.append({"role": "model", "content": full_response})
