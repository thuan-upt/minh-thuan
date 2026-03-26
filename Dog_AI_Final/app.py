import streamlit as st
import torch
import timm
import gdown
import os
from PIL import Image
from rembg import remove, new_session
from torchvision import transforms

# --- CẤU HÌNH HỆ THỐNG ---
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' # ID Drive của Minh Thuận
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="UPT AI Scanner", page_icon="🐾")

# --- TỐI ƯU HÓA TẢI MODEL ---
@st.cache_resource
def load_resources():
    # 1. Tải model từ Drive nếu chưa có
    if not os.path.exists(MODEL_PATH):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        gdown.download(url, MODEL_PATH, quiet=False)

    # 2. Khởi tạo Session tách nền (Chỉ làm 1 lần duy nhất để tiết kiệm RAM)
    # Sử dụng model 'u2netp' (bản lite) để web chạy nhanh hơn
    rembg_session = new_session("u2netp") 

    # 3. Nạp danh sách loài và Model Swin Transformer
    class_names = torch.load("class_names.pth", map_location="cpu")
    model = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(class_names))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    
    return model, class_names, rembg_session

# Nạp tài nguyên vào bộ nhớ đệm
with st.spinner("Đang khởi động hệ thống AI..."):
    model, class_names, bg_session = load_resources()

# --- GIAO DIỆN NGƯỜI DÙNG ---
st.title("🐾 AI Breed & Seafood Scanner")
st.info("Hệ thống nhận diện sử dụng thuật toán Swin Transformer & U2-Net")

uploaded_file = st.file_uploader("Tải ảnh để phân tích", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns(2)
    img = Image.open(uploaded_file)
    with col1:
        st.image(img, caption="Ảnh gốc", use_container_width=True)
    
    if st.button("🚀 Bắt đầu Phân tích Cao cấp"):
        with st.spinner("AI đang tách nền và quét đặc điểm sinh học..."):
            # BƯỚC 1: TÁCH NỀN TỐI ƯU
            # Chỉ xử lý ảnh ở kích thước vừa đủ để tiết kiệm tài nguyên
            clean_img = remove(img, session=bg_session).convert('RGB')
            
            with col2:
                st.image(clean_img, caption="AI đã tách nền", use_container_width=True)
            
            # BƯỚC 2: TIỀN XỬ LÝ (TRANSFORM)
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(clean_img).unsqueeze(0)
            
            # BƯỚC 3: DỰ ĐOÁN VỚI SWIN TRANSFORMER
            with torch.no_grad():
                output = model(img_t)
                prob = torch.nn.functional.softmax(output[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # BƯỚC 4: HIỂN THỊ KẾT QUẢ CHUYÊN NGHIỆP
            st.success(f"### Kết quả nhận diện: {class_names[idx].upper()}")
            
            # Thanh tiến trình hiển thị độ tin cậy
            confidence_score = float(conf.item())
            st.write(f"Độ chính xác dự đoán: **{confidence_score*100:.2f}%**")
            st.progress(confidence_score)

            # Phân loại thông báo dựa trên loài 
            label = class_names[idx].lower()
            if "phu quoc" in label:
                st.warning("🐕 Đây là chó xoáy Phú Quốc - Đặc hữu của Việt Nam!")
            elif "fish" in label or "snapper" in label:
                st.info("🐠 Đối tượng được xác định thuộc nhóm hải sản thương phẩm.")
