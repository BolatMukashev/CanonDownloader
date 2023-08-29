from pathlib import Path
import shutil
from rembg import remove
from PIL import Image, ImageFilter
from enum import Enum
from typing import Callable
from send2trash import send2trash
import functools


from loguru import logger

# Настройка логирования в файл и на консоль
logger.add("app.log", rotation="500 MB", compression="zip")
logger.add(sink="console", format="<green>{time}</green> <level>{message}</level>")

#logger.debug("Это отладочное сообщение")
#logger.info("Это информационное сообщение")
#logger.warning("Это предупреждение")
#logger.error("Это сообщение об ошибке")


# "C:\Windows\System32\cmd.exe" /k команда
# pyinstaller --onefile canon_downloader.py


class ImagesTypes(Enum):
	JPG = '*.JPG'
	JPEG = '*.jpeg'
	PNG = '*.png'


def progress_checker(start: str, finish: str = '	✓'):
	"""
	Декоратор для отслеживания прогресса выполнения программы
	start - сообщение перед выполнением функции
	finish - сообщение после выполнения функции
	"""
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			logger.info(start, end='')
			val = func(*args, **kwargs)
			logger.info(finish)
			return val
		return wrapper
	return decorator


class Images:
	"""Получить путь ко всем изображениям в директории"""
	def __init__(self, path_: Path):
		self.path_ = path_
	
	def get_images(self):
		"""interface method"""
		images = []
		types = [x.value for x in ImagesTypes]
		for type_ in types:
			imgs = self.path_.glob(type_)
			images.extend(imgs)
		return images

	def get_renamed_images(self):
		res = self.path_.glob('renamed_*')
		return list(res)

	@progress_checker(start='Переименовываем оригиналы')
	def rename_images(self):
		images = self.get_images()
		for img in images:
			name = 'renamed_' + img.name
			img.rename(self.path_.joinpath(name))

	@progress_checker(start='Перемещаем оригиналы фотографий в корзину')
	def delete_images(self, only_renamed = False):
		images = self.get_images() if not only_renamed else self.get_renamed_images()
		for img in images:
			send2trash(img)


class FileMover:
	""" Перемещает фотографии из cd-карты фотоапарата в папку Client"""
	photo_path = [Path('D:/DCIM/100CANON'), Path('H:/DCIM/100CANON'), Path('G:/DCIM/100CANON'), Path('E:/DCIM/100CANON')]
	target_path = Path('C:/Users/Астана11б/Pictures/Client/neiro')

	@progress_checker(start='Перемещаем фотографии с cd-карты камеры в папку Client')
	def move(self):
		images = []
		for p in self.photo_path:
			imgs = Images(p).get_images()
			images.extend(imgs)
		for el in images:
			shutil.move(el, Path(self.target_path, el.name))

	# Path("C:/Users/bolat/Desktop/Client/neiro/1.jpeg").rename("C:/Users/bolat/Desktop/Client/neiro+/1.jpeg")


class Remover:
	""" Удаляет фон с фотографий """

	def __init__(self, path: Path, path_to_save: Path):
		self.path = path
		self.path_to_save = path_to_save

	@progress_checker(start='Удаляем фон с изображений')
	def remove_bg(self):
		images = Images(self.path).get_images()
		for img in images:
			output_path = str(Path(self.path_to_save, img.stem + '.png'))
			with open(img, 'rb') as i:
				with open(output_path, 'wb') as o:
					input_ = i.read()
					output = remove(input_) # alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10
					o.write(output)

	@progress_checker(start='Увеличиваем резкость')
	def sharpness_up(self):
		images = Images(self.path_to_save).get_images()
		for el in images:
			if not el.name.endswith('.png'):
				img = Image.open(el)
				img = img.filter(ImageFilter.EDGE_ENHANCE)
				img.save(el)


if __name__ == '__main__':
	path = Path("C:/Users/Астана11б/Pictures/Client/neiro")
	path_to_save = Path("C:/Users/Астана11б/Pictures/Client/neiro+")

	Images(path).delete_images(only_renamed=True)
	Images(path_to_save).delete_images()
	FileMover().move()
	Remover(path, path_to_save).remove_bg()
	Remover(path, path_to_save).sharpness_up()
	Images(path).rename_images()
