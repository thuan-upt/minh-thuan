import streamlit as st
import torch
import timm
import os
import gdown
from PIL import Image
from rembg import remove, new_session
from torchvision import transforms

# --- THÔNG TIN HỆ THỐNG ---
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="AI Breed Scanner", page_icon="🐾")

# --- HÀM NẠP TÀI NGUYÊN (DÙNG CACHE ĐỂ TIẾT KIỆM RAM) ---
@st.cache_resource
def init_ai():
    # 1. Tải model từ Drive nếu chưa có
    if not os.path.exists(MODEL_PATH):
        gdown.download(f'https://drive.google.com/uc?id={FILE_ID}', MODEL_PATH, quiet=False)

    # 2. Nạp class_names (File này phải có trên GitHub của bạn)
    classes = torch.load("class_names.pth", map_location="cpu")
    
    # 3. Khởi tạo Swin Transformer Tiny
    net = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(classes))
    net.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    net.eval()
    
    # 4. Khởi tạo session tách nền bản rút gọn (u2netp) để không bị treo
    rem_session = new_session("u2netp")
    
    return net, classes, rem_session

# Thực thi khởi động
try:
    model, class_names, bg_session = init_ai()
    st.sidebar.success("✅ AI System Ready")
except Exception as e:
    st.sidebar.error("⏳ Đang khởi tạo... Vui lòng đợi 1-2 phút")

# --- GIAO DIỆN ---
st.title("🐾 AI Breed & Seafood Scanner")
st.write("**Sinh viên thực hiện:** Minh Thuận (UPT)")

file = st.file_uploader("Tải ảnh Chó hoặc Cá...", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file)
    st.image(img, caption="Ảnh gốc", use_container_width=True)
    
    if st.button("🚀 Bắt đầu Phân tích"):
        with st.spinner("Đang tách nền và nhận diện..."):
            # BƯỚC 1: TÁCH NỀN (U2-Netp)
            clean_img = remove(img, session=bg_session).convert('RGB')
            
            # BƯỚC 2: TIỀN XỬ LÝ (TRANSFORM)
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(clean_img).unsqueeze(0)
            
            # BƯỚC 3: DỰ ĐOÁN (SWIN TRANSFORMER)
            with torch.no_grad():
                out = model(img_t)
                prob = torch.nn.functional.softmax(out[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # BƯỚC 4: KẾT QUẢ
            st.divider()
            st.success(f"### Kết quả: {class_names[idx].upper()}")
            st.write(f"Độ tin cậy: **{conf.item()*100:.2f}%**")
            st.progress(float(conf.item()))
