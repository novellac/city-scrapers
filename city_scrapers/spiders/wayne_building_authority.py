# -*- coding: utf-8 -*-

# THIS SPIDER USES A MIXIN FOR SHARED FUNCTIONALITY.
# MIXINS ARE STORED IN /city-scrapers/city-scrapers/mixins
# YOU CAN OVERRIDE THE MIXIN HERE BY CREATING YOUR OWN DEFINITION.

import re
from datetime import datetime
from dateutil.parser import parse as dateparse
from city_scrapers.spider import Spider
from city_scrapers.mixins.wayne_commission import Wayne_commission


class Wayne_building_authoritySpider(Wayne_commission, Spider):
    name = 'wayne_building_authority'
    agency_id = 'Wayne County Building Authority'
    start_urls = ['https://www.waynecounty.com/boards/buildingauthority/meetings.aspx']
    meeting_name = 'Wayne County Building Authority'

    # Override the mixin for any unique attributes.
    location = {
        'name': '6th Floor, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'neighborhood': '',
    }

    def _parse_entries(self, response):
        current_year = datetime.now().year
        current_year_non_empty_rows = response.xpath('//section[contains(.,"%s")]//tbody/tr[child::td/text()]' %current_year)

        return current_year_non_empty_rows

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        # Strong text indicates a replacement meeting date
        strong_text = item.xpath('.//td[2]/strong/text()').extract_first()
        if strong_text is not None:
            date_str = strong_text
        else:
            date_str = item.xpath('.//td[2]/text()').extract_first()

        time_str = item.xpath('.//td[3]/text()').extract_first()
        date_time_str = dateparse('{0} {1}'.format(date_str, time_str))

        return {'date': date_time_str.date(), 'time': date_time_str.time(), 'note': ''}

    def _parse_status(self, item, data):
        """
        Parse or generate status of meeting.
        Postponed meetings all have replacement dates which we account for in
        the _parse_start method.
        """

        # Our status may be buried inside a number of other elements
        status_str = item.xpath('.//td[4]//text()').extract_first()
        # Meetings that are truly cancelled will be marked here.
        if 'CANCEL' in status_str.upper():
            return 'cancelled'
        # If it's not cancelled, use the status logic from spider.py
        else:
            return self._generate_status(data, '')