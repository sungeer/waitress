


CREATE TABLE conversations (
    id         INT NOT NULL AUTO_INCREMENT COMMENT '主键',
    thread_id  CHAR(18) NOT NULL           COMMENT '主题 ID',
    title      VARCHAR(255) NOT NULL       COMMENT '会话主题',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uq_thread_id (thread_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='会话表';


CREATE TABLE messages (
    id              INT NOT NULL AUTO_INCREMENT COMMENT '主键',
    conversation_id INT NOT NULL                COMMENT '会话 ID',
    role            VARCHAR(20) NOT NULL        COMMENT '角色',  -- 'system', 'user', 'assistant'
    content         TEXT NOT NULL               COMMENT '消息内容',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    INDEX idx_conversation_id (conversation_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='消息表';


CREATE TABLE users (
    id                INT          NOT NULL AUTO_INCREMENT COMMENT '主键',
    username          VARCHAR(64)  NOT NULL                COMMENT '用户名，全局唯一',
    display_name      VARCHAR(64)      NULL                COMMENT '显示名称',
    email             VARCHAR(254)     NULL                COMMENT '邮箱地址，全局唯一',
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '账号创建时间',
    last_login_at     DATETIME         NULL                COMMENT '最近一次登录时间',
    PRIMARY KEY (id),
    UNIQUE KEY uq_username (username),
    UNIQUE KEY uq_email (email)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='用户表';
