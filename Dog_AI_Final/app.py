import streamlit as st
import torch
import timm
import os
import gdown
from PIL import Image
from rembg import remove, new_session
from torchvision import transforms

# --- CẤU HÌNH ---
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="UPT AI Breed Scanner", page_icon="🐾")

# --- NẠP TÀI NGUYÊN SIÊU NHẸ ---
@st.cache_resource
def load_all():
    # 1. Tải model từ Drive nếu chưa có
    if not os.path.exists(MODEL_PATH):
        gdown.download(f'https://drive.google.com/uc?id={FILE_ID}', MODEL_PATH, quiet=False)
    
    # 2. Nạp class names (File này phải nằm trên GitHub của bạn)
    class_names = torch.load("class_names.pth", map_location="cpu")
    
    # 3. Khởi tạo Swin Transformer Tiny (Bản nhẹ nhất)
    model = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(class_names))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    
    # 4. Session tách nền Lite (u2netp) - Giúp tránh lỗi 503
    session = new_session("u2netp") 
    
    return model, class_names, session

# Khởi chạy hệ thống
with st.spinner("Hệ thống đang khởi động thuật toán cao cấp..."):
    try:
        model, class_names, bg_session = load_all()
        st.sidebar.success("✅ Hệ thống AI đã sẵn sàng!")
    except Exception as e:
        st.sidebar.error("⏳ Đang nạp dữ liệu... Hãy đợi 1-2 phút.")

# --- GIAO DIỆN ---
st.title("🐾 AI Breed & Seafood Scanner")
st.write("**Sinh viên thực hiện:** Minh Thuận (UPT)")

file = st.file_uploader("Tải ảnh Chó hoặc Cá...", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=300)
    
    if st.button('🚀 Bắt đầu Quét AI'):
        with st.spinner('AI đang tách nền và phân tích...'):
            # Tách nền (U2-Netp)
            clean_img = remove(img, session=bg_session).convert('RGB')
            
            # Tiền xử lý Swin Transformer
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(clean_img).unsqueeze(0)
            
            # Nhận diện đặc điểm sinh học
            with torch.no_grad():
                out = model(img_t)
                prob = torch.nn.functional.softmax(out[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            st.divider()
            st.success(f"### Kết quả: {class_names[idx].upper()}")
            st.write(f"Độ chính xác: **{conf.item()*100:.2f}%**")
            st.progress(float(conf.item()))
