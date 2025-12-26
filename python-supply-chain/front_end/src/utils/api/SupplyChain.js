import request from '@/utils/request'

export function SupplyChain(obj){

    return request({
        url: 'supply_chain/',
        method: 'get',
        params: obj,
        timeout:6000000,
    })
}


export function Get_version(obj){

    return request({
        url: 'get_version/',
        method: 'get',
        params: obj,
    })
}

export function Get_extra(obj){

    return request({
        url: 'get_extra/',
        method: 'get',
        params: obj,
    })
}