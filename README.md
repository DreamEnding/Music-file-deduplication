# Music-file-deduplication
# 音乐文件去重工具

[English Version](README_EN.md) | [中文版](README.md)


## 项目简介
本仓库提供了一款用于去除重复音乐文件的工具，支持多种常见格式，包括 MP3、WAV、FLAC、M4A 等。

本工具主要适用于处理简体中文命名的重复音乐文件。例如：
- `汪苏泷-站台.flac`
- `站台-汪苏泷.flac`

## 功能特点
- **支持多种音频格式**：兼容 MP3、WAV、FLAC、M4A 等格式。
- **智能匹配文件**：基于文件名进行去重，适用于简体中文命名的音乐文件。
- **可自定义删除策略**：提供多种优先级规则，用户可选择优先删除以下文件：
  - **无专辑封面的文件**
  - **低码率的文件**
  - **无歌词的文件**

## 许可协议
本项目采用 MIT 许可证，您可以自由地使用、修改和分发本软件，但需包含原始许可证文本。

MIT License

Copyright (c) [2024] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
