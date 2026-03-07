# Repository Guidelines

## Project Structure & Module Organization
This repository is organized as a staged NLP pipeline for legal judgment analysis. Core modules live in numbered directories:

- `01数据预处理/`: cleans raw case text and writes `processed_data.txt`.
- `02分词/`: segmentation experiments and the LTP-based tokenizer used by later stages.
- `03基于CRF的事件要素抽取/`: CRF++ training, scoring, and result visualization.
- `04应用/` and `07案件相似度/`: downstream similarity workflows.
- `06判决结果预测/`: feature extraction plus PyTorch regression and classification models.
- `05其他工具/`: one-off utilities for labeling, Excel merging, and database export.
- `标准数据/` and `参考文档/`: sample data and notes.

Run scripts from the repository root so relative paths such as `data/train6.csv` resolve correctly.

## Build, Test, and Development Commands
There is no single build entrypoint; contributors run stage scripts directly.

- `python 01数据预处理/data_preprocess.py`: preprocess raw judgments.
- `python "02分词/分词算法/05LTP分词/LTP分词_词性标注_命名实体识别.py"`: generate token, POS, and NER output.
- `crf_learn template train.data model`: train the CRF++ extractor in `03基于CRF的事件要素抽取/`.
- `crf_test -m model test.data >> output.txt`: run CRF++ inference.
- `python "06判决结果预测/pytorch多分类/net.py"`: train and evaluate the classifier.
- `python "07案件相似度/案件特征提取.py"`: extract similarity features for a single case.

## Coding Style & Naming Conventions
Use Python with UTF-8 source encoding and 4-space indentation. Follow the existing script-oriented style: `snake_case` for variables/functions, descriptive filenames, and module-local data files. Keep Chinese directory names intact; new files should match the naming style of the surrounding module. Prefer small, explicit scripts over framework-heavy abstractions.

## Testing Guidelines
There is no automated `pytest` suite yet. For each change, rerun the affected stage and verify the generated `.txt` or `.csv` outputs in that module. When adding logic, include a minimal reproducible sample under the relevant module or `标准数据/` and document expected output in the PR.

## Commit & Pull Request Guidelines
Recent history uses short summaries such as `优化代码`, `优化了数据预处理代码`, and `Update README.md`. Keep commits focused and concise; use an imperative summary and mention the module changed. PRs should describe the pipeline stage affected, required local dependencies, sample input/output changes, and any path updates or model assumptions.

## Configuration Tips
Several scripts hard-code local paths such as `/home/zhangshiwei/...` for LTP and CRF++ assets. Replace these with paths valid on your machine before running, and avoid introducing new absolute paths in committed code.
