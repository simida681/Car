# 汽车购买系统 - 系统设计文档

## 1. 系统架构设计

### 1.1 整体架构
```
┌─────────────────┐     ┌─────────────────┐
│   前端 (HTML)   │────▶│   后端 (Python) │
│   响应式设计    │◀────│   Flask API     │
└─────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   JSON 文件存储  │
                       └─────────────────┘
```

### 1.2 目录结构
```
汽车购买系统/
├── backend/
│   ├── app.py          # Flask主应用
│   └── data/           # JSON数据文件
│       ├── users.json
│       ├── cars.json
│       ├── carts.json
│       └── orders.json
├── frontend/
│   ├── index.html      # 首页
│   ├── cars.html       # 车型列表
│   ├── car-detail.html # 车型详情
│   ├── login.html      # 登录
│   ├── register.html   # 注册
│   ├── cart.html       # 购物车
│   ├── payment.html    # 支付页面
│   ├── orders.html     # 订单列表
│   ├── order-detail.html # 订单详情
│   ├── admin.html      # 后台管理
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── docs/
    └── 文档文件
```

## 2. 数据库设计

### 2.1 用户表 (users.json)
```json
{
  "id": "user001",
  "username": "用户名",
  "password": "SHA256加密密码",
  "email": "邮箱地址",
  "role": "user|admin",
  "created_at": "创建时间"
}
```

### 2.2 车型表 (cars.json)
```json
{
  "id": "car001",
  "brand": "品牌",
  "model": "型号",
  "year": 2024,
  "price": 249900,
  "category": "电动车|混动|燃油",
  "color": "颜色",
  "image": "图片URL",
  "description": "描述",
  "specs": { "发动机": "..." },
  "features": ["功能列表"],
  "stock": 10,
  "sales": 156
}
```

### 2.3 购物车表 (carts.json)
```json
{
  "user_id": "user001",
  "items": [
    { "car_id": "car001", "quantity": 1, "added_at": "..." }
  ]
}
```

### 2.4 订单表 (orders.json)
```json
{
  "id": "ORD20240321...",
  "user_id": "user001",
  "items": [{ "car_id": "...", "car": {...}, "quantity": 1 }],
  "total": 249900,
  "status": "pending_payment|paid|shipped|completed",
  "payment_method": "wechat|alipay",
  "created_at": "...",
  "paid_at": "..."
}
```

## 3. API设计

### 3.1 认证接口
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录

### 3.2 车型接口
- `GET /api/cars` - 获取车型列表（支持筛选）
- `GET /api/cars/:id` - 获取车型详情
- `GET /api/brands` - 获取品牌列表
- `GET /api/categories` - 获取类型列表

### 3.3 购物车接口
- `GET /api/user/cart` - 获取购物车
- `POST /api/user/cart` - 添加到购物车
- `DELETE /api/user/cart/:car_id` - 移除商品
- `DELETE /api/user/cart` - 清空购物车

### 3.4 订单接口
- `POST /api/orders` - 创建订单
- `GET /api/orders` - 获取订单列表
- `GET /api/orders/:id` - 获取订单详情

### 3.5 支付接口
- `POST /api/payment/create/:order_id` - 创建支付
- `GET /api/payment/status/:order_id` - 获取支付状态
- `POST /api/payment/simulate/:order_id` - 模拟支付

### 3.6 管理接口（需管理员权限）
- `GET /api/admin/stats` - 获取统计数据
- `POST /api/admin/cars` - 添加车型
- `PUT /api/admin/cars/:id` - 更新车型
- `DELETE /api/admin/cars/:id` - 删除车型
- `GET /api/admin/orders` - 获取所有订单

## 4. 安全性设计

### 4.1 认证与授权
- JWT令牌认证，有效期7天
- Token包含用户ID、用户名、角色信息
- 管理员接口需管理员角色验证

### 4.2 密码安全
- 使用SHA256进行密码哈希
- 不存储明文密码

### 4.3 CORS配置
- 支持跨域请求
- 允许携带认证信息

## 5. 前端设计

### 5.1 页面结构
- 统一的头部导航
- 响应式布局
- 统一的页脚

### 5.2 交互设计
- 异步API请求
- 加载状态提示
- 错误信息提示
- 成功消息反馈
