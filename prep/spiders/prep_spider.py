import re
import scrapy


def clean_name(dirty):
    clean = re.sub("[^\w ]", " ", dirty.lower())
    clean = re.sub(" +", " ", clean)

    return clean


class PrepSpider(scrapy.Spider):
    name = "prep"
    start_urls = [
        "http://prep.jornada.com.mx/rptDistrital_part.html"
    ]

    def parse(self, response):
        yield self.parse_summary(response)

        rows = response.css("div#DivRoot tbody tr")
        a_elements = [row.css("td a") for row in rows]
        for a in a_elements:
            link = a.css("::attr(href)").extract_first()
            district = a.css("::text").extract_first()
            yield response.follow(link, self.parse_district, meta={"district": district})

    def parse_summary(self, response):
        table = response.css("div#DivRoot table")
        thead = table.css("thead")
        tbody = table.css("tbody")

        column_head = thead.css("tr")[2].css("td")
        column_names = ['']*len(column_head)

        # extract column names
        for i, td in enumerate(column_head):
            img = td.css("img")
            if not img:
                column_names[i] = clean_name(" ".join(td.css("strong::text").extract()))
            else:
                img_name = img.css("::attr(src)").extract_first()
                column_names[i] = clean_name(re.search("/(.+)\.gif$", img_name).group(1))

        # some extra columns are needed
        column_names.insert(3, "actas_capturadas_prop")
        column_names.insert(5, "actas_contabilizadas_prop")
        column_names.insert(7, "actas_con_inconsistencias_prop")

        # extract data (sorry for the one liner)
        rows = tbody.css("tr")
        data = [[" ".join(col.css("::text").extract()) for col in row.css("td")] for row in rows]

        return {
            "district": "summary",
            "names": column_names,
            "data": data
        }

    def parse_district(self, response):
        table = response.css("div#DivRoot table")
        thead = table.css("thead")
        tbody = table.css("tbody")

        column_head = thead.css("td")
        column_names = ['']*len(column_head)

        # extract column names
        for i, td in enumerate(column_head):
            img = td.css("img")
            if not img:
                column_names[i] = clean_name(" ".join(td.css("strong::text").extract()))
            else:
                img_name = img.css("::attr(src)").extract_first()
                column_names[i] = clean_name(re.search("/(.+)\.gif$", img_name).group(1))

        # extract data (sorry for the one liner)
        rows = tbody.css("tr")
        data = [[" ".join(col.css("::text").extract()) for col in row.css("td")] for row in rows]

        return {
            "district": response.meta["district"],
            "names": column_names,
            "data": data
        }