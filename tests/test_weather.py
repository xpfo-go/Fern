import unittest

from dotenv import load_dotenv

from src.call_tools.weather import WeatherTools

load_dotenv(dotenv_path='../config/.env')


class WeatherToolsTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_search_city_location_id(self):
        try:
            tool = WeatherTools()
            out = await tool.search_city_location_id("青岛")
            print(out)
            self.assertNotEqual(out.__sizeof__(), 0)
        except Exception as e:
            self.assertFalse(e)

    async def test_search_city_weather(self):
        location_id = '101120201'
        try:
            tool = WeatherTools()
            out = await tool.search_city_weather(location_id)
            print(out)
            self.assertNotEqual(out.__sizeof__(), 0)
        except Exception as e:
            self.assertFalse(e)


if __name__ == '__main__':
    unittest.main()
