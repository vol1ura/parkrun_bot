import os
import re
import json
import pytest
from unittest.mock import patch
import aresponses

from utils import vk


@pytest.mark.asyncio
async def test_get_random_photo(aresponses):
    # Мокируем ответы VK API
    mock_albums_response = {
        'response': {
            'count': 1,
            'items': [
                {'id': 'wall', 'title': 'Test Album'}
            ]
        }
    }
    
    mock_photos_response = {
        'response': {
            'count': 1,
            'items': [
                {
                    'id': 1,
                    'album_id': 'wall',
                    'owner_id': -212432495,
                    'sizes': [
                        {'type': 's', 'height': 100, 'width': 150, 'url': 'test_photo_url_small'},
                        {'type': 'm', 'height': 200, 'width': 300, 'url': 'test_photo_url_medium'},
                        {'type': 'x', 'height': 400, 'width': 600, 'url': 'test_photo_url'},
                        {'type': 'y', 'height': 600, 'width': 800, 'url': 'test_photo_url_large'},
                        {'type': 'z', 'height': 800, 'width': 1000, 'url': 'test_photo_url_xlarge'}
                    ]
                }
            ]
        }
    }
    
    # Настраиваем моки для API запросов
    aresponses.add(
        'api.vk.com',
        '/method/photos.getAlbums',
        'get',
        aresponses.Response(
            status=200,
            text=json.dumps(mock_albums_response),
            content_type='application/json'
        )
    )
    
    aresponses.add(
        'api.vk.com',
        '/method/photos.get',
        'get',
        aresponses.Response(
            status=200,
            text=json.dumps(mock_photos_response),
            content_type='application/json'
        )
    )
    
    # Патчим random.choice для предсказуемости
    with patch('random.choice', side_effect=lambda x: x[0]):
        photo_url = await vk.get_random_photo('test_token')
        assert isinstance(photo_url, str)
        assert photo_url == 'test_photo_url'
    
    # Тестируем случай, когда нет фотографий
    mock_photos_response['response']['items'] = []
    aresponses.add(
        'api.vk.com',
        '/method/photos.getAlbums',
        'get',
        aresponses.Response(
            status=200,
            text=json.dumps(mock_albums_response),
            content_type='application/json'
        )
    )
    
    aresponses.add(
        'api.vk.com',
        '/method/photos.get',
        'get',
        aresponses.Response(
            status=200,
            text=json.dumps(mock_photos_response),
            content_type='application/json'
        )
    )
    
    with patch('random.choice', side_effect=lambda x: x[0]):
        photo_url = await vk.get_random_photo('test_token')
        assert photo_url is None
    
    # Тестируем случай, когда у фото меньше 3 размеров
    mock_photos_response['response']['items'] = [{
        'id': 1,
        'album_id': 'wall',
        'owner_id': -212432495,
        'sizes': [
            {'type': 's', 'height': 100, 'width': 150, 'url': 'test_photo_url_small'},
            {'type': 'm', 'height': 200, 'width': 300, 'url': 'test_photo_url_medium'}
        ]
    }]
    
    aresponses.add(
        'api.vk.com',
        '/method/photos.getAlbums',
        'get',
        aresponses.Response(
            status=200,
            text=json.dumps(mock_albums_response),
            content_type='application/json'
        )
    )
    
    aresponses.add(
        'api.vk.com',
        '/method/photos.get',
        'get',
        aresponses.Response(
            status=200,
            text=json.dumps(mock_photos_response),
            content_type='application/json'
        )
    )
    
    with patch('random.choice', side_effect=lambda x: x[0]):
        photo_url = await vk.get_random_photo('test_token')
        assert isinstance(photo_url, str)
        assert photo_url == 'test_photo_url_medium'


def test_make_vk_api_url():
    url = vk.make_vk_api_url('test_token', 'test_method', '-1234567890', '111')
    assert re.fullmatch(r'https://api\.vk\.com/method/test_method\?owner_id=-1234567890'
                        r'&album_id=111&access_token=test_token&v=5.130', url)
