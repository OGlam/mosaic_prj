import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from main.models import Tag, MosaicItem, MosaicSite, MosaicPicture
import pandas as pd
import requests


def get_data():
    get_photos()
    xlmosaics = pd.ExcelFile("imports/oglam-mosaics.csv.xlsx").parse("oglam-mosaics.csv")
    ids = xlmosaics.MISP_RASHUT.unique()

    for id in ids:
        get_mosaic(id, xlmosaics)


def get_photos():
    xlphotos = pd.ExcelFile("imports/listing_of_photos.xlsx").parse("Sheet1")
    photo_names = xlphotos.name.unique()
    print(photo_names)
    xlcnts = pd.ExcelFile("imports/Copy of רשימת חפצים ונגטיבים עם נגטיב מקור והעתק דיגיטאלי.xlsx").parse("גיליון1")
    # get the connection between photo number and misp_rashut:
    xlcnts = xlcnts.loc[xlcnts['neg_misp'].isin(photo_names)]
    xlmosaics = pd.ExcelFile("imports/oglam-mosaics.csv.xlsx").parse("oglam-mosaics.csv")
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
            if misp_rashut == None:
                print("Error! can't find ", photo)
                continue
            mosaic = get_mosaic(misp_rashut, xlmosaics)
            if mosaic == None:
                print("failed")
                continue
            create_photo(mosaic, photo, xlphotos)


def get_misp_rashut(photo, xlcnts):
    rashut_nums = xlcnts.loc[xlcnts['neg_misp'] == photo]
    if not rashut_nums.empty:
        misp_rashut = rashut_nums.iloc[0]['misp_rashut_b']
        return misp_rashut
    pass


i = 0


def get_or_create_mosaic_site(misp_rashut, xlmosaics):
    mosaic_info = xlmosaics.loc[xlmosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    site_id = mosaic_info.iloc[0]['MOTSA_E'].split('(')[1].split(')')[0]
    mosaic_sites = MosaicSite.objects.filter(site_id=site_id)
    if len(mosaic_sites) > 0:
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
    else:
        return 100
    pass


def get_dimensions_info(new_mos, obj_dimensions_str):
    if obj_dimensions_str is None or not (isinstance(obj_dimensions_str, str)):
        return
    obj_dimensions_str = obj_dimensions_str.lower().replace("length", "\nlength").replace("width", "\nwidth"). \
        replace("area", "\narea").replace("other", "\nother").replace("thickness","\nthickness").\
        replace("height","\nheight").replace("\n\n", "\n")
    dimensions = str(obj_dimensions_str).split("\n")
    print(dimensions)
    for dimension in dimensions:
        nums = [int(s) for s in dimension.split() if s.isdigit()]
        if len(nums) > 1:
            print("too many numbers can't parse - ", dimension)
            continue
        if len(nums) == 0:
            print("no numbers to parse", dimension)
            continue
        if "length" in dimension.lower() or "height" in dimension.lower():
            print("Success", dimension)
            new_mos.length = nums[0] * get_coef(dimension)
            continue
        if "width" in dimension.lower():
            print("Success", dimension)
            new_mos.width = nums[0] * get_coef(dimension)
            continue
        if "area" in dimension.lower():
            print("Success", dimension)
            new_mos.area = nums[0] * get_coef(dimension)
            continue
        print("Failed", dimension)
    pass


def get_mosaic(misp_rashut, xlmosaics):
    mosaic_items = MosaicItem.objects.filter(misp_rashut__startswith=misp_rashut)
    if len(mosaic_items) > 0:  # TODO use exist instead of len
        return mosaic_items[0]

    # check if a mosaic site exists, if not - create it
    mosaic_site = get_or_create_mosaic_site(misp_rashut, xlmosaics)

    # get the info from the excel

    mosaic_info = xlmosaics.loc[xlmosaics['MISP_RASHUT'].str.startswith(misp_rashut)]
    # create new mosaic item
    new_mos = MosaicItem()
    new_mos.mosaic_site = mosaic_site
    new_mos.save()
    print("saved item")
    new_mos.misp_rashut = misp_rashut
    new_mos.save()
    print("saved rashut")
    new_mos.description_en = mosaic_info.iloc[0]['OBJ_DESC_E']
    internete = mosaic_info.iloc[0]['INTERNETE']
    if internete and isinstance(internete, str):
        new_mos.description_en += ("\n" + internete)

    new_mos.description_he = mosaic_info.iloc[0]['OBJ_DESC']
    interneth = mosaic_info.iloc[0]['INTERNETH']
    if interneth and isinstance(interneth, str):
        new_mos.description_he += ("\n" + interneth)

    get_dimensions_info(new_mos, mosaic_info.iloc[0]['OBJ_DIM_E'])

    new_mos.rishayon = mosaic_info.iloc[0]['RISHAYON']
    new_mos.save()
    print("saved rishayon")

    new_mos.materials = (mosaic_info.iloc[0]['MATERIAL_OBJ_E']).split(",")
    if isinstance(new_mos.rishayon, str) and '/' in new_mos.rishayon:
        new_mos.year = (new_mos.rishayon.split('/', 1)[1])
    if (isinstance(mosaic_info.iloc[0]['BIBE'], str)):  # TODO
        new_mos.bibliography_he = mosaic_info.iloc[0]['BIBE']

    if (isinstance(mosaic_info.iloc[0]['BIBH'], str)):  # TODO
        new_mos.bibliography_en = mosaic_info.iloc[0]['BIBH']

    print("not saved33", i)

    new_mos.save()
    print("saved", i)
    tagscol_en = split_if_needed(mosaic_info.iloc[0]['TIPUS_E'])
    tagscol_he = split_if_needed(mosaic_info.iloc[0]['TIPUS'])
    # tagscol_en = strip_spaces(tagscol_en) TODO enable after script is running
    # tagscol_he = strip_spaces(tagscol_he)




    tagsFromDB = Tag.objects.all()
    for idx, tag_from_file in enumerate(tagscol_en):
        for tag_from_db in tagsFromDB:
            if tag_from_db.tag_en in str(tag_from_file):
                print(tag_from_db.tag_en, tag_from_file)
                new_mos.tags.add(tag_from_db)
        if not (tagsFromDB.filter(tag_en=tag_from_file).exists()):
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


def split_if_needed(string):
    if isinstance(string, str) and ',' in string:
        return (string).split(",")
    else:
        return [(string)]


def strip_spaces(string):
    return [x.strip(' ') for x in string]


def create_photo(mosaic, photoname, xlphotos):
    photo_row = xlphotos.loc[xlphotos['name'] == photoname]
    if not photo_row.empty:
        link = photo_row.iloc[0]['download_link']
        photo_full_name = photo_row.iloc[0]['name_orig']
        filename = os.path.join(settings.BASE_DIR, f'images_to_upload/{photo_full_name}')
        if not (os.path.exists(filename) and os.path.isfile(filename)):
            filename = download_pic(link, photo_full_name)
    else:
        return
    new_pic = MosaicPicture()
    new_pic.mosaic = mosaic
    new_pic.negative_id = photoname
    print(photoname, filename)
    try:
        file_object = open(filename, "br")
        print("opened ", filename)
    except IOError:
        print("Could not open file! Make sure the file is in the folder", filename)
    new_pic.picture = UploadedFile(file_object)
    new_pic.save()
    pass


def download_pic(link, photoname):
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
