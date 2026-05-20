


-- 会话表
CREATE TABLE `conversations` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键',
    `thread_id` CHAR(18) NOT NULL COMMENT '主题 ID',
    `title` VARCHAR(255) NOT NULL COMMENT '会话主题',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_thread_id` (`thread_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';


-- 消息表
CREATE TABLE `messages` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键',
    `conversation_id` INT NOT NULL COMMENT '会话 ID',
    `role` VARCHAR(20) NOT NULL COMMENT '角色',  -- 'system', 'user', 'assistant'
    `content` TEXT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_conversation_i`d (`conversation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';


-- 审批任务表
CREATE TABLE `approval_tasks` (
    `id`            INT           NOT NULL AUTO_INCREMENT,
    `thread_id`     CHAR(36)      NOT NULL COMMENT '图线程 ID（UUID）',
    `approver_id`   VARCHAR(64)   NOT NULL DEFAULT '' COMMENT '待审批人 ID',
    `content`       VARCHAR(512)  NOT NULL COMMENT '原始请求内容',
    `order_id`      VARCHAR(32)   NOT NULL DEFAULT '' COMMENT '订单编号',
    `amount`        DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '订单金额',
    `risk_level`    TINYINT       NOT NULL DEFAULT 0 COMMENT '风险等级',
    `status`        TINYINT       NOT NULL DEFAULT 0 COMMENT '0=待审批 1=已通过 2=已拒绝',
    `operator`      VARCHAR(64)   NOT NULL DEFAULT '' COMMENT '实际审批人',
    `reject_reason` VARCHAR(255)  NOT NULL DEFAULT '' COMMENT '拒绝理由',
    `created_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_thread_id` (`thread_id`),
    INDEX           `idx_approver_status` (`approver_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批任务表';


CREATE TABLE `users` (
    `id`            INT          NOT NULL AUTO_INCREMENT COMMENT '主键',
    `ref_id`        INT          NOT NULL                COMMENT '前端项目里的用户ID',
    `username`      VARCHAR(64)  NOT NULL                COMMENT '用户名，全局唯一',
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP                    COMMENT '账号创建时间',
    `last_login_at` DATETIME         NULL                COMMENT '最近一次登录时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_ref_id`    (`ref_id`),
    UNIQUE KEY `uq_username` (`username`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='用户表';
