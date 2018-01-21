import os
import random

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from main.models import Tag, MosaicItem, MosaicSite, MosaicPicture
import pandas as pd
import requests


def get_data():
    xlmosaics = pd.ExcelFile("imports/oglam-mosaics.csv.xlsx").parse("oglam-mosaics.csv")
    get_photos(xlmosaics)
    ids = xlmosaics.MISP_RASHUT.unique()

    for id in ids:
        get_mosaic(id, xlmosaics)


def get_photos(xlmosaics):
    xlphotos = pd.ExcelFile("imports/listing_of_photos.xlsx").parse("Sheet1")
    photo_names = xlphotos.name.unique()
    print(photo_names)
    xlcnts = pd.ExcelFile("imports/Copy of רשימת חפצים ונגטיבים עם נגטיב מקור והעתק דיגיטאלי.xlsx").parse("גיליון1")
    # get the connection between photo number and misp_rashut:
    xlcnts = xlcnts.loc[xlcnts['neg_misp'].isin(photo_names)]
    print("Length" + str(len(photo_names)))
    # to import from filesystem
    # from os import listdir
    # from os.path import isfile, join
    # mypath = os.path.join(settings.BASE_DIR, 'images_to_upload/')
    # photo_names = ["-".join(f.split("-",2)[:2]).split(".")[0] for f in listdir(mypath) if isfile(join(mypath, f))]
    photo_negative_ids = [x.negative_id for x in MosaicPicture.objects.all()]
    # for photo in photo_names:
    for photo in photo_names:
        if not (photo in photo_negative_ids):
            misp_rashut = get_misp_rashut(photo, xlcnts)
            if not misp_rashut:
                print("Error! can\'t find ", photo)
                continue
            mosaic = get_mosaic(misp_rashut, xlmosaics)
            if not mosaic:
                print("failed")
                continue
            create_photo(mosaic, photo, xlphotos)


def get_misp_rashut(photo, xlcnts):
    rashut_nums = xlcnts.loc[xlcnts['neg_misp'] == photo]
    if not rashut_nums.empty:
        misp_rashut = rashut_nums.iloc[0]['misp_rashut_b']
        return misp_rashut
    return None


def get_or_create_mosaic_site(misp_rashut, xl_mosaics):
    mosaic_info = xl_mosaics.loc[xl_mosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    site_id = mosaic_info.iloc[0]['MOTSA_E'].split('(')[1].split(')')[0]
    mosaic_site = MosaicSite.objects.filter(site_id=site_id).first()
    if mosaic_site:
        return mosaic_site

    # else create a new site
    new_mosaic_site = MosaicSite()
    print("site_id", site_id)
    new_mosaic_site.site_id = site_id
    new_mosaic_site.featured = True
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


def get_dimensions_info(obj_dimensions_str):
    d = {}

    if not obj_dimensions_str:
        return d

    dimensions = str(obj_dimensions_str).split("\n")

    for dimension in dimensions:
        nums = [int(s) for s in dimension.split() if s.isdigit()]
        if len(nums) > 1:
            print("too many numbers can't parse")
            return d
        if len(nums) == 0:
            print("no numbers to parse")
            return d
        if "length" in dimension.lower() or "height" in dimension.lower():
            d['length'] = nums[0] * get_coef(dimension)
            continue
        if "width" in dimension.lower():
            d['width'] = nums[0] * get_coef(dimension)
            continue
        if "area" in dimension.lower():
            d['area'] = nums[0] * get_coef(dimension)
    return d


def get_mosaic(misp_rashut, xl_mosaics):
    mosaic_item = MosaicItem.objects.filter(misp_rashut__startswith=misp_rashut).first()
    if mosaic_item:
        return mosaic_item

    # check if a mosaic site exists, if not - create it
    mosaic_site = get_or_create_mosaic_site(misp_rashut, xl_mosaics)

    # get the info from the excel
    mosaic_info = xl_mosaics.loc[xl_mosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    # create new mosaic item
    new_mos = MosaicItem()
    new_mos.mosaic_site = mosaic_site
    new_mos.misp_rashut = misp_rashut

    new_mos.description_en = mosaic_info.iloc[0]['OBJ_DESC_E']
    internete = mosaic_info.iloc[0]['INTERNETE']
    if internete and isinstance(internete, str):
        new_mos.description_en += ("\n" + internete)

    new_mos.description_he = mosaic_info.iloc[0]['OBJ_DESC']
    interneth = mosaic_info.iloc[0]['INTERNETH']
    if interneth and isinstance(interneth, str):
        new_mos.description_he += ("\n" + interneth)

    dimensions = get_dimensions_info(mosaic_info.iloc[0]['OBJ_DIM_E'])
    new_mos.length = dimensions.get('length', None)
    new_mos.width = dimensions.get('width', None)
    new_mos.area = dimensions.get('area', None)

    new_mos.rishayon = mosaic_info.iloc[0]['RISHAYON']

    new_mos.materials = (mosaic_info.iloc[0]['MATERIAL_OBJ_E']).split(",")
    if isinstance(new_mos.rishayon, str) and '/' in new_mos.rishayon:
        new_mos.year = (new_mos.rishayon.split('/', 1)[1])
    if (isinstance(mosaic_info.iloc[0]['BIBE'], str)):  # TODO
        new_mos.bibliography_he = mosaic_info.iloc[0]['BIBE']
    if (isinstance(mosaic_info.iloc[0]['BIBH'], str)):  # TODO
        new_mos.bibliography_en = mosaic_info.iloc[0]['BIBH']

    tagscol_en = split_if_needed(mosaic_info.iloc[0]['TIPUS_E'])
    tagscol_he = split_if_needed(mosaic_info.iloc[0]['TIPUS'])
    # tagscol_en = strip_spaces(tagscol_en) TODO enable after script is running
    # tagscol_he = strip_spaces(tagscol_he)

    new_mos.save()  # Save object to we can add m2m relation.

    tags = Tag.objects.all()
    for idx, tag_from_file in enumerate(tagscol_en):
        for tag_from_db in tags:
            if tag_from_db.tag_en in str(tag_from_file):
                print(tag_from_db.tag_en, tag_from_file)
                new_mos.tags.add(tag_from_db)
        if not tags.filter(tag_en=tag_from_file).exists():
            if tag_from_file:
                new_tag = Tag.objects.create(
                    tag_en=tag_from_file,
                    tag_he=tagscol_he[idx]
                )
                new_mos.tags.add(new_tag)
    # TODO: COMPLETE THE MISSING FIELDS FOR MOSAIC ITEM

    return new_mos


def split_if_needed(string):
    if isinstance(string, str) and ',' in string:
        return string.split(",")
    return [string]


def strip_spaces(string):
    return [x.strip(' ') for x in string]


def create_photo(mosaic, photoname, xlphotos):
    photo_row = xlphotos.loc[xlphotos['name'] == photoname]
    if not photo_row.empty:
        link = photo_row.iloc[0]['download_link']
        photo_full_name = photo_row.iloc[0]['name_orig']
        filename = os.path.join(settings.BASE_DIR,  'images_to_upload/{}'.format(photo_full_name))
        if not (os.path.exists(filename) and os.path.isfile(filename)):
            filename = download_pic(link, photo_full_name)
    else:
        return
    new_pic = MosaicPicture()
    new_pic.is_cover = random.choice([True, False])
    new_pic.mosaic = mosaic
    new_pic.negative_id = photoname
    print(photoname, filename)
    try:
        file_object = open(filename, "br")
        print("opened ", filename)
        new_pic.picture = UploadedFile(file_object)
    except IOError:
        # In this case we don't save the object because picture field is required
        print("Could not open file! Make sure the file is in the folder", filename)
        return False
    new_pic.save()

    # TODO: ADD MISSING FIELDS TO MOSAIC PICTURE


def download_pic(link, photo_name):
    res = requests.get(link, stream=True)
    if not os.path.exists(os.path.join(settings.BASE_DIR, 'images_to_upload')):
        os.makedirs(os.path.join(settings.BASE_DIR, 'images_to_upload'))
    filename = os.path.join(
        settings.BASE_DIR, 'images_to_upload/{}'.format(photo_name)
    )
    with open(filename, 'wb') as fd:
        for chunk in res.iter_content(chunk_size=128):
            fd.write(chunk)

    return filename





def add_info_to_pictures():
    picture_rows = pd.ExcelFile("imports/רשימת חפצים ונגטיבים עם מידע על הנגטיבים (1).xlsx").parse("גיליון1")
    picture_names = picture_rows.neg_misp.unique()
    pictures_in_db = MosaicPicture.objects.filter(negative_id__in=picture_names)
    for picture in pictures_in_db:
        picture_info = picture_rows.loc[picture_rows['neg_misp'] == picture.negative_id]
        date = picture_info.iloc[0].neg_date
        photographer_eng = picture_info.iloc[0].photographer_en
        photographer_he = picture_info.iloc[0].photographer_he
        # print (date, type(date), pd.to_datetime(date), photographer_eng, photographer_he)
        picture.taken_date = parse_date(date)
        picture.photographer_name_en = parse_name(photographer_eng)
        picture.photographer_name_he = parse_name(photographer_he)
        picture.save()


def parse_date(date):
    if date:
        return pd.to_datetime(date)
    return None

def parse_name(photographer):
    if "unknown" in photographer.lower() or "לא ידוע" in photographer or not photographer:
        return ""
    return photographer