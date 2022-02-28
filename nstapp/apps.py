from django.apps import AppConfig
import boto3
import tensorflow_hub as hub

class NstappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nstapp'
    hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')

    s3 = boto3.client('s3', aws_access_key_id='AKIAW35GBHX2HOFBVFKW',
                      aws_secret_access_key='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', region_name='ap-northeast-2')