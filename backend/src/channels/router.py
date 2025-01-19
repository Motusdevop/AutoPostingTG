from typing import List

from fastapi import APIRouter, HTTPException, Depends
from channels.schemas import NewChannel, Channel, Channels

import os

from repository import ChannelRepository
from models import ChannelORM
from auth.tools import authenticate_user

router = APIRouter(prefix='/channels', tags=['channels'])


@router.get('/get_all')
async def get_all(authorized: bool = Depends(authenticate_user)):
    if authorized:
        res = ChannelRepository.get_all()
        channels = []
        for x in res:
            channels.append(Channel.model_validate(x))

        return channels
    else:
        raise HTTPException(status_code=401)


@router.get('/get/{id}')
async def get_by_id(id: int, authorized: bool = Depends(authenticate_user)) -> Channel | None:
    if authorized:
        channel: ChannelORM = ChannelRepository.get(id)
        if channel is None:
            return None
        return Channel.model_validate(channel)
    else:
        raise HTTPException(status_code=401)

@router.post('/add')
async def add_channel(channel: NewChannel, authorized: bool = Depends(authenticate_user)):
    if authorized:
        data = channel.model_dump()
        try:
            os.makedirs(f'/Users/matvey/AutoPostingChannels/{data["name"]}', exist_ok=True)

            path_to_source_dir = f'/Users/matvey/AutoPostingChannels/{data["name"]}/source/'
            path_to_except_dir = f'/Users/matvey/AutoPostingChannels/{data["name"]}/except/'
            path_to_done_dir = f'/Users/matvey/AutoPostingChannels/{data["name"]}/done/'

            os.makedirs(path_to_source_dir, exist_ok=True)
            os.makedirs(path_to_except_dir, exist_ok=True)
            os.makedirs(path_to_done_dir, exist_ok=True)

            channel = ChannelORM(**data,
                                 path_to_source_dir=path_to_source_dir,
                                 path_to_except_dir=path_to_except_dir,
                                 path_to_done_dir=path_to_done_dir
                                 )



            ChannelRepository.add(channel)
            return {'status': 'ok'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    else:
        raise HTTPException(status_code=401)

@router.delete('/delete/{id}')
async def delete_channel(id: int, authorized: bool = Depends(authenticate_user)):
    if authorized:
        try:
            ChannelRepository.delete(id)
            return {'status': 'ok'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    else:
        raise HTTPException(status_code=401)

@router.put('/update/{id}')
async def update_channel(channel: Channel, authorized: bool = Depends(authenticate_user)):
    if authorized:
        try:
            data = channel.model_dump()
            ChannelRepository.update(ChannelORM(**data))
            return {'status': 'ok'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    else:
        raise HTTPException(status_code=401)
