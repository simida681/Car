# 汽车购买系统 - 部署指南

## 1. 环境要求

### 1.1 运行环境
- **操作系统**: Windows / macOS / Linux
- **Python**: 3.8+
- **浏览器**: Chrome / Firefox / Edge / Safari

### 1.2 依赖安装

```bash
# 安装Python依赖
pip install flask flask-cors pyjwt
```

## 2. 项目结构

```
汽车购买系统/
├── backend/
│   ├── app.py          # Flask后端应用
│   └── data/           # 数据目录（自动创建）
├── frontend/
│   ├── index.html      # 首页
│   ├── cars.html       # 车型列表
│   ├── car-detail.html # 车型详情
│   ├── login.html      # 登录
│   ├── register.html   # 注册
│   ├── cart.html       # 购物车
│   ├── payment.html   # 支付页面
│   ├── orders.html     # 订单列表
│   ├── order-detail.html # 订单详情
│   ├── admin.html      # 后台管理
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── docs/
    └── 文档
```

## 3. 启动后端服务

### 3.1 Windows
```cmd
cd backend
python app.py
```

### 3.2 macOS / Linux
```bash
cd backend
python3 app.py
```

### 3.3 验证后端启动
后端服务启动后，访问: http://localhost:5000/

应该返回:
```json
{"message": "汽车购买系统API", "version": "1.0.0"}
```

## 4. 启动前端

### 4.1 使用IDE预览
在VS Code或其他IDE中，直接打开 `frontend/index.html` 文件，使用Live Server或浏览器预览功能打开。

### 4.2 手动打开
直接用浏览器打开 `frontend/index.html` 文件

## 5. 初始数据

系统首次启动时会自动创建示例数据：

### 5.1 管理员账户
- **用户名**: admin
- **密码**: admin123
- **权限**: 管理员，可访问后台管理

### 5.2 示例车型
系统预置8款热门新能源汽车:
- 特斯拉 Model 3
- 特斯拉 Model Y
- 宝马 i4
- 奔驰 EQE
- 比亚迪 汉EV
- 奥迪 e-tron GT
- 理想 L9
- 蔚来 ET7

## 6. 功能测试

### 6.1 业务流程
1. **注册/登录** - 创建账户或使用admin账户
2. **浏览车型** - 查看车型列表，使用筛选功能
3. **查看详情** - 点击车型查看详细参数
4. **加入购物车** - 选择车型加入购物车
5. **提交订单** - 确认购物车商品，创建订单
6. **支付** - 扫描二维码（模拟支付）
7. **查看订单** - 在订单列表查看订单状态

### 6.2 后台管理
1. 使用admin账户登录
2. 访问管理后台
3. 查看数据统计
4. 管理车型和订单

## 7. 常见问题

### 7.1 后端启动失败
- 确认Python已安装: `python --version`
- 确认依赖已安装: `pip list | findstr flask`

### 7.2 前端无法连接后端
- 确认后端正在运行（端口5000）
- 确认浏览器允许跨域请求

### 7.3 数据文件位置
所有数据文件存储在 `backend/data/` 目录下的JSON文件中。

## 8. 生产环境部署

### 8.1 修改配置
- 修改 `SECRET_KEY` 为更安全的随机字符串
- 考虑使用数据库替代JSON文件存储
- 添加HTTPS支持

### 8.2 使用Nginx部署
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        root /path/to/frontend;
        index index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

## 9. 联系方式

如有问题，请联系技术支持。
