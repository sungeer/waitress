


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
    `id`           INT           NOT NULL AUTO_INCREMENT,
    `thread_id`    CHAR(36)      NOT NULL COMMENT '图线程 ID（UUID）',
    `approver_id`  VARCHAR(64)   NOT NULL DEFAULT '' COMMENT '待审批人 ID',
    `content`      VARCHAR(512)  NOT NULL COMMENT '原始请求内容',
    `recipient`    VARCHAR(128)  NOT NULL COMMENT '接收人（LLM 提取）',
    `message`      VARCHAR(512)  NOT NULL COMMENT '通知内容（LLM 提取）',
    `status`       TINYINT       NOT NULL DEFAULT 0 COMMENT '0=待审批 1=已通过 2=已拒绝',
    `operator`     VARCHAR(64)   NOT NULL DEFAULT '' COMMENT '实际审批人',
    `created_at`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_thread_id` (`thread_id`),
    INDEX          `idx_approver_status` (`approver_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批任务表';
