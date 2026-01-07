`out/graph.mmd` 是站点结构的唯一事实源。

**Mermaid** 用于结构正确性校验（如内链是否存在、关系是否异常）,`build.py` 负责构建 `graph.mmd`。

**Gephi** 仅用于结构的可读性审视与美化展示，不参与结构生成。  
`mmd2gephi.py` 用于将 `graph.mmd` 转换为 Gephi 可用的输入文件，随后在桌面端 Gephi 中进行人工可视化设计，导出的结构快照放置于项目根目录的 `assets/site-structure/` 中。