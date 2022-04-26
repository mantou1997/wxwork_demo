import json

import requests
import xlrd
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import HttpResponse
# from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from wechatpy.work import WeChatClient
from .serializer import UserInfoModelSerializer
from .models import UserInfo


# Create your views here.
class MyExcelView(ModelViewSet):
    """视图集"""
    #这两句代表：查所有、查单一、新增、修改、删除
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoModelSerializer

    @action(methods=['post'], detail=False)
    def myexcel(self, request):
        # 1.获取token
        appid = 'db723212-3835-46a8-96d0-e760114dc0fb'
        secret = '7c625c45-a2b7-40db-a4ed-cc63d34e4d8a'
        accessToken = getToken(appid, secret)

        # token缓存至内存
        cache.set('token', accessToken, 60*60*2)
        #print(cache.get('token'))

        # 获取上传的文件对象
        excelfile = request.FILES.get("excelfile")

        wb = xlrd.open_workbook(filename=None, file_contents=excelfile.read())
        ws = wb.sheets()[0]

        # 2.读取Excel每一行
        for row in range(1, ws.nrows):
            name = ws.cell_value(row, 0)
            cn_name = ws.cell_value(row, 1)
            content = ws.cell_value(row, 2)
            if content == "清空":
                content = ""
            print(name, cn_name, content)

            # 3.token，获取userid
            wxId = getUserId(cn_name, accessToken)
            if wxId == "false":
                continue
            # print(wxId)

            corp_id = 'wx1deaa225db7d8ad5'
            secret = 'k17z57QaTptGQseICE2xZ7jde9H2VklMdHr1Ju8KgbE'
            # 4.调用企业微信API
            isOk = updateApi(corp_id, secret, wxId, cn_name, content, excelfile)
            if isOk == 'true':
                #logging.INFO('用户更新成功')
                print(cn_name + '用户更新成功')
                return JsonResponse({'message':'用户更新成功'},status=200)
            else:
                print(cn_name + '用户更新失败')
                return JsonResponse({'message':'用户更新成功'},status=500)



# 2.获取token
def getToken(appid, secret):
    # url="https://itapis.cvte.com/iac/app/access_token?appid=db723212-3835-46a8-96d0-e760114dc0fb&secret=7c625c45-a2b7-40db-a4ed-cc63d34e4d8a"
    url = "https://itapis.cvte.com/iac/app/access_token?" + "appid=" + appid + "&" + "secret=" + secret
    # print(url)

    payload = {}
    headers = {
        'Cookie': 'BIGipServerpool_idc_ingress_nginx_prd_it=3710784778.12405.0000'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    # str转dict
    # print(eval(response.text)['data']['accessToken'])
    accessToken = eval(response.text)['data']['accessToken']
    return accessToken


# 3.token，域账号获取userid
def getUserId(cn_name, accessToken):
    url = "http://wx-api.gz.cvte.cn/user/search?data=" + cn_name

    payload = {}
    headers = {
        'access-token': '89ce0d7e-338c-406a-bcdd-8bb72f56ad17'
    }
    headers['access-token'] = accessToken
    response = requests.request("GET", url, headers=headers, data=payload)

    # str转dict
    d = json.loads(response.text)['data']
    # 判断wxId是否为空
    for key in d:
        if d[key] != None:
            wxId = json.loads(response.text)['data']['data']['wxId']
            break
        else:
            print(cn_name + '\000用户查询不到wxId')
            wxId = "false"
            break

    return wxId


# 4.调用企业微信API
def updateApi(corp_id, secret, wxId, cn_name, content, excelfile):
    client = WeChatClient(corp_id, secret)

    # 获取extattr
    user = client.user.get(wxId)
    extattrAdd = user['extattr']

    # 调用更新-具体字段-方法
    # extattrAdd=updateZyz(extattrAdd,cn_name,content)
    excelfile = str(excelfile)
    if excelfile == '志愿者字段值替换.xlsx':
        extattrAdd = updateZyz(extattrAdd, cn_name, content)
    elif excelfile == '认证字段值替换.xlsx':
        extattrAdd = updateAuth(extattrAdd, cn_name, content)
    elif excelfile == '归属字段值替换.xlsx':
        extattrAdd = updateGs(extattrAdd, cn_name, content)
    else:
        print('文件名错误')
        return 'false'
    # print(extattrAdd)

    # 调用更改api
    try:
        client.user.update(user_id=wxId, extattr=extattrAdd)
        pass
        return 'true'
    except:
        return 'false'


# =========================调用更新-具体字段-方法======================
# 志愿者 字段 替换
def updateZyz(extattrAdd, cn_name, content):
    # 1. 判断attrs是否为空
    if not extattrAdd['attrs']:
        print(cn_name + '===========用户attrs为空')
        extattrAdd['attrs'] = [{'name': '志愿者', 'value': '', 'type': 0, 'text': {'value': ''}}]

    # 2.判断 志愿者 是否为空
    isOkZyz = '0'
    for item in extattrAdd['attrs']:
        # 更新
        if item["name"] == "志愿者":
            isOkZyz = '1'
            # print("有志愿者")
            break
    if isOkZyz == '0':
        extattrAdd['attrs'] = [{'name': '志愿者', 'value': '', 'type': 0, 'text': {'value': ''}}]
        print(cn_name + '=====无志愿者属性，已添加')

    # 3.添加星星
    for itemm in extattrAdd['attrs']:
        if itemm['name'] == '志愿者':
            extattrAdd['attrs'] = [{'name': '志愿者', 'value': content, 'type': 0, 'text': {'value': content}}]

    return extattrAdd


# 归属 字段 替换
def updateGs(extattrAdd, cn_name, content):
    # 1. 判断attrs是否为空
    if not extattrAdd['attrs']:
        print(cn_name + '===========用户attrs为空')
        extattrAdd['attrs'] = [{'name': '归属', 'value': '', 'type': 0, 'text': {'value': ''}}]

    # 2.判断 归属 是否为空
    isOkZyz = '0'
    for item in extattrAdd['attrs']:
        # 更新
        if item["name"] == "归属":
            isOkZyz = '1'
            # print("有志愿者")
            break
    if isOkZyz == '0':
        extattrAdd['attrs'] = [{'name': '归属', 'value': '', 'type': 0, 'text': {'value': ''}}]
        print(cn_name + '=====无归属属性，已添加')

    # 3.添加星星
    for itemm in extattrAdd['attrs']:
        if itemm['name'] == '归属':
            extattrAdd['attrs'] = [{'name': '归属', 'value': content, 'type': 0, 'text': {'value': content}}]

    return extattrAdd


# 认证 字段 替换
def updateAuth(extattrAdd, cn_name, content):
    # 1. 判断attrs是否为空
    if not extattrAdd['attrs']:
        print(cn_name + '===========用户attrs为空')
        extattrAdd['attrs'] = [{'name': '认证', 'value': '', 'type': 0, 'text': {'value': ''}}]

    # 2.判断 认证 是否为空
    isOkZyz = '0'
    for item in extattrAdd['attrs']:
        # 更新
        if item["name"] == "认证":
            isOkZyz = '1'
            # print("有志愿者")
            break
    if isOkZyz == '0':
        extattrAdd['attrs'] = [{'name': '认证', 'value': '', 'type': 0, 'text': {'value': ''}}]
        print(cn_name + '=====无认证字段，已添加')

    # 3.添加星星
    for itemm in extattrAdd['attrs']:
        if itemm['name'] == '认证':
            extattrAdd['attrs'] = [{'name': '认证', 'value': content, 'type': 0, 'text': {'value': content}}]

    return extattrAdd
