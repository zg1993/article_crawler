    use crawler;
    
    DROP TABLE IF EXISTS article;

    CREATE TABLE article (
      aid VARCHAR(20) NOT NULL PRIMARY KEY,
      title VARCHAR(200) NOT NULL,
      link TEXT NOT NULL, -- 文章链接
      -- update_time TIMESTAMP NOT NULL, --  文章更新的时间戳
      update_time INT NOT NULL, 
      cover TEXT NOT NULL,
      content MEDIUMTEXT
    ) DEFAULT CHARSET=utf8mb4;

    -- insert into article (aid, title, link, update_time,cover) values ('2674775906_1', 
    --     '渤海银行关于调整人民币存款挂牌利率的公告',
    --     'http://mp.weixin.qq.com/s?__biz=MjM5NDM5ODUzNQ==&mid=2674775906&idx=1&sn=6d978316a3c0b49efc21402197c97e49&chksm=bc111f4a8b66965c477bd50b62a9304280e8361a7ba93ab004d59328df74b51129b75902d36f#rd',
    --     from_unixtime(1687136155),
    --     'https://mmbiz.qlogo.cn/mmbiz_jpg/CicWTKtA8bDay2yAfuwlzc89mn2UIlGoYHzrhUad8prAXPR7oianAsSxyzgfwUbaFEZU9dlusC8TIaCZDDhJicy7A/0?wx_fmt=jpeg'
    --  );