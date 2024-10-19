import pandas as pd
import os
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

def setAlpha(img, a):
    alpha = img.split()[3]  # 获取 alpha 通道
    alpha = alpha.point(lambda p: a)  # 调整 alpha 值
    img.putalpha(alpha)
    return img

#这里使用的完整地址，取决于你的文件的存储地址
file_path = os.path.join('data', '2024-10-19_21-25-45_word_counts.csv')
image_path = os.path.join('images', 'bnu.jpg')
save_path = 'results.png'
df = pd.read_csv(file_path)
word_counts_dict = dict(zip(df['Word'], df['Count']))

image = Image.open(image_path)

mask = np.array(image)
image = image.convert("RGBA")


cycle_mask = np.zeros(mask.shape)
for i in range(cycle_mask.shape[0]):
    for j in range(cycle_mask.shape[1]):
        if (i - cycle_mask.shape[0] / 2)**2 + (j - cycle_mask.shape[0] / 2)**2 < cycle_mask.shape[0]**2 / 4:
            cycle_mask[i, j, :] = 0
        else:
            cycle_mask[i, j, :] = 255

wc = WordCloud(background_color="white", max_words=50, mask=cycle_mask,
                contour_width=3, contour_color='firebrick').generate_from_frequencies(word_counts_dict)

# 将背景和蒙版合成
wordcloud_image = wc.to_image().convert("RGBA")
image = setAlpha(image, 0)
wordcloud_image = setAlpha(wordcloud_image, 200)
combined = Image.alpha_composite(image, wordcloud_image)

# 生成词云
plt.figure(figsize=(10, 5))
plt.imshow(combined, interpolation='bilinear')
plt.axis('off')  # 不显示坐标轴
plt.savefig(save_path, bbox_inches='tight')
plt.show()
