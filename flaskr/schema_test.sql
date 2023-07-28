use crawler;

-- DROP TABLE IF EXISTS test;

CREATE TABLE IF NOT EXISTS test(
  id INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  update_time INT NOT NULL,
  tsp TIMESTAMP NOT NULL,
  content MEDIUMTEXT,
  js json NOT NULL,
  UNIQUE KEY `title` (`title`),
  PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8mb4;

-- alter table task drop `source`;

-- 添加字段 更新代码先执行
-- ALTER TABLE task add `source` VARCHAR(50) character set utf8mb4 NOT NULL DEFAULT '微信公众号'; 
-- 修改article topic字段类型建立外键链接
-- alter table article modify column `topic` INT DEFAULT 1;
-- alter table article add constraint FK_ID foreign key (topic) references task (id) on delete set null;
-- 提交extracted_from文章摘自
-- alter table article add `extracted_from` VARCHAR(50) character set utf8mb4 DEFAULT '';
-- task 添加unique约束
alter table task add unique(name)

-- test 添加delete_time
-- alter table task drop `delete_time`
alter table task add `last_execute_time` DATETIME;
alter table task add `execute_status` SMALLINT DEFAULT 1;
alter table task add `start_time` VARCHAR(20) DEFAULT '';
alter table task add `end_time` VARCHAR(20) DEFAULT '';




-- test
-- alter table test drop `delete_time`
-- ALTER TABLE test add `delete_time` DATETIME;
-- alter table test modify column `topic` INT NOT NULL DEFAULT 1;


-- insert into test (title, update_time, tsp, content, js) values ('能源专题',
-- 1689039638,
-- from_unixtime(1689039639),
-- '<p>123</p>',
-- '[ "中碳联", "绿普惠订阅号", "零碳未来时代", "碳广角", "深圳发布", "绿色供应链电网之家", "中创碳投", "气候投融资", "和碳视角", "广州碳排放权交易中心有限公司", "能源杂谈", "碳个朋友", "Cteam气候行动", "碳达峰中和", "零碳宝BCTC", "碳阻迹", "国际能源小数据",  "碳索未来 TL CARBON", "碳中和洞见", "易碳家", "光伏能源圈"]'
-- );

--  insert into task (name, official_accounts, search_keys) values ('测试专题', 
-- '[ "抚州发布"]',
-- '[]'
-- );