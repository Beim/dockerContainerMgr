# 简介
管理neo4j docker 容器集群



# 环境要求

- docker
- python3



# 使用

服务端：

```bash
# 安装依赖
$ pip install -r requirements.txt
# 运行
$ python bin/server.py
```



客户端参考`/bin/client.py`



# 配置

配置文件`/config/config.json`

配置说明

```json
{
    "grpc": {
        "port": 50020, // server 端口
        "max_workers": 10
    },
    "labels": ["shNeo4j"], // 容器标签
    "image": "neo4j:latest",  // 镜像
    "environment": {
        "NEO4J_AUTH": "neo4j/123123"  // neo4j 用户密码
    },
    "ports": { // 指定容器暴露端口，设置null 随机选择
        "7474/tcp": null, 
        "7687/tcp": null
    },
    "max_memory_usage": 70 // 系统内存超过该值时，不允许创建容器
}
```

