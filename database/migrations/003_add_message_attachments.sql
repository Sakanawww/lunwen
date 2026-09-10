-- ---------------------------------------------------------------------
-- 003_add_message_attachments.sql
-- 智能答疑：为用户消息增加附件支持（存储文件名，文件本体落盘在
-- data/uploads/chat/ 目录，不入库）。
-- ---------------------------------------------------------------------

ALTER TABLE messages
  ADD COLUMN attachment TEXT NULL COMMENT '附件信息（JSON: 文件名/大小/类型）' AFTER sources;