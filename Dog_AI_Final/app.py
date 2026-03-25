import streamlit as st
import torch
import timm
import gdown
import os
from PIL import Image
from rembg import remove
from torchvision import transforms

# --- CẤU HÌNH HỆ THỐNG ---
# ID file từ link Drive bạn cung cấp
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="UPT AI Dog & Fish Scanner", page_icon="🐾", layout="centered")

# --- GIAO DIỆN NGƯỜI DÙNG ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🐾 AI Breed & Seafood Scanner</h1>", unsafe_allow_stdio=True)
st.write("<p style='text-align: center;'>Dự án nhận diện thông minh - Đại học Phan Thiết (UPT)</p>", unsafe_allow_stdio=True)

# --- HÀM TẢI MÔ HÌNH ---
@st.cache_resource
def load_ai():
    # 1. Tải file trọng số từ Google Drive nếu chưa có trên server
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Đang tải mô hình AI từ Google Drive (khoảng 150MB)..."):
            url = f'https://drive.google.com/uc?id={FILE_ID}'
            try:
                gdown.download(url, MODEL_PATH, quiet=False)
            except Exception as e:
                st.error(f"Lỗi tải file từ Drive: {e}")
                st.stop()

    # 2. Tải danh sách loài (File class_names.pth phải có sẵn trên GitHub)
    try:
        classes = torch.load("class_names.pth", map_location="cpu")
    except Exception as e:
        st.error("Không tìm thấy file class_names.pth trên GitHub!")
        st.stop()
    
    # 3. Khởi tạo cấu trúc mô hình Swin Transformer
    net = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(classes))
    
    # 4. Nạp trọng số vào mô hình
    net.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    net.eval()
    return net, classes

# Gọi hàm tải AI
model, class_names = load_ai()

# --- KHU VỰC XỬ LÝ ẢNH ---
uploaded_file = st.file_uploader("Tải ảnh chó hoặc hải sản lên đây...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Ảnh gốc đã tải lên", use_container_width=True)
    
    if st.button("🚀 Bắt đầu nhận diện"):
        with st.spinner("AI đang phân tích đặc điểm loài..."):
            # Bước 1: Tách nền bằng rembg để tăng độ chính xác
            clean_img = remove(img).convert('RGB')
            
            # Bước 2: Tiền xử lý ảnh (Resize 224x224, Normalize)
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(clean_img).unsqueeze(0)
            
            # Bước 3: Dự đoán bằng mô hình
            with torch.no_grad():
                out = model(img_t)
                prob = torch.nn.functional.softmax(out[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # Bước 4: Hiển thị kết quả
            ten_loai = class_names[idx]
            st.success(f"### Kết quả: {ten_loai.upper()}")
            st.progress(float(conf.item()))
            st.write(f"Độ tin cậy: **{conf.item()*100:.2f}%**")
            
            # Hiển thị thông tin bổ sung dựa trên loài
            # Chú thích về chó Việt Nam
            if "Phu Quoc" in ten_loai:
                st.info("💡 **Ghi chú:** Chó xoáy Phú Quốc là 'quốc khuyển' Việt Nam, nổi tiếng với xoáy lông trên lưng.")
            elif "Hmong" in ten_loai:
                st.info("💡 **Ghi chú:** Chó H'mông cộc đuôi là giống chó săn cổ xưa của người dân tộc vùng cao.")
            # Chú thích về hải sản
            elif "fish" in ten_loai.lower() or "Snapper" in ten_loai:
                st.info("🐠 **Hải sản:** Đây là loài thủy sản nằm trong danh mục quản lý của bạn.")
