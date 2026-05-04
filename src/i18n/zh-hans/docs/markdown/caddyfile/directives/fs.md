---
title: "fs（Caddyfile 指令）"
---

# fs

设置用于执行文件 I/O 的文件系统。

这使您能够连接到云端运行的远程文件系统、具有文件式接口的数据库，甚至读取嵌入在 Caddy 二进制文件中的文件。

首先，您必须使用[全局选项](/docs/caddyfile/options#filesystem) [`filesystem`](/docs/caddyfile/options#filesystem) 声明一个文件系统名称，然后才能使用此指令指定要使用的文件系统。

该指令通常与[`file_server`指令](file_server)配合使用以提供静态文件，或与[`try_files`指令](try_files)配合使用，根据文件的存在情况进行重写。此外，它通常还与[`root`指令](root)配合使用，以设置文件系统中的根路径。


## 语法

```caddy-d
fs [<matcher>] <filesystem>
```

## 示例

使用名为 `foo`，使用一个名为 `custom` ，该模块可能需要身份验证：

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

仅从 `foo` 文件系统，其余内容则来自默认文件系统：

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
