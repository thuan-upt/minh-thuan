import streamlit as st
import torch
import timm
import os
import gdown
from PIL import Image
from rembg import remove
from torchvision import transforms

# --- TẢI MODEL TỪ DRIVE ---
@st.cache_resource
def download_model():
    file_id = '1VhP5z4f2pAk4ip5dZ2YsgWwfKMM3OA1i' 
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'dog_swin_model.pth'
    
    if not os.path.exists(output):
        with st.spinner('Đang tải bộ não AI từ Drive (Vui lòng đợi giây lát)...'):
            gdown.download(url, output, quiet=False)
    return output

# --- NẠP MODEL VÀ DANH SÁCH LOÀI ---
@st.cache_resource
def load_all():
    device = torch.device("cpu")
    model_path = download_model()
    
    # Đảm bảo file class_names.pth đã có trên GitHub của bạn
    class_names = torch.load("class_names.pth", map_location=device)
    
    model = timm.create_model('swin_tiny_patch4_window7_224', pretrained=False, num_classes=len(class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model, class_names, device

model, class_names, device = load_all()

# --- GIAO DIỆN CHÍNH ---
st.title("🐾 AI Dog & Fish Recognition")
st.write("Dự án IT - Sinh viên Minh Thuận (UPT)")

uploaded_file = st.file_uploader("Chọn ảnh để nhận diện...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='Ảnh gốc', use_container_width=True)
    
    if st.button('🚀 Bắt đầu Quét'):
        with st.spinner('AI đang phân tích...'):
            # Tách nền
            clean_img = remove(image).convert('RGB')
            
            # Tiền xử lý
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            img_t = transform(clean_img).unsqueeze(0)
            
            # Dự đoán
            with torch.no_grad():
                output = model(img_t)
                prob = torch.nn.functional.softmax(output[0], dim=0)
                conf, idx = torch.max(prob, 0)
            
            # Hiển thị
            st.success(f"### Kết quả: {class_names[idx].upper()}")
            st.write(f"Độ tin cậy: {conf.item()*100:.2f}%")
