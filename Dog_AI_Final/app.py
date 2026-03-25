import streamlit as st
import torch
import timm
import gdown
import os
import gc
from PIL import Image
from rembg import remove
from torchvision import transforms

# --- CẤU HÌNH HỆ THỐNG ---
# ID file từ Google Drive bạn đã cung cấp
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="UPT AI Scanner", page_icon="🐾", layout="centered")

# --- GIAO DIỆN ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🐾 AI Breed & Seafood Scanner</h1>", unsafe_allow_stdio=True)
st.write("<p style='text-align: center;'>Dự án nhận diện Chó nội địa & Hải sản - UPT 2026</p>", unsafe_allow_stdio=True)

# --- HÀM TẢI MÔ HÌNH TỐI ƯU ---
@st.cache_resource
def load_ai():
    # 1. Tải file từ Drive nếu chưa có
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Đang kết nối Drive để tải mô hình AI..."):
            url = f'https://drive.google.com/uc?id={FILE_ID}'
            gdown.download(url, MODEL_PATH, quiet=False)

    # 2. Giải phóng bộ nhớ đệm trước khi load
    gc.collect()
    
    # 3. Load danh sách loài (class_names.pth)
    # File này chứa các loài: Phu Quoc Ridgeback, Hmong Docked Tail, Snapper...
    classes = torch.load("class_names.pth", map_location="cpu", weights_only=True)
    
    # 4. Khởi tạo cấu trúc mô hình Swin Transformer Tiny
    net = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(classes))
    
    # 5. Nạp trọng số và xóa biến tạm ngay lập tức để tiết kiệm RAM
    state_dict = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    net.load_state_dict(state_dict)
    
    del state_dict # Xóa dữ liệu thừa
    gc.collect()   # Dọn dẹp bộ nhớ hệ thống
    
    net.eval()
    return net, classes

# Khởi chạy nạp AI
try:
    model, class_names = load_ai()
except Exception as e:
    st.error(f"Lỗi khởi động hệ thống: {e}")
    st.stop()

# --- KHU VỰC XỬ LÝ ẢNH ---
uploaded_file = st.file_uploader("Tải ảnh chó hoặc hải sản lên...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Ảnh gốc", use_container_width=True)
    
    if st.button("🚀 Bắt đầu phân tích"):
        with st.spinner("AI đang tách nền và nhận diện..."):
            # Bước 1: Tách nền bằng rembg
            # Nếu web vẫn bị lỗi 503, bạn có thể tạm tắt dòng này để tiết kiệm RAM
            try:
                clean_img = remove(img).convert('RGB')
            except:
                clean_img = img.convert('RGB') # Dự phòng nếu rembg lỗi
            
            # Bước 2: Tiền xử lý theo chuẩn Swin Transformer
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(clean_img).unsqueeze(0)
            
            # Bước 3: Dự đoán
            with torch.no_grad():
                out = model(img_t)
                prob = torch.nn.functional.softmax(out[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # Bước 4: Hiển thị kết quả
            ten_loai = class_names[idx]
            st.success(f"### Kết quả: {ten_loai.upper()}")
            st.progress(float(conf.item()))
            st.write(f"Độ tin cậy: **{conf.item()*100:.2f}%**")
            
            # Chú thích đặc biệt (Dựa trên dữ liệu class_names của bạn)
            if "Phu Quoc" in ten_loai:
                st.info("💡 **Ghi chú:** Đây là giống chó xoáy Phú Quốc - Quốc khuyển của Việt Nam.")
            elif "Hmong" in ten_loai:
                st.info("💡 **Ghi chú:** Chó H'mông cộc đuôi - loài chó săn trung thành của vùng cao phía Bắc.")
            elif "fish" in ten_loai.lower() or "Snapper" in ten_loai:
                st.info("🐠 **Hải sản:** Loài này thuộc danh mục quản lý hải sản thương mại.")

        # Giải phóng bộ nhớ sau mỗi lần dự đoán
        gc.collect()
