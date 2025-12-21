# CustomPlugins - 自定义插件仓库

本仓库用于存放自定义开发的 MoviePilot 插件。

## 目录结构

```
CustomPlugins/
├── plugins/              # 插件目录
│   └── [plugin_name]/    # 各个插件
│       ├── __init__.py   # 插件主文件
│       ├── requirements.txt  # 插件依赖（可选）
│       └── icon.png      # 插件图标（可选）
├── package.json          # V1 插件元数据
├── package.v2.json       # V2 插件元数据
└── README.md             # 本文件
```

## 插件列表

目前没有插件，等待开发...

## 开发说明

每个插件需要：
1. 在 `plugins/` 目录下创建插件文件夹
2. 实现继承自 `_PluginBase` 的插件类
3. 在 `package.json` 或 `package.v2.json` 中添加插件元数据

详细开发指南请参考根目录的 `claude.md` 文档。
