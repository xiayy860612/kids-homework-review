# 错题收集功能设计文档

**创建日期**: 2025-01-23
**功能**: 新增错题收集功能，支持学生自主录入错题

## 1. 需求概述

### 1.1 功能定位
学生自主录入错题的功能，便于后续复习和整理。

### 1.2 核心功能
- 提交错题截图（Base64 存储在数据库）
- 填写标题
- 指定学科（管理员预设）
- 添加标签（混合模式：预设标签 + 自定义标签）
- 编辑错题信息
- 查看错题列表

### 1.3 约束条件
- 仅个人可见（用户只能看到自己录入的错题）
- 仅支持文件上传（不支持 URL）
- 无搜索/筛选功能
- 无删除功能（仅支持编辑）

## 2. 整体架构

### 2.1 后端架构

**新增数据模型**：
- `WrongQuestion` - 错题主表
- `Subject` - 学科表
- `Tag` - 标签表
- `WrongQuestionTag` - 错题-标签关联表

**新增服务层**：
- `WrongQuestionService` - 错题业务逻辑

**新增 API 路由**：
- `/api/wrong-questions` - 错题 CRUD
- `/api/subjects` - 学科管理
- `/api/tags` - 标签管理

### 2.2 前端架构

**路由结构**：
```
app/dashboard/
├── page.tsx                    # Dashboard 首页（新增"新增错题"按钮）
└── wrong-questions/
    ├── page.tsx                # 错题列表页
    ├── new/
    │   └── page.tsx            # 新建错题页
    └── [id]/
        └── edit/
            └── page.tsx        # 编辑错题页
```

**组件设计**：
- `WrongQuestionForm.tsx` - 可复用的表单组件
- `ImageUpload.tsx` - 图片上传预览组件
- `TagSelector.tsx` - 标签选择器

## 3. 数据库设计

### 3.1 wrong_questions 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| title | String(200) | NOT NULL | 错题标题 |
| subject_id | Integer | FK → subjects.id, NOT NULL | 所属学科 |
| image_base64 | Text | NOT NULL | 截图 Base64 |
| created_at | DateTime | DEFAULT NOW() | 创建时间 |
| updated_at | DateTime | ON UPDATE NOW() | 更新时间 |

### 3.2 subjects 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| name | String(50) | Unique, NOT NULL | 学科名称 |
| description | String(200) | | 描述 |
| is_active | Boolean | DEFAULT True | 是否启用 |

### 3.3 tags 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| name | String(50) | Unique, NOT NULL | 标签名称 |
| is_preset | Boolean | DEFAULT True | 是否为预设标签 |

### 3.4 wrong_question_tags 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| wrong_question_id | Integer | FK → wrong_questions.id | 错题 ID |
| tag_id | Integer | FK → tags.id | 标签 ID |
| **(PK)** | | **Composite PK** | 复合主键 |

### 3.5 初始数据

**预设学科**：
语文、数学、英语、物理、化学、生物、历史、地理、政治

**预设标签**：
计算错误、概念不清、粗心大意、审题错误、思路错误

## 4. API 端点设计

### 4.1 错题 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/wrong-questions` | 创建错题 | 必需 |
| GET | `/api/wrong-questions` | 获取当前用户的错题列表 | 必需 |
| GET | `/api/wrong-questions/{id}` | 获取错题详情 | 必需 |
| PUT | `/api/wrong-questions/{id}` | 更新错题 | 必需 |

**创建错题请求示例**：
```json
POST /api/wrong-questions
{
  "title": "二次函数求最值问题",
  "subject_id": 2,
  "tag_ids": [1, 3],
  "image_base64": "data:image/png;base64,iVBORw0KGgo..."
}
```

**创建错题响应示例**：
```json
{
  "id": 1,
  "title": "二次函数求最值问题",
  "subject": {"id": 2, "name": "数学"},
  "tags": [{"id": 1, "name": "计算错误"}, {"id": 3, "name": "思路错误"}],
  "created_at": "2025-01-23T10:30:00Z"
}
```

### 4.2 学科 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/subjects` | 获取所有可用学科 | 必需 |
| POST | `/api/subjects` | 创建学科（管理员） | 必需 |

### 4.3 标签 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/tags` | 获取所有标签（预设+自定义） | 必需 |
| POST | `/api/tags` | 创建自定义标签 | 必需 |

## 5. 前端页面设计

### 5.1 Dashboard 首页 (`app/dashboard/page.tsx`)
- 添加"新增错题"按钮（ShadCN Button，primary 变色，配 Plus 图标）
- 点击跳转到 `/dashboard/wrong-questions/new`

### 5.2 错题列表页 (`app/dashboard/wrong-questions/page.tsx`)
- 列表展示，使用 ShadCN `Table` 组件
- 每行显示：标题、学科、标签、创建时间
- 每行有"编辑"按钮
- 顶部"新增错题"按钮

### 5.3 新建错题页 (`app/dashboard/wrong-questions/new/page.tsx`)
- 表单字段：
  - 标题：ShadCN `Input`
  - 学科：ShadCN `Select`
  - 标签：自定义 `TagSelector`（多选 + 支持新建）
  - 截图：自定义 `ImageUpload`（文件选择 + 预览）
- 提交成功后跳转到列表页

### 5.4 编辑错题页 (`app/dashboard/wrong-questions/[id]/edit/page.tsx`)
- 复用 `WrongQuestionForm` 组件
- 预填充现有数据
- 图片支持替换或保留

## 6. 错误处理

### 6.1 前端错误处理
- 图片上传：限制 5MB，仅支持 JPG/PNG
- 表单验证：标题必填、学科必选、至少一个标签
- API 错误：使用 ShadCN `useToast` 提示
- 网络错误：友好提示 + 重试

### 6.2 后端错误处理
- 图片大小：Base64 后不超过 10MB
- Pydantic 数据验证
- 权限检查：确保只能访问自己的错题
- 数据库错误：事务回滚

## 7. 测试策略（TDD）

### 7.1 后端测试
- `tests/api/test_wrong_questions.py` - API 端点测试
- `tests/services/test_wrong_question_service.py` - 业务逻辑测试
- `tests/models/test_wrong_question.py` - 模型测试
- 目标覆盖率：90%+

### 7.2 前端测试
- `tests/components/WrongQuestionForm.test.tsx` - 表单组件测试
- `tests/components/ImageUpload.test.tsx` - 图片上传测试
- 集成测试：模拟完整创建流程

## 8. 技术栈确认

- **后端**: Python + FastAPI + SQLAlchemy + SQLite
- **前端**: Next.js 16 + React 19 + TypeScript + Tailwind CSS + ShadCN UI
- **认证**: JWT Bearer Token
- **表单**: React Hook Form + Zod
- **测试**: pytest (后端) + Jest (前端)