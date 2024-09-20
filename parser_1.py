import pandas as pd
# import numpy as np
from bs4 import BeautifulSoup
import requests
# import csv
from tqdm import tqdm

FILE_OUT_NAME = "flats_house_kg.csv"

link_base = "https://www.house.kg/kupit-kvartiru?page="

columns = ["rooms_num_square", "type_offer", "price",
           "views", "likes", "address",
           "apartment_complex", "floors", "furniture",
           "series", "building_type_year", "added_ago",
           "condition", "ceil_height", "gas", "docs",
           "heating", "parking", "is_change", "is_ipoteka",
           "is_installment", "door", "balcony", "floor",
           "different", "telephone", "internet", "security",
           "sanuzel", "user_name", "description", "analytic",
           "longitude", "latitude",
           "link"]

data = {i: [] for i in columns}


def get_text_for_analytic(text):
    res = ""
    flag = False
    for i in text:
        if i == "<":
            flag = True
        elif i == ">":
            flag = False
        elif flag:
            continue
        elif i not in ("\t", "\n"):
            res += i

    return res


right_border = int(input("Until which page do you want to parse: "))  # 648


for i in tqdm(range(1, right_border+1), desc='Парсинг страниц'):
    link = link_base + str(i)
    page_req = requests.get(link)
    page_soup = BeautifulSoup(page_req.text, "html.parser")
    page_table = page_soup.find("div", attrs={"class": "listings-wrapper"})

    if page_table is None:
        continue

    flats = page_table.find_all("div",
                                attrs={"itemtype": "https://schema.org/Apartment", "class": "listing"})
    for flat in flats:
        flat_data = {i: None for i in columns}
        flat_link = "https://www.house.kg" + flat.find("a")["href"]
        flat_data["link"] = flat_link
        flat_req = requests.get(flat_link)
        flat_soup = BeautifulSoup(flat_req.text, "html.parser")

        header = flat_soup.find("div", attrs={"class": "details-header"})
        description_check = flat_soup.find("div", attrs={"class": "details-main"})

        if description_check is None or header is None:
            continue

        description = description_check.find("div", attrs={"class": "left"})

        user_name = flat_soup.find("div", attrs={"id": "block-user"})
        description_from_user = flat_soup.find("div", attrs={"class": "description"})

        map_div = flat_soup.find("div", attrs={"class": "map-wrapper"})
        if map_div is not None:
            flat_data["longitude"] = map_div.find("div", id="map2gis").get("data-lon")
            flat_data["latitude"] = map_div.find("div", id="map2gis").get("data-lat")

        analytic = flat_soup.find_all("p", attrs={"class": "compare-text with-dot"})

        if analytic is not None and len(analytic) > 1:
            flat_data["analytic"] = get_text_for_analytic(analytic[0].text) + "\n" + get_text_for_analytic(analytic[1].text)

        if description_from_user is not None:
            flat_data["description"] = description_from_user.find("p").text.strip()

        if user_name is not None:
            flat_data["user_name"] = user_name.find("a", attrs={"class": "name"}).text.strip()

        rooms_num_square = header.find("h1")
        if rooms_num_square is not None:
            flat_data["rooms_num_square"] = rooms_num_square.text.strip()

        address = header.find("div", attrs={"class": "address"})
        if address is not None:
            flat_data["address"] = address.text.strip()

        apartment_complex = header.find("div", attrs={"class": "c-name"})
        if apartment_complex is not None:
            flat_data["apartment_complex"] = apartment_complex.text.strip()

        price = header.find('div', attrs={"class": "price-som"})
        if price is not None:
            flat_data["price"] = price.text.strip()

        views = header.find("span", attrs={"class": "view-count"})
        if views is not None:
            flat_data["views"] = views.text.strip()

        likes = header.find("span", attrs={"class": "favourite-count table-comments"})
        if likes is not None:
            flat_data["likes"] = likes.text.strip()

        added_ago = header.find("span", attrs={"class": "added-span"})
        if added_ago is not None:
            flat_data["added_ago"] = added_ago.text.strip()

        type_offer = description.find("div", string="Тип предложения")
        if type_offer is not None:
            flat_data["type_offer"] = type_offer.find_next("div", attrs={"class": "info"}).text.strip()

        floors = description.find("div", string="Этаж")
        if floors is not None:
            flat_data["floors"] = floors.find_next("div", attrs={"class": "info"}).text.strip()

        furniture = description.find("div", string="Мебель")
        if furniture is not None:
            flat_data["furniture"] = furniture.find_next("div", attrs={"class": "info"}).text.strip()

        series = description.find("div", string="Серия")
        if series is not None:
            flat_data["series"] = series.find_next("div", attrs={"class": "info"}).text.strip()

        building = description.find("div", string="Дом")
        if building is not None:
            flat_data["building_type_year"] = building.find_next("div", attrs={"class": "info"}).text.strip()

        condition = description.find("div", string="Состояние")
        if condition is not None:
            flat_data["condition"] = condition.find_next("div", attrs={"class": "info"}).text.strip()

        ceil_height = description.find("div", string="Высота потолков")
        if ceil_height is not None:
            flat_data["ceil_height"] = ceil_height.find_next("div", attrs={"class": "info"}).text.strip()

        parking = description.find("div", string="Парковка")
        if parking is not None:
            flat_data["parking"] = parking.find_next("div", attrs={"class": "info"}).text.strip()

        docs = description.find("div", string="Правоустанавливающие документы")
        if docs is not None:
            flat_data["docs"] = docs.find_next("div", attrs={"class": "info"}).text.strip()

        heating = description.find("div", string="Отопление")
        if heating is not None:
            flat_data["heating"] = heating.find_next("div", attrs={"class": "info"}).text.strip()

        gas = description.find("div", string="Газ")
        if gas is not None:
            flat_data["gas"] = gas.find_next("div", attrs={"class": "info"}).text.strip()

        is_change = description.find("div", string="Возможность обмена")
        if is_change is not None:
            flat_data["is_change"] = is_change.find_next("div", attrs={"class": "info"}).text.strip()

        is_ipoteka = description.find("div", string="Возможность ипотеки")
        if is_ipoteka is not None:
            flat_data["is_ipoteka"] = is_ipoteka.find_next("div", attrs={"class": "info"}).text.strip()

        is_installment = description.find("div", string="Возможность рассрочки")
        if is_installment is not None:
            flat_data["is_installment"] = is_installment

        door = description.find("div", string="Входная дверь")
        if door is not None:
            flat_data["door"] = door.find_next("div", attrs={"class": "info"}).text.strip()

        balcony = description.find("div", string="Балкон")
        if balcony is not None:
            flat_data["balcony"] = balcony.find_next("div", attrs={"class": "info"}).text.strip()

        floor = description.find("div", string="Пол")
        if floor is not None:
            flat_data["floor"] = floor.find_next("div", attrs={"class": "info"}).text.strip()

        different = description.find("div", string="Разное")
        if different is not None:
            flat_data["different"] = different.find_next("div", attrs={"class": "info"}).text.strip()

        telephone = description.find("div", string="Телефон")
        if telephone is not None:
            flat_data["telephone"] = telephone.find_next("div", attrs={"class": "info"}).text.strip()

        internet = description.find("div", string="Интернет")
        if internet is not None:
            flat_data["internet"] = internet.find_next("div", attrs={"class": "info"}).text.strip()

        security = description.find("div", string="Безопасность")
        if security is not None:
            flat_data["security"] = security.find_next("div", attrs={"class": "info"}).text.strip()

        sanuzel = description.find("div", string="Санузел")
        if sanuzel is not None:
            flat_data["sanuzel"] = sanuzel.find_next("div", attrs={"class": "info"}).text.strip()

        for column in flat_data:
            data[column].append(flat_data[column])


df = pd.DataFrame(data)
df.to_csv(FILE_OUT_NAME, index=False)
print('End of program')
