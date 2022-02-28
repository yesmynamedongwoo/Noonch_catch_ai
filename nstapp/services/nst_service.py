from ninja.files import UploadedFile
from ninja import File
import tensorflow as tf
import numpy as np
from nstapp.apps import NstappConfig
from io import BytesIO
from PIL import Image
import requests
from crawling.service.crawling import search_img
import random


def upload_tensor_img(bucket, tensor, key):
    # normalize 해제
    tensor = np.array(tensor * 255, dtype=np.uint8)
    # image 화
    image = Image.fromarray(tensor[0])
    # 메모리에다가 이미지를 파일 형태로 저장
    buffer = BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)  # 0번째 포인터위치부터 파일을 읽으라는 뜻
    # s3 에다가 업로드
    NstappConfig.s3.put_object(Bucket=bucket, Key=f"{key}.png", Body=buffer, ACL='public-read', ContentType= 'application-octet-stream')
    # s3 에 올라간 파일의 링크를 리턴함
    location = NstappConfig.s3.get_bucket_location(Bucket=bucket)['LocationConstraint']
    url = "https://s3-%s.amazonaws.com/%s/%s.png" % (location, bucket, key)
    return url


def load_style(path_to_style, max_dim):
    # 이미지의 최대 크기 제한
    img = tf.io.read_file(path_to_style)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)

    # 이미지의 채널 부분 제외하고, 이미지의 가로/세로 shape 를 추출함
    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    # 이미지의 가로/세로 중에서 긴 부분의 길이를 추출함
    long_dim = max(shape)
    # 이미지의 최대 크기를 제한하기 위해서, 제한하고자 하는 길이 / 긴 부분의 길이를 구함
    scale = max_dim / long_dim

    # 이미지의 가로/세로 길이 * (제한하고자 하는 길이 / 긴 부분의 길이) 해서 축소될 길이(shape)를 구함
    new_shape = tf.cast(shape * scale, tf.int32)
    # 축소될 길이를 구했으니 해당 길이대로 resize 함
    img = tf.image.resize(img, new_shape)
    # batch dimension 추가
    img = img[tf.newaxis, :]
    return img


def nst_apply(key: str) -> str:
    style_path = tf.keras.utils.get_file('kandinsky5.jpg',
                                         'htps://storage.googleapis.com/download.tensorflow.org/example_images/Vassily_Kandinsky%2C_1913_-_Composition_7.jpg'
                                         )

    style_path2 = tf.keras.utils.get_file('marvel.jpg',
                                         'http://www.gamtoon.com/wupload2/180808_mbb_3.jpg'
                                         )

    style_path3 = tf.keras.utils.get_file('cartoon.jpg',
                                         'https://noonch-catch-ai.s3.ap-northeast-2.amazonaws.com/Picsart_22-02-28_19-37-02-083.jpg'
                                         )

    style_path4 = tf.keras.utils.get_file('gohe.jpg',
                                          'https://noonch-catch-ai.s3.ap-northeast-2.amazonaws.com/aaaaaaaaaaaaaa.jpg'
                                          )
    style_path5 = tf.keras.utils.get_file('black.jpg',
                                          'https://noonch-catch-ai.s3.ap-northeast-2.amazonaws.com/Picsart_22-02-28_16-08-24-552.jpg'
                                          )
    style_path6 = tf.keras.utils.get_file('cenedecirco.jpg',
                                          'https://noonch-catch-ai.s3.ap-northeast-2.amazonaws.com/cenedecirco.jpg'
                                          )


    style_path_all = [style_path,style_path2,style_path3,style_path4,style_path5,style_path6]



    choicelstyle = random.choice(style_path_all)


    keyword_img = search_img(key)
    response = requests.get(keyword_img)
    print(keyword_img)

    # 이미지 읽기
    # img = Image.open(response.file).convert('RGB')
    img = Image.open(BytesIO(response.content)).convert('RGB')
    content_image = tf.keras.preprocessing.image.img_to_array(img)
    # 스타일도 위처럼 읽어와도 되지만, 스타일은 비율이 유지되어야만 올바르게 적용됨
    # 스타일 비율도 일괄적으로 resizing 할 경우 결과가 이상할 수 있음에 유의
    # load_style 함수는 비율을 유지하면서 스타일 이미지 크기를 줄이는 함수
    style_image = load_style(choicelstyle, 1024)

    # float32 타입으로 바꾸고, newaxis 를 통해 배치 차원을 추가한 후에 255 로 나눠서 normalize 함
    # 이후 256, 256 으로 리사이즈
    content_image = content_image.astype(np.float32)[np.newaxis, ...] / 255.
    content_image = tf.image.resize(content_image, (256, 256))

    stylized_image = NstappConfig.hub_module(tf.constant(content_image), tf.constant(style_image))[0]
    image_url = upload_tensor_img('noonch-catch-ai', stylized_image, key)
    return image_url