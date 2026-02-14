# TextVideo - 终端字符动画播放器

将 MP4/MOV 视频转换为 ASCII 字符动画，在终端中直接播放。

## 安装

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py your_video.mp4
```

## 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `video` | - | 视频文件路径 (mp4/mov/avi等) | **必填** |
| `--fps` | `-f` | 播放帧率 | 30 |
| `--width` | `-w` | ASCII 宽度 (字符数) | 自动检测 |
| `--charset` | `-c` | 字符集 (从暗到亮) | ` .:-=+*#%@` |
| `--contrast` | - | 对比度倍数 | 1.0 |
| `--loop` | `-l` | 循环播放 | 关闭 |
| `--progress` | `-p` | 显示帧数进度 | 关闭 |

## 示例

```bash
# 基础播放
python main.py video.mov

# 指定帧率和宽度
python main.py video.mov --fps 24 --width 120

# 更高对比度
python main.py video.mov --contrast 1.5

# 循环播放
python main.py video.mov --loop
```

---

## 技术原理

### 1. 整体流程

```
视频文件 (MP4/MOV)
     │
     ▼
┌─────────────────┐
│ VideoFrameExtractor │  ← 用 OpenCV 读取视频，提取每一帧
│   (core.py)     │    帧 = RGB 像素矩阵 (height × width × 3)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AsciiConverter │  ← 将像素转换为 ASCII 字符
│ (converter.py)  │
└────────┬────────┘
         │
    1. 缩放图像 (根据终端宽度)
    2. 转灰度 (RGB → 0-255)
    3. 映射到字符
         │
         ▼
┌─────────────────┐
│  TerminalPlayer │  ← 在终端渲染字符
│   (player.py)   │
└────────┬────────┘
         │
    1. 获取终端尺寸
    2. ANSI 清屏
    3. 逐帧显示
         │
         ▼
   终端显示 ASCII 动画
```

### 2. 从视频帧到文字帧

**步骤 1: 缩放**

原图可能是 1920×1080 像素，通过 PIL 缩放到终端适配的尺寸（如 80×21 字符）：

```python
img = img.resize((80, 21), Image.Resampling.LANCZOS)
```

这个过程使用 Lanczos 插值算法，自动将大量像素"合并"成少量像素。

**步骤 2: RGB 转灰度**

使用人眼敏感度加权公式：

```
Gray = 0.299×R + 0.587×G + 0.114×B
```

```python
gray_img = img.convert('L')  # PIL 自动完成
```

**步骤 3: 映射到字符**

灰度值 0-255 映射到字符集（从暗到亮）：

```python
charset = " .:-=+*#%@"  # 10 个字符

pixel = 180  # 灰度值
char_index = int(pixel / 256 * len(charset))  # = 7
char = charset[char_index]  # = '+'
```

```
原图: 1920×1080 像素
      │
      │  缩放
      ▼
   80×21 像素 (1680 个)
      │
      │  灰度 + 映射字符
      ▼
   80×21 字符
```

### 3. 终端播放原理

核心代码在 `player.py`：

```python
def render_frame(frame):
    sys.stdout.write('\033[H\033[J')  # 清屏 + 光标回到左上角
    sys.stdout.write(frame)            # 写入 ASCII 帧
    sys.stdout.flush()
```

**ANSI 转义序列：**

| 序列 | 含义 |
|------|------|
| `\033` | ESC 的 ASCII 码 (27) |
| `[H` | 移动光标到 home (左上角) |
| `[J` | 清除屏幕 |

**播放循环：**

```python
for frame in ascii_frames:
    render_frame(frame)      # 显示当前帧
    time.sleep(1/30)         # 控制帧率 (30fps)
```

### 4. 对比度参数原理

公式：

```python
pixels = ((pixels - 128) * contrast + 128)
pixels = np.clip(pixels, 0, 255)
```

以 128 为中心点，拉伸或压缩灰度范围：

```
原图灰度:   ██████████  (0-255 均匀分布)

对比度 1.0: ██████████  (不变)

对比度 1.5: ██      ███  (黑白更分明，中间灰被压缩)
```

**适用场景：**
- 视频画面偏灰时，增大对比度可以增强清晰度
- 推荐值：1.0 ~ 1.5

---

## 文件结构

```
TextVideo/
├── main.py                 # CLI 入口
├── requirements.txt        # 依赖
└── video_to_ascii/
    ├── __init__.py
    ├── core.py             # 视频帧提取
    ├── converter.py        # ASCII 转换
    └── player.py           # 终端播放
```
