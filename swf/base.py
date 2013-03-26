# -*- coding:utf-8 -*-

import boto.swf


def aws_connexion(aws_access_key_id, aws_secret_access_key):
    return boto.swf.layer1.Layer1(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)
