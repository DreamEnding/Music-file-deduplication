# Music File Deduplication Tool

## Project Overview
This repository provides a tool for removing duplicate music files, supporting multiple common formats, including MP3, WAV, FLAC, and M4A.

This tool is primarily designed to handle duplicate music files named in Simplified Chinese. For example:
- `汪苏泷-站台.flac`
- `站台-汪苏泷.flac`

## Features
- **Supports multiple audio formats**: Compatible with MP3, WAV, FLAC, M4A, and more.
- **Intelligent file matching**: Deduplication is based on filename similarity, optimized for Simplified Chinese music file names.
- **Customizable deletion strategies**: Users can choose priority rules to remove files based on:
  - **Files without album covers**
  - **Low-bitrate files**
  - **Files without lyrics**


## License
This project is licensed under the MIT License, allowing free use, modification, and distribution, provided the original license text is included.

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
