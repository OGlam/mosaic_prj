import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from main.models import Tag, MosaicItem, MosaicSite, MosaicPicture
import pandas as pd
import requests


def getData():
    print("hi3")
    xlphotos = pd.ExcelFile("listing_of_photos.xlsx").parse("Sheet1")
    photo_names = xlphotos.name.unique()
    print(photo_names)
    xlcnts = pd.ExcelFile("Copy of רשימת חפצים ונגטיבים עם נגטיב מקור והעתק דיגיטאלי.xlsx").parse("גיליון1")
    # get the connection between photo number and misp_rashut:
    xlcnts = xlcnts.loc[xlcnts['neg_misp'].isin(photo_names)]
    xlmosaics = pd.ExcelFile("oglam-mosaics.csv.xlsx").parse("oglam-mosaics.csv")

    for photo in photo_names:
        misp_rashut = getMispRashut(photo, xlcnts)
        if misp_rashut == None:
            continue
        mosaic = getMosaic(misp_rashut, xlmosaics)
        if mosaic == None:
            print("failed")
            continue
        createPhoto(mosaic, photo, xlphotos)

def getMispRashut(photo, xlcnts):
    rashut_nums = xlcnts.loc[xlcnts['neg_misp'] == photo]
    if not rashut_nums.empty:
        misp_rashut = rashut_nums.iloc[0]['misp_rashut_b']
        return misp_rashut
    pass

i=0


def getOrCreateMosaicSite(misp_rashut, xlmosaics):
    mosaic_info = xlmosaics.loc[xlmosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    site_id = mosaic_info.iloc[0]['MOTSA_E'].split('(')[1].split(')')[0]
    mosaic_sites = MosaicSite.objects.filter(site_id = site_id)
    if len(mosaic_sites) > 0:
        return mosaic_sites[0]

    # else create a new site
    new_mosaic_site = MosaicSite()
    print ("site_id", site_id)
    new_mosaic_site.site_id = site_id
    new_mosaic_site.title_en = new_mosaic_site.origin_en = mosaic_info.iloc[0]['MOTSA_E'].split('(')[0]
    new_mosaic_site.title_he = new_mosaic_site.origin_he = mosaic_info.iloc[0]['MOTSA'].split('(')[0]
    new_mosaic_site.period = mosaic_info.iloc[0]['TKU_OBJ_E']
    new_mosaic_site.save()
    # TODO: COMPLETE THE MISSING FIELDS FOR MOSAIC SITE
    return new_mosaic_site


def getCoef(dimension):
    if "cm" in dimension.lower() or not "m" in dimension.lower():
        return 1
    else:
        return 100
    pass


def getDimensionsInfo(new_mos, obj_dimensions_str):
    if obj_dimensions_str == None:
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
            new_mos.length = nums[0] * getCoef(dimension)
            continue
        if "width" in dimension.lower():
            new_mos.width = nums[0] * getCoef(dimension)
            continue
        new_mos.area = nums[0]
    pass




def getMosaic(misp_rashut, xlmosaics):
    mosaic_items = MosaicItem.objects.filter(misp_rashut__startswith = misp_rashut)
    if len(mosaic_items) > 0:
        return mosaic_items[0]

    #check if a mosaic site exists, if not - create it
    mosaic_site = getOrCreateMosaicSite(misp_rashut, xlmosaics)

    # get the info from the excel
    mosaic_info = xlmosaics.loc[xlmosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    # create new mosaic item
    new_mos = MosaicItem()
    new_mos.mosaic_site = mosaic_site
    new_mos.misp_rashut = misp_rashut
    new_mos.description = mosaic_info.iloc[0]['OBJ_DESC_E']
    getDimensionsInfo(new_mos, mosaic_info.iloc[0]['OBJ_DIM_E'])
    tagscol = mosaic_info.iloc[0]['TIPUS_E']
    tagsFromDB = Tag.objects.all()
    print("not saved", i)
    new_mos.save()
    print("saved", i)

    for tag in tagsFromDB:
        if tag.tag_en in str(tagscol):
            print(tag.tag_en, tagscol)
            new_mos.tags.add(tag)

    new_mos.save()
    # TODO: COMPLETE THE MISSING FIELDS FOR MOSAIC ITEM
    return new_mos



    pass


def createPhoto(mosaic, photoname, xlphotos):
    photo_row = xlphotos.loc[xlphotos['name'] == photoname]
    if not photo_row.empty:
        link = photo_row.iloc[0]['download_link']
        photo_full_name = photo_row.iloc[0]['name_orig']
    else:
        return
    new_pic = MosaicPicture()
    new_pic.mosaic = mosaic
    new_pic.negative_id = photoname
    filename = os.path.join(
        settings.BASE_DIR, f'images_to_upload/{photo_full_name}'
    )
    print(photoname, filename)
    try:
        file_object = open(filename, "br")
        print("opened ",filename)
    except IOError:
        print ("Could not open file! Make sure the file is in the folder", filename)
    new_pic.picture = UploadedFile(file_object)
    new_pic.save()

    #TODO: ADD MISSING FIELDS TO MOSAIC PICTURE

    pass

def downloadPic(link, photoname):
    res = requests.get(link, stream=True)
    filename = os.path.join(
        settings.BASE_DIR, f'temp_images/{photoname}.jpg'
    )
    with open(filename, 'wb') as fd:
        for chunk in res.iter_content(chunk_size=128):
            fd.write(chunk)

    return filename

