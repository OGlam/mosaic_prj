import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from main.models import Tag, MosaicItem, MosaicSite, MosaicPicture
import pandas as pd
import requests


def get_data():
    print("hi3")
    xl_photos = pd.ExcelFile("imports/listing_of_photos.xlsx").parse("Sheet1")
    photo_names = xl_photos.name.unique()
    print(photo_names)
    xl_cnts = pd.ExcelFile("imports/Copy of רשימת חפצים ונגטיבים עם נגטיב מקור והעתק דיגיטאלי.xlsx").parse("גיליון1")
    # get the connection between photo number and misp_rashut:
    xl_cnts = xl_cnts.loc[xl_cnts['neg_misp'].isin(photo_names)]
    xl_mosaics = pd.ExcelFile("imports/oglam-mosaics.csv.xlsx").parse("oglam-mosaics.csv")

    for photo in photo_names:
        misp_rashut = get_misp_rashut(photo, xl_cnts)
        if not misp_rashut:
            continue
        mosaic = get_mosaic(misp_rashut, xl_mosaics)
        if not mosaic:
            print("failed")
            continue
        create_photo(mosaic, photo, xl_photos)


def get_misp_rashut(photo, xl_cnts):
    rashut_nums = xl_cnts.loc[xl_cnts['neg_misp'] == photo]
    if not rashut_nums.empty:
        misp_rashut = rashut_nums.iloc[0]['misp_rashut_b']
        return misp_rashut


def get_or_create_mosaic_site(misp_rashut, xl_mosaics):
    mosaic_info = xl_mosaics.loc[xl_mosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    site_id = mosaic_info.iloc[0]['MOTSA_E'].split('(')[1].split(')')[0]
    mosaic_sites = MosaicSite.objects.filter(site_id=site_id)
    if mosaic_sites:
        return mosaic_sites[0]

    # else create a new site
    new_mosaic_site = MosaicSite()
    print("site_id", site_id)
    new_mosaic_site.site_id = site_id
    new_mosaic_site.title_en = new_mosaic_site.origin_en = mosaic_info.iloc[0]['MOTSA_E'].split('(')[0]
    new_mosaic_site.title_he = new_mosaic_site.origin_he = mosaic_info.iloc[0]['MOTSA'].split('(')[0]
    new_mosaic_site.period = mosaic_info.iloc[0]['TKU_OBJ_E']
    new_mosaic_site.save()
    # TODO: COMPLETE THE MISSING FIELDS FOR MOSAIC SITE
    return new_mosaic_site


def get_coef(dimension):
    if "cm" in dimension.lower() or not "m" in dimension.lower():
        return 1
    return 100


def get_dimensions_info(new_mos, obj_dimensions_str):
    if not obj_dimensions_str:
        return
    dimensions = str(obj_dimensions_str).split("\n")
    for dimension in dimensions:
        nums = [int(s) for s in dimension.split() if s.isdigit()]
        if len(nums) > 1:
            print("too many numbers can't parse")
            return
        if len(nums) == 0:
            print("no numbers to parse")
            return
        if "length" in dimension.lower():
            new_mos.length = nums[0] * get_coef(dimension)
            continue
        if "width" in dimension.lower():
            new_mos.width = nums[0] * get_coef(dimension)
            continue
        new_mos.area = nums[0]


def get_mosaic(misp_rashut, xl_mosaics):
    mosaic_items = MosaicItem.objects.filter(misp_rashut__startswith=misp_rashut)
    if mosaic_items:
        return mosaic_items[0]

    # check if a mosaic site exists, if not - create it
    mosaic_site = get_or_create_mosaic_site(misp_rashut, xl_mosaics)

    # get the info from the excel
    mosaic_info = xl_mosaics.loc[xl_mosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    # create new mosaic item
    new_mos = MosaicItem()
    new_mos.mosaic_site = mosaic_site
    new_mos.misp_rashut = misp_rashut
    new_mos.description = mosaic_info.iloc[0]['OBJ_DESC_E']
    get_dimensions_info(new_mos, mosaic_info.iloc[0]['OBJ_DIM_E'])
    tags_col = mosaic_info.iloc[0]['TIPUS_E']
    tags = Tag.objects.all()
    print("not saved", 0)
    new_mos.save()
    print("saved", 0)

    for tag in tags:
        if tag.tag_en in str(tags_col):
            print(tag.tag_en, tags_col)
            new_mos.tags.add(tag)

    new_mos.save()
    # TODO: COMPLETE THE MISSING FIELDS FOR MOSAIC ITEM
    return new_mos


def create_photo(mosaic, photo_name, xl_photos):
    photo_row = xl_photos.loc[xl_photos['name'] == photo_name]
    if not photo_row.empty:
        link = photo_row.iloc[0]['download_link']
        photo_full_name = photo_row.iloc[0]['name_orig']
        filename = download_pic(link, photo_full_name)
    else:
        return
    new_pic = MosaicPicture()
    new_pic.mosaic = mosaic
    new_pic.negative_id = photo_name
    print(photo_name, filename)
    try:
        file_object = open(filename, "br")
        print("opened ", filename)
        new_pic.picture = UploadedFile(file_object)
    except IOError:
        print("Could not open file! Make sure the file is in the folder", filename)
    new_pic.save()

    # TODO: ADD MISSING FIELDS TO MOSAIC PICTURE


def download_pic(link, photo_name):
    res = requests.get(link, stream=True)
    if not os.path.exists(os.path.join(settings.BASE_DIR, 'images_to_upload')):
        os.makedirs(os.path.join(settings.BASE_DIR, 'images_to_upload'))
    filename = os.path.join(
        settings.BASE_DIR, f'images_to_upload/{photo_name}'
    )
    with open(filename, 'wb') as fd:
        for chunk in res.iter_content(chunk_size=128):
            fd.write(chunk)

    return filename
