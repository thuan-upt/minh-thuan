document.addEventListener('DOMContentLoaded', () => {

    // --- KHU VỰC TÙY CHỈNH ---
    // Thay đổi nội dung, link ảnh, link nhạc ở đây
    const config = {
        // Nhạc nền
        musicUrl: "mp3/mychi.mp3",

        // Lời nhắn trong popup
        modalMessage: {
            line1: "Hôm nay là 20/10, một ngày đặc biệt dành cho những người con gái đặc biệt.",
            line2: "bạn Thảo là một trong số đó, dịu dàng, tốt bụng và luôn giúp đỡ những người xung quanh.",
        },

        // Các lời chúc chạy nối tiếp
        sequentialMessages: [
            "Chúc bạn Thảo một ngày mới thật tươi đẹp!",
            "Cười lên nhé! Hôm nay là một ngày tuyệt vời!",
            "Gửi đến bạn Thảo một câu chúc thật ấm áp",
            "bạn Thảo là người bạn tốt và đáng mến",
            "Chúc bạn Thảo luôn may mắn và thành công",
            "Cảm ơn bạn Thảo đã luôn là chính mình ❤️"
        ],
        
        // Ảnh cho màn hình trái tim 3D (dùng nhiều ảnh cho đa dạng)
        heartSceneImages: [
            'img/anh1.jpg', 'img/anh2.jpg',
            'img/anh3.jpg', 'img/anh4.jpg',
            'img/anh5.jpg', 'img/anh6.jpg'
            
        ],
        
        // Ảnh cho slider ở phía trước (chọn vài ảnh đẹp nhất)
        sliderImages: [
            'img/anh1.jpg',
            'img/anh2.jpg',
            'img/anh3.jpg',
            'img/anh4.jpg',
            'img/anh5.jpg',
            'img/anh6.jpg'
        ]
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

    // --- Cài đặt ban đầu ---
    backgroundMusic.src = config.musicUrl;

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

    // --- Sự kiện click màn hình đầu tiên ---
    screens.initial.addEventListener('click', () => {
        backgroundMusic.play().catch(e => console.error("Lỗi khi phát nhạc:", e));
        switchScreen('initial', 'flower');
        
        setTimeout(() => {
            modal.classList.add('visible');
            startTyping();
        }, 3500);
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
        const imageCount = 80;
        
        // TỰ ĐỘNG ĐIỀU CHỈNH BÁN KÍNH 3D THEO MÀN HÌNH
        const screenWidth = window.innerWidth;
        const screenHeight = window.innerHeight;
        const smallerDimension = Math.min(screenWidth, screenHeight);
        const radius = Math.max(150, smallerDimension * 0.4); // Đảm bảo bán kính không quá nhỏ

        for (let i = 0; i < imageCount; i++) {
            const card = document.createElement('div');
            card.classList.add('image-card');
            const img = document.createElement('img');
            img.src = config.heartSceneImages[i % config.heartSceneImages.length];
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
        foregroundSliderImg.src = config.sliderImages[0];
        setInterval(() => {
            sliderIndex = (sliderIndex + 1) % config.sliderImages.length;
            foregroundSliderImg.src = config.sliderImages[sliderIndex];
        }, 5000);
    }
});