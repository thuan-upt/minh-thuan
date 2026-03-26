import streamlit as st
import torch
import timm
import gdown
import os
from PIL import Image
from rembg import remove
from torchvision import transforms

# --- CẤU HÌNH GOOGLE DRIVE ---
# Thay 'YOUR_FILE_ID' bằng mã ID file dog_swin_model.pth của bạn
FILE_ID = 'YOUR_FILE_ID_HERE'
MODEL_PATH = 'dog_swin_model.pth'

# --- GIAO DIỆN ---
st.set_page_config(page_title="AI Dog & Fish Scanner", page_icon="🐾", layout="centered")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🐾 AI Breed & Seafood Scanner</h1>", unsafe_allow_stdio=True)
st.write("<p style='text-align: center;'>Hệ thống nhận diện thông minh dành cho chó và hải sản (Dự án UPT)</p>", unsafe_allow_stdio=True)

# --- LOAD MODEL ---
@st.cache_resource
def load_ai():
    # 1. Tải model từ Google Drive nếu chưa tồn tại trên server
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Đang tải mô hình AI từ Google Drive... Vui lòng đợi trong giây lát."):
            url = f'https://drive.google.com/uc?id={FILE_ID}'
            gdown.download(url, MODEL_PATH, quiet=False)

    # 2. Load danh sách loài
    classes = torch.load("class_names.pth", map_location="cpu")
    
    # 3. Load khung mô hình
    net = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(classes))
    
    # 4. Nạp trọng số từ file đã tải
    net.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    net.eval()
    return net, classes

model, class_names = load_ai()

# --- XỬ LÝ ---
uploaded_file = st.file_uploader("Tải ảnh lên để AI bắt đầu quét...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Ảnh gốc", use_container_width=True)
    
    if st.button("🚀 Bắt đầu phân tích"):
        with st.spinner("AI đang tách nền và nhận diện đặc điểm..."):
            # 1. Tách nền chuyên nghiệp
            clean_img = remove(img).convert('RGB')
            
            # 2. Tiền xử lý
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(clean_img).unsqueeze(0)
            
            # 3. Dự đoán
            with torch.no_grad():
                out = model(img_t)
                prob = torch.nn.functional.softmax(out[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # 4. Hiển thị kết quả
            st.success(f"### Kết quả: {class_names[idx].upper()}")
            st.progress(float(conf.item()))
            st.write(f"Độ tin cậy: **{conf.item()*100:.2f}%**")
            
            # Thông tin bổ sung dựa trên danh sách loài của bạn
            if "Phu Quoc" in class_names[idx]:
                st.info("💡 **Ghi chú:** Chó xoáy Phú Quốc là quốc khuyển Việt Nam, nổi tiếng với xoáy lông lưng.")
            elif "fish" in class_names[idx].lower() or "Snapper" in class_names[idx]:
                st.info("🐠 **Hải sản:** Đây là loài cá phổ biến trong hệ thống quản lý hải sản của bạn.")