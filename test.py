import streamlit as st
import google.generativeai as genai
import json

#GIAO DIỆN
st.set_page_config(page_title="AI Tạo Trắc Nghiệm", page_icon="📝", layout="centered")
st.title("📝Tạo Câu Hỏi Trắc Nghiệm")
st.subheader("Phù hợp cho bài thuyết trình hoặc ôn tập💀💔")

#AI GEMINI

API_KEY = "AQ.Ab8RN6JrLeLCyTxQYMgYJ1r4vQ5d5V12VmnuTXGE1IIstMmNpg" 

if API_KEY == "ĐIỀN_API_KEY_GEMINI_CỦA_BẠN_VÀO_ĐÂY":
    st.warning("điền Gemini API Key")
else:
    genai.configure(api_key=API_KEY)

#GIAO DIỆN NHẬP LIỆU
lecture_content = st.text_area("Dán nội dung bài giảng hoặc ghi chú vào đây:", height=200, 
                               placeholder="Ví dụ: Rễ cây hấp thụ nước và ion khoáng từ đất qua các tế bào lông hút...")

col1, col2 = st.columns(2)
with col1:
    num_questions = st.slider("Số lượng câu hỏi cần tạo:", min_value=1, max_value=10, value=3)
with col2:
    difficulty = st.selectbox("Mức độ khó:", ["Nhận biết (Dễ)", "Thông hiểu (Vừa)", "Vận dụng (Khó)"])

#XỬ LÝ KHI BẤM NÚT
if st.button("Bắt đầu tạo câu hỏi"):
    if not lecture_content.strip():
        st.error("❌ Hãy nhập nội dung bài giảng!")
    elif API_KEY == "ĐIỀN_API_KEY_GEMINI_CỦA_BẠN_VÀO_ĐÂY":
        st.error("❌ Chưa cấu hình API Key!")
    else:
        with st.spinner("Đợi xíu..."):
            try:
                # Định hình Prompt (yêu cầu) gửi cho AI để ép nó trả về cấu trúc JSON cho dễ lập trình
                prompt = f"""
                Bạn là một giáo viên cấp 3 vui tính nhưng nghiêm túc. Dựa trên nội dung bài giảng sau đây:
                "{lecture_content}"
                
                Hãy tạo ra đúng {num_questions} câu hỏi trắc nghiệm ở mức độ "{difficulty}".
                Mỗi câu hỏi bắt buộc phải có 4 lựa chọn (A, B, C, D) và chỉ có 1 đáp án đúng duy nhất.
                
                Hãy trả về kết quả strictly dưới dạng JSON Array, không thêm bất kỳ văn bản nào khác ngoài JSON. Cấu trúc JSON như sau:
                [
                  {{
                    "question": "Câu hỏi 1 là gì?",
                    "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
                    "answer": "Đáp án A",
                    "explanation": "Giải thích ngắn gọn tại sao đúng"
                  }}
                ]
                """
                
                # Gọi mô hình Gemini
                model = genai.GenerativeModel("gemini-3.6-flash")
                response = model.generate_content(prompt)
                
                # Làm sạch dữ liệu trả về và ép kiểu sang JSON
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                quiz_data = json.loads(clean_text)
                
                # Lưu vào session_state để lưu lại trạng thái câu hỏi khi làm bài
                st.session_state.quiz_data = quiz_data
                st.session_state.user_answers = {}
                st.success("🎉 Đã tạo xong câu hỏi! Làm bài ngay bên dưới 👇")
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi tạo câu hỏi: {e}")

#HIỂN THỊ ĐỀ THI VÀ CHẤM ĐIỂM
if "quiz_data" in st.session_state:
    st.write("---")
    st.header("✍️")
    
    # Hiển thị từng câu hỏi
    for idx, q in enumerate(st.session_state.quiz_data):
        st.write(f"**Câu {idx+1}: {q['question']}**")
        
        # Tạo radio button cho học sinh chọn đáp án
        user_choice = st.radio(
            f"Chọn đáp án cho câu {idx+1}:", 
            options=q['options'], 
            key=f"q_{idx}",
            index=None, # Không chọn sẵn đáp án nào
            label_visibility="collapsed"
        )
        st.session_state.user_answers[idx] = user_choice
        st.write("")

    # Nút nộp bài
    if st.button("💯Nộp bài xem điểm"):
        score = 0
        total = len(st.session_state.quiz_data)
        
        st.write("---")
        st.header("📊 KẾT QUẢ CỦA BẠN")
        
        for idx, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.user_answers.get(idx)
            correct_ans = q['answer']
            
            if user_ans == correct_ans:
                score += 1
                st.success(f"✅ **Câu {idx+1}: Chính xác!**")
            else:
                st.error(f"❌ **Câu {idx+1}: Sai rồi!** (Bạn chọn: {user_ans if user_ans else 'Chưa chọn'})")
                st.info(f"💡 *Đáp án đúng là:* {correct_ans}")
            
            st.caption(f"ℹ️ *Giải thích:* {q['explanation']}")
            st.write("")
            
        # Tính điểm hệ 10
        final_score = round((score / total) * 10, 2)
        if final_score >= 8:
            st.balloons()
            st.success(f"😎 Quá đỉnh! Điểm số: {final_score}/10 ({score}/{total} câu)")
        elif final_score >= 5:
            st.warning(f"😮 Tạm ổn nè! Điểm số: {final_score}/10 ({score}/{total} câu). Cố gắng thêm nhé!")
        else:
            st.error(f"💔 Toang rồi ông giáo ạ! Điểm số: {final_score}/10 ({score}/{total} câu). Học lại bài đi 💀")

