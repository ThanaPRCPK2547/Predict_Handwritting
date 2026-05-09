(function () {
  if (localStorage.getItem("darkMode") === "true") {
    document.documentElement.classList.add("dark");
  }

  const TOKEN_KEY = "thaiDigitToken";
  const USER_KEY = "thaiDigitUser";
  const API_BASE = localStorage.getItem("thaiDigitApiBase")
    || (window.location.protocol === "file:" ? "http://localhost:8000" : "");

  function decodeToken(token) {
    try {
      const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
      return JSON.parse(atob(payload));
    } catch (error) {
      return {};
    }
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getUser() {
    const token = getToken();
    if (!token) return null;
    const payload = decodeToken(token);
    return {
      username: payload.sub || localStorage.getItem(USER_KEY) || "",
      role: payload.role || "user",
      exp: payload.exp || 0,
    };
  }

  function isTokenExpired(user) {
    return !user || !user.exp || Date.now() >= user.exp * 1000;
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function authHeaders() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function normalizeError(detail) {
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg || JSON.stringify(item)).join(", ");
    }
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object") return JSON.stringify(detail);
    return "Request failed";
  }

  async function request(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    const hasBody = options.body !== undefined && options.body !== null;
    const isFormData = hasBody && options.body instanceof FormData;
    const isUrlEncoded = hasBody && options.body instanceof URLSearchParams;

    if (options.auth !== false) Object.assign(headers, authHeaders());
    if (hasBody && !isFormData && !isUrlEncoded && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
    if (isUrlEncoded && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/x-www-form-urlencoded";
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      body: hasBody && headers["Content-Type"] === "application/json"
        ? JSON.stringify(options.body)
        : options.body,
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      if (response.status === 401) logout();
      throw new Error(normalizeError(data.detail || data));
    }
    return data;
  }

  async function login(username, password) {
    const form = new URLSearchParams({ username, password });
    const data = await request("/login", { method: "POST", body: form, auth: false });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(USER_KEY, username);
    return getUser();
  }

  async function register(username, password, role) {
    return request("/register", {
      method: "POST",
      auth: false,
      body: { username, password, role },
    });
  }

  function requireAuth(options = {}) {
    const user = getUser();
    if (isTokenExpired(user)) {
      logout();
      window.location.href = "login.html";
      return null;
    }
    if (options.admin && user.role !== "admin") {
      window.location.href = "predictor.html";
      return null;
    }
    return user;
  }

  function thaiDigit(value) {
    const single = ["๐", "๑", "๒", "๓", "๔", "๕", "๖", "๗", "๘", "๙"];
    const n = Number(value);
    if (n >= 10 && n <= 15) {
      return single[Math.floor(n / 10)] + single[n % 10];
    }
    return single[n] || "--";
  }

  function canvasToPixels(canvas) {
    const small = document.createElement("canvas");
    small.width = 28;
    small.height = 28;
    const smallCtx = small.getContext("2d", { willReadFrequently: true });
    smallCtx.clearRect(0, 0, 28, 28);
    smallCtx.drawImage(canvas, 0, 0, 28, 28);

    const data = smallCtx.getImageData(0, 0, 28, 28).data;
    const pixels = [];
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const a = data[i + 3] / 255;
      const luma = 0.299 * r + 0.587 * g + 0.114 * b;
      pixels.push(Math.round(Math.max(0, 255 - luma) * a));
    }
    return pixels;
  }

  async function predict(pixels) {
    return request("/predict", {
      method: "POST",
      body: { canvas: { pixels } },
    });
  }

  async function train(pixels, label) {
    return request("/train", {
      method: "POST",
      body: { canvas: { pixels }, label: Number(label) },
    });
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href="login.html"]');
    if (link && link.textContent.toLowerCase().includes("logout")) logout();
  });

  window.ThaiDigitAPI = {
    apiBase: API_BASE,
    getUser,
    login,
    logout,
    predict,
    register,
    request,
    requireAuth,
    thaiDigit,
    train,
    canvasToPixels,
  };
}());
