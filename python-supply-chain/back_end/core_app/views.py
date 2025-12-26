from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import re
from fetch_cve.get_cve import get_cve
import json
from my_pip._internal.commands import create_command
from find_extra._internal.commands import create_command as create_command_extra
@csrf_exempt
def supply_chain(request):
    response = {}
    response['graph']=[]
    try:
        pack_name = request.GET.get('name')
        pack_version = request.GET.get('version')

        pack_extra=request.GET.get('extra')
        pack_extra=pack_extra.replace('_', '-')

        pack=pack_name
        root_name = pack_name
        if pack_extra!='':
            pack=pack+'['+pack_extra+']'
            root_name = pack

        if pack_version!='':
            pack=pack+'=='+pack_version
        print(pack)
        cmd_name = 'install'
        cmd_args = [pack]
        command = create_command(cmd_name, isolated=False)
        result = command.main(cmd_args)
        # 如果存在extra和原来的包重复，则只留下extra
        remove_list = []
        for key in result.graph._forwards:
            if key != None:
                matchObj = re.match(r'(\w+)\[([\w-]+)\]', key)
                if matchObj:
                    remove_list.append(matchObj.group(1))
        for item in remove_list:
            result.graph.remove(item)
        print("rootname是"+root_name)
        for key in result.graph._forwards:
            if key!=None and key!='<Python from Requires-Python>':
                temp={}
                temp['is_root']=0
                if key==root_name:
                    temp['is_root'] = 1
                temp['name']=str(result.mapping[key])
                temp['dependences']=[]
                for dep in result.graph._forwards[key]:
                    if(dep!='<Python from Requires-Python>'):
                        temp['dependences'].append(str(result.mapping[dep]))

                # 增加cve查询
                temp['cves'] = []
                parts=str(result.mapping[key]).split()
                cve_pack=parts[0]
                cve_version=parts[1]
                cve_list=get_cve(cve_pack,cve_version)
                cve_list_temp=[]
                for cve in cve_list:
                    cve_temp = {}
                    cve_temp['cve_cna'] = cve.cve_cna
                    cve_temp['cve_create_time'] = cve.cve_create_time
                    cve_temp['cve_description'] = cve.cve_description
                    cve_temp['cve_no'] = cve.cve_no
                    cve_temp['cve_url'] = cve.cve_url
                    cve_list_temp.append(cve_temp)
                temp['cves']=cve_list_temp
                if cve_list_temp==[]:
                    temp['has_cve']=0
                else:
                    temp['has_cve'] = 1
                response['graph'].append(temp)


        response['msg'] = 'success'
        response['status'] = 200
    except Exception as e:
        response['msg'] = str(e)
        response['status'] = 400

    return JsonResponse(response)


def get_versions(request):
    response={}
    pack_name = request.GET.get('name')
    cmd_name = 'index'
    cmd_args = ['versions', pack_name]
    command = create_command(cmd_name, isolated=False)
    result = command.main(cmd_args)
    if result==1:
        response['status']=404
    else:
        response['status'] = 200
    response['versions']=result
    return JsonResponse(response)

def get_extra(request):
    response = {}
    pack_name = request.GET.get('name')
    pack_version = request.GET.get('version')
    if pack_version!='':
        pack=pack_name+'=='+pack_version
    else:
        pack=pack_name
    cmd_name = 'install'
    cmd_args = [pack]
    command = create_command_extra(cmd_name, isolated=False)
    result = command.main(cmd_args)
    if result==1:
        response['status']=404
    else:
        response['status'] = 200
    response['extra'] = result
    return JsonResponse(response)