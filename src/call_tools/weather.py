import json
import os
from typing import List

import requests
import urllib3
from mcp.server import FastMCP
from mcp.types import TextContent


class WeatherTools:
    def __init__(self):
        self.API_KEY = os.getenv('QWEATHER_API_KEY')
        self.BASE_URL = os.getenv('QWEATHER_API_URL')
        self.GEO_API = os.getenv('QWEATHER_GEO_API')
        urllib3.disable_warnings()
    
    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="获取某个地区的真实的天气预报", description="获取某个地区的真实的天气预报")
        async def search_city_location_info(city_name: str) -> list[TextContent]:
            try:
                city_list = await self.search_city_location_id(city_name)
                city_weather = []
                for item in city_list:
                    weather_daily = await self.search_city_weather(item["location_id"])
                    city_weather.append({
                        "city_name": f'{item["adm2"]}{item["adm1"]}{item["name"]}',
                        "weather_daily": weather_daily
                    })
                    # 只查第一个
                    break
                return [TextContent(type="text", text=json.dumps(city_weather))]
            except Exception as e:
                return [TextContent(type="text", text=str(e))]

    async def http_get(self, url) -> requests.Response:
        headers = {
            'X-QW-Api-Key': f'{self.API_KEY}',
            "Accept-Encoding": "gzip"
        }

        response = requests.get(
            url=url,
            headers=headers,
            verify=False,
        )

        return response

    async def search_city_weather(self, location_id: str) -> List:
        response: requests.Response = await self.http_get(url=f'{self.BASE_URL}/?location={location_id}')
        res = response.json()
        if not response.ok:
            print(res)
            raise res['error']['detail']

        weather_data = []
        for item in res["daily"]:
            weather_data.append(
                {
                    "date": item["fxDate"],
                    "description": f'{item["textDay"]}' if item["textDay"] == item[
                        "textNight"] else f'白天{item["textDay"]}, 夜间{item["textNight"]}',
                    "wind_dir": f'{item["windDirDay"]}' if item["windDirDay"] == item[
                        "windDirNight"] else f'{item["windDirDay"]}, {item["windDirNight"]}',
                    "wind": f'风力{item["windScaleDay"]}级' if item["windScaleDay"] == item[
                        "windScaleNight"] else f'白天风力{item["windScaleDay"]}级, 夜间风力{item["windScaleNight"]}级',
                    "temperature_max": f'{item["tempMax"]}摄氏度',
                    "temperature_min": f'{item["tempMin"]}摄氏度',
                    "humidity": f'{item["tempMin"]}%'
                }
            )
        return weather_data

    async def search_city_location_id(self, city_name: str) -> List:
        response: requests.Response = await self.http_get(url=f'{self.GEO_API}/?location={city_name}')
        res = response.json()
        if not response.ok:
            raise res['error']['detail']

        if len(res['location']) == 0:
            raise "未获取到城市或地区，请重试"

        locations = []
        for item in res['location']:
            locations.append({
                "name": item["name"],
                "adm1": item["adm1"],
                "adm2": item["adm2"],
                "location_id": item["id"]
            })
        return locations
