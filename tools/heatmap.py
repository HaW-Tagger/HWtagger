import matplotlib.pyplot as plt
from tools.files import subfolders_load
import os
import seaborn as sns
import numpy as np
from collections import defaultdict


def heatmap(name, images_dir, analysis_dir, num):
    # get the data
    huh = subfolders_load(images_dir)
    data = [x[1] for x in huh]

    # get the sorted prevalence 100 tags list
    flat_data = []
    for x in data:
        flat_data.extend(x)
    prevalence = defaultdict(lambda: 0)
    for t in flat_data:
        prevalence[t] += 1
    prevalence_list = list(prevalence.items())
    sorted_prevalence = sorted(prevalence_list, key=lambda x: x[1], reverse=True)[:num]
    sorted_unique_tags = [x[0] for x in sorted_prevalence]

    matrix = [[0.0 for y in sorted_prevalence] for x in sorted_prevalence]

    for img in data:
        for i in range(len(img)):
            if img[i] in sorted_unique_tags:
                for k in range(i+1, len(img)):
                    if img[k] in sorted_unique_tags:
                        matrix[sorted_unique_tags.index(img[i])][sorted_unique_tags.index(img[k])] += 1
                        matrix[sorted_unique_tags.index(img[k])][sorted_unique_tags.index(img[i])] += 1

    for row in range(len(matrix)):
        for col in range(row+1, len(matrix)):
            matrix[row][col] = 0.0

    for row in range(len(matrix)):
        for col in range(len(matrix)):
            if matrix[row][col] != 0.0:
                matrix[row][col] = matrix[row][col]*2/(sorted_prevalence[row][1]+sorted_prevalence[col][1])

    matrix_array = np.array(matrix)
    masked_matrix = np.ma.masked_where(matrix_array == 0.0, matrix_array)

    # Create a matrix where each row corresponds to a list and each column corresponds to a tag
    # matrix = [[1 if tag in sublist else 0 for tag in unique_tags] for sublist in data]

    # Compute the correlation matrix
    plt.figure(figsize=(40,40))
    correlation_matrix = sns.heatmap(masked_matrix, annot=False, xticklabels=sorted_unique_tags, yticklabels=sorted_unique_tags, square=True)
    plt.title(name+": Heatmap", fontsize=25)
    plt.suptitle("1.0 means they are always together in the same image, 0.0 means they are never together inside the same image", fontsize=12, y=0.10)
    plt.savefig(os.path.join(analysis_dir, name), bbox_inches='tight', pad_inches=0.1)
