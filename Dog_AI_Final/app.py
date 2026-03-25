import streamlit as st
import torch
import timm
import gdown
import os
import gc
from PIL import Image
from torchvision import transforms

# --- CẤU HÌNH HỆ THỐNG ---
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="UPT AI Scanner", page_icon="🐾")

# --- GIAO DIỆN ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🐾 AI Breed & Seafood Scanner</h1>", unsafe_allow_html=True)
st.info("Hệ thống nhận diện Chó nội địa & Hải sản - Dự án UPT")

# --- HÀM TẢI MÔ HÌNH ---
@st.cache_resource
def load_ai():
    # 1. Tự động xác định đường dẫn thư mục hiện tại
    base_path = os.path.dirname(__file__)
    class_file = os.path.join(base_path, "class_names.pth")
    model_file = os.path.join(base_path, MODEL_PATH)

    # 2. Tải model từ Drive nếu chưa có
    if not os.path.exists(model_file):
        with st.spinner("Đang tải dữ liệu AI từ Google Drive..."):
            url = f'https://drive.google.com/uc?id={FILE_ID}'
            gdown.download(url, model_file, quiet=False)

    gc.collect()

    # 3. Load danh sách loài (Phu Quoc, Hmong, Fish...) [cite: 1, 2]
    if not os.path.exists(class_file):
        st.error(f"Lỗi: Không tìm thấy file {class_file} trong thư mục!")
        st.stop()
        
    classes = torch.load(class_file, map_location="cpu", weights_only=True)
    
    # 4. Khởi tạo mô hình Swin Transformer Tiny
    net = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(classes))
    
    # 5. Nạp trọng số
    state_dict = torch.load(model_file, map_location="cpu", weights_only=True)
    net.load_state_dict(state_dict)
    
    del state_dict
    gc.collect()
    net.eval()
    return net, classes

# Khởi chạy hệ thống
try:
    model, class_names = load_ai()
except Exception as e:
    st.error(f"Lỗi khởi động: {e}")
    st.stop()

# --- XỬ LÝ ẢNH ---
uploaded_file = st.file_uploader("Tải ảnh chó hoặc hải sản lên...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB')
    st.image(img, caption="Ảnh gốc", use_container_width=True)
    
    if st.button("🚀 Bắt đầu phân tích"):
        with st.spinner("AI đang nhận diện..."):
            # Tiền xử lý ảnh
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
            
            # Kết quả nhận diện
            ten_loai = class_names[idx]
            st.success(f"### Kết quả: {ten_loai.upper()}")
            st.write(f"Độ tin cậy: **{conf.item()*100:.2f}%**")
            
            # Chú thích dựa trên dữ liệu bạn cung cấp [cite: 1, 2]
            if "Phu Quoc" in ten_loai:
                st.info("💡 **Ghi chú:** Chó xoáy Phú Quốc là quốc khuyển Việt Nam, nổi tiếng với xoáy lông lưng.")
            elif "Hmong" in ten_loai:
                st.info("💡 **Ghi chú:** Chó H'mông cộc đuôi - loài chó săn cổ xưa vùng cao phía Bắc.")
            elif "fish" in ten_loai.lower() or "Snapper" in ten_loai:
                st.info("🐠 **Hải sản:** Loài này thuộc danh mục quản lý hải sản của hệ thống.")
        gc.collect()
