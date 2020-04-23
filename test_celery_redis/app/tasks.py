import os
from celery import shared_task
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfFileWriter, PdfFileReader
from datetime import datetime
from pytz import timezone
import base64


def break_pdf_into_parts(file):
    list_of_pdf_page_names = []
    with open('media/'+file, "rb") as f:
        input_pdf = PdfFileReader(f)
        file_name = file.split(".")[0]  # Name of file without extension itself
        for page in range(input_pdf.numPages):
            output = PdfFileWriter()
            output.addPage(input_pdf.getPage(page))
            with open('media/'+file_name+'-page%s.pdf' % page, "wb") as outputStream:
                output.write(outputStream)
                list_of_pdf_page_names.append(file_name+'-page%s.pdf' % page)
    return list_of_pdf_page_names


def convert_pdf_to_image(file):
    file_name = file.split(".")[0]
    image = convert_from_path('media/'+file, dpi=200, fmt='jpg')
    saved_image_name = None
    for page in image:
        page.save('%s.jpg' % ('media/'+file_name), 'JPEG')
        saved_image_name = '%s.jpg' % file_name
    return saved_image_name

@shared_task
def ocr(file, file_name):
    region_time_zone = timezone('America/Sao_Paulo')
    try:
        start_date_and_time = datetime.now(region_time_zone)
        file_decoded = base64.b64decode(file)
        with open('media/'+file_name, "wb") as f:
            f.write(file_decoded)  # file saved in server

        image_list = []
        extension_name = file_name.split(".")[1]
        if extension_name == "pdf":
            list_of_pdf_page_names = break_pdf_into_parts(file_name)
            for pdf_page_name in list_of_pdf_page_names:
                image_list.append(convert_pdf_to_image(pdf_page_name))
        else:
            image_list.append(file_name)  # user send a image to ocr api

        # applying ocr

        content_extracted_from_images = []
        for image in image_list:
            content_extracted_from_images.append(pytesseract.image_to_string(Image.open('media/'+image), lang='por'))

        # cleaning the trash
        directory = 'media'
        for root, dir, files in os.walk(directory):
            for file in files:
                if file_name.split('.')[0] in file:
                    os.remove('media/' + file)

        end_date_and_time = datetime.now(region_time_zone)
        result = {
            'name': file_name,
            'number_of_pages': len(content_extracted_from_images),
            'start_date_and_time': start_date_and_time,
            'end_date_and_time': end_date_and_time,
            'content_extracted_from_images': content_extracted_from_images
        }

        return result

    except Exception as error:
        # cleaning the trash
        directory = 'media'
        for root, dir, files in os.walk(directory):
            for file in files:
                if file_name.split('.')[0] in file:
                    os.remove('media/' + file)
        result = {
            'error': error
        }
        return result
