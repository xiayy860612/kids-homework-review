# Architecture Documentation

## Domain Model Class Diagram

```mermaid
classDiagram
    %% Core Domain Entities
    class User {
        +int id
        +str username
        +str hashed_password
        +str display_name
        +str|None avatar_url
        +str role
        +bool is_active
        +datetime created_at
        +datetime updated_at
    }

    class WrongQuestion {
        +int id
        +int user_id
        +str title
        +int subject_id
        +str image_base64
        +datetime created_at
        +datetime updated_at
        +Subject subject
        +list~Tag~ tags
    }

    class Subject {
        +int id
        +str name
        +str|None description
        +bool is_active
    }

    class Tag {
        +int id
        +str name
        +bool is_preset
        +list~WrongQuestion~ wrong_questions
    }

    class WrongQuestionTag {
        +int wrong_question_id
        +int tag_id
    }

    %% Relationships
    User *--> "N" WrongQuestion
    WrongQuestion "N" o--> "1" Subject : subject_id
    WrongQuestion *--> "N" WrongQuestionTag : wrong_question_id
    WrongQuestionTag o--> "1" Tag : tag_id
```

## Domain Model Description

### Entities

| Entity | Description | Key Fields |
| :--- | :--- | :--- |
| **User** | 用户实体，用于身份认证和用户管理 | username, hashed_password, display_name, role, is_active |
| **WrongQuestion** | 错题核心实体，存储学生错题图片及相关信息 | title, image_base64, user_id, subject_id |
| **Subject** | 学科分类实体，用于对错题进行学科归类 | name, description, is_active |
| **Tag** | 标签实体，提供灵活的错题标记方式 | name, is_preset |

### Domain Services

| Service | Responsibility |
| :--- | :--- |
| **AuthService** | 用户认证、用户数据转换 |
| **WrongQuestionService** | 错题的 CRUD 操作及关联关系管理 |
| **SubjectService** | 学科管理 |
| **TagService** | 标签管理（预设标签和自定义标签） |
