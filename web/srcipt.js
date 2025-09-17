
    function login() {
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;

      if (username === "thuan" && password === "9999") {
        localStorage.setItem("user", JSON.stringify({ name: username }));
        window.location.href = "home.html";
      } else {
        const error = document.getElementById("error");
        error.textContent = "Sai tên đăng nhập hoặc mật khẩu!";
        setTimeout(() => error.textContent = "", 3000);
      }
    }

    function parseJwt(token) {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c =>
        '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      ).join(''));
      return JSON.parse(jsonPayload);
    }

    function handleCredentialResponse(response) {
      const data = parseJwt(response.credential);
      console.log("Google user:", data);

      // Lưu thông tin người dùng
      localStorage.setItem("user", JSON.stringify(data));

      // Điều hướng
      window.location.href = "home.html";
    }
