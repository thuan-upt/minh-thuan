import streamlit as st
import torch
import timm
import gdown
import os
import gc
from PIL import Image
from torchvision import transforms

# --- CẤU HÌNH ---
# ID file từ link Google Drive bạn đã cung cấp [cite: 1]
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="UPT AI Scanner", page_icon="🐾")

# --- GIAO DIỆN ---
# Sửa lỗi: Đổi unsafe_allow_stdio thành unsafe_allow_html
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🐾 AI Breed & Seafood Scanner</h1>", unsafe_allow_html=True)
st.info("Hệ thống đang chạy chế độ tối ưu bộ nhớ cho server UPT.")

# --- LOAD AI ---
@st.cache_resource
def load_ai():
    # Tải model từ Drive nếu chưa có [cite: 2]
    if not os.path.exists(MODEL_PATH):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        try:
            gdown.download(url, MODEL_PATH, quiet=False)
        except Exception as e:
            st.error(f"Lỗi tải mô hình: {e}")
            st.stop()

    gc.collect()
    # Load danh sách loài từ file trên GitHub [cite: 2]
    try:
        classes = torch.load("class_names.pth", map_location="cpu", weights_only=True)
    except:
        st.error("Không tìm thấy file class_names.pth!")
        st.stop()
    
    # Khởi tạo mô hình Swin Transformer Tiny [cite: 1]
    net = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(classes))
    
    # Nạp trọng số và giải phóng RAM [cite: 1]
    state_dict = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    net.load_state_dict(state_dict)
    
    del state_dict
    gc.collect()
    net.eval()
    return net, classes

# Khởi tạo ứng dụng
try:
    model, class_names = load_ai()
except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
    st.stop()

# --- XỬ LÝ ẢNH ---
uploaded_file = st.file_uploader("Tải ảnh chó hoặc hải sản (JPG, PNG)...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB')
    st.image(img, caption="Ảnh đầu vào", use_container_width=True)
    
    if st.button("🚀 Phân tích ngay"):
        with st.spinner("AI đang nhận diện đặc điểm..."):
            # Tiền xử lý ảnh theo chuẩn mô hình [cite: 1]
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(img).unsqueeze(0)
            
            # Dự đoán [cite: 1]
            with torch.no_grad():
                out = model(img_t)
                prob = torch.nn.functional.softmax(out[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # Hiển thị kết quả nhận diện giống chó/hải sản [cite: 1]
            ten_loai = class_names[idx]
            st.success(f"### Kết quả: {ten_loai.upper()}")
            st.write(f"Độ tin cậy: **{conf.item()*100:.2f}%**")
            
            # Ghi chú cho các giống chó Việt Nam và hải sản [cite: 1]
            if "Phu Quoc" in ten_loai:
                st.info("💡 **Ghi chú:** Chó xoáy Phú Quốc là giống chó quý có xoáy lông lưng đặc trưng của Việt Nam.")
            elif "Hmong" in ten_loai:
                st.info("💡 **Ghi chú:** Chó H'mông cộc đuôi - loài chó săn cổ xưa vùng cao phía Bắc.")
            elif "fish" in ten_loai.lower() or "Snapper" in ten_loai:
                st.info("🐠 **Hải sản:** Loài này nằm trong danh mục quản lý hải sản của hệ thống.")
        
        # Dọn dẹp bộ nhớ sau khi phân tích
        gc.collect()
