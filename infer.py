import argparse
import functools
import cv2
import numpy as np
from PIL import ImageFont
import matplotlib.pyplot as plt
from utils.predictor import DetectionPredictor
from utils.utils import add_arguments, print_arguments

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
add_arg('use_gpu',          bool,   True,                           '是否使用GPU进行预测')
add_arg('use_tensorrt',     bool,   False,                          '是否使用TensorRT加速')
add_arg('image_path',       str,    'dataset/test.jpg',             '预测的图片路径')
add_arg('image_shape',      str,    '640,640',                      '导出模型图像输入大小')
add_arg('model_dir',        str,    'output_inference/PPYOLOE_M',   '预测模型文件夹路径')
add_arg('labels_list_path', str,    'dataset/label_list.txt',       '数据标签列表文件路径')
args = parser.parse_args()
print_arguments(args)


def main():
    image_shape = [int(s) for s in args.image_shape.split(',')]
    # 字体的格式
    font_style = ImageFont.truetype("utils/simsun.ttc", 14, encoding="utf-8")
    predictor = DetectionPredictor(model_dir=args.model_dir,
                                   labels_list_path=args.labels_list_path,
                                   use_gpu=args.use_gpu,
                                   use_tensorrt=args.use_tensorrt,
                                   height=image_shape[0],
                                   width=image_shape[1])
    image = cv2.imdecode(np.fromfile(args.image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    result = predictor.infer([image])[0]
    print('识别结果：', result)
    # 在图片上画结果
    img = predictor.draw_box(image, results=result, font_style=font_style)
    # 显示图像
    
    fig = plt.gcf()
    fig.set_size_inches(18, 10)
    plt.axis("off")
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()


if __name__ == "__main__":
    main()
