const API_BASE = `${window.location.protocol}//${window.location.hostname}:5000/api`;

const API = {
    cars: `${API_BASE}/cars`,
    car: (id) => `${API_BASE}/cars/${id}`,
    brands: `${API_BASE}/brands`,
    categories: `${API_BASE}/categories`,
    register: `${API_BASE}/register`,
    login: `${API_BASE}/login`,
    profile: `${API_BASE}/user/profile`,
    cart: `${API_BASE}/user/cart`,
    orders: `${API_BASE}/orders`,
    order: (id) => `${API_BASE}/orders/${id}`,
    payment: (orderId) => `${API_BASE}/payment/create/${orderId}`,
    paymentStatus: (orderId) => `${API_BASE}/payment/status/${orderId}`,
    simulatePayment: (orderId) => `${API_BASE}/payment/simulate/${orderId}`,
    adminStats: `${API_BASE}/admin/stats`,
    adminCars: `${API_BASE}/admin/cars`,
    adminCar: (id) => `${API_BASE}/admin/cars/${id}`,
    adminOrders: `${API_BASE}/admin/orders`,
    adminUsers: `${API_BASE}/admin/users`
};

const Utils = {
    getToken: () => localStorage.getItem('token'),
    setToken: (token) => localStorage.setItem('token', token),
    removeToken: () => localStorage.removeItem('token'),
    getUser: () => {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
    setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
    removeUser: () => localStorage.removeItem('user'),
    isLoggedIn: () => !!Utils.getToken(),
    isAdmin: () => {
        const user = Utils.getUser();
        return user && user.role === 'admin';
    },
    formatPrice: (price) => {
        return '¥' + price.toLocaleString('zh-CN');
    },
    formatDate: (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    async request(url, options = {}) {
        const token = Utils.getToken();
        if (token) {
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${token}`
            };
        }
        if (options.body && typeof options.body === 'object') {
            options.headers = {
                ...options.headers,
                'Content-Type': 'application/json'
            };
            options.body = JSON.stringify(options.body);
        }
        try {
            const response = await fetch(url, options);
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            return data;
        } catch (error) {
            console.error('Request error:', error);
            throw error;
        }
    },
    showToast: (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};

const Auth = {
    async login(username, password) {
        const data = await Utils.request(API.login, {
            method: 'POST',
            body: { username, password }
        });
        Utils.setToken(data.token);
        Utils.setUser(data.user);
        return data;
    },
    async register(username, email, password) {
        const data = await Utils.request(API.register, {
            method: 'POST',
            body: { username, email, password }
        });
        Utils.setToken(data.token);
        Utils.setUser(data.user);
        return data;
    },
    logout() {
        Utils.removeToken();
        Utils.removeUser();
        window.location.href = 'index.html';
    }
};

const Cars = {
    async getAll(params = {}) {
        const url = new URL(API.cars);
        Object.keys(params).forEach(key => {
            if (params[key]) url.searchParams.append(key, params[key]);
        });
        return Utils.request(url);
    },
    async getById(id) {
        return Utils.request(API.car(id));
    },
    async getBrands() {
        return Utils.request(API.brands);
    },
    async getCategories() {
        return Utils.request(API.categories);
    }
};

const Cart = {
    async get() {
        return Utils.request(API.cart);
    },
    async add(carId, quantity = 1) {
        return Utils.request(API.cart, {
            method: 'POST',
            body: { car_id: carId, quantity }
        });
    },
    async remove(carId) {
        return Utils.request(API.cart + '/' + carId, {
            method: 'DELETE'
        });
    },
    async clear() {
        return Utils.request(API.cart, {
            method: 'DELETE'
        });
    }
};

const Orders = {
    async create(paymentMethod = 'wechat') {
        return Utils.request(API.orders, {
            method: 'POST',
            body: { payment_method: paymentMethod }
        });
    },
    async getAll() {
        return Utils.request(API.orders);
    },
    async getById(id) {
        return Utils.request(API.order(id));
    },
    async createPayment(orderId) {
        return Utils.request(API.payment(orderId), {
            method: 'POST'
        });
    },
    async getPaymentStatus(orderId) {
        return Utils.request(API.paymentStatus(orderId));
    },
    async simulatePayment(orderId) {
        return Utils.request(API.simulatePayment(orderId), {
            method: 'POST'
        });
    }
};

const Admin = {
    async getStats() {
        return Utils.request(API.adminStats);
    },
    async getCars() {
        return Utils.request(API.adminCars);
    },
    async addCar(carData) {
        return Utils.request(API.adminCars, {
            method: 'POST',
            body: carData
        });
    },
    async updateCar(carId, carData) {
        return Utils.request(API.adminCar(carId), {
            method: 'PUT',
            body: carData
        });
    },
    async deleteCar(carId) {
        return Utils.request(API.adminCar(carId), {
            method: 'DELETE'
        });
    },
    async getOrders(status) {
        const url = status ? `${API.adminOrders}?status=${status}` : API.adminOrders;
        return Utils.request(url);
    },
    async updateOrder(orderId, data) {
        return Utils.request(API.order(orderId), {
            method: 'PUT',
            body: data
        });
    },
    async getUsers() {
        return Utils.request(API.adminUsers);
    }
};

function renderHeader() {
    const isLoggedIn = Utils.isLoggedIn();
    const user = Utils.getUser();
    const isAdmin = Utils.isAdmin();
    
    let navHtml = `
        <li><a href="index.html">首页</a></li>
        <li><a href="cars.html">车型</a></li>
    `;
    
    if (isLoggedIn) {
        navHtml += `
            <li><a href="cart.html">购物车 <span class="cart-badge" id="cartCount">0</span></a></li>
            <li><a href="orders.html">我的订单</a></li>
        `;
        if (isAdmin) {
            navHtml += `<li><a href="admin.html">管理后台</a></li>`;
        }
    }
    
    let userHtml = '';
    if (isLoggedIn) {
        userHtml = `
            <span>欢迎, ${user.username}</span>
            <button class="btn btn-outline btn-sm" onclick="Auth.logout()">退出</button>
        `;
    } else {
        userHtml = `
            <a href="login.html" class="btn btn-outline btn-sm">登录</a>
            <a href="register.html" class="btn btn-primary btn-sm">注册</a>
        `;
    }
    
    document.getElementById('headerNav').innerHTML = navHtml;
    document.getElementById('userMenu').innerHTML = userHtml;
    
    if (isLoggedIn) {
        loadCartCount();
    }
}

async function loadCartCount() {
    try {
        const cart = await Cart.get();
        const count = cart.items.length;
        const badge = document.getElementById('cartCount');
        if (badge) badge.textContent = count;
    } catch (e) {
        console.error('Failed to load cart count');
    }
}

function renderFooter() {
    const currentYear = new Date().getFullYear();
    document.getElementById('footerYear').textContent = currentYear;
}

function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.remove();
}

function renderCarCard(car) {
    return `
        <div class="car-card" onclick="window.location.href='car-detail.html?id=${car.id}'">
            <img src="${car.image}" alt="${car.brand} ${car.model}" class="car-image" onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
            <div class="car-info">
                <div class="car-brand-model">
                    <span class="car-brand">${car.brand}</span>
                </div>
                <div class="car-model">${car.model}</div>
                <div class="car-price">${Utils.formatPrice(car.price)} <span>起</span></div>
                <div class="car-tags">
                    <span class="car-tag">${car.year}款</span>
                    <span class="car-tag">${car.category}</span>
                    <span class="car-tag">${car.color}</span>
                </div>
                <div class="car-meta">
                    <span>库存: ${car.stock}辆</span>
                    <span>已售: ${car.sales}辆</span>
                </div>
            </div>
        </div>
    `;
}

function renderFilterSection() {
    return `
        <div class="filter-section">
            <div class="filter-row">
                <div class="filter-group">
                    <label>品牌:</label>
                    <select id="filterBrand">
                        <option value="">全部</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>类型:</label>
                    <select id="filterCategory">
                        <option value="">全部</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>价格:</label>
                    <div class="price-input">
                        <input type="number" id="minPrice" placeholder="最低">
                        <span>-</span>
                        <input type="number" id="maxPrice" placeholder="最高">
                    </div>
                </div>
                <button class="btn btn-primary" onclick="applyFilters()">筛选</button>
                <button class="btn btn-outline" onclick="resetFilters()">重置</button>
            </div>
        </div>
    `;
}

async function loadFilterOptions() {
    try {
        const [brands, categories] = await Promise.all([
            Cars.getBrands(),
            Cars.getCategories()
        ]);
        
        const brandSelect = document.getElementById('filterBrand');
        const categorySelect = document.getElementById('filterCategory');
        
        brands.forEach(brand => {
            brandSelect.innerHTML += `<option value="${brand}">${brand}</option>`;
        });
        
        categories.forEach(cat => {
            categorySelect.innerHTML += `<option value="${cat}">${cat}</option>`;
        });
    } catch (e) {
        console.error('Failed to load filter options');
    }
}

function applyFilters() {
    const brand = document.getElementById('filterBrand')?.value;
    const category = document.getElementById('filterCategory')?.value;
    const minPrice = document.getElementById('minPrice')?.value;
    const maxPrice = document.getElementById('maxPrice')?.value;
    
    const params = new URLSearchParams();
    if (brand) params.append('brand', brand);
    if (category) params.append('category', category);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    
    window.location.href = `cars.html?${params.toString()}`;
}

function resetFilters() {
    window.location.href = 'cars.html';
}

function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        brand: params.get('brand') || '',
        category: params.get('category') || '',
        min_price: params.get('min_price') || '',
        max_price: params.get('max_price') || '',
        search: params.get('search') || ''
    };
}
