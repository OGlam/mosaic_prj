import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from main.models import Tag, MosaicItem, MosaicSite, MosaicPicture
import pandas as pd
import requests


def get_data():
    get_photos()
    xlmosaics = pd.ExcelFile("oglam-mosaics.csv.xlsx").parse("oglam-mosaics.csv")
    xl_photos = pd.ExcelFile("imports/listing_of_photos.xlsx").parse("Sheet1")
    photo_names = xl_photos.name.unique()
    ids = xlmosaics.MISP_RASHUT.unique()

    for id in ids:
        getMosaic(id, xlmosaics)

def get_photos():
    xlphotos = pd.ExcelFile("listing_of_photos.xlsx").parse("Sheet1")
    photo_names = xlphotos.name.unique()
    print(photo_names)
    xl_cnts = pd.ExcelFile("imports/Copy of רשימת חפצים ונגטיבים עם נגטיב מקור והעתק דיגיטאלי.xlsx").parse("גיליון1")
    # get the connection between photo number and misp_rashut:
    xlcnts = xlcnts.loc[xlcnts['neg_misp'].isin(photo_names)]
    xlmosaics = pd.ExcelFile("oglam-mosaics.csv.xlsx").parse("oglam-mosaics.csv")
    print("Length" + str(len(photo_names)))
    # to import from filesystem
    # from os import listdir
    # from os.path import isfile, join
    # mypath = os.path.join(settings.BASE_DIR, 'images_to_upload/')
    # photo_names = ["-".join(f.split("-",2)[:2]).split(".")[0] for f in listdir(mypath) if isfile(join(mypath, f))]
    i = 0
    photo_negative_ids = [x.negative_id for x in MosaicPicture.objects.all()]
    # for photo in photo_names:
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
        if not (photo in photo_negative_ids):
            misp_rashut = getMispRashut(photo, xlcnts)
            if misp_rashut == None:
                print("Error! can't find ", photo)
                continue
            mosaic = getMosaic(misp_rashut, xlmosaics)
            if mosaic == None:
                print("failed")
                continue
            createPhoto(mosaic, photo, xlphotos)


def get_misp_rashut(photo, xl_cnts):
    rashut_nums = xl_cnts.loc[xl_cnts['neg_misp'] == photo]

def getMispRashut(photo, xlcnts):
    rashut_nums = xlcnts.loc[xlcnts['neg_misp'] == photo]
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
    new_mosaic_site.period = str(mosaic_info.iloc[0]['TKU_OBJ_E']).lower()

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

def getMosaic(misp_rashut, xlmosaics):
    mosaic_items = MosaicItem.objects.filter(misp_rashut__startswith = misp_rashut)
    if len(mosaic_items) > 0: # TODO use exist instead of len
        return mosaic_items[0]

    # check if a mosaic site exists, if not - create it
    mosaic_site = get_or_create_mosaic_site(misp_rashut, xl_mosaics)

    # get the info from the excel
    mosaic_info = xl_mosaics.loc[xl_mosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    # create new mosaic item
    new_mos = MosaicItem()
    new_mos.mosaic_site = mosaic_site
    new_mos.save()
    print("saved item")
    new_mos.misp_rashut = misp_rashut
    new_mos.description = mosaic_info.iloc[0]['OBJ_DESC_E']
    get_dimensions_info(new_mos, mosaic_info.iloc[0]['OBJ_DIM_E'])
    tags_col = mosaic_info.iloc[0]['TIPUS_E']
    tags = Tag.objects.all()
    print("not saved", 0)
    new_mos.save()
    print("saved rashut")
    new_mos.description_en = mosaic_info.iloc[0]['OBJ_DESC_E']
    internete = mosaic_info.iloc[0]['INTERNETE']
    if internete and isinstance(internete, str):
        new_mos.description_en += ("\n" + internete)

    new_mos.description_he = mosaic_info.iloc[0]['OBJ_DESC']
    interneth = mosaic_info.iloc[0]['INTERNETH']
    if interneth and isinstance(interneth,str):
        new_mos.description_he+=("\n" + interneth)

    getDimensionsInfo(new_mos, mosaic_info.iloc[0]['OBJ_DIM_E'])

    new_mos.rishayon = mosaic_info.iloc[0]['RISHAYON']
    new_mos.save()
    print("saved rishayon")

    new_mos.materials = (mosaic_info.iloc[0]['MATERIAL_OBJ_E']).split(",")
    if isinstance(new_mos.rishayon,str) and '/' in new_mos.rishayon:
        new_mos.year = (new_mos.rishayon.split('/', 1)[1])
    if (isinstance(mosaic_info.iloc[0]['BIBE'],str)): #TODO
        new_mos.bibliography_he = mosaic_info.iloc[0]['BIBE']

    if(isinstance(mosaic_info.iloc[0]['BIBH'],str)): #TODO
        new_mos.bibliography_en = mosaic_info.iloc[0]['BIBH']


    print("not saved33", i)

    new_mos.save()
    print("saved", 0)
    print("saved", i)
    tagscol_en = split_if_needed(mosaic_info.iloc[0]['TIPUS_E'])
    tagscol_he = split_if_needed(mosaic_info.iloc[0]['TIPUS'])
    # tagscol_en = strip_spaces(tagscol_en) TODO enable after script is running
    # tagscol_he = strip_spaces(tagscol_he)


    for tag in tags:
        if tag.tag_en in str(tags_col):
            print(tag.tag_en, tags_col)
            new_mos.tags.add(tag)


    tagsFromDB = Tag.objects.all()
    for idx, tag_from_file in enumerate(tagscol_en):
        for tag_from_db in tagsFromDB:
            if tag_from_db.tag_en in str(tag_from_file):
                print(tag_from_db.tag_en, tag_from_file)
                new_mos.tags.add(tag_from_db)
        if not(tagsFromDB.filter(tag_en=tag_from_file).exists()):
            if (tag_from_file):
                new_tag = Tag()
                new_tag.tag_en = tag_from_file
                new_tag.tag_he = tagscol_he[idx]
                new_tag.save()
                new_mos.tags.add(new_tag)
    new_mos.save()
    print("finshed and saved")
    # TODO: COMPLETE THE MISSING FIELDS FOR MOSAIC ITEM
    return new_mos


def create_photo(mosaic, photo_name, xl_photos):
    photo_row = xl_photos.loc[xl_photos['name'] == photo_name]

    pass


def split_if_needed(string):
    if isinstance(string,str) and ',' in string:
        return (string).split(",")
    else:
        return [(string)]

def strip_spaces(string):
    return  [x.strip(' ') for x in string]


def     createPhoto(mosaic, photoname, xlphotos):
    photo_row = xlphotos.loc[xlphotos['name'] == photoname]
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
    new_pic.negative_id = photoname
    filename = os.path.join(
        settings.BASE_DIR, f'images_to_upload/{photo_full_name}')
    print(photoname, filename)
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
