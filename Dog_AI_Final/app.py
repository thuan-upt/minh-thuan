import streamlit as st
import torch
import timm
import os
import gdown
from PIL import Image
from rembg import remove, new_session
from torchvision import transforms

# --- CẤU HÌNH HỆ THỐNG ---
# ID file dog_swin_model.pth của Minh Thuận
FILE_ID = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
MODEL_PATH = 'dog_swin_model.pth'

st.set_page_config(page_title="UPT AI Breed Scanner", page_icon="🐾", layout="centered")

# --- HÀM TẢI TÀI NGUYÊN (TỐI ƯU RAM) ---
@st.cache_resource
def load_resources():
    # 1. Tải model từ Google Drive nếu chưa có trên server
    if not os.path.exists(MODEL_PATH):
        url = f'https://drive.google.com/uc?id={FILE_ID}'
        gdown.download(url, MODEL_PATH, quiet=False)

    # 2. Khởi tạo session tách nền bản Lite (u2netp) để tránh treo web
    bg_session = new_session("u2netp") 

    # 3. Nạp danh sách loài
    # Đảm bảo file class_names.pth đã được upload lên cùng thư mục trên GitHub
    class_names = torch.load("class_names.pth", map_location="cpu")
    
    # 4. Khởi tạo và nạp trọng số Model Swin Transformer
    model = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(class_names))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    
    return model, class_names, bg_session

# Thực thi nạp tài nguyên
with st.spinner("Đang khởi động hệ thống AI... Vui lòng đợi."):
    try:
        model, class_names, bg_session = load_resources()
        st.sidebar.success("✅ Hệ thống AI đã sẵn sàng!")
    except Exception as e:
        st.sidebar.error(f"❌ Lỗi khởi động: {e}")

# --- GIAO DIỆN NGƯỜI DÙNG ---
st.title("🐾 AI Breed & Seafood Scanner")
st.markdown("---")
st.write("**Sinh viên thực hiện:** Minh Thuận (UPT)")
st.write("Thuật toán: **Swin Transformer** (Nhận diện) & **U2-Net** (Tách nền)")

uploaded_file = st.file_uploader("Chọn ảnh chó hoặc hải sản để nhận diện...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Hiển thị ảnh gốc
    img = Image.open(uploaded_file)
    st.image(img, caption="Ảnh bạn đã tải lên", use_container_width=True)
    
    if st.button("🚀 Bắt đầu Phân tích"):
        with st.spinner("AI đang tách nền và quét đặc điểm đặc trưng..."):
            # BƯỚC 1: TÁCH NỀN
            # Chuyển đổi để loại bỏ nền nhiễu, giúp Swin Transformer tập trung vào vật thể
            clean_img = remove(img, session=bg_session).convert('RGB')
            
            # BƯỚC 2: TIỀN XỬ LÝ (TRANSFORM)
            tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = tf(clean_img).unsqueeze(0)
            
            # BƯỚC 3: DỰ ĐOÁN
            with torch.no_grad():
                output = model(img_t)
                prob = torch.nn.functional.softmax(output[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # BƯỚC 4: HIỂN THỊ KẾT QUẢ
            st.divider()
            result_name = class_names[idx].upper()
            confidence = conf.item()
            
            st.subheader(f"Kết quả: {result_name}")
            st.write(f"Độ tin cậy của AI: **{confidence*100:.2f}%**")
            st.progress(confidence)
            
            # Hiển thị ảnh đã tách nền để minh họa quá trình AI làm việc
            with st.expander("Xem quy trình AI xử lý ảnh (Tách nền)"):
                st.image(clean_img, caption="Ảnh sau khi tách nền")
