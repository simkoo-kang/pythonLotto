from munch import Munch

from config.config_manager import ConfigManager
from util.file_util import FileUtil


config_manager = ConfigManager(__file__)

# 값 읽기
print(config_manager.settings)

settings = config_manager.settings

for key, value in settings.items():
    if isinstance(value, Munch):
        print(f"key: {key} ")
        for skey, svalue in value.items():
            print(f"\tkey: {skey} = value: {svalue}")
    else:
        print(f"key: {key} = value: {value}")

print(settings.default)
print(settings.default.volume)

del settings.default.bgm_on

# settings.clear()

print(config_manager.settings)
print(settings)

# 값 수정 및 저장
# settings.bgm_volume = 0.8
# if settings.default:
#     del settings.default

# config.save()

class ConfigTest:
    def __init__(self):
        file_util = FileUtil()
        print(FileUtil.get_absolute_class_path(file_util))

ct = ConfigTest()
