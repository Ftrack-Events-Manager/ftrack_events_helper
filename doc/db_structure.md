# 数据库储存信息结构
## EventsLogs
```json5
[
  {
    "msg": "日志消息",
    "type": "info",
    "group": "所属事件组",
    // time字段可以用于mongodb定时删除指定日期后的数据的字段
    "time": "datatimeObject",
    "local_time": "20210828 2:58:12",
    "event": "事件名称"
  }
]
```

## EventsInfos
和事件组同级的事件就是未被使用的事件，否则会被加到对应的事件组的events字段里
```json5
[
  // 事件类型
  { 
    "type": "event",
    "name": "事件名",
    "path": "事件文件路径",
    "id": "uuid",
    "priority": 100,  // 事件优先级
    "enabled": true  // 事件是否被启用
  },
  // 事件组类型
  {
    "id": "uuid",
    "type": "group",
    "name": "事件组名",
    "status": "run",  // 运行状态 run/stop
    "events": [
      { 
        "type": "event",
        "name": "事件名",
        "path": "事件文件路径",
        "id": "uuid",
        "priority": 100,
        "enabled": true
      },
    ] 
  }
]
```
