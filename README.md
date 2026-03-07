# 针对法律裁判文书的案情抽取及其应用

## 1. 项目简介
本项目以交通肇事案件裁判文书为研究对象，完成一条完整的法律文本处理流程：

1. 数据预处理
2. 分词、词性标注、命名实体识别
3. 基于 CRF 的事件要素抽取
4. 基于抽取结果的判决结果预测
5. 案件相似度分析

这个仓库按“处理步骤”组织目录，而不是按标准 Python 包组织。

## 2. 目录说明
- `01数据预处理/`：清洗原始案件文本，生成预处理结果
- `02分词/`：分词算法实验，主流程使用 LTP
- `03基于CRF的事件要素抽取/`：CRF 训练、测试、结果展示
- `04应用/`：案件相似度应用示例
- `05其他工具/`：数据库导出、Excel 合并、标注检查等工具
- `06判决结果预测/`：特征提取、多分类、回归
- `07案件相似度/`：针对单个案件抽取特征并查找相似案件

## 3. 先理解两种运行目标
这个项目有两种常见使用方式：

### 方式 A：先把项目跑通
只安装基础 Python 依赖，尽量复用仓库中已有的中间结果。

### 方式 B：完整重跑全部流程
除了基础依赖，还需要自己安装：
- `pyltp`
- LTP 模型文件
- `CRF++`

建议先完成“方式 A”。

## 4. 基础依赖安装
基础依赖是指：

- `numpy`
- `scipy`
- `gensim`
- `torch`
- `jieba`
- `xlrd`
- `xlwt`
- `pymysql`

仓库已经提供：

```bash
pip install -r requirements.txt
```

## 5. macOS 安装说明

### 5.1 推荐做法
建议使用 Python 虚拟环境，不要直接装到系统 Python 里。

### 5.2 创建虚拟环境
在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5.3 先检查环境
```bash
python run_project.py --step check
```

### 5.4 推荐首次运行方式
```bash
python run_project.py --skip-train
```

如果能正常执行，再尝试：

```bash
python run_project.py
```

### 5.5 macOS 上的额外说明
- 仓库里自带的 `crf_test.exe` 是 Windows 版本，macOS 上通常不能直接运行
- 因此在 macOS 上，项目会优先使用仓库已有的 CRF 缓存结果
- `pyltp` 在新版本 macOS 上可能不容易直接安装成功，如果只是想先跑通项目，可以先不装

### 5.6 如果你想在 macOS 上完整重跑
你需要额外准备：

1. 可用的 `pyltp`
2. LTP 模型目录，例如 `ltp_data_v3.4.0`
3. macOS 可执行版本的 `crf_test`

然后设置环境变量：

```bash
export LTP_DATA_DIR=/你的路径/ltp_data_v3.4.0
export CRF_TEST_BIN=/你的路径/crf_test
```

再执行：

```bash
python run_project.py --no-cache
```

## 6. Windows 安装说明

### 6.1 推荐做法
建议使用 `venv` 或 Conda。下面先给出最通用的 `venv` 方式。

### 6.2 创建虚拟环境
在项目根目录执行：

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6.3 先检查环境
```bat
python run_project.py --step check
```

### 6.4 推荐首次运行方式
```bat
python run_project.py --skip-train
```

### 6.5 Windows 上的额外说明
- 仓库中 `03基于CRF的事件要素抽取/实验/05/` 下带有 `crf_test.exe`
- 因此 Windows 上通常更容易重新跑 CRF 相关步骤
- 但如果你的系统架构、权限或运行库不匹配，也可能还是无法直接运行，这时同样可以先使用缓存结果

### 6.6 如果你想在 Windows 上完整重跑
除了基础依赖，还需要准备：

1. `pyltp`
2. LTP 模型目录
3. 可运行的 `crf_test.exe`

设置环境变量示例：

```bat
set LTP_DATA_DIR=D:\你的路径\ltp_data_v3.4.0
set CRF_TEST_BIN=D:\你的路径\crf_test.exe
```

然后执行：

```bat
python run_project.py --no-cache
```

## 7. LTP 和 CRF++ 的作用

### 7.1 LTP 是做什么的
LTP 负责：
- 分词
- 词性标注
- 命名实体识别

对应脚本：

```bash
python "02分词/分词算法/05LTP分词/LTP分词_词性标注_命名实体识别.py"
```

### 7.2 CRF++ 是做什么的
CRF++ 负责事件要素抽取，也就是把前一步的分词标注结果进一步转成结构化标签。

如果没有可运行的 `crf_test`，仓库会尽量使用已有缓存结果继续执行。

## 8. 第一次运行建议
如果你只是想先把项目跑通，不要一开始就纠结所有依赖是否齐全。仓库中已经保留了一部分中间结果文件，脚本会优先复用这些缓存。

推荐顺序如下：

### 第一步：检查环境
```bash
python run_project.py --step check
```

这个命令会告诉你：
- Python 路径
- CRF 模型是否存在
- `crf_test` 是否可用
- 仓库里是否已有缓存结果

### 第二步：先跑通主流程，不训练模型
```bash
python run_project.py --skip-train
```

这样可以先生成或复用中间数据，不必等待训练。

### 第三步：再运行完整流程
```bash
python run_project.py
```

如果你的环境已经装好了 PyTorch、LTP、CRF++，这个命令会尽量完整执行整个主流程。

## 9. 一键运行脚本说明
统一入口是根目录下的：

```bash
python run_project.py
```

支持的常用参数：

- `python run_project.py --step check`
  - 只检查环境和缓存
- `python run_project.py --step features`
  - 只执行“事件抽取结果 -> 特征文件”这一步
- `python run_project.py --skip-train`
  - 执行主流程，但跳过模型训练
- `python run_project.py --no-cache`
  - 不使用仓库中的缓存结果，强制依赖真实环境重新计算

## 10. 如果想按步骤单独运行

### 10.1 数据预处理
```bash
python 01数据预处理/data_preprocess.py
```

输入：
- `01数据预处理/original_data.txt`

输出：
- `01数据预处理/preprocessed_data.txt`
- `01数据预处理/processed_data.txt`

### 10.2 LTP 分词、词性标注、命名实体识别
```bash
python "02分词/分词算法/05LTP分词/LTP分词_词性标注_命名实体识别.py"
```

输出：
- `02分词/分词算法/05LTP分词/分词_词性标注_命名实体识别_结果.txt`

如果没有安装 `pyltp`，这一步可能无法重新执行，但不影响使用已有缓存继续学习后续流程。

### 10.3 生成特征
```bash
python run_project.py --step features
```

输出：
- `06判决结果预测/特征提取/data.csv`：分类任务数据
- `06判决结果预测/特征提取/data_for_regression.csv`：回归任务数据

### 10.4 生成多分类训练数据
```bash
python "06判决结果预测/pytorch多分类/数据预处理.py"
```

输出目录：
- `06判决结果预测/pytorch多分类/data/`

### 10.5 训练多分类模型
```bash
python "06判决结果预测/pytorch多分类/net.py"
```

结果文件：
- `06判决结果预测/pytorch多分类/result.csv`

### 10.6 训练回归模型
```bash
python "06判决结果预测/pytorch回归/数据预处理.py"
python "06判决结果预测/pytorch回归/net.py"
```

## 11. 相似案件分析怎么跑
如果你想对单个案件做特征提取并查找相似案件：

1. 把案件文本写入 `07案件相似度/case.txt`
2. 运行：

```bash
python "07案件相似度/案件特征提取.py"
```

输出：
- `07案件相似度/pattern.csv`
- `07案件相似度/类似案件.txt`

## 12. 常见问题

### 12.1 提示“未安装 pyltp”
说明你当前机器没有安装 LTP Python 接口。可以：

1. 先继续使用仓库已有缓存结果
2. 或者自己安装 `pyltp` 并设置 `LTP_DATA_DIR`

### 12.2 提示 `crf_test` 不可用
常见原因是：
- 没安装 CRF++
- 当前系统是 macOS / Linux，但仓库内自带的是 Windows 版 `crf_test.exe`
- Windows 上的 `crf_test.exe` 和当前系统环境不匹配

这时项目会尽量使用已有缓存结果继续执行。

### 12.3 为什么有些步骤没有重新计算？
因为项目默认优先使用缓存，目的是降低初次运行门槛。如果你想强制重新生成，请使用：

```bash
python run_project.py --no-cache
```

### 12.4 哪一步最容易出问题？
通常是：
- LTP 模型路径没配置好
- CRF++ 不可执行
- Python 环境缺少依赖

建议先运行：

```bash
python run_project.py --step check
```

## 13. 推荐命令顺序
如果你希望先确认环境，再逐步执行主流程，推荐命令顺序如下：

```bash
python run_project.py --step check
python run_project.py --skip-train
python run_project.py
```
