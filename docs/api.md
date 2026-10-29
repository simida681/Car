# 汽车购买系统 - API 文档

## 基础信息
- **Base URL**: `http://localhost:5000/api`
- **认证方式**: Bearer Token (JWT)
- **请求格式**: JSON
- **响应格式**: JSON

---

## 认证接口

### 用户注册
**POST** `/register`

**请求体:**
```json
{
  "username": "用户名",
  "email": "邮箱地址",
  "password": "密码"
}
```

**响应:**
```json
{
  "message": "Registration successful",
  "token": "jwt_token",
  "user": {
    "id": "user001",
    "username": "用户名",
    "email": "邮箱",
    "role": "user"
  }
}
```

---

### 用户登录
**POST** `/login`

**请求体:**
```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应:**
```json
{
  "message": "Login successful",
  "token": "jwt_token",
  "user": {
    "id": "user001",
    "username": "用户名",
    "email": "邮箱",
    "role": "user"
  }
}
```

---

## 车型接口

### 获取车型列表
**GET** `/cars`

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| brand | string | 品牌筛选 |
| category | string | 类型筛选 |
| min_price | int | 最低价格 |
| max_price | int | 最高价格 |
| search | string | 搜索关键词 |

**响应:** 返回车型数组

---

### 获取车型详情
**GET** `/cars/{car_id}`

**响应:**
```json
{
  "id": "car001",
  "brand": "特斯拉",
  "model": "Model 3",
  "year": 2024,
  "price": 249900,
  "category": "电动车",
  "color": "黑色",
  "image": "https://...",
  "description": "描述",
  "specs": {...},
  "features": ["..."],
  "stock": 10,
  "sales": 156
}
```

---

### 获取品牌列表
**GET** `/brands`

---

### 获取类型列表
**GET** `/categories`

---

## 购物车接口

### 获取购物车
**GET** `/user/cart`

**需要认证**

**响应:**
```json
{
  "items": [
    {
      "car_id": "car001",
      "car": {...},
      "quantity": 1,
      "added_at": "..."
    }
  ],
  "total": 249900
}
```

---

### 添加到购物车
**POST** `/user/cart`

**需要认证**

**请求体:**
```json
{
  "car_id": "car001",
  "quantity": 1
}
```

---

### 移除商品
**DELETE** `/user/cart/{car_id}`

**需要认证**

---

### 清空购物车
**DELETE** `/user/cart`

**需要认证**

---

## 订单接口

### 创建订单
**POST** `/orders`

**需要认证**

**请求体:**
```json
{
  "payment_method": "wechat"
}
```

**响应:**
```json
{
  "message": "Order created successfully",
  "order": {
    "id": "ORD20240321001",
    ...
  }
}
```

---

### 获取订单列表
**GET** `/orders`

**需要认证**

---

### 获取订单详情
**GET** `/orders/{order_id}`

**需要认证**

---

## 支付接口

### 创建支付
**POST** `/payment/create/{order_id}`

**需要认证**

**响应:**
```json
{
  "order_id": "ORD...",
  "amount": 249900,
  "payment_method": "wechat",
  "status": "pending",
  "qr_code_url": "/payment/qrcode.html?..."
}
```

---

### 获取支付状态
**GET** `/payment/status/{order_id}`

**需要认证**

---

### 模拟支付
**POST** `/payment/simulate/{order_id}`

**需要认证**

---

## 管理接口

### 获取统计数据
**GET** `/admin/stats`

**需要管理员权限**

**响应:**
```json
{
  "total_sales": 1500000,
  "total_orders": 50,
  "paid_orders": 45,
  "total_users": 100,
  "sales_by_brand": {...},
  "top_cars": [...],
  "monthly_sales": {...}
}
```

---

### 添加车型
**POST** `/admin/cars`

**需要管理员权限**

---

### 更新车型
**PUT** `/admin/cars/{car_id}`

**需要管理员权限**

---

### 删除车型
**DELETE** `/admin/cars/{car_id}`

**需要管理员权限**

---

### 获取所有订单
**GET** `/admin/orders`

**需要管理员权限**

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 状态筛选 |

---

### 更新订单状态
**PUT** `/admin/orders/{order_id}`

**需要管理员权限**

**请求体:**
```json
{
  "status": "shipped"
}
```

---

## 错误响应

所有错误响应格式:
```json
{
  "error": "错误信息"
}
```

**状态码:**
- 200: 成功
- 400: 请求错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误
