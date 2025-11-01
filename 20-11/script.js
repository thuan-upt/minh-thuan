document.addEventListener('DOMContentLoaded', () => {

    // Biến toàn cục để lưu tên giảng viên
    let lecturerName = '';
    let normalizedName = '';

    // --- KHU VỰC TÙY CHỈNH ---
    const config = {
        musicUrl: "mp3/nt.mp3", // Giữ nguyên nhạc của bạn

        // Lời nhắn sẽ được cập nhật sau khi nhập tên
        modalMessage: {
            line1: "",
            line2: ""
        },

        // Lời chúc nối tiếp (cũng sẽ được cập nhật)
        sequentialMessages: [],
        
        // Mảng ảnh (sẽ được tạo tự động)
        heartSceneImages: [],
        sliderImages: [],
        
        // Ảnh dự phòng (QUAN TRỌNG)
        defaultImage: 'img/default.png' 
    };
    // --- KẾT THÚC KHU VỰC TÙY CHỈNH ---


    // --- Lấy các phần tử từ DOM ---
    const loader = document.getElementById('loader');
    const screens = {
        initial: document.getElementById('initial-screen'),
        flower: document.getElementById('flower-scene'),
        heart: document.getElementById('heart-scene')
    };
    const modal = document.getElementById('message-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const backgroundMusic = document.getElementById('background-music');
    const seqMessagesContainer = document.getElementById('sequential-messages');
    const foregroundSliderImg = document.querySelector('.foreground-slider img');
    
    // Các phần tử của form
    const submitNameBtn = document.getElementById('submitNameBtn');
    const teacherNameInput = document.getElementById('teacherNameInput');
    
    // Các phần tử nội dung động
    const modalTitleDynamic = document.getElementById('modal-title-dynamic');
    const loveTextDynamic = document.getElementById('love-text-dynamic');


    // --- Cài đặt ban đầu ---
    backgroundMusic.src = config.musicUrl;
    foregroundSliderImg.src = config.defaultImage; // Đặt ảnh dự phòng ban đầu

    // --- Xử lý màn hình chờ ---
    window.addEventListener('load', () => {
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
        }, 500);
    });
    
    // --- Hàm chuyển màn hình mượt mà ---
    function switchScreen(currentScreen, nextScreen) {
        screens[currentScreen].classList.remove('active');
        setTimeout(() => {
            screens[nextScreen].classList.add('active');
        }, 500);
    }

    // --- === CÁC HÀM MỚI CHO 20/11 === ---

    // 1. Hàm chuẩn hóa tên giảng viên
    function normalizeName(name) {
        return name.toLowerCase()
            .replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a")
            .replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e")
            .replace(/ì|í|ị|ỉ|ĩ/g, "i")
            .replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o")
            .replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u")
            .replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y")
            .replace(/đ/g, "d")
            .replace(/\s/g, "-") // Thay khoảng trắng bằng dấu gạch ngang
            .replace(/[^a-z0-9-]/g, ""); // Loại bỏ các ký tự đặc biệt
    }

    // 2. Hàm tạo mảng ảnh tự động
    function generateImageArrays(baseName) {
        // Giả sử bạn có 10 ảnh cho mỗi giảng viên
        const imageCount = 10; 
        
        config.heartSceneImages = [];
        config.sliderImages = [];

        for (let i = 1; i <= imageCount; i++) {
            // Đường dẫn sẽ là: images/thay-nguyen-van-a/1.jpg
            const imgPath = `images/${baseName}/${i}.jpg`;
            
            config.heartSceneImages.push(imgPath);
            
            // Lấy 5 ảnh cuối cho slider
            if (i > imageCount - 5) {
                config.sliderImages.push(imgPath);
            }
        }
    }
    
    // 3. Hàm cập nhật nội dung động (lời chúc, tiêu đề)
    function updateDynamicContent(name) {
        // Cập nhật tiêu đề modal
        modalTitleDynamic.textContent = `Gửi ${name} 💌`;
        
        // Cập nhật lời chúc trong modal
        config.modalMessage.line1 = `Nhân ngày 20/11, em có vài lời muốn gửi đến ${name}.`;
        config.modalMessage.line2 = `Chúc ${name} luôn vui vẻ, mạnh khỏe và giữ mãi ngọn lửa nhiệt huyết với nghề.`;

        // Cập nhật lời chúc nối tiếp
        config.sequentialMessages = [
            `Chúc ${name} một ngày 20/11 thật ý nghĩa!`,
            "Cảm ơn đã luôn tận tâm với chúng em.",
            "Mong luôn mạnh khỏe và hạnh phúc.",
            `Gửi đến ${name} ngàn lời chúc tốt đẹp nhất!`,
            "Thầy/Cô là người truyền cảm hứng tuyệt vời!",
            "Cảm ơn Thầy/Cô vì tất cả ❤️"
        ];
        
        // Cập nhật chữ 3D
        loveTextDynamic.textContent = `${name} 💖`;
        
    }
   

    // --- === KẾT THÚC HÀM MỚI === ---


    // --- Sự kiện click nút Gửi (Thay thế cho sự kiện click màn hình cũ) ---
    submitNameBtn.addEventListener('click', () => {
        lecturerName = teacherNameInput.value.trim();
        
        if (lecturerName === "") {
            alert("Bạn vui lòng nhập tên Thầy/Cô!");
            return;
        }

        // 1. Chuẩn bị nội dung
        normalizedName = normalizeName(lecturerName);
        generateImageArrays(normalizedName);
        updateDynamicContent(lecturerName);

        // 2. Bắt đầu trải nghiệm
        backgroundMusic.play().catch(e => console.error("Lỗi khi phát nhạc:", e));
        switchScreen('initial', 'flower');
        
        // 3. Hiển thị modal sau khi hoa xuất hiện
        setTimeout(() => {
            modal.classList.add('visible');
            startTyping();
        }, 3500);
    });

    // Thêm sự kiện Enter cho ô nhập
    teacherNameInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            submitNameBtn.click();
        }
    });

    
    // --- Hiệu ứng gõ chữ trong Modal ---
    function typeWriter(element, text, speed, callback) {
        let i = 0;
        element.innerHTML = '';
        function typing() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(typing, speed);
            } else if (callback) {
                callback();
            }
        }
        typing();
    }

    function startTyping() {
        const typedText1 = document.getElementById('typed-text-1');
        const typedText2 = document.getElementById('typed-text-2');
        typeWriter(typedText1, config.modalMessage.line1, 50, () => {
            typeWriter(typedText2, config.modalMessage.line2, 50);
        });
    }

    // --- Sự kiện đóng modal và hiển thị lời chúc nối tiếp ---
    closeModalBtn.addEventListener('click', () => {
        modal.classList.remove('visible');
        startSequentialMessages();
    });

    // --- Hiển thị các lời chúc nối tiếp ---
    function startSequentialMessages() {
        let messageIndex = 0;
        const showNextMessage = () => {
            if (messageIndex < config.sequentialMessages.length) {
                const msg = seqMessagesContainer;
                msg.textContent = config.sequentialMessages[messageIndex];
                msg.style.opacity = 1;
                msg.style.transform = 'translateY(0)';

                setTimeout(() => {
                    msg.style.opacity = 0;
                    msg.style.transform = 'translateY(-20px)';
                    messageIndex++;
                    setTimeout(showNextMessage, 1000); 
                }, 2000); 
            } else {
                setTimeout(() => {
                    switchScreen('flower', 'heart');
                    generate3DImages();
                    startForegroundSlider();
                }, 1000);
            }
        };
        showNextMessage();
    }

    // --- Tạo các ảnh 3D cho màn hình trái tim ---
    function generate3DImages() {
        const world = document.querySelector('.world');
        world.innerHTML = '';
        const imageCount = 80; // Số lượng ảnh 3D
        
        const screenWidth = window.innerWidth;
        const screenHeight = window.innerHeight;
        const smallerDimension = Math.min(screenWidth, screenHeight);
        // TĂNG bán kính sắp xếp ảnh để chúng dàn trải hơn, ít chồng chéo
        const radius = Math.max(200, smallerDimension * 0.5); // Thay đổi giá trị này
        // Có thể thử các giá trị như smallerDimension * 0.6 hoặc 0.7 nếu muốn xa hơn nữa

        for (let i = 0; i < imageCount; i++) {
            const card = document.createElement('div');
            card.classList.add('image-card');
            const img = document.createElement('img');
            
            // Lấy ảnh từ mảng đã tạo, xoay vòng
            img.src = config.heartSceneImages[i % config.heartSceneImages.length];
            // THÊM ẢNH DỰ PHÒNG
            img.onerror = function() { this.src = config.defaultImage; };
            
            card.appendChild(img);

            const theta = Math.acos((2 * Math.random()) - 1);
            const phi = Math.random() * 2 * Math.PI;

            const x = radius * Math.sin(theta) * Math.cos(phi);
            const y = radius * Math.sin(theta) * Math.sin(phi);
            const z = radius * Math.cos(theta);
            
            card.style.transform = `translate3d(${x}px, ${y}px, ${z}px) rotateY(${phi}rad) rotateX(${theta}rad)`;
            world.appendChild(card);
        }
    }
    
    // --- Bắt đầu chạy Slider ảnh ở phía trước ---
    function startForegroundSlider() {
        let sliderIndex = 0;
        
        // THÊM ẢNH DỰ PHÒNG
        foregroundSliderImg.onerror = function() { this.src = config.defaultImage; };
        
        if(config.sliderImages.length > 0) {
            foregroundSliderImg.src = config.sliderImages[0];
            setInterval(() => {
                sliderIndex = (sliderIndex + 1) % config.sliderImages.length;
                foregroundSliderImg.src = config.sliderImages[sliderIndex];
            }, 5000); // Đổi ảnh sau mỗi 5 giây
        } else {
            foregroundSliderImg.src = config.defaultImage;
        }
    }
});