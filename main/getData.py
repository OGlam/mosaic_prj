import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from main.models import Tag, MosaicItem, MosaicSite, MosaicPicture
import pandas as pd
import requests


def getData():
    print("hi3")
    # this is on my personal computer - should be on the net
    xlphotos = pd.ExcelFile("listing_of_photos.xlsx").parse("Sheet1")
    photo_names = xlphotos.name.unique()
    print(photo_names)

    xlcnts = pd.ExcelFile("Copy of רשימת חפצים ונגטיבים עם נגטיב מקור והעתק דיגיטאלי.xlsx").parse("גיליון1")
    # print(xlcnts.head())
    # rashut_nums = xlcncts[photo_names]
    # print(rashut_nums.head())
    # get the connection between photo number and misp_rashut
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
        sds = createPhoto(mosaic, photo, xlphotos)

def getMispRashut(photo, xlcnts):
    # print("getMispRashut")
    rashut_nums = xlcnts.loc[xlcnts['neg_misp'] == photo]
    # print(rashut_nums)
    if not rashut_nums.empty:
        misp_rashut = rashut_nums.iloc[0]['misp_rashut_b']
        # misp_rashut = misp_rashut.split("/")[0]
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
    new_mosaic_site.title = new_mosaic_site.origin = mosaic_info.iloc[0]['MOTSA_E'].split('(')[0]
    new_mosaic_site.period = mosaic_info.iloc[0]['TKU_OBJ_E']
    new_mosaic_site.save()
    return new_mosaic_site


def getMosaic(misp_rashut, xlmosaics):
    mosaic_items = MosaicItem.objects.filter(misp_rashut__startswith = misp_rashut)
    if len(mosaic_items) > 0:
        return mosaic_items[0]

    #check if a mosaic site exists
    mosaic_site = getOrCreateMosaicSite(misp_rashut, xlmosaics)

    # mosaic_info = xlmosaics.loc[xlmosaics['MISP_RASHUT'] == misp_rashut]
    mosaic_info = xlmosaics.loc[xlmosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    global i
    if i<5:
        print(mosaic_info.iloc[0:3, 0:4], i)
        i = i+1
    # create new mosaic item
    new_mos = MosaicItem()
    new_mos.mosaic_site = mosaic_site
    new_mos.misp_rashut = misp_rashut
    new_mos.description = mosaic_info.iloc[0]['OBJ_DESC_E']
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
    return new_mos



    pass


def createPhoto(mosaic, photoname, xlphotos):
    # print (MosaicPicture.objects.all().delete())
    # return
    photo_row = xlphotos.loc[xlphotos['name'] == photoname]
    if not photo_row.empty:
        link = photo_row.iloc[0]['download_link']
    else:
        return
    # if len(MosaicPicture.objects.filter(negative_id=photoname)) > 0:
    #     return
    new_pic = MosaicPicture()
    new_pic.mosaic = mosaic
    new_pic.negative_id = photoname
    new_pic.picture = link
    # print(link, photoname)
    filename = uploadPic(link, photoname)
    print(photoname, filename)
    new_pic.picture = UploadedFile(open(filename, "br"))
    new_pic.save()

    pass

def uploadPic(link, photoname):
    res = requests.get(link, stream=True)
    filename = os.path.join(
        settings.BASE_DIR, f'temp_images/{photoname}.jpg'
    )
    with open(filename, 'wb') as fd:
        for chunk in res.iter_content(chunk_size=128):
            fd.write(chunk)

    return filename

