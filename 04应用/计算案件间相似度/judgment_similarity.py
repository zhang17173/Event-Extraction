#!/usr/bin/env python
# _*_coding:utf-8 _*_

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
from gensim.models import word2vec
from scipy import linalg

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)


def sentence_vector(model: word2vec.Word2Vec, sentence: str, vector_size: int) -> np.ndarray:
    words = [word for word in sentence.split(" ") if word]
    if not words:
        return np.zeros(vector_size)
    vectors = [model.wv[word] for word in words if word in model.wv]
    if not vectors:
        return np.zeros(vector_size)
    return np.mean(vectors, axis=0)


def vector_similarity(model: word2vec.Word2Vec, s1: str, s2: str, vector_size: int) -> float:
    v1 = sentence_vector(model, s1, vector_size)
    v2 = sentence_vector(model, s2, vector_size)
    denominator = linalg.norm(v1) * linalg.norm(v2)
    if denominator == 0:
        return 0.0
    return float(np.dot(v1, v2) / denominator)


def main() -> None:
    parser = argparse.ArgumentParser(description="计算案件之间的文本相似度。")
    parser.add_argument("--input", default="案件.txt", help="已分词的案件文本，每行一个案件。")
    parser.add_argument("--output", default="result.txt", help="输出结果文件。")
    parser.add_argument("--vector-size", type=int, default=100, help="词向量维度。")
    parser.add_argument("--seed", type=int, default=42, help="随机种子。")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    contents = input_path.read_text(encoding="utf-8").splitlines()
    contents = [line.strip() for line in contents if line.strip()]
    if not contents:
        raise RuntimeError("输入文件中没有可用案件。请保证每行至少有一个已分词案件。")

    sentences = word2vec.LineSentence(str(input_path))
    model = word2vec.Word2Vec(sentences, hs=1, min_count=1, window=5, vector_size=args.vector_size, seed=args.seed)
    matrix = np.zeros((len(contents), len(contents)))
    for i in range(len(contents)):
        for j in range(i, len(contents)):
            similarity = vector_similarity(model, contents[i].strip(), contents[j].strip(), args.vector_size)
            matrix[i][j] = similarity
            matrix[j][i] = similarity

    with output_path.open("w", encoding="utf-8") as f:
        for index, content in enumerate(contents):
            if len(contents) == 1:
                similar_index = 0
            else:
                similar_index = int(np.argsort(matrix[index])[-2])
            f.write(f"案件{index + 1}:\t{content}\n")
            f.write(f"案件{similar_index + 1}:\t{contents[similar_index]}\n")
            f.write(f"相似度： {matrix[index][similar_index]}\n\n")


if __name__ == "__main__":
    main()
