import streamlit as st
import torch
import timm
import gdown
import os
import gc
from PIL import Image
from torchvision import transforms

# --- CẤU HÌNH ---
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="UPT AI Scanner", page_icon="🐾")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🐾 AI Breed & Seafood Scanner</h1>", unsafe_allow_stdio=True)
st.info("Hệ thống đang chạy chế độ tối ưu bộ nhớ cho server UPT.")

# --- LOAD AI ---
@st.cache_resource
def load_ai():
    if not os.path.exists(MODEL_PATH):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        gdown.download(url, MODEL_PATH, quiet=False)

    gc.collect()
    # Load class names từ file GitHub của bạn [cite: 1]
    classes = torch.load("class_names.pth", map_location="cpu", weights_only=True)
    
    # Khởi tạo Swin Tiny [cite: 1]
    net = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(classes))
    
    state_dict = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    net.load_state_dict(state_dict)
    
    del state_dict
    gc.collect()
    net.eval()
    return net, classes

try:
    model, class_names = load_ai()
except Exception as e:
    st.error(f"Lỗi nạp Model: {e}")
    st.stop()

# --- XỬ LÝ ---
uploaded_file = st.file_uploader("Tải ảnh chó hoặc hải sản...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB')
    st.image(img, caption="Ảnh đầu vào", use_container_width=True)
    
    if st.button("🚀 Phân tích"):
        with st.spinner("AI đang nhận diện..."):
            # Tiền xử lý trực tiếp không qua xóa nền để tránh lỗi 503
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(img).unsqueeze(0)
            
            with torch.no_grad():
                out = model(img_t)
                prob = torch.nn.functional.softmax(out[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            ten_loai = class_names[idx]
            st.success(f"### Kết quả: {ten_loai.upper()}")
            st.write(f"Độ tin cậy: **{conf.item()*100:.2f}%**")
            
            # Ghi chú cho các loài chó Việt Nam và hải sản [cite: 1]
            if "Phu Quoc" in ten_loai:
                st.info("💡 Chó xoáy Phú Quốc - Đặc hữu của Việt Nam.")
            elif "Hmong" in ten_loai:
                st.info("💡 Chó H'mông cộc đuôi vùng cao.")
            elif "fish" in ten_loai.lower() or "Snapper" in ten_loai:
                st.info("🐠 Danh mục hải sản UPT.")
        gc.collect()
